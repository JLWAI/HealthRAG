#!/bin/bash
# Auto-fix code formatting issues
# Usage: ./scripts/fix_formatting.sh

set -e  # Exit on error

echo "🔧 Fixing code formatting..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo "Run: source activate_venv.sh"
    exit 1
fi

# Install dev dependencies if needed
if ! command -v black &> /dev/null; then
    echo "📦 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "1️⃣  Running Black formatter..."
black src/ tests/
echo ""

echo "2️⃣  Running isort (import sorting)..."
isort src/ tests/
echo ""

echo -e "${GREEN}✅ Formatting complete!${NC}"
echo ""
echo "Files have been automatically formatted."
echo "Review changes with: git diff"
echo ""
