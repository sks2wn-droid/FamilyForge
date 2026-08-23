# FamilyForge

**Easy, free, private toolkit for digitizing and organizing family photos.**

Turn boxes of old prints into a clean, searchable digital archive. No subscriptions. Everything stays on your computer.

---

## Fastest way to start (ZIP)

1. **Download the ZIP**  
   Go to the green **Code** button on this page → **Download ZIP**.  
   (Or grab a release if one is available.)

2. **Extract** the folder anywhere you like.

3. **Run it**

   **Windows**  
   Double-click `start.bat`

   **Mac / Linux**  
   Open Terminal in the folder and run:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

4. Your browser will open automatically with the FamilyForge interface.

That’s it. The first run installs the needed packages (takes a minute or two). After that it starts almost instantly.

---

## What you can do today

- Point it at a folder of scanned photos
- Automatically straighten, crop scanner borders, and improve faded pictures
- Start naming the people in the photos
- Keep everything private and local

Later we can add AI face restoration, full face recognition, photo books, and Immich integration — the friendly interface is already ready for them.

---

## Requirements

- Python 3.9 or newer (most computers already have it)
- That’s all for the core experience

Optional later: a GPU for faster AI restore (not required).

---

## Manual start (if you prefer)

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Project layout

- `app.py` – the easy-to-use interface
- `db.py` – keeps track of your photos and people
- `familyforge/` – the cleanup and processing tools
- `start.bat` / `start.sh` – one-click launchers

Enjoy digitizing your family history!
