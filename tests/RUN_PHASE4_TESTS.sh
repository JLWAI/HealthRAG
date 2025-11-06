#!/bin/bash
# Quick reference for running Phase 4 tests
# Created: November 6, 2025

echo "=========================================="
echo "Phase 4 Test Suite Runner"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running all Phase 4 module tests...${NC}"
echo ""

# Run each test file separately to show progress
echo "1/4: Testing Progress Photos..."
pytest tests/test_progress_photos.py -v --tb=short

echo ""
echo "2/4: Testing Body Measurements..."
pytest tests/test_body_measurements.py -v --tb=short

echo ""
echo "3/4: Testing TDEE Analytics..."
pytest tests/test_tdee_analytics.py -v --tb=short

echo ""
echo "4/4: Testing Progress Reports..."
pytest tests/test_progress_reports.py -v --tb=short

echo ""
echo "=========================================="
echo "SUMMARY: Running all Phase 4 tests together"
echo "=========================================="

# Run all together with coverage
pytest tests/test_progress_photos.py \
       tests/test_body_measurements.py \
       tests/test_tdee_analytics.py \
       tests/test_progress_reports.py \
       --cov=src/progress_photos \
       --cov=src/body_measurements \
       --cov=src/tdee_analytics \
       --cov=src/progress_reports \
       --cov-report=term-missing \
       --cov-report=html \
       -v

echo ""
echo -e "${GREEN}Coverage report saved to: htmlcov/index.html${NC}"
echo ""
echo "Quick stats:"
pytest tests/test_progress_photos.py \
       tests/test_body_measurements.py \
       tests/test_tdee_analytics.py \
       tests/test_progress_reports.py \
       --tb=no -q

echo ""
echo "=========================================="
echo "Individual module commands:"
echo "=========================================="
echo "Progress Photos:      pytest tests/test_progress_photos.py -v"
echo "Body Measurements:    pytest tests/test_body_measurements.py -v"
echo "TDEE Analytics:       pytest tests/test_tdee_analytics.py -v"
echo "Progress Reports:     pytest tests/test_progress_reports.py -v"
echo ""
echo "All Phase 4:          pytest tests/test_progress_photos.py tests/test_body_measurements.py tests/test_tdee_analytics.py tests/test_progress_reports.py"
echo "With coverage:        pytest tests/test_*.py --cov=src --cov-report=html"
echo ""
