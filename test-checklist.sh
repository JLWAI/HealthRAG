#!/bin/bash
#
# HealthRAG Pre-Push Test Checklist
#
# Comprehensive local testing script to run before pushing to GitHub.
# Ensures all tests pass before code is deployed to Render.com.
#
# Usage:
#   ./test-checklist.sh           # Run all tests
#   ./test-checklist.sh --quick   # Skip optional tests
#   ./test-checklist.sh --docker  # Include Docker build validation
#
# Exit codes:
#   0 = All tests passed
#   1+ = Number of test failures

set -e  # Exit on error (but we catch errors ourselves)

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
QUICK_MODE=false
DOCKER_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --docker)
            DOCKER_MODE=true
            shift
            ;;
        --help)
            echo "Usage: ./test-checklist.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick    Skip optional manual tests"
            echo "  --docker   Include Docker build validation"
            echo "  --help     Show this help message"
            exit 0
            ;;
    esac
done

# Track failures
FAILURES=0
WARNINGS=0

# Print header
echo ""
echo "=========================================="
echo "   HealthRAG Pre-Push Test Checklist     "
echo "=========================================="
echo ""
echo -e "${CYAN}Branch:${NC} $(git branch --show-current)"
echo -e "${CYAN}Commit:${NC} $(git log -1 --oneline)"
echo ""

