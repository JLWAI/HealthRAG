# 🎯 TASK: Implement Comprehensive Browser Testing for HealthRAG

## Context

You are implementing **automated browser testing** for HealthRAG, a Streamlit-based fitness/nutrition tracking application with an Adaptive TDEE system. The testing framework uses **Playwright** (Microsoft's modern browser automation tool) with full **Docker containerization**.

**Current Status**:
- ✅ Testing infrastructure created (Docker, fixtures, documentation)
- ✅ 13 example test implementations provided (Tier 1-2)
- ⏳ **YOUR TASK**: Implement remaining test scenarios and validate the system

---

## 📚 Key Documentation (READ FIRST)

### Primary Reference
**File**: `.codex/prompts/automated_browser_testing.md` (1,228 LOC)

This file contains:
- Complete Playwright test examples for 13 scenarios
- Helper function documentation
- Docker setup instructions
- Streamlit-specific wait strategies
- Mock strategies for APIs/camera
- All 50 test scenario specifications

### Supporting Files
- **`docker-compose.test.yml`** - Testing environment configuration
- **`tests/Dockerfile.playwright`** - Test runner container
- **`tests/browser/conftest.py`** - Reusable fixtures and helpers (580 LOC)

---

## 🎯 Your Mission

Implement **end-to-end browser tests** for HealthRAG covering:

1. **Tier 1** (5 scenarios) - ✅ DONE - Core user personas
2. **Tier 2** (8 scenarios) - ✅ DONE - Adaptive TDEE edge cases
3. **Tier 3** (7 scenarios) - ⏳ TODO - Exercise goal variations
4. **Tier 4** (8 scenarios) - ⏳ TODO - Diet outcome edge cases
5. **Tier 5** (12 scenarios) - ⏳ TODO - Multi-goal combinations
6. **Tier 6** (10 scenarios) - ⏳ TODO - Workflow integrations

**Total**: 50 comprehensive scenarios

---

## 📋 Step-by-Step Implementation Plan

### Phase 1: Setup & Validation (30 minutes)

1. **Read the comprehensive testing documentation**
   ```bash
   # Open and read this file thoroughly
   cat .codex/prompts/automated_browser_testing.md
   ```

2. **Verify Docker Compose setup**
   ```bash
   # Test that Docker setup works
   docker-compose -f docker-compose.test.yml up --abort-on-container-exit

   # This should start HealthRAG + run existing tests
   # Expected: 13 tests in Tier 1-2 should pass (if implemented)
   ```

3. **Verify fixtures work**
   ```bash
   # Check that conftest.py loads correctly
   pytest tests/browser/ --collect-only

   # Should show test collection without errors
   ```

### Phase 2: Implement Tier 3 - Exercise Goal Variations (2-3 hours)

**File to create**: `tests/browser/test_tier3_exercise_goals.py`

Implement 7 scenarios (see `.codex/prompts/automated_browser_testing.md` for details):

```python
import pytest
from playwright.async_api import Page, expect

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_strength_focused_cutting(page: Page, streamlit_ready, create_profile):
    """
    Scenario 3.1: Cutting while maintaining/gaining strength.

    Profile: Modified Beginner Ben
    - Primary goal: Preserve strength during deficit
    - Exercise: Heavy compounds (3x/week, low volume)
    - Diet: Moderate deficit (-500 cal)

    Workflow:
    1. Create profile with strength focus
    2. Log 14 days of weight loss (210 → 208 lbs)
    3. Log 14 days of strength workouts (PRs maintained/increased)
    4. Log 14 days of high-protein food (1g/lb)
    5. Verify Adaptive TDEE shows on-track
    6. Verify coaching emphasizes strength preservation
    """
    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Implementation here (follow Tier 1-2 patterns)
    # Use helper fixtures: create_profile(), log_weight_series(), log_food_series()
    # Reference: automated_browser_testing.md Scenario 3.1

    pass  # Replace with implementation

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_hypertrophy_focused_bulking(page: Page, streamlit_ready, create_profile):
    """Scenario 3.2: Bulking for maximum muscle size"""
    # Implementation (18-22 sets/muscle/week, moderate surplus)
    pass

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_powerlifting_recomp(page: Page, streamlit_ready, create_profile):
    """Scenario 3.3: Strength gains while staying in weight class"""
    pass

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_endurance_athlete_cutting(page: Page, streamlit_ready, create_profile):
    """Scenario 3.4: Runner/cyclist cutting for performance"""
    pass

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_bodybuilding_contest_prep(page: Page, streamlit_ready, create_profile):
    """Scenario 3.5: Extreme fat loss for show (12 weeks out)"""
    pass

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_crossfit_maintenance(page: Page, streamlit_ready, create_profile):
    """Scenario 3.6: CrossFit performance + aesthetics maintenance"""
    pass

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_minimal_time_commitment(page: Page, streamlit_ready, create_profile):
    """Scenario 3.7: Busy professional (2-3x/week training)"""
    pass
```

**Run tests**:
```bash
docker-compose -f docker-compose.test.yml run playwright-tests \
  pytest tests/browser/test_tier3_exercise_goals.py -v
```

### Phase 3: Implement Tier 4 - Diet Outcome Edge Cases (2-3 hours)

**File to create**: `tests/browser/test_tier4_diet_outcomes.py`

Implement 8 scenarios:
- Very aggressive deficit (-1000 cal/day, -2 lb/week)
- Very small deficit (-100 cal/day, -0.2 lb/week)
- Large surplus (+700 cal/day, +1.4 lb/week)
- High protein emphasis (1.2g/lb bodyweight)
- Low carb preference (keto-ish)
- Refeed day inclusion (diet breaks)
- Inconsistent adherence (±250 cal variance)
- Extreme weight fluctuations (water retention)

**Pattern**:
```python
@pytest.mark.tier4
@pytest.mark.asyncio
async def test_very_aggressive_deficit(page: Page, streamlit_ready, create_profile):
    """
    Scenario 4.1: Rapid Fat Loss Protocol

    Setup: -1000 cal/day deficit
    Expected: System warns about losing too fast (+150 cal recommendation)
    Validation: Minimum protein maintained, coaching emphasizes sustainability
    """
    # Implementation
    pass
```

### Phase 4: Implement Tier 5 - Multi-Goal Combinations (3-4 hours)

**File to create**: `tests/browser/test_tier5_multi_goal.py`

Implement 12 scenarios combining exercise goals + diet outcomes:
- Cut + Strength + Moderate Deficit
- Cut + Hypertrophy + Aggressive Deficit
- Bulk + Strength + Small Surplus
- Bulk + Hypertrophy + Moderate Surplus
- Recomp + Strength + Maintenance
- Recomp + Hypertrophy + Small Deficit
- etc.

**Parametrize for efficiency**:
```python
@pytest.mark.tier5
@pytest.mark.parametrize("exercise_goal,diet_goal,expected_outcome", [
    ("strength", "moderate_deficit", "strength_maintained_fat_lost"),
    ("hypertrophy", "small_surplus", "lean_muscle_gain"),
    ("endurance", "small_deficit", "performance_weight_loss"),
    # ... 12 total combinations
])
@pytest.mark.asyncio
async def test_multi_goal_combinations(
    page: Page,
    streamlit_ready,
    create_profile,
    exercise_goal: str,
    diet_goal: str,
    expected_outcome: str
):
    """Parametrized test for all goal combinations"""
    # Implementation with dynamic profile creation based on parameters
    pass
```

### Phase 5: Implement Tier 6 - Workflow Integrations (2-3 hours)

**File to create**: `tests/browser/test_tier6_workflow.py`

Implement 10 workflow integration scenarios:

```python
@pytest.mark.tier6
@pytest.mark.asyncio
async def test_complete_14day_onboarding(page: Page, streamlit_ready):
    """
    Scenario 6.1: Full user onboarding journey

    Workflow:
    1. New user arrives (no profile)
    2. Creates profile
    3. Reviews initial macro plan
    4. Logs 14 days consistently
    5. Views Adaptive TDEE analysis
    6. Applies macro adjustment
    7. Continues to Day 21
    8. Validates adjustment worked
    """
    # End-to-end flow, most comprehensive test
    pass

@pytest.mark.tier6
@pytest.mark.asyncio
async def test_barcode_scanner_workflow(page: Page, streamlit_ready, mock_barcode_api, mock_camera):
    """
    Scenario 6.4: Barcode scanner integration

    Workflow:
    1. Enable camera in nutrition tracking
    2. Mock camera stream
    3. Scan product barcode (mock UPC: "012345678901")
    4. System fetches from Open Food Facts (mocked)
    5. Adjust serving size (1 → 2 containers)
    6. Add to food log
    7. Verify daily totals updated
    """
    # Use mock fixtures to simulate camera/API
    await mock_barcode_api(page, "012345678901", {
        "product_name": "Greek Yogurt",
        "nutriments": {"energy-kcal": 100, "proteins": 15}
    })
    await mock_camera(page, "012345678901")

    # Implementation
    pass

# Additional scenarios: profile updates, meal templates, copy yesterday, etc.
```

### Phase 6: Cross-Browser Validation (1 hour)

Run all tests across browsers:

```bash
# Chromium (default)
BROWSER=chromium docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Firefox
BROWSER=firefox docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# WebKit (Safari engine)
BROWSER=webkit docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Phase 7: Report Generation & Bug Documentation (1 hour)

1. **Generate comprehensive test report**
   ```bash
   # Report already generated at playwright-report/index.html
   open playwright-report/index.html
   ```

2. **Create bug report for any failures**

   **File to create**: `test_results/BUG_REPORT.md`

   Template:
   ```markdown
   # HealthRAG Browser Test Bug Report

   **Date**: 2025-01-15
   **Browser**: Chromium 120.0
   **Test Suite Version**: 1.0

   ## Summary
   - Total Tests: 50
   - Passed: X
   - Failed: Y
   - Skipped: Z

   ## Critical Bugs

   ### Bug 1: [Short Description]
   **Test**: `test_beginner_ben_cutting_journey`
   **Severity**: Critical
   **Status**: New

   **Description**:
   When logging weight on Day 7, the system throws a database error.

   **Steps to Reproduce**:
   1. Create profile (Ben Beginner, cutting)
   2. Log weights for Days 1-6 (successful)
   3. Attempt to log weight for Day 7
   4. Error: "UNIQUE constraint failed: weight_entries.date"

   **Expected Behavior**:
   Weight should be logged successfully, replacing existing entry for that date.

   **Actual Behavior**:
   Database error occurs, weight not logged.

   **Screenshot**: `test-results/screenshots/bug1-weight-log-error.png`
   **Video**: `test-results/videos/test_beginner_ben_cutting_journey-chromium.webm`
   **Trace**: `trace-results/test_beginner_ben-chromium.zip`

   **Suggested Fix**:
   Update `WeightTracker.log_weight()` to use `INSERT OR REPLACE` instead of `INSERT`.
   File: `src/adaptive_tdee.py:123`

   ---

   ## Major Bugs

   [Continue pattern for all failures]

   ## Minor Issues

   [UI/UX issues, non-blocking]
   ```

3. **Coverage matrix**

   **File to create**: `test_results/COVERAGE_MATRIX.csv`

   ```csv
   Scenario ID,Tier,Persona,Goal Combo,Browser,Status,Duration (s),Notes
   1.1,Tier1,Beginner Ben,Cut + Moderate Deficit,Chromium,PASS,45.2,
   1.2,Tier1,Intermediate Ian,Bulk + Small Surplus,Chromium,PASS,48.7,
   1.3,Tier1,Cutting Claire,Cut + Aggressive Deficit,Chromium,FAIL,32.1,Weight log DB error on Day 7
   2.1,Tier2,Ben Variant,Losing Too Fast,Chromium,PASS,50.3,
   ...
   ```

---

## 🛠️ Key Implementation Tips

### 1. Reuse Existing Patterns

**Good** (reuse helpers):
```python
# Use the helper fixtures!
await create_profile(page, {
    "name": "Test User",
    "age": 30,
    "sex": "Male",
    # ... etc
})

await log_weight_series(page, weights=[210, 209, 208], start_date="2025-01-01")
await log_food_series(page, avg_calories=2100, avg_protein=210, num_days=14)
```

**Bad** (reinventing the wheel):
```python
# Don't manually repeat profile creation in every test
await page.click("text=Create New Profile")
await page.fill("input[aria-label='Name']", "Test User")
# ... 20 more lines
```

### 2. Use Playwright Auto-Waiting

**Good** (let Playwright wait):
```python
await page.click("button:has-text('Log Weight')")
await expect(page.locator("text=210.5 lbs")).to_be_visible()
```

**Bad** (explicit waits):
```python
import time
await page.click("button:has-text('Log Weight')")
time.sleep(2)  # ❌ Don't do this!
```

### 3. Handle Streamlit Quirks

Always use the `streamlit_ready` fixture:
```python
@pytest.mark.asyncio
async def test_something(page: Page, streamlit_ready):
    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)  # ✅ Wait for Streamlit to be ready

    # Now interact with app
