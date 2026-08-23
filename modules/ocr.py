"""
Simple OCR helpers for FamilyForge.
Focused on photo backs, stamps, and printed notes.
Requires: pytesseract + system Tesseract OCR
"""
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

def is_available() -> bool:
    return HAS_OCR

def preprocess_for_ocr(image_path: str, enhance: bool = True):
    """Prepare a photo (or photo back) for better OCR results."""
    if not HAS_OCR:
        raise ImportError("pytesseract, opencv-python, pillow required")
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if enhance:
        # Contrast + denoise
        gray = cv2.equalizeHist(gray)
        gray = cv2.medianBlur(gray, 3)
    # Adaptive threshold often works better on faded paper
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return thresh

def extract_text(
    image_path: str,
    lang: str = "eng",
    psm: int = 6,
    preprocess: bool = True,
) -> Tuple[str, float]:
    """
    Extract text from an image.
    Returns (text, average_confidence).
    Confidence is approximate (0-100).
    """
    if not HAS_OCR:
        return "[OCR not available – install pytesseract and Tesseract OCR]", 0.0

    try:
        if preprocess:
            processed = preprocess_for_ocr(image_path)
            # pytesseract can take numpy array
            data = pytesseract.image_to_data(
                processed, lang=lang, config=f"--psm {psm}", output_type=pytesseract.Output.DICT
            )
        else:
            data = pytesseract.image_to_data(
                Image.open(image_path), lang=lang, config=f"--psm {psm}", output_type=pytesseract.Output.DICT
            )

        texts = []
        confs = []
        for i, conf in enumerate(data["conf"]):
            if int(conf) > 0:  # -1 means no recognition
                txt = data["text"][i].strip()
                if txt:
                    texts.append(txt)
                    confs.append(int(conf))

        full_text = " ".join(texts).strip()
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return full_text, avg_conf
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return f"[OCR error: {e}]", 0.0

def extract_text_simple(image_path: str) -> str:
    """Convenience wrapper – just return the text string."""
    text, _ = extract_text(image_path)
    return text

if __name__ == "__main__":
    print("OCR module ready." if HAS_OCR else "OCR dependencies missing.")
