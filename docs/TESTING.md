# HealthRAG Testing Guide

## Overview

HealthRAG uses a **local-first testing workflow** to ensure high quality deployments and minimize unnecessary Render.com deploys.

**Philosophy**: Test everything locally before pushing. Only push to `main` when confident code is production-ready.

---

## 🧪 Testing Tools

### 1. Local Testing (`test-checklist.sh`)

Comprehensive pre-push validation script that runs all tests locally.

**Usage**:
```bash
# Run all tests (recommended before pushing)
./test-checklist.sh

# Quick mode (skip manual validation)
./test-checklist.sh --quick

# Include Docker build validation
./test-checklist.sh --docker
```

**What it tests**:
- ✅ Python syntax validation
- ✅ Import checks
- ✅ Unit tests (48+ tests)
  - Adaptive TDEE calculations
  - EWMA trend weight
  - Macro calculations
  - Profile system
- ✅ Integration tests
  - RAG system
- ✅ Manual UI validation prompt
- ✅ Optional Docker build

**Exit codes**:
- `0` = All tests passed (safe to push)
- `1+` = Number of failures (DO NOT PUSH)

### 2. Unit Tests (`pytest`)

Run specific test suites:

```bash
# All tests
pytest tests/ -v

# Adaptive TDEE tests only
pytest tests/test_adaptive_tdee.py tests/test_adaptive_tdee_calculations.py -v

# Calculation tests
pytest tests/test_calculations.py -v

# Profile tests
pytest tests/test_profile.py -v

# With coverage report
pytest --cov=src tests/ --cov-report=html
```

### 3. Browser Tests (`playwright`)

End-to-end testing with Playwright (Docker-based):

```bash
# Run all browser tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Run specific tier
docker-compose -f docker-compose.test.yml run playwright-tests \
  pytest tests/browser/test_tier1_personas.py -v

# Cross-browser testing
for browser in chromium firefox webkit; do
  BROWSER=$browser docker-compose -f docker-compose.test.yml up --abort-on-container-exit
done

# View results
open playwright-report/index.html
```

### 4. Manual Testing

```bash
# Start Streamlit locally
streamlit run src/main.py

# Access at http://localhost:8501

# Test critical flows:
# 1. Create profile
# 2. Log weight (multiple days)
# 3. Log food (multiple days)
# 4. View Adaptive TDEE (after 14+ days)
# 5. Apply macro adjustment
```

---

## 🔄 Daily Development Workflow

### Morning: Start New Feature

```bash
# 1. Pull latest main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feat/meal-templates

# 3. Code and test throughout the day
# ... make changes ...
pytest tests/test_new_feature.py -v
streamlit run src/main.py
```

### Before Pushing: Validate

```bash
# 4. Run comprehensive tests
./test-checklist.sh

# If tests pass ✅
git add .
git commit -m "Add meal template feature

Tested:
- Unit tests pass (48/48)
- Manual UI validation complete
- Critical flows verified

Ready for production."

git push origin feat/meal-templates

# If tests fail ❌
# Fix issues, test again, then push
pytest tests/ -vv  # See detailed errors
```

### When Feature Complete: Merge to Main

```bash
# 5. Final validation
git checkout main
git pull origin main
git merge feat/meal-templates

# Run tests on merged code
./test-checklist.sh

# If all pass, push to main
git push origin main  # ✅ Triggers Render deploy

# Monitor deployment
# https://dashboard.render.com
```

---

## 📋 When to Push to Main

### ✅ Push to Main When:

- **All unit tests pass** (48+ tests green)
- **Browser tests pass** (if running)
- **Manual UI testing complete**
  - Profile creation works
  - Weight/food logging works
  - Adaptive TDEE displays correctly
  - No console errors
- **Feature is complete** (not WIP)
- **Database migrations ready** (if applicable)
- **Environment variables set** (in Render dashboard)
- **You're ready for it to go live**

### ❌ Don't Push to Main When:

