#!/bin/bash
# Activate virtual environment with proper library paths for ZBar

# Export library path for ZBar (needed for barcode scanning)
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated with ZBar support"
echo "📦 Python: $(which python3)"
echo "📷 ZBar library: /opt/homebrew/lib/libzbar.dylib"
echo ""
echo "To run the app:"
echo "  streamlit run src/main.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
