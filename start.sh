#!/bin/bash
echo ""
echo " FamilyForge - starting..."
echo ""

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing / updating packages (first run may take a minute)..."
pip install -r requirements.txt --quiet

echo ""
echo "Launching FamilyForge..."
echo "A browser window should open shortly."
echo ""
streamlit run app.py
