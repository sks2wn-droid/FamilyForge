# FamilyForge

**Easy, free, private toolkit for digitizing and organizing family photos.**

Turn boxes of old prints into a clean, searchable digital archive. No subscriptions. Everything stays on your computer.

---

## Step-by-Step Installation Guide (Windows)

This is the method that works most reliably.

### 1. Install Python (only needed once)

1. Go to https://www.python.org/downloads/
2. Download the latest **Python 3.12** (or 3.11) installer for Windows.
3. Run the installer.
4. **IMPORTANT**: On the first screen, check the box that says **“Add python.exe to PATH”**.
5. Click “Install Now” and finish the installation.
6. Restart your computer (or at least close and reopen any open Command Prompt windows).

### 2. Download FamilyForge

1. On this GitHub page, click the green **Code** button → **Download ZIP**.
2. Extract the ZIP anywhere you like (for example Desktop or Documents).
3. You should now have a folder called something like `FamilyForge-main`.

### 3. First-time setup (manual method – most reliable)

1. Open the extracted FamilyForge folder.
2. Hold the **Shift** key and right-click inside the folder → choose **“Open PowerShell window here”** or **“Open in Terminal”**.
3. Copy and paste these commands **one by one**, pressing Enter after each:

```bat
py -3 -m venv venv
```

```bat
venv\Scripts\activate
```

```bat
python -m pip install --upgrade pip
```

```bat
pip install streamlit opencv-python-headless numpy pillow
```

```bat
streamlit run app.py
```

4. After the last command you should see a line that says:

```
Local URL: http://localhost:8501
```

5. Open that address in Chrome or Edge (or the browser should open automatically).

You only need to do the long install steps **once**. After that, starting is much faster (see below).

### 4. Starting FamilyForge next time

1. Open the FamilyForge folder.
2. Open PowerShell / Terminal in that folder again.
3. Run only these two lines:

```bat
venv\Scripts\activate
streamlit run app.py
```

---

## Alternative: One-click start.bat

After you have successfully run the manual method once, you can try double-clicking `start.bat`.

If the black window opens and closes immediately, use the manual method above instead — it is more reliable.

---

## What you can do today

- **Clean Up Photos** – straighten, crop scanner borders, improve faded pictures, reduce dust
- **Browse** – see thumbnails of your cleaned photos
- **Name the People** – basic face detection (clustering coming next)
- Everything stays private on your computer

---

## Project layout

- `app.py` – the friendly interface
- `familyforge/` – the cleanup and processing tools
- `db.py` – photo and people tracking (being expanded)
- `start.bat` / `start.sh` – launchers
- `requirements.txt` – the packages we need

---

## Coming next

- Face clustering (group the same person together)
- OCR for text on the backs of photos
- Better installation experience
- Memory book / album generator
- Immich export helpers

Enjoy digitizing your family history!
