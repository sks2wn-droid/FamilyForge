"""
FamilyForge - Streamlit Command Center
Main entry point for the family photo scanning & organization toolkit.
"""

import streamlit as st
import sqlite3
from pathlib import Path
import os

# Page config
st.set_page_config(
    page_title="FamilyForge",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polish
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a365d;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4a5568;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🖼️ FamilyForge")
st.sidebar.markdown("**Family Photo Scanning Toolkit**")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Import & Process", "Face Review", "Gallery & Search", "Albums & Export", "Settings"],
    label_visibility="collapsed"
)

# Placeholder DB connection (will use real SQLite)
def get_db_connection():
    db_path = Path("familyforge.db")
    conn = sqlite3.connect(db_path)
    return conn

# === DASHBOARD ===
if page == "Dashboard":
    st.markdown('<p class="main-header">FamilyForge Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your command center for digitizing and organizing family history</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Photos", "0", "Ready to import")
    with col2:
        st.metric("Processed", "0", "0%")
    with col3:
        st.metric("People Identified", "0")
    with col4:
        st.metric("Pending Review", "0")
    
    st.divider()
    
    st.subheader("Quick Actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📁 Import Folder", use_container_width=True):
            st.info("Switch to Import & Process page")
    with c2:
        if st.button("✨ Run Batch Enhance", use_container_width=True):
            st.info("Coming soon – classical + AI restore")
    with c3:
        if st.button("👤 Cluster Faces", use_container_width=True):
            st.info("Coming soon – InsightFace clustering")
    
    st.subheader("Recent Activity")
    st.info("No activity yet. Start by importing a folder of scanned photos.")

# === IMPORT & PROCESS ===
elif page == "Import & Process":
    st.header("Import & Process")
    st.write("Batch process scanned photos: deskew, crop, enhance, optional AI restore.")
    
    input_folder = st.text_input("Input folder path", value="./scans/raw")
    output_folder = st.text_input("Output folder path", value="./scans/processed")
    
    st.subheader("Processing Options")
    col_a, col_b = st.columns(2)
    with col_a:
        do_classical = st.checkbox("Classical enhance (deskew, crop, levels, dust)", value=True)
        do_ai_restore = st.checkbox("AI face restore (GFPGAN/CodeFormer)", value=False)
        do_upscale = st.checkbox("AI upscale (Real-ESRGAN)", value=False)
    with col_b:
        do_faces = st.checkbox("Detect faces & extract embeddings", value=True)
        do_ocr = st.checkbox("OCR photo backs / text", value=False)
        quality = st.slider("JPEG quality for access copies", 70, 100, 92)
    
    if st.button("🚀 Start Batch Processing", type="primary"):
        with st.spinner("Processing... (prototype – real pipeline coming)"):
            st.success("Pipeline would run here. See preprocess.py and restore modules.")
            st.progress(100)
    
    st.subheader("Before / After Preview")
    st.info("Interactive comparison slider will appear here once images are processed.")

# === FACE REVIEW ===
elif page == "Face Review":
    st.header("Face Review & Clustering")
    st.write("Review auto-detected face clusters. Name family members, merge similar clusters, seed with known photos.")
    
    st.info("Prototype: Clusters will appear as cards with representative faces once InsightFace pipeline runs.")
    
    with st.expander("Seed Mode – Label known family members"):
        st.write("Upload a few clear photos of each person or label existing detections to bootstrap recognition.")
        st.file_uploader("Upload known face photos", accept_multiple_files=True)

# === GALLERY & SEARCH ===
elif page == "Gallery & Search":
    st.header("Gallery & Search")
    
    filters = st.columns(4)
    with filters[0]:
        st.selectbox("Person", ["All"] + ["Grandma", "Dad", "Mom"])  # placeholder
    with filters[1]:
        st.selectbox("Decade", ["All", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s"])
    with filters[2]:
        st.selectbox("Status", ["All", "Raw", "Enhanced", "Reviewed"])
    with filters[3]:
        st.text_input("Keyword / OCR search")
    
    st.info("Photo grid / timeline view will render here.")

# === ALBUMS & EXPORT ===
elif page == "Albums & Export":
    st.header("Albums & Export")
    
    st.subheader("Create Memory Book")
    st.write("Select photos or auto-generate by person / decade. Export beautiful PDF or HTML.")
    
    if st.button("Generate Sample PDF Album"):
        st.success("PDF generator (reportlab / weasyprint) will create a chronological album with captions here.")
    
    st.subheader("Export Options")
    st.checkbox("Prepare folder structure for Immich External Library")
    st.checkbox("Sync processed to Google Drive")
    st.checkbox("Export XMP sidecars for digiKam / Lightroom compatibility")
    
    if st.button("Export Selected"):
        st.info("Export logic coming.")

# === SETTINGS ===
elif page == "Settings":
    st.header("Settings")
    
    st.subheader("Paths")
    st.text_input("Masters (TIFF) folder", "./masters")
    st.text_input("Processed folder", "./processed")
    st.text_input("Database path", "./familyforge.db")
    
    st.subheader("Models")
    st.text_input("Real-ESRGAN model path")
    st.text_input("GFPGAN / CodeFormer model path")
    st.checkbox("Prefer GPU if available", value=True)
    
    st.subheader("Family Members (seed list)")
    st.text_area("Known people (one per line)", "Grandma Edith\nGrandpa Robert\nMom\nDad")
    
    if st.button("Save Settings"):
        st.success("Settings saved (prototype).")

st.sidebar.markdown("---")
st.sidebar.caption("FamilyForge v0.1 • Built with ❤️ for your family archive")
