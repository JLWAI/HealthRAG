---
name: Weekly Dependency Update
about: Weekly maintenance task for updating dependencies and security patches
title: '[DEPS] Weekly Dependency Update - Week of [DATE]'
labels: dependencies, maintenance, security
assignees: ''
---

## 📦 Weekly Dependency Management

**Week of:** [Insert date - e.g., 2025-01-15]
**Last Updated:** [Previous update date]
**Assigned To:** @[username]

---

## 🎯 Objectives

- [ ] Update all Python dependencies to latest compatible versions
- [ ] Check for security vulnerabilities
- [ ] Test critical functionality after updates
- [ ] Document any breaking changes
- [ ] Update requirements files

---

## 📋 Pre-Update Checklist

### 1. Environment Preparation
```bash
# Create backup branch
git checkout -b deps/weekly-update-$(date +%Y-%m-%d)

# Verify current environment
python3 --version
pip3 list --outdated

# Check for security advisories
pip3 install pip-audit
pip-audit
```

### 2. Current Dependency Status
- [ ] List all outdated packages: `pip3 list --outdated`
- [ ] Check for CVEs: `pip-audit`
- [ ] Review GitHub Dependabot alerts (if enabled)
- [ ] Check Python version compatibility

---

## 🔧 Update Procedure

### Step 1: Core Dependencies (CRITICAL - Test Thoroughly)

#### MLX Stack (Apple Silicon)
```bash
# Check current versions
pip3 show mlx mlx-lm

# Update if new versions available
pip3 install --upgrade mlx mlx-lm

# Test MLX functionality
python3 -c "import mlx.core as mx; print(mx.__version__)"
python3 src/rag_system.py  # Quick smoke test
```

**Testing Required:**
- [ ] MLX model loads successfully
- [ ] RAG queries work with MLX backend
- [ ] No performance regression

---

#### LangChain Dependencies
```bash
# Current versions
pip3 show langchain langchain-community chromadb

# Update (CAUTION: Breaking changes common)
pip3 install --upgrade langchain langchain-community chromadb

# Address deprecation warnings
grep -r "LangChainDeprecationWarning" src/
```

**Known Issues to Watch:**
- `HuggingFaceEmbeddings` → `langchain-huggingface` migration
- `Chroma` → `langchain-chroma` migration
- Community package splits

**Testing Required:**
- [ ] Vector store initialization works
- [ ] Document retrieval functions correctly
- [ ] Embeddings generation successful
- [ ] No new deprecation warnings in logs

---

#### Streamlit & UI Components
```bash
# Update Streamlit
pip3 install --upgrade streamlit

# Test UI components
streamlit run src/main.py --server.port 8503
```

**Testing Required:**
- [ ] App loads without errors
- [ ] Camera input works (`st.camera_input()`)
- [ ] File uploads functional
- [ ] Charts/metrics display correctly
- [ ] Session state preserved

---

### Step 2: Data & API Dependencies

#### Food/Nutrition APIs
```bash
# Update requests and API clients
pip3 install --upgrade requests urllib3

# Test API connections
export USDA_FDC_API_KEY=$(grep USDA_FDC_API_KEY data/.env | cut -d '=' -f2)
python3 src/food_api_fdc.py
python3 src/food_api_off.py
```

**Testing Required:**
- [ ] USDA FDC API calls successful
- [ ] Open Food Facts API working
- [ ] Barcode scanning functional
- [ ] Rate limiting respected

---

#### Database & Storage
```bash
# Update database libraries
pip3 install --upgrade sqlite3  # Built-in, but check compatibility

# Test database operations
python3 -c "import sqlite3; print(sqlite3.version)"
python3 tests/test_meal_prep_workflow.py
```

**Testing Required:**
- [ ] Database migrations work
- [ ] CRUD operations successful
- [ ] Foreign key constraints enforced
- [ ] Backup/restore functional

---

### Step 3: Image Processing & Barcode Scanning
```bash
# Update imaging libraries
pip3 install --upgrade Pillow pyzbar

# Verify ZBar system library
brew list zbar
brew upgrade zbar  # If outdated

# Test barcode scanning
python3 -c "from pyzbar import pyzbar; from PIL import Image; print('OK')"
```

**Testing Required:**
- [ ] Barcode detection works
- [ ] Image processing functional
- [ ] Camera integration works in Streamlit

---

### Step 4: Data Processing & Scientific Computing
```bash
# Update NumPy, Pandas, etc.
pip3 install --upgrade numpy pandas openpyxl

# Test data operations
python3 -c "import numpy as np; import pandas as pd; print('OK')"
python3 src/calculations.py  # Test nutrition calculations
```

**Testing Required:**
- [ ] Calculations produce correct results
- [ ] Excel export/import works
- [ ] CSV parsing functional

---