```

### 4. Mock External Dependencies

For barcode scanner tests:
```python
@pytest.mark.asyncio
async def test_barcode(page: Page, mock_barcode_api, mock_camera):
    # Mock Open Food Facts API
    await mock_barcode_api(page, "012345678901", {
        "product_name": "Greek Yogurt",
        "nutriments": {"energy-kcal": 100, "proteins": 15}
    })

    # Mock camera/barcode detector
    await mock_camera(page, "012345678901")

    # Now test barcode scanning flow
```

### 5. Debug with Trace Viewer

When tests fail:
```bash
# View the trace in Playwright's visual debugger
playwright show-trace trace-results/test-name-chromium.zip

# This shows:
# - DOM snapshots at each step
# - Network requests
# - Console logs
# - Exact failure point
```

---

## ✅ Success Criteria

Your implementation is complete when:

1. **All 50 test files created** (Tier 3-6)
   - `test_tier3_exercise_goals.py` (7 tests)
   - `test_tier4_diet_outcomes.py` (8 tests)
   - `test_tier5_multi_goal.py` (12 tests)
   - `test_tier6_workflow.py` (10 tests)

2. **All tests run successfully**
   ```bash
   docker-compose -f docker-compose.test.yml up --abort-on-container-exit
   # Expected: 50 tests collected, ≥45 pass (90%+)
   ```

3. **Cross-browser validation passes**
   - Chromium: ≥90% pass
   - Firefox: ≥85% pass (may have minor UI quirks)
   - WebKit: ≥80% pass (Safari has different behavior)

4. **Reports generated**
   - `playwright-report/index.html` (HTML test report)
   - `test_results/BUG_REPORT.md` (bug documentation)
   - `test_results/COVERAGE_MATRIX.csv` (scenario coverage)
   - `trace-results/*.zip` (failure traces)
   - `test-results/videos/*.webm` (failure videos)

5. **Test execution time**
   - Full suite: <25 minutes
   - Tier 1-2: <5 minutes
   - Tier 3-6: <20 minutes

---

## 🚨 Common Issues & Solutions

### Issue 1: "Streamlit element not found"
**Solution**: Use `streamlit_ready` fixture and wait for `[data-testid="stApp"]`

### Issue 2: "Element is not clickable"
**Solution**: Streamlit may be re-rendering. Add `await page.wait_for_load_state('networkidle')`

### Issue 3: "Database locked" errors
**Solution**: Ensure previous test cleaned up properly. Use `@pytest.fixture(scope="function")` for database fixtures.

### Issue 4: Tests pass locally but fail in Docker
**Solution**: Check BASE_URL is `http://healthrag:8501` not `localhost` in Docker network.

### Issue 5: Camera mock not working
**Solution**: Verify mock is set up before navigating to camera page. Use `page.route()` before page loads.

---

## 📦 Deliverables Checklist

- [ ] `tests/browser/test_tier3_exercise_goals.py` (7 scenarios implemented)
- [ ] `tests/browser/test_tier4_diet_outcomes.py` (8 scenarios implemented)
- [ ] `tests/browser/test_tier5_multi_goal.py` (12 scenarios implemented)
- [ ] `tests/browser/test_tier6_workflow.py` (10 scenarios implemented)
- [ ] All tests passing (≥90% pass rate)
- [ ] Cross-browser validation complete
- [ ] `playwright-report/index.html` generated
- [ ] `test_results/BUG_REPORT.md` created
- [ ] `test_results/COVERAGE_MATRIX.csv` created
- [ ] Video/trace artifacts for failures

---

## 🎬 Ready to Start?

1. **Read the comprehensive documentation**:
   ```bash
   cat .codex/prompts/automated_browser_testing.md
   ```

2. **Start with Tier 3** (easiest after seeing Tier 1-2 examples):
   ```bash
   # Create test file
   touch tests/browser/test_tier3_exercise_goals.py

   # Implement scenarios following Tier 1-2 patterns
   # Run tests
   docker-compose -f docker-compose.test.yml run playwright-tests \
     pytest tests/browser/test_tier3_exercise_goals.py -v
   ```

3. **Iterate through Tiers 4, 5, 6**

4. **Generate reports and document bugs**

5. **Celebrate 🎉** - You've implemented production-grade browser testing!

---

## 📞 Need Help?

- **Playwright docs**: https://playwright.dev/python/docs/intro
- **pytest-playwright**: https://playwright.dev/python/docs/test-runners
- **Streamlit docs**: https://docs.streamlit.io/
- **Reference examples**: See Tier 1-2 in `automated_browser_testing.md`

**Good luck! 🚀**
