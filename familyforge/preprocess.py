"""
Classical preprocessing for scanned family photos.
Straighten, crop borders, reduce dust, improve contrast.
Requires: opencv-python, numpy
"""
from pathlib import Path
from typing import Tuple, List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    HAS_CV = True
except ImportError:
    HAS_CV = False

def _require_cv():
    if not HAS_CV:
        raise ImportError("Please install opencv-python and numpy:\npip install opencv-python numpy")

def deskew(image, max_angle: float = 15.0):
    """Correct small rotation."""
    _require_cv()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image, 0.0
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 500:
        return image, 0.0
    rect = cv2.minAreaRect(largest)
    angle = rect[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) > max_angle or abs(angle) < 0.3:
        return image, 0.0
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated, float(angle)

def auto_crop(image, padding: int = 12, min_area_ratio: float = 0.05):
    """Remove large scanner borders."""
    _require_cv()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
    h, w = gray.shape
    min_area = min_area_ratio * h * w
    good = [c for c in contours if cv2.contourArea(c) >= min_area]
    if not good:
        return image
    xs, ys, ws, hs = zip(*(cv2.boundingRect(c) for c in good))
    x = max(0, min(xs) - padding)
    y = max(0, min(ys) - padding)
    x2 = min(w, max([xx + ww for xx, ww in zip(xs, ws)]) + padding)
    y2 = min(h, max([yy + hh for yy, hh in zip(ys, hs)]) + padding)
    return image[y:y2, x:x2]

def reduce_artifacts(image, ksize: int = 3):
    _require_cv()
    if ksize % 2 == 0:
        ksize += 1
    return cv2.medianBlur(image, ksize)

def enhance(image, clip_limit: float = 2.0):
    _require_cv()
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    l = clahe.apply(l)
    l = cv2.normalize(l, None, 0, 255, cv2.NORM_MINMAX)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

def process_photo(input_path, output_path, do_deskew=True, do_crop=True, do_artifacts=True, do_enhance=True, jpeg_quality=92):
    """Process one photo."""
    _require_cv()
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(input_path))
    if img is None:
        raise ValueError(f"Could not read {input_path}")
    orig_shape = img.shape[:2]
    angle = 0.0
    if do_deskew:
        img, angle = deskew(img)
    if do_crop:
        img = auto_crop(img)
    if do_artifacts:
        img = reduce_artifacts(img)
    if do_enhance:
        img = enhance(img)
    if output_path.suffix.lower() not in {".jpg", ".jpeg"}:
        if input_path.suffix.lower() in {".tif", ".tiff"}:
            output_path = output_path.with_suffix(".jpg")
    cv2.imwrite(str(output_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    return {
        "input": str(input_path),
        "output": str(output_path),
        "original_size": orig_shape[::-1],
        "final_size": (img.shape[1], img.shape[0]),
        "deskew_angle": round(angle, 2),
    }

def process_batch(input_dir, output_dir, **kwargs):
    """Process all images in a folder."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
    files = sorted(f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in exts)
    results = []
    for f in files:
        out = output_dir / f.name
        try:
            results.append(process_photo(f, out, **kwargs))
        except Exception as e:
            logger.error("Failed %s: %s", f, e)
            results.append({"input": str(f), "error": str(e)})
    return results

# Aliases for the package __init__
process_one = process_photo
process_folder = process_batch
