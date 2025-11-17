#!/bin/bash
# HealthRAG Dependency Installation Script
# Installs all required dependencies for the complete system

set -e  # Exit on error

echo "========================================"
echo "HealthRAG Dependency Installation"
echo "========================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.10.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Check if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "2. Installing macOS system dependencies..."

    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install from: https://brew.sh"
        exit 1
    fi
    echo "✅ Homebrew found"

    # Install ZBar for barcode scanning
    echo "   Installing ZBar (barcode scanning library)..."
    if brew list zbar &>/dev/null; then
        echo "   ✅ ZBar already installed"
    else
        brew install zbar
        echo "   ✅ ZBar installed"
    fi
    echo ""
else
    echo "2. Non-macOS system detected. Install ZBar manually:"
    echo "   Ubuntu/Debian: sudo apt-get install libzbar0"
    echo "   Fedora: sudo dnf install zbar"
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "3. Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "3. Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "4. Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "5. Upgrading pip..."
pip3 install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install Python dependencies
echo "6. Installing Python dependencies..."
echo "   This may take several minutes..."
pip3 install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f "data/.env" ]; then
    echo "7. Setting up .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example data/.env
        echo "⚠️  Created data/.env from template"
        echo "   Please add your USDA_FDC_API_KEY to data/.env"
        echo "   Get your API key at: https://fdc.nal.usda.gov/api-key-signup"
    else
        echo "ℹ️  No .env.example found. You'll need to create data/.env manually"
    fi
else
    echo "7. ✅ data/.env already exists"
fi
echo ""

# Create data directories if they don't exist
echo "8. Creating data directories..."
mkdir -p data/pdfs data/vector_stores logs
echo "✅ Data directories created"
echo ""

# Verify critical imports
echo "9. Verifying installations..."
python3 << 'EOF'
import sys
errors = []

# Test critical imports
try:
    import streamlit
    print("   ✅ Streamlit")
except ImportError as e:
    errors.append(f"Streamlit: {e}")

try:
    import langchain
    print("   ✅ LangChain")
except ImportError as e:
    errors.append(f"LangChain: {e}")

try:
    from PIL import Image
    print("   ✅ Pillow (image processing)")
except ImportError as e:
    errors.append(f"Pillow: {e}")

try:
    from pyzbar import pyzbar
    print("   ✅ pyzbar (barcode scanning)")
except ImportError as e:
    errors.append(f"pyzbar: {e}")

try:
    import pandas
    print("   ✅ Pandas")
except ImportError as e:
    errors.append(f"Pandas: {e}")

try:
    import openpyxl
    print("   ✅ OpenPyXL (Excel support)")
except ImportError as e:
    errors.append(f"OpenPyXL: {e}")

try:
    from dotenv import load_dotenv
    print("   ✅ python-dotenv")
except ImportError as e:
    errors.append(f"python-dotenv: {e}")

if errors:
    print("\n❌ Errors found:")
    for error in errors:
        print(f"   - {error}")
    sys.exit(1)
else:
    print("\n✅ All critical dependencies verified!")
EOF

echo ""
echo "========================================"
echo "✅ Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Add your USDA API key to data/.env:"
echo "   USDA_FDC_API_KEY=your_key_here"
echo ""
echo "2. Add your fitness PDFs to data/pdfs/"
echo ""
echo "3. Start the application:"
echo "   ./start_healthrag.sh"
echo "   or"
echo "   streamlit run src/main.py"
echo ""
echo "For MLX backend (Apple Silicon):"
echo "   pip3 install -r requirements-mlx.txt"
echo ""
echo "========================================"
