# OCR for Family Photo Backs

## Quick reality check (2026)

Open-source OCR is still limited on cursive handwriting found on the backs of old family photos.

- **Tesseract** (what we ship first): Excellent on clean *printed* text (dates, studio stamps, names). Weak on cursive handwriting.
- EasyOCR / PaddleOCR: Somewhat better on handwriting but still far from perfect and heavier to install.

## What we recommend for FamilyForge right now

Use the built-in Tesseract pipeline for:
- Printed dates
- Studio stamps
- Clear block-letter notes

For difficult cursive, the best free approach is still to read it yourself and type the note into the photo’s metadata.

## Installation (Windows)

1. Install Tesseract from the official Windows installer:
   https://github.com/UB-Mannheim/tesseract/wiki
2. During install, note the path (usually `C:\Program Files\Tesseract-OCR`)
3. Add that folder to your system PATH, or tell pytesseract where it is:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```
4. In the FamilyForge virtual environment:
   ```bat
   pip install pytesseract
   ```

After that the OCR button will work.