### Step 5: Development & Testing Tools
```bash
# Update dev dependencies
pip3 install --upgrade pytest black flake8 mypy

# Run linting
black src/ --check
flake8 src/

# Run type checking
mypy src/ --ignore-missing-imports
```

**Testing Required:**
- [ ] Test suite passes: `pytest tests/`
- [ ] Linting passes with no new issues
- [ ] Type hints remain valid

---

## 🧪 Comprehensive Testing Checklist

### Critical Path Testing (MUST PASS)

#### 1. RAG System
```bash
# Test both backends
python3 -c "from rag_system import HealthRAG; rag = HealthRAG('mlx'); print(rag.query('test'))"
python3 -c "from rag_system import HealthRAG; rag = HealthRAG('ollama'); print(rag.query('test'))"
```
- [ ] MLX backend works
- [ ] Ollama backend works
- [ ] Model switching functional
- [ ] Query responses correct

#### 2. Nutrition Tracking
```bash
# Run complete workflow test
python3 tests/test_meal_prep_workflow.py
```
- [ ] Food search works (USDA + OFF)
- [ ] Barcode lookup functional
- [ ] Meal templates work
- [ ] Copy yesterday feature works
- [ ] Recent foods displayed correctly

#### 3. User Profile & Calculations
```bash
# Test profile and nutrition calculations
python3 -c "from profile import UserProfile; from calculations import calculate_nutrition_plan; print('OK')"
```
- [ ] Profile creation works
- [ ] Macro calculations correct
- [ ] TDEE calculations accurate
- [ ] Phase-specific advice correct

#### 4. Training Program Generation
```bash
# Test program generator
python3 -c "from program_generator import ProgramGenerator; print('OK')"
```
- [ ] Program generation works
- [ ] Exercise selection correct
- [ ] Equipment filtering works
- [ ] Export to Excel/CSV works

#### 5. Workout Logging
```bash
# Test workout logger
python3 -c "from workout_logger import WorkoutLogger; logger = WorkoutLogger(); print('OK')"
```
- [ ] Workout logging works
- [ ] Exercise history retrieval works
- [ ] Progress tracking functional
- [ ] Autoregulation analysis works

#### 6. End-to-End Streamlit Test
```bash
# Start app and test manually
streamlit run src/main.py --server.port 8503

# Manual testing checklist in browser:
```
- [ ] App loads without errors
- [ ] Profile creation works
- [ ] Nutrition tracking functional
- [ ] Camera barcode scanning works
- [ ] Training program displays correctly
- [ ] Workout logging works
- [ ] Chat interface responds
- [ ] All tabs accessible
- [ ] No console errors

---

## 📝 Requirements File Updates

### Update all requirements files:

```bash
# Main requirements
pip3 freeze > requirements-new.txt
# Carefully merge with requirements.txt, preserving pinned versions

# MLX-specific
pip3 freeze | grep -E "(mlx|numpy|torch)" > requirements-mlx-new.txt

# Ollama-specific
pip3 freeze | grep -E "(langchain|ollama|chromadb)" > requirements-ollama-new.txt
```

**Review Changes:**
- [ ] Compare `requirements.txt` vs `requirements-new.txt`
- [ ] Verify no unexpected version jumps (e.g., 1.0 → 2.0)
- [ ] Check for new transitive dependencies
- [ ] Document any pinned versions and why

**Files to Update:**
- [ ] `requirements.txt` - Main dependencies
- [ ] `requirements-mlx.txt` - MLX-specific
- [ ] `requirements-ollama.txt` - Ollama-specific
- [ ] `.env.example` - If new env vars needed
- [ ] `README.md` - If setup instructions changed

---

## 🔒 Security Review

### Check for Known Vulnerabilities
```bash
# Run security audit
pip-audit --desc

# Check CVE database
pip-audit --format json > security-audit.json
```

**Review Results:**
- [ ] Document all HIGH/CRITICAL vulnerabilities
- [ ] Update vulnerable packages immediately
- [ ] Check for available patches
- [ ] Test after security updates

### Dependency Review
- [ ] Remove unused dependencies: `pipdeptree --warn silence | grep -v "=="`
- [ ] Check for abandoned packages (no updates >2 years)
- [ ] Review transitive dependencies for security issues
- [ ] Verify all packages from trusted sources (PyPI)

---

## 📄 Documentation Updates

### Update Documentation if Needed:

- [ ] `docs/SETUP.md` - Installation instructions
- [ ] `docs/FOOD_TRACKING_IMPLEMENTATION.md` - API changes
- [ ] `README.md` - Dependency requirements
- [ ] Inline code comments for breaking changes

### Version Compatibility Matrix

