# Contributing to HealthRAG

Thank you for considering contributing to HealthRAG! This guide will help you get started.

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/HealthRAG.git
cd HealthRAG
```

### 2. Set Up Development Environment

```bash
# Install dependencies
chmod +x setup_dependencies.sh
./setup_dependencies.sh

# Activate virtual environment
source activate_venv.sh

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Pre-commit Checks

**Before committing, always run:**

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check linting
flake8 src/ tests/

# Run tests
pytest tests/ -m "not slow"

# Check coverage
pytest --cov=src --cov-report=term tests/
```

## Pull Request Process

### 1. Create a Feature Branch

```bash
# Always branch from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/your-feature-name
```

**Branch naming conventions:**
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/fixes

### 2. Make Your Changes

- Write tests for new features
- Update documentation as needed
- Follow existing code style
- Keep commits atomic and descriptive

### 3. Run Full Test Suite

```bash
# Run all tests
pytest tests/ -v

# Check coverage (must be ≥75%)
pytest --cov=src --cov-report=term --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feat/your-feature-name

# Create PR on GitHub
# Use the PR template and fill out all sections
```

## CI/CD Checks

All PRs must pass these checks before merging:

### ✅ Test Suite
- Unit tests (Python 3.10 and 3.11)
- Integration tests
- Coverage ≥75%

### ✅ Code Quality
- Flake8 linting (no errors)
- Black formatting (properly formatted)
- isort import sorting (properly sorted)
- MyPy type checking (warnings only, non-blocking)

### ✅ Security
- Trivy vulnerability scan
- Bandit security linting

**If checks fail:**
1. Check the workflow logs
2. Fix issues locally
3. Re-run the checks:
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   pytest tests/
   ```
4. Push fixes

## Code Style Guide

### Python Style

**Follow PEP 8 with these modifications:**
- Line length: 100 characters (not 79)
- Use Black for formatting (opinionated)
- Use isort for import sorting
- Maximum complexity: 15

**Example:**

```python
"""Module docstring explaining purpose."""

# Standard library imports
import json
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import numpy as np
import pandas as pd
from langchain.chains import RetrievalQA

# Local imports
from src.profile import UserProfile
from src.calculations import calculate_tdee


def calculate_macros(
    profile: UserProfile,
    goal: str = "maintain",
    activity_level: str = "moderate",
) -> Dict[str, float]:
    """
    Calculate macronutrient targets based on user profile and goals.

    Args:
        profile: User profile with weight, height, age, sex
        goal: One of "cut", "bulk", "recomp", "maintain"
        activity_level: Activity level (sedentary to very_active)

    Returns:
        Dictionary with protein, fat, carbs in grams, and calories

    Raises:
        ValueError: If goal or activity_level is invalid
    """
    # Implementation here
    pass
```

### Testing Style

**Use pytest with descriptive test names:**

```python
import pytest
from src.profile import UserProfile


class TestUserProfile:
    """Test suite for UserProfile class."""

    def test_create_profile_with_valid_data(self):
        """Should successfully create profile with all required fields."""
        profile = UserProfile(
            name="Test User",
            age=30,
            weight=75.0,
            height=180,
            sex="male",
        )
        assert profile.name == "Test User"
        assert profile.age == 30

    def test_create_profile_with_invalid_age(self):
        """Should raise ValueError for age < 18."""
        with pytest.raises(ValueError, match="Age must be at least 18"):
            UserProfile(name="Test", age=15, weight=75, height=180, sex="male")

    @pytest.mark.slow
    def test_complex_calculation(self):
        """Slow test for complex calculation (marked for optional skip)."""
        # Complex test here
        pass
```

### Documentation Style

**Use Google-style docstrings:**

```python
def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE).

    Uses activity multipliers from Mifflin-St Jeor formula.

    Args:
        bmr: Basal Metabolic Rate in kcal/day
        activity_level: Activity level descriptor
            - "sedentary": Little or no exercise
            - "light": Exercise 1-3 days/week
            - "moderate": Exercise 3-5 days/week
            - "active": Exercise 6-7 days/week
            - "very_active": Physical job or training 2x/day

    Returns:
        TDEE in kcal/day as a float

    Raises:
        ValueError: If activity_level is not recognized

    Examples:
        >>> calculate_tdee(1800, "moderate")
        2700.0
        >>> calculate_tdee(1500, "sedentary")
        1800.0
    """
    # Implementation
    pass
```

## Testing Guidelines

### Test Coverage Requirements

- **Minimum coverage:** 75% overall
- **New features:** Must include tests
- **Bug fixes:** Add regression test
- **Critical paths:** 100% coverage (profile, calculations, tracking)

### Test Categories

**Use pytest markers:**

```python
@pytest.mark.unit
def test_simple_calculation():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_database_interaction():
    """Integration test with database."""
    pass

@pytest.mark.slow
def test_full_program_generation():
    """Slow test (>1 second)."""
    pass
```

