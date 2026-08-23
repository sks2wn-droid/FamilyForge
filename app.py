"""
FamilyForge - Easy Family Photo Scanning Toolkit
A beginner-friendly front end for digitizing, cleaning, and organizing family photos.
"""

import streamlit as st
from pathlib import Path
import time

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FamilyForge",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Warm, clean styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #5d6d7e;
        margin-bottom: 1.8rem;
    }
    .roadmap-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.4rem;
        height: 100%;
        text-align: center;
        transition: box-shadow 0.2s;
    }
    .roadmap-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .roadmap-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3498db;
        margin-bottom: 0.5rem;
    }
    .success-box {
        background: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .info-box {
        background: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    div[data-testid="stSidebar"] {
        background-color: #fafbfc;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 🖼️ FamilyForge")
st.sidebar.caption("Your family photo helper")

page = st.sidebar.radio(
    "Where do you want to go?",
    [
        "Home",
        "Clean Up Photos",
        "Name the People",
        "Look Through Photos",
        "Make Albums & Share",
        "Preferences",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Tip:** Start on Home. "
    "It walks you through everything step by step."
)
st.sidebar.caption("FamilyForge v0.1 • Free & private")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_stats():
    return {"total": 0, "cleaned": 0, "people": 0, "pending": 0}

def count_images(folder: Path):
    exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
    if not folder.exists():
        return 0
    return sum(1 for f in folder.iterdir() if f.is_file() and f.suffix.lower() in exts)

# ===========================================================================
# HOME
# ===========================================================================
if page == "Home":
    st.markdown('<p class="main-header">Welcome to FamilyForge</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Turn boxes of old family photos into a beautiful, '
        'searchable digital archive — for free and completely private.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### What would you like to do?")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📷 I just scanned some photos", use_container_width=True, type="primary"):
            st.info("Go to **Clean Up Photos** in the sidebar to get started.")
    with c2:
        if st.button("🗂️ I already have digital photos", use_container_width=True):
            st.info("You can jump to **Name the People** or **Look Through Photos**.")
    with c3:
        if st.button("🛠️ Show me everything", use_container_width=True):
            st.info("Use the sidebar to explore any section.")

    st.divider()

    st.markdown("### How it works (simple 4 steps)")
    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown(
            '<div class="roadmap-card">'
            '<div class="roadmap-number">1</div>'
            '<strong>Scan your photos</strong><br><br>'
            'Use a flatbed scanner or the free <em>scansplitter</em> tool '
            'to turn prints into digital files.'
            '</div>',
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            '<div class="roadmap-card">'
            '<div class="roadmap-number">2</div>'
            '<strong>Clean them up</strong><br><br>'
            'FamilyForge straightens, crops, and improves faded or dusty scans '
            'with one click.'
            '</div>',
            unsafe_allow_html=True,
        )
    with r3:
        st.markdown(
            '<div class="roadmap-card">'
            '<div class="roadmap-number">3</div>'
            '<strong>Name the people</strong><br><br>'
            'You label a few faces. The computer finds the rest of the family '
            'automatically.'
            '</div>',
            unsafe_allow_html=True,
        )
    with r4:
        st.markdown(
            '<div class="roadmap-card">'
            '<div class="roadmap-number">4</div>'
            '<strong>Share & keep forever</strong><br><br>'
            'Create albums, make photo books, or put everything in a private '
            'library the whole family can browse.'
            '</div>',
            unsafe_allow_html=True,
        )

    with st.expander("More detail – the free tools we use together"):
        st.markdown(
            """
**1. Scanning**  
We recommend the free tool **scansplitter** for multi-photo scans and album pages.

**2. Cleaning & organizing**  
That’s what FamilyForge does – straighten, remove borders, improve clarity, find faces, and help you name people.

**3. Long-term library**  
When you’re ready, the free program **Immich** gives you a beautiful Google-Photos-style experience. Everything stays private on your hardware.
            """
        )

    st.markdown(
        '<div class="info-box">'
        'No photos yet. Start by going to <strong>Clean Up Photos</strong> '
        'and pointing FamilyForge at a folder of scanned images.'
        '</div>',
        unsafe_allow_html=True,
    )

# ===========================================================================
# CLEAN UP PHOTOS – now with real processing
# ===========================================================================
elif page == "Clean Up Photos":
    st.markdown('<p class="main-header">Clean Up Your Scans</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">We’ll straighten crooked photos, remove scanner borders, '
        'and make old pictures clearer. You choose how much help you want.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### 1. Where are your scanned photos?")
    input_folder = st.text_input(
        "Folder path",
        value="./scans",
        help="Type or paste the full path to the folder that contains your scanned images.",
        label_visibility="collapsed",
        placeholder=r"Example: C:\Users\You\Pictures\FamilyScans",
    )
    output_folder = st.text_input(
        "Where should the cleaned photos be saved?",
        value="./cleaned",
        help="A new folder will be created if it doesn’t exist.",
    )

    # Show how many images are waiting
    in_path = Path(input_folder)
    n_images = count_images(in_path)
    if in_path.exists():
        st.caption(f"Found **{n_images}** image(s) in that folder.")
    else:
        st.caption("Folder not found yet – enter a valid path.")

    st.markdown("### 2. What would you like us to do?")

    do_straighten = st.checkbox(
        "**Straighten & crop** – fix tilted photos and remove white scanner borders",
        value=True,
    )
    do_clearer = st.checkbox(
        "**Make clearer** – improve contrast and faded colors",
        value=True,
    )
    do_faces = st.checkbox(
        "**Find faces** – detect people so you can name them later (coming soon)",
        value=False,
        disabled=True,
    )

    with st.expander("Extra options (optional)"):
        do_ai_restore = st.checkbox("Restore faces with AI (coming soon)", value=False, disabled=True)
        quality = st.slider("JPEG quality for cleaned copies", 75, 100, 92)

    st.markdown("")
    if st.button("✨ Clean These Photos", type="primary", use_container_width=True):
        if not input_folder or not Path(input_folder).exists():
            st.error("Please enter a valid folder path that contains images.")
        elif n_images == 0:
            st.warning("No supported images found in that folder (.jpg, .png, .tif, etc.).")
        else:
            try:
                from familyforge.preprocess import process_batch
            except Exception as e:
                st.error(
                    "Could not load the cleaning engine. Make sure you installed the packages:\n"
                    "`pip install opencv-python numpy pillow`\n\n"
                    f"Details: {e}"
                )
            else:
                with st.spinner(f"Cleaning {n_images} photo(s)… this may take a little while"):
                    progress = st.progress(0)
                    status = st.empty()

                    # We call the batch function; for progress we can process one-by-one if preferred
                    try:
                        results = process_batch(
                            input_folder,
                            output_folder,
                            do_deskew=do_straighten,
                            do_crop=do_straighten,
                            do_artifacts=do_clearer,
                            do_enhance=do_clearer,
                            jpeg_quality=quality,
                        )
                        progress.progress(100)

                        successes = [r for r in results if "error" not in r]
                        failures = [r for r in results if "error" in r]

                        st.markdown(
                            f'<div class="success-box">'
                            f'<strong>Done!</strong> Cleaned {len(successes)} photo(s).'\n                            f'<br>Saved to: <code>{Path(output_folder).resolve()}</code>'
                            f'<br><br>'
                            f'Next suggested step: go to <strong>Name the People</strong> '
                            f'(face detection coming soon).'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        if failures:
                            st.warning(f"{len(failures)} file(s) had problems.")
                            with st.expander("See problems"):
                                for f in failures:
                                    st.write(f.get("input"), "→", f.get("error"))

                    except Exception as e:
                        st.error(f"Something went wrong while cleaning: {e}")

    st.markdown("### Preview")
    st.info(
        "After processing, your cleaned photos will be in the output folder. "
        "You can open that folder to check them."
    )

# ===========================================================================
# NAME THE PEOPLE
# ===========================================================================
elif page == "Name the People":
    st.markdown('<p class="main-header">Name the People in Your Photos</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Click a face and type who it is. '
        'You only need to name a few examples — FamilyForge will find the rest '
        'of that person for you.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-box">'
        'No faces have been found yet.<br>'
        'First go to <strong>Clean Up Photos</strong> and process a folder. '
        'Face detection is coming in the next update.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### When faces appear they will look like this:")
    demo1, demo2, demo3 = st.columns(3)
    with demo1:
        st.image("https://via.placeholder.com/180x180?text=Face+1", caption="Unknown person")
        st.text_input("This is…", key="demo1", placeholder="e.g. Grandma Edith")
        st.button("Save name", key="save1")
    with demo2:
        st.image("https://via.placeholder.com/180x180?text=Face+2", caption="Unknown person")
        st.text_input("This is…", key="demo2", placeholder="e.g. Uncle Bob")
        st.button("Save name", key="save2")
    with demo3:
        st.image("https://via.placeholder.com/180x180?text=Face+3", caption="Unknown person")
        st.text_input("This is…", key="demo3", placeholder="e.g. Mom")
        st.button("Save name", key="save3")

    with st.expander("Tips for best results"):
        st.markdown(
            """
- Name the clearest, most front-facing photos first.
- After you name 3–5 people, the system can match many more automatically.
- Children’s faces change a lot over the years – you may need to name a few from different decades.
            """
        )

# ===========================================================================
# LOOK THROUGH PHOTOS
# ===========================================================================
elif page == "Look Through Photos":
    st.markdown('<p class="main-header">Look Through Your Photos</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Search by person, decade, or keyword. '
        'Everything stays on your computer.</p>',
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.selectbox("Person", ["Anyone", "Grandma", "Dad", "Mom"])
    with f2:
        st.selectbox("Decade", ["Any time", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s"])
    with f3:
        st.selectbox("Status", ["All photos", "Only cleaned", "Needs review"])
    with f4:
        st.text_input("Search words", placeholder="birthday, beach, Christmas…")

    st.info(
        "Your photo grid will appear here once you have processed some images.\n\n"
        "You will be able to click any photo to see it larger, add notes, or add it to an album."
    )

# ===========================================================================
# MAKE ALBUMS & SHARE
# ===========================================================================
elif page == "Make Albums & Share":
    st.markdown('<p class="main-header">Make Albums & Share</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Create beautiful collections and share them with family — '
        'still completely private.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### Create a Memory Book")
    st.write(
        "Pick photos (or let FamilyForge choose by person or decade) "
        "and generate a printable PDF or web album."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        st.selectbox("Who is this album about?", ["Whole family", "Grandma Edith", "Mom & Dad"])
    with col_b:
        st.selectbox("Time period", ["All years", "1950s–1960s", "1970s", "1980s"])

    if st.button("📖 Create Memory Book PDF", type="primary"):
        st.success("In the full version a beautiful PDF will be generated here with captions and a timeline.")

    st.divider()
    st.markdown("### Other ways to share")
    st.checkbox("Prepare a folder that Immich can use as a private family library")
    st.checkbox("Copy cleaned photos to Google Drive (for backup)")
    st.checkbox("Export files that work with digiKam or other photo programs")

    if st.button("Start Export"):
        st.info("Export options will run here once the backend is connected.")

# ===========================================================================
# PREFERENCES
# ===========================================================================
elif page == "Preferences":
    st.markdown('<p class="main-header">Preferences</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Most people never need to change these. '
        'They are here if you want more control.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### Folders")
    st.text_input("Where original scans live", value="./scans")
    st.text_input("Where cleaned photos are saved", value="./cleaned")
    st.text_input("Database file", value="./familyforge.db")

    st.markdown("### Optional AI models")
    st.caption("Only needed if you turn on the advanced restore options.")
    st.text_input("Folder for AI models", value="./models")
    st.checkbox("Use the computer’s GPU when available (faster)", value=True)

    st.markdown("### Family names (optional starting list)")
    st.text_area(
        "People you already know (one name per line)",
        value="Grandma Edith\nGrandpa Robert\nMom\nDad",
        help="These names will appear as suggestions when you start labeling faces.",
    )

    if st.button("Save Preferences"):
        st.success("Preferences saved. (In the full version they will persist.)")

# Footer
st.markdown("---")
st.caption(
    "FamilyForge is free, open-source, and keeps all your photos on your own computer. "
    "No accounts, no subscriptions, no cloud required."
)
