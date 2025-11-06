#!/bin/bash
# Run CI checks locally before pushing
# Usage: ./scripts/run_ci_locally.sh

set -e  # Exit on error

echo "🚀 Running CI checks locally..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

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

# 1. Code Formatting
section "1️⃣  Code Formatting (Black)"
if black --check src/ tests/; then
    echo -e "${GREEN}✅ Black formatting: PASSED${NC}"
else
    echo -e "${RED}❌ Black formatting: FAILED${NC}"
    echo ""
    echo "Fix with: black src/ tests/"
    exit 1
fi

# 2. Import Sorting
section "2️⃣  Import Sorting (isort)"
if isort --check-only src/ tests/; then
    echo -e "${GREEN}✅ Import sorting: PASSED${NC}"
else
    echo -e "${RED}❌ Import sorting: FAILED${NC}"
    echo ""
    echo "Fix with: isort src/ tests/"
    exit 1
fi

# 3. Linting
section "3️⃣  Linting (Flake8)"
if flake8 src/ tests/; then
    echo -e "${GREEN}✅ Flake8 linting: PASSED${NC}"
else
    echo -e "${RED}❌ Flake8 linting: FAILED${NC}"
    exit 1
fi

# 4. Type Checking
section "4️⃣  Type Checking (MyPy)"
if mypy src/ --ignore-missing-imports --show-error-codes; then
    echo -e "${GREEN}✅ Type checking: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  Type checking: WARNINGS (non-blocking)${NC}"
fi

# 5. Unit Tests
section "5️⃣  Unit Tests"
if pytest tests/ -m "unit" --cov=src --cov-report=term; then
    echo -e "${GREEN}✅ Unit tests: PASSED${NC}"
else
    echo -e "${RED}❌ Unit tests: FAILED${NC}"
    exit 1
fi

# 6. Integration Tests
section "6️⃣  Integration Tests"
if pytest tests/ -m "integration and not slow" --cov=src --cov-append --cov-report=term; then
    echo -e "${GREEN}✅ Integration tests: PASSED${NC}"
else
    echo -e "${RED}❌ Integration tests: FAILED${NC}"
    exit 1
fi

# 7. Coverage Check
section "7️⃣  Coverage Check (≥75%)"
if coverage report --fail-under=75; then
    echo -e "${GREEN}✅ Coverage check: PASSED${NC}"
else
    echo -e "${RED}❌ Coverage check: FAILED (must be ≥75%)${NC}"
    echo ""
    echo "Run: coverage html"
    echo "Then open: htmlcov/index.html"
    exit 1
fi

# 8. Security Scan
section "8️⃣  Security Scan (Bandit)"
if bandit -r src/ -ll; then
    echo -e "${GREEN}✅ Security scan: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  Security scan: WARNINGS (review output)${NC}"
fi

# Final Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ All CI checks passed!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Ready to push to GitHub! 🚀"
echo ""
echo "Next steps:"
echo "  1. git add ."
echo "  2. git commit -m \"your message\""
echo "  3. git push origin your-branch"
echo ""