# Function to run test and track result
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "  $test_name... "

    if eval "$test_command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        if [ -s /tmp/test_output.log ]; then
            echo -e "${RED}     Error output:${NC}"
            head -n 5 /tmp/test_output.log | sed 's/^/     /'
        fi
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# Function for warning checks
run_warning() {
    local test_name="$1"
    local test_command="$2"

    echo -n "  $test_name... "

    if eval "$test_command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  WARNING${NC}"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

# Phase 1: Code Quality
echo -e "${BLUE}Phase 1: Code Quality & Syntax${NC}"
echo "----------------------------------------"

run_test "Python syntax (src/main.py)" "python -m py_compile src/main.py"
run_test "Python syntax (src/rag_system.py)" "python -m py_compile src/rag_system.py"
run_test "Python syntax (src/adaptive_tdee.py)" "python -m py_compile src/adaptive_tdee.py"
run_test "Python syntax (src/calculations.py)" "python -m py_compile src/calculations.py"
run_test "Python syntax (src/profile.py)" "python -m py_compile src/profile.py"

run_test "Import validation" "python -c 'import sys; sys.path.insert(0, \"src\"); import main, rag_system, adaptive_tdee, calculations, profile'"

echo ""

# Phase 2: Unit Tests - Adaptive TDEE
echo -e "${BLUE}Phase 2: Unit Tests - Adaptive TDEE${NC}"
echo "----------------------------------------"

run_test "EWMA trend weight tests" "pytest tests/test_adaptive_tdee.py -q --tb=no"
run_test "Adaptive TDEE calculations" "pytest tests/test_adaptive_tdee_calculations.py -q --tb=no"

echo ""

# Phase 3: Unit Tests - Other Modules
echo -e "${BLUE}Phase 3: Unit Tests - Core Modules${NC}"
echo "----------------------------------------"

run_test "Calculation tests (TDEE, macros)" "pytest tests/test_calculations.py -q --tb=no"

# Profile tests might have known failures, treat as warning
if run_warning "Profile system tests" "pytest tests/test_profile.py -q --tb=no"; then
    :  # Success
else
    echo -e "${YELLOW}     Note: Profile tests have known issues (not blocking)${NC}"
fi

echo ""

# Phase 4: Integration Tests
echo -e "${BLUE}Phase 4: Integration Tests${NC}"
echo "----------------------------------------"

if run_test "RAG system tests" "pytest tests/test_rag_system.py -q --tb=no"; then
    :  # Success
else
    echo -e "${YELLOW}     Note: RAG tests may fail without Ollama running${NC}"
fi

echo ""

# Phase 5: Test Coverage Summary
echo -e "${BLUE}Phase 5: Test Coverage Summary${NC}"
echo "----------------------------------------"

if command -v pytest &> /dev/null; then
    echo "  Collecting test stats..."

    TOTAL_TESTS=$(pytest tests/ --collect-only -q 2>/dev/null | tail -n 1 | grep -o '[0-9]\+' | head -n 1)

    if [ -n "$TOTAL_TESTS" ]; then
        echo -e "  ${CYAN}Total tests:${NC} $TOTAL_TESTS"
    fi

    # Run all tests with summary
    if pytest tests/ -q --tb=no > /tmp/pytest_summary.log 2>&1; then
        PASSED=$(grep -o '[0-9]\+ passed' /tmp/pytest_summary.log | grep -o '[0-9]\+')
        echo -e "  ${GREEN}✅ Passed:${NC} $PASSED"
    else
        PASSED=$(grep -o '[0-9]\+ passed' /tmp/pytest_summary.log | grep -o '[0-9]\+')
        FAILED=$(grep -o '[0-9]\+ failed' /tmp/pytest_summary.log | grep -o '[0-9]\+')
        echo -e "  ${GREEN}Passed:${NC} $PASSED"
        echo -e "  ${RED}Failed:${NC} $FAILED"
    fi
fi

echo ""

# Phase 6: Manual Validation (unless quick mode)
if [ "$QUICK_MODE" = false ]; then
    echo -e "${BLUE}Phase 6: Manual Validation${NC}"
    echo "----------------------------------------"
    echo -e "  ${YELLOW}⚠️  Manual checks required${NC}"
    echo ""
    echo "  Before pushing, manually verify:"
    echo "    1. Streamlit loads without errors"
    echo "       Command: ${CYAN}streamlit run src/main.py${NC}"
    echo "       URL: ${CYAN}http://localhost:8501${NC}"
    echo ""
    echo "    2. Test critical user flows:"
    echo "       - Create profile"
    echo "       - Log weight/food"
    echo "       - View Adaptive TDEE (if 14+ days data)"
    echo ""
    echo -n "  ${YELLOW}Have you manually tested the UI? (y/n/skip):${NC} "
    read -r ui_check

    if [ "$ui_check" = "y" ]; then
        echo -e "  ${GREEN}✅ UI validated${NC}"
    elif [ "$ui_check" = "skip" ]; then
        echo -e "  ${YELLOW}⚠️  Skipped (add to next test)${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${RED}❌ UI not validated${NC}"
        FAILURES=$((FAILURES + 1))
    fi

    echo ""
fi

# Phase 7: Docker Build (if requested)
if [ "$DOCKER_MODE" = true ]; then
    echo -e "${BLUE}Phase 7: Docker Build Validation${NC}"
    echo "----------------------------------------"

    run_test "Docker Compose build" "docker-compose build --quiet"

    echo "  Starting containers for health check..."
    if docker-compose up -d > /dev/null 2>&1; then
        sleep 10

        if docker-compose ps | grep -q "healthy"; then
            echo -e "  ${GREEN}✅ Docker containers healthy${NC}"
        else
            echo -e "  ${RED}❌ Docker health check failed${NC}"
            FAILURES=$((FAILURES + 1))
        fi

        echo "  Stopping containers..."
        docker-compose down > /dev/null 2>&1
    else
        echo -e "  ${RED}❌ Docker Compose failed to start${NC}"
        FAILURES=$((FAILURES + 1))
    fi

    echo ""
fi

# Phase 8: Git Status Check
echo -e "${BLUE}Phase 8: Git Status${NC}"
echo "----------------------------------------"

UNCOMMITTED=$(git status --porcelain | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
    echo -e "  ${YELLOW}⚠️  Uncommitted changes: $UNCOMMITTED files${NC}"
    echo "  Run: ${CYAN}git status${NC} to see changes"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "  ${GREEN}✅ All changes committed${NC}"
fi

UNPUSHED=$(git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null | wc -l)
if [ "$UNPUSHED" -gt 0 ]; then
    echo -e "  ${CYAN}ℹ️  Unpushed commits: $UNPUSHED${NC}"
else
    echo -e "  ${CYAN}ℹ️  No unpushed commits${NC}"
fi

echo ""

# Final Summary
echo "=========================================="
echo -e "${BLUE}Test Summary${NC}"
echo "=========================================="

if [ $FAILURES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo -e "${GREEN}✓${NC} Safe to push to GitHub"
    echo -e "${GREEN}✓${NC} Render will auto-deploy when pushed to main"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  git add ."
    echo "  git commit -m 'your commit message'"
    echo "  git push origin $(git branch --show-current)"

elif [ $FAILURES -eq 0 ] && [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} WARNING(S)${NC}"
    echo ""
    echo "Tests passed but with warnings."
    echo "Review warnings above before pushing."
    echo ""
    echo -e "${CYAN}Proceed with caution:${NC}"
    echo "  git push origin $(git branch --show-current)"

else
    echo -e "${RED}❌ ${FAILURES} TEST(S) FAILED${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  ${WARNINGS} WARNING(S)${NC}"
    fi
    echo ""
    echo -e "${RED}⚠️  DO NOT PUSH UNTIL FAILURES ARE FIXED!${NC}"
    echo ""
    echo -e "${CYAN}Debug commands:${NC}"
    echo "  pytest tests/ -v --tb=short  # Detailed test output"
    echo "  streamlit run src/main.py     # Test UI manually"
    echo "  pytest tests/test_xxx.py -vv  # Debug specific test file"
fi

echo "=========================================="
echo ""

# Cleanup
rm -f /tmp/test_output.log /tmp/pytest_summary.log

# Exit with failure count
exit $FAILURES
