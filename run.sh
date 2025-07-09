#!/bin/bash

# Smart Document Field & Value Extractor - Run Script
# This script activates the environment and runs the application

echo "🚀 Starting Smart Document Field & Value Extractor..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Please run ./setup.sh first."
    exit 1
fi

echo "✅ Starting Streamlit application..."
echo "🌐 The app will open in your browser at http://localhost:8501"
echo ""

# Run the application
streamlit run app.py
