#!/bin/bash

# Smart Document Field & Value Extractor - Setup Script
# This script sets up the environment and runs the application

echo "🚀 Setting up Smart Document Field & Value Extractor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🎉 To run the application:"
echo "   1. Activate the virtual environment: source .venv/bin/activate"
echo "   2. Run the app: streamlit run app.py"
echo ""
echo "📖 Or simply run: ./run.sh"
echo ""