- **Work in progress** (use feature branch instead)
- **Tests are failing** (red tests = red flag)
- **Debugging in progress** (commit locally, don't push)
- **Experimental code** (create feat/experiment branch)
- **UI has console errors** (fix before pushing)
- **"Just saving work"** (use `git stash` instead)

---

## 🌿 Git Workflow Best Practices

### Use Feature Branches

```bash
# Good: Separate branches for separate features
git checkout -b feat/meal-templates
git checkout -b feat/workout-calendar
git checkout -b fix/database-bug
git checkout -b docs/update-readme

# Bad: Working directly on main
git checkout main  # ❌ Don't do this during development
```

### Commit Often Locally, Push When Done

```bash
# Make many local commits (safe, fast)
git commit -m "WIP: add TDEE calculation"
git commit -m "WIP: add UI component"
git commit -m "WIP: fix calculation bug"

# But DON'T push until feature is complete and tested
./test-checklist.sh  # Validate first
git push origin feat/adaptive-tdee  # Then push
```

### Use Git Stash for Context Switching

```bash
# Need to switch branches but work isn't ready to commit?
git stash save "WIP: working on adaptive TDEE UI"

# Switch branches, do other work
git checkout fix/urgent-bug

# Come back later
git checkout feat/adaptive-tdee
git stash pop
```

### Keep Commit Messages Informative

```bash
# Good commit messages
git commit -m "Add adaptive TDEE feature

Implements MacroFactor-style TDEE calculation using:
- EWMA trend smoothing (alpha=0.3)
- Back-calculation from weight change + intake
- Adherence-neutral adjustment thresholds

Tested:
- 24/24 unit tests pass
- Manual UI validation complete
- 14-day workflow verified

Closes #42"

# Bad commit messages
git commit -m "fix stuff"  # ❌ Too vague
git commit -m "WIP"        # ❌ Not descriptive
```

---

## 🚨 Handling Urgent Hotfixes

If production is broken and you need to deploy a fix quickly:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/database-error

# 2. Make minimal fix
# ... fix the specific bug ...

# 3. Test ONLY the hotfix
pytest tests/test_database.py -v
./test-checklist.sh --quick  # Skip optional tests

# 4. Fast-track to main
git checkout main
git merge hotfix/database-error
git push origin main  # ✅ Deploys immediately (~5 min)

# 5. Monitor deployment
# https://dashboard.render.com
```

---

## 🐳 Docker Testing

### Local Docker Testing

```bash
# Build and start containers
docker-compose build
docker-compose up -d

# Check health
docker-compose ps
curl http://localhost:8501/_stcore/health

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Weekly Docker Validation

```bash
# Every Friday, validate Docker still works
docker-compose build
docker-compose up -d
sleep 10
curl http://localhost:8501/_stcore/health
docker-compose down

# Catches Docker issues before they hit production
```

---

## 📊 Cost Optimization

### Before Local-First Testing

- **Pushes**: 5-10 times/day during active development
- **Render builds**: 150-300 per month
- **Build time**: 1,500+ minutes/month
- **Cost**: $$$ (high)

### After Local-First Testing

- **Pushes to main**: 1-2 times/week (only when ready)
- **Render builds**: 8-12 per month
- **Build time**: 40-60 minutes/month
- **Cost**: $ (96% reduction!)

**Key insight**: Feature branches don't trigger Render deploys. Only pushes to `main` do.

---

## 🔍 Debugging Failed Tests

### Unit Test Failures

```bash
# See detailed error output
pytest tests/ -vv --tb=short

# Run specific failing test
pytest tests/test_adaptive_tdee.py::TestEWMA::test_trend_weight -vv

# Drop into debugger on failure
pytest tests/ --pdb

# Show print statements
pytest tests/ -s
```

### Streamlit UI Issues

```bash
# Start with verbose logging
streamlit run src/main.py --logger.level debug

# Check browser console for errors
# (Open DevTools in browser: F12)

# Check Streamlit logs
cat ~/.streamlit/logs/streamlit.log
```

### Docker Issues

```bash
# View container logs
docker-compose logs healthrag
docker-compose logs -f  # Follow logs

# Exec into container
docker-compose exec healthrag bash

# Rebuild from scratch
docker-compose down -v  # Remove volumes
docker-compose build --no-cache
docker-compose up
```

---

## 📈 Test Coverage Goals

### Current Coverage

- **Adaptive TDEE**: 48 tests (100% coverage)
- **Calculations**: 25 tests (100% coverage)
- **Profile System**: 30+ tests (~80% coverage)
- **RAG System**: 7 tests (basic coverage)

### Coverage Gaps

- [ ] Nutrition tracking edge cases
- [ ] Workout logging validation
- [ ] Barcode scanner error handling
- [ ] Multi-user profile switching

### Running Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src tests/ --cov-report=html

# Open report
open htmlcov/index.html

# View in terminal
pytest --cov=src tests/ --cov-report=term-missing
```

---

## ✅ Pre-Merge Checklist

Before merging to `main`, verify:

- [ ] `./test-checklist.sh` passes (0 failures)
- [ ] Manual UI testing complete
- [ ] No console errors in browser
- [ ] Database migrations applied (if any)
- [ ] Environment variables set in Render (if new ones)
- [ ] Documentation updated (if API changes)
- [ ] Commit message is descriptive
- [ ] Ready for feature to go live

---

## 🎯 Quick Reference

```bash
# Daily testing
./test-checklist.sh              # Before every push

# Specific test suites
pytest tests/test_adaptive_tdee.py -v              # TDEE tests
pytest tests/test_calculations.py -v               # Calculations
pytest tests/ -k "test_profile" -v                 # Profile tests

# Manual testing
streamlit run src/main.py                          # Local UI

# Docker testing
docker-compose up -d                               # Start containers
docker-compose down                                # Stop containers

# Browser testing (when implemented)
docker-compose -f docker-compose.test.yml up       # E2E tests
```

---

## 📚 Additional Resources

- **pytest docs**: https://docs.pytest.org/
- **Streamlit docs**: https://docs.streamlit.io/
- **Playwright docs**: https://playwright.dev/python/
- **Docker Compose**: https://docs.docker.com/compose/

---

**Remember**: Test locally, push confidently! 🚀
