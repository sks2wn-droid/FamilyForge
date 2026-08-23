"""
FamilyForge classical image preprocessing for scanned family photos.

- Deskew (straighten)
- Auto-crop scanner borders
- Dust / scratch reduction
- Auto levels + CLAHE enhancement

Requires: opencv-python-headless, numpy, Pillow
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


def _to_bgr(image: Union[np.ndarray, Image.Image]) -> np.ndarray:
    if isinstance(image, Image.Image):
        rgb = np.array(image.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    return image.copy()


def deskew(image: np.ndarray, max_angle: float = 15.0) -> Tuple[np.ndarray, float]:
    """Detect and correct small skew. Returns (image, angle_degrees)."""
    img = _to_bgr(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=100,
        minLineLength=max(img.shape[1] // 4, 50), maxLineGap=20
    )
    angle = 0.0
    if lines is not None and len(lines) > 0:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:
                continue
            ang = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if ang < -45:
                ang += 90
            elif ang > 45:
                ang -= 90
            angles.append(ang)
        if angles:
            angle = float(np.median(angles))

    if abs(angle) < 0.3:
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 0.1 * img.shape[0] * img.shape[1]:
                rect = cv2.minAreaRect(largest)
                angle = rect[-1]
                if angle < -45:
                    angle += 90
                elif angle > 45:
                    angle -= 90

    if abs(angle) > max_angle or abs(angle) < 0.2:
        return img, 0.0

    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated, angle


def auto_crop(image: np.ndarray, padding: int = 8, min_area_ratio: float = 0.15) -> np.ndarray:
    """Remove scanner borders / background by finding the main photo contour."""
    img = _to_bgr(image)
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 10
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img
    candidates = [c for c in contours if cv2.contourArea(c) > min_area_ratio * h * w]
    if not candidates:
        candidates = [max(contours, key=cv2.contourArea)]
    largest = max(candidates, key=cv2.contourArea)
    x, y, cw, ch = cv2.boundingRect(largest)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(w, x + cw + padding)
    y2 = min(h, y + ch + padding)
    cropped = img[y1:y2, x1:x2]
    return cropped if cropped.size > 0 else img


def reduce_artifacts(image: np.ndarray, strength: str = "mild") -> np.ndarray:
    """Mild median + selective inpaint for dust/scratches."""
    img = _to_bgr(image)
    ksize = {"mild": 3, "medium": 5, "strong": 7}.get(strength, 3)
    denoised = cv2.medianBlur(img, ksize)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    _, dark_mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)
    for c in contours:
        if cv2.contourArea(c) < 40:
            cv2.drawContours(mask, [c], -1, 255, -1)
    if np.any(mask):
        return cv2.inpaint(denoised, mask, 3, cv2.INPAINT_TELEA)
    return denoised


def enhance(image: np.ndarray, use_clahe: bool = True, clip_limit: float = 2.0) -> np.ndarray:
    """Percentile auto-levels + optional CLAHE on L channel."""
    img = _to_bgr(image).astype(np.float32)
    for c in range(3):
        channel = img[:, :, c]
        p_low, p_high = np.percentile(channel, (1, 99))
        if p_high > p_low:
            img[:, :, c] = np.clip((channel - p_low) * 255.0 / (p_high - p_low), 0, 255)
    img = np.uint8(img)
    if use_clahe:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return img


def process_photo(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    do_deskew: bool = True,
    do_crop: bool = True,
    do_artifacts: bool = True,
    do_enhance: bool = True,
    artifact_strength: str = "mild",
    suffix: str = "_enhanced",
    quality: int = 95,
) -> Optional[Path]:
    """Run the full classical pipeline on one photo."""
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
        if img is None:
            pil = Image.open(input_path)
            img = _to_bgr(pil)
        if do_deskew:
            img, _ = deskew(img)
        if do_crop:
            img = auto_crop(img)
        if do_artifacts:
            img = reduce_artifacts(img, strength=artifact_strength)
        if do_enhance:
            img = enhance(img)
        stem = input_path.stem + suffix
        ext = input_path.suffix.lower()
        if ext in {".tif", ".tiff"}:
            out_path = output_dir / f"{stem}.tif"
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            Image.fromarray(rgb).save(out_path, compression="tiff_lzw")
        else:
            out_path = output_dir / f"{stem}.jpg"
            cv2.imwrite(str(out_path), img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        logger.info(f"Processed {input_path.name} -> {out_path.name}")
        return out_path
    except Exception as e:
        logger.error(f"Failed to process {input_path}: {e}")
        return None


def process_batch(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    recursive: bool = False,
    **kwargs,
) -> List[Path]:
    """Process all supported images in a folder."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    pattern = "**/*" if recursive else "*"
    results = []
    for path in sorted(input_dir.glob(pattern)):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            out = process_photo(path, output_dir, **kwargs)
            if out:
                results.append(out)
    logger.info(f"Batch complete: {len(results)} photos processed")
    return results