**Run specific test categories:**

```bash
pytest -m unit              # Fast unit tests only
pytest -m integration       # Integration tests
pytest -m "not slow"        # Skip slow tests
pytest -m "slow"            # Only slow tests
```

### Browser Tests (E2E)

**Only run manually or on schedule:**

```bash
# Install Playwright browsers first
playwright install chromium

# Start Streamlit app
streamlit run src/main.py &

# Run browser tests
pytest tests/browser/ --headed --slowmo=1000
```

**When to add browser tests:**
- Critical user flows (login, profile creation, workout logging)
- UI-heavy features (dashboards, charts, forms)
- Cross-browser compatibility issues

## Project Structure

```
HealthRAG/
├── .github/
│   ├── workflows/          # GitHub Actions CI/CD
│   │   ├── test.yml        # Test suite (auto)
│   │   ├── lint.yml        # Code quality (auto)
│   │   ├── browser-tests.yml  # E2E tests (manual)
│   │   └── deploy.yml      # Deployment (auto on main)
│   ├── CICD.md             # CI/CD documentation
│   └── CONTRIBUTING.md     # This file
├── src/                    # Source code
│   ├── main.py             # Streamlit app
│   ├── rag_system.py       # RAG engine
│   ├── profile.py          # User profile
│   ├── calculations.py     # TDEE/macros
│   ├── adaptive_tdee.py    # Adaptive TDEE algorithm
│   ├── weekly_checkin.py   # Weekly check-ins
│   └── ...                 # Other modules
├── tests/                  # Test suite
│   ├── fixtures/           # Test data
│   ├── browser/            # E2E tests
│   └── test_*.py           # Unit/integration tests
├── data/                   # Data files (gitignored)
├── docs/                   # Documentation
├── config/                 # Configuration
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml          # Tool configuration
├── pytest.ini              # Pytest configuration
└── .flake8                 # Flake8 configuration
```

## Git Workflow

### Commit Message Format

**Use conventional commits:**

```
type(scope): short description

Longer description if needed

- Bullet points for details
- Additional context

Fixes #123
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/fixes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Build/tooling changes

**Examples:**

```
feat(adaptive-tdee): add EWMA trend weight calculation

- Implement exponential weighted moving average
- Alpha = 0.3 (MacroFactor-style smoothing)
- 7-day minimum data requirement

Fixes #45
```

```
fix(food-logger): handle duplicate barcode entries

Previously, scanning the same barcode twice would create
duplicate entries. Now checks for existing entries and
offers to update quantity instead.

Fixes #78
```

### Rebase vs Merge

**For feature branches:**
- Rebase on main before creating PR
- Keep commit history clean
- Squash small fixup commits

```bash
git checkout main
git pull origin main
git checkout feat/your-feature
git rebase main
```

**For merging PRs:**
- Use "Squash and merge" for small PRs
- Use "Rebase and merge" for well-structured commits
- Never use regular merge (no merge commits)

## Review Process

### What to Expect

1. **Automated checks** run first (tests, linting, security)
2. **Code review** by maintainer (1-3 business days)
3. **Feedback iteration** (if needed)
4. **Final approval** and merge

### Review Criteria

**Code quality:**
- Follows style guide
- Has appropriate tests
- Documentation is updated
- No obvious bugs or issues

**Architecture:**
- Fits existing patterns
- Doesn't break existing features
- Reasonable complexity
- Reusable where appropriate

**Testing:**
- Coverage ≥75%
- Tests are meaningful
- Edge cases covered
- No flaky tests

## Common Issues

### Coverage Below 75%

**Check uncovered lines:**

```bash
pytest --cov=src --cov-report=term-missing tests/
```

**Add tests for uncovered code:**

```python
# If you see:
# src/calculations.py  85%  Missing: 45-50

# Add test:
def test_edge_case_for_lines_45_50():
    """Test the uncovered code path."""
    # Test implementation
    pass
```

### Linting Failures

**Auto-fix most issues:**

```bash
black src/ tests/
isort src/ tests/
```

**Check remaining issues:**

```bash
flake8 src/ tests/ --show-source
```

### Import Errors in Tests

**Use absolute imports in tests:**

```python
# ❌ Bad
from ..src.profile import UserProfile

# ✅ Good
from src.profile import UserProfile
```

### Slow Tests

**Mark slow tests:**

```python
@pytest.mark.slow
def test_full_integration():
    """This test takes >1 second."""
    pass
```

**Skip during development:**

```bash
pytest -m "not slow"
```

## Getting Help

- **Documentation:** Check `CLAUDE.md`, `VISION.md`, `SCENARIOS.md`
- **CI/CD:** See `.github/CICD.md`
- **Issues:** Search existing issues first
- **Questions:** Open a discussion on GitHub

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to HealthRAG! 🎉
