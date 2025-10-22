#!/bin/bash

# ScappyDoo Launcher Script
# This script launches the ScappyDoo GUI application

echo "================================================"
echo "       🐕 ScappyDoo - Permit Scraper"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3 to use ScappyDoo."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "🚀 Launching ScappyDoo..."
echo "The app will open in your default browser."
echo ""
echo "Press Ctrl+C to stop the application."
echo "================================================"
echo ""

# Launch Streamlit
streamlit run app.py --server.headless=true