| Component | Version | Tested | Notes |
|-----------|---------|--------|-------|
| Python | 3.10.2 | [ ] | Min: 3.10 |
| MLX | X.X.X | [ ] | Apple Silicon only |
| LangChain | X.X.X | [ ] | Check deprecations |
| Streamlit | X.X.X | [ ] | UI compatibility |
| pyzbar | X.X.X | [ ] | Barcode scanning |
| Pillow | X.X.X | [ ] | Image processing |
| ChromaDB | X.X.X | [ ] | Vector store |
| OpenPyXL | X.X.X | [ ] | Excel export |

---

## 🚀 Deployment Checklist

### Before Merging:
- [ ] All tests pass locally
- [ ] No new errors in Streamlit logs
- [ ] Performance benchmarks acceptable
- [ ] Memory usage within limits
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### Git Workflow:
```bash
# Commit changes
git add requirements*.txt src/ tests/ docs/
git commit -m "chore(deps): weekly dependency update - $(date +%Y-%m-%d)

- Updated MLX to vX.X.X
- Updated LangChain to vX.X.X
- Updated Streamlit to vX.X.X
- Fixed N security vulnerabilities
- All tests passing
- See issue #XXX for details"

# Push and create PR
git push -u origin deps/weekly-update-$(date +%Y-%m-%d)
gh pr create --title "Weekly Dependency Update - $(date +%Y-%m-%d)" \
             --body "Closes #XXX" \
             --label "dependencies,maintenance"
```

### PR Review Checklist:
- [ ] CI/CD pipeline passes (if configured)
- [ ] No merge conflicts
- [ ] Requirements files updated
- [ ] Documentation updated
- [ ] Tests pass on clean environment
- [ ] Security audit clean

---

## ⚠️ Rollback Plan

If issues discovered after merge:

### Immediate Rollback:
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to previous tag
git reset --hard <previous-tag>
git push --force origin main  # DANGER: Only if just merged
```

### Gradual Rollback (Specific Packages):
```bash
# Identify problematic package
pip3 show <package-name>

# Downgrade to previous version
pip3 install <package-name>==<previous-version>

# Test and commit fix
git commit -am "fix(deps): rollback <package-name> to vX.X.X due to [issue]"
```

### Recovery Steps:
1. Document the issue in this issue
2. Create new issue for the specific problem
3. Pin problematic package version in requirements.txt
4. Schedule investigation for next week
5. Notify users if production affected

---

## 📊 Weekly Report Template

### Summary for This Week:

**Packages Updated:** X total
- Critical: X packages
- Security patches: X packages
- Minor updates: X packages

**Security Issues:**
- HIGH: X (Details: ...)
- MEDIUM: X (Details: ...)
- LOW: X (Details: ...)

**Breaking Changes:**
- [ ] None
- [ ] Yes (Details: ...)

**Test Results:**
- Unit tests: PASS/FAIL (X/Y tests)
- Integration tests: PASS/FAIL
- Manual testing: PASS/FAIL

**Time Spent:** ~X hours

**Issues Found:**
1. [Issue description]
2. [Issue description]

**Next Week Action Items:**
- [ ] Action item 1
- [ ] Action item 2

---

## 🤖 Automation Recommendations

### Future Improvements:

1. **GitHub Actions Workflow:**
   - Create `.github/workflows/dependency-update.yml`
   - Run weekly on schedule (Sundays 2am)
   - Auto-create PR with updated dependencies
   - Run test suite automatically

2. **Dependabot Configuration:**
   - Enable Dependabot for security updates
   - Configure `.github/dependabot.yml`
   - Auto-merge minor/patch updates
   - Manual review for major updates

3. **Pre-commit Hooks:**
   - Add `pip-audit` to pre-commit hooks
   - Block commits with known vulnerabilities
   - Auto-format requirements files

4. **Monitoring:**
   - Set up alerts for new CVEs
   - Monitor package release notes
   - Track breaking changes in dependencies

---

## 📚 Resources

### Documentation:
- [Python Package Index (PyPI)](https://pypi.org/)
- [CVE Database](https://cve.mitre.org/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [Dependabot Docs](https://docs.github.com/en/code-security/dependabot)

### Key Dependencies:
- [MLX Documentation](https://ml-explore.github.io/mlx/)
- [LangChain Docs](https://python.langchain.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [ChromaDB Docs](https://docs.trychroma.com/)

### Security Resources:
- [Python Security Advisories](https://github.com/pypa/advisory-database)
- [Snyk Vulnerability Database](https://security.snyk.io/)

---

## ✅ Completion Checklist

- [ ] All dependency updates tested
- [ ] Security vulnerabilities addressed
- [ ] Requirements files updated
- [ ] Documentation updated
- [ ] Tests passing
- [ ] PR created and merged
- [ ] Issue closed with summary
- [ ] Next week's issue created

---

**Estimated Time:** 2-4 hours (depending on breaking changes)
**Priority:** Medium (unless security issues: HIGH)
**Frequency:** Weekly (Every Monday or Sunday evening)
