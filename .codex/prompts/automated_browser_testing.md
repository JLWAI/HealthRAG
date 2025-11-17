# Automated Browser Testing for HealthRAG - Playwright + Docker

## 🎯 Objective
Implement comprehensive browser testing using **Playwright** (Microsoft's modern automation framework) with full Docker support, covering 50+ end-to-end scenarios across user personas, adaptive TDEE edge cases, and workflow integrations.

**Why Playwright?**
- ✅ Auto-waiting (no explicit waits needed)
- ✅ Cross-browser support (Chromium, Firefox, WebKit)
- ✅ Built-in trace viewer, video recording, screenshots
- ✅ Network interception for API mocking
- ✅ Better Codex integration (Microsoft partnership)
- ✅ Modern async/await Python syntax

---

## 📋 Prerequisites

### Option A: Docker Testing (Recommended)
```bash
# One command to run all tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# View results
open playwright-report/index.html
open trace-results/trace.zip  # Playwright Trace Viewer
```

### Option B: Local Testing
```bash
# Install Playwright
pip install playwright pytest-playwright pytest-asyncio
playwright install chromium firefox webkit

# Run tests
pytest tests/browser/ -v

# Run with headed mode (see browser)
pytest tests/browser/ --headed --slowmo 1000
```

### Environment Variables
```bash
# Docker Compose sets these automatically
export BASE_URL="http://localhost:8501"
export HEADLESS="true"
export BROWSER="chromium"  # or firefox, webkit
export SLOWMO="0"  # milliseconds to slow down operations
export VIDEO="on-failure"  # or always, off
export TRACE="on-failure"  # or always, off
```

---

## 🏗️ Test Architecture

### File Structure
```
tests/browser/
├── conftest.py                    # Playwright fixtures + helpers
├── test_tier1_personas.py         # 5 core persona scenarios
├── test_tier2_adaptive_tdee.py    # 8 Adaptive TDEE edge cases
├── test_tier3_exercise_goals.py   # 7 exercise goal variations
├── test_tier4_diet_outcomes.py    # 8 diet outcome edge cases
├── test_tier5_multi_goal.py       # 12 multi-goal combinations
├── test_tier6_workflow.py         # 10 workflow integrations
└── helpers/
    ├── streamlit.py               # Streamlit-specific wait strategies
    ├── profiles.py                # Profile creation helpers
    ├── logging.py                 # Weight/food/workout logging
    ├── assertions.py              # Custom TDEE assertions
    └── mocks.py                   # Barcode/camera/API mocking
```

### Playwright Configuration
```python
# pytest.ini additions
[pytest]
asyncio_mode = auto
markers =
    tier1: Core persona scenarios
    tier2: Adaptive TDEE edge cases
    tier3: Exercise goal variations
    tier4: Diet outcome edge cases
    tier5: Multi-goal combinations
    tier6: Workflow integrations
    slow: Slow-running tests (>30s)
```

---

## 🧪 Test Scenario Matrix (50 Scenarios)

### Tier 1: Core User Personas (5 scenarios)

#### **Scenario 1.1: Beginner Ben - Cutting Journey**

**Profile**:
- Male, 30 years, 5'10", 210 lbs, Sedentary
- Goal: Cut to 190 lbs (-20 lbs)
- Experience: Beginner (6 months)

**14-Day Workflow**:
1. Create profile → Get initial macros (2100 cal, 210g protein)
2. Log daily weight: 210 → 208 lbs (-1 lb/week trend)
3. Log daily food: Average 2100 cal/day (±100 variance)
4. Day 14: View Adaptive TDEE → Expected: 2600 cal, "✅ On track"
5. Validate: No macro adjustment recommended

**Playwright Implementation**:
```python
import pytest
from playwright.async_api import Page, expect
import random

@pytest.mark.tier1
@pytest.mark.asyncio
async def test_beginner_ben_cutting_journey(page: Page, streamlit_ready):
    """
    Scenario 1.1: Complete 14-day cutting journey with on-track result.

    Validates:
    - Profile creation flow
    - Daily weight/food logging
    - EWMA trend weight calculation
    - Adaptive TDEE back-calculation
    - "On track" recommendation (no adjustment)
    """

    # ===== DAY 1: Profile Creation =====
    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Navigate to profile creation (sidebar)
    await page.click("text=Create New Profile")

    # Fill profile form
    await page.fill("input[aria-label='Name']", "Ben Beginner")
    await page.fill("input[aria-label='Age']", "30")
    await page.select_option("select[aria-label='Sex']", "Male")
    await page.fill("input[aria-label='Weight (lbs)']", "210")
    await page.fill("input[aria-label='Height (inches)']", "70")  # 5'10"
    await page.select_option("select[aria-label='Activity Level']", "sedentary")
    await page.fill("input[aria-label='Goal Weight (lbs)']", "190")
    await page.select_option("select[aria-label='Phase']", "cut")

    # Submit profile
    await page.click("button:has-text('Create Profile')")

    # Wait for success message
    await expect(page.locator("text=Profile created successfully")).to_be_visible()

    # Verify initial macro plan displayed
    await page.click("text=📊 Your Nutrition Plan")

    # Assertions on initial macros
    calories_text = await page.locator('[data-testid="calories-value"]').text_content()
    calories = int(calories_text.replace(",", "").replace(" cal", ""))
    assert 2050 <= calories <= 2150, f"Expected ~2100 cal, got {calories}"

    protein_text = await page.locator('[data-testid="protein-value"]').text_content()
    protein = int(protein_text.replace("g", ""))
    assert 200 <= protein <= 220, f"Expected ~210g protein, got {protein}"


    # ===== DAYS 1-14: Weight Logging =====
    weights = [210.0 - (i * 0.143) for i in range(14)]  # 210 → 208 lbs

    for day, weight in enumerate(weights, start=1):
        # Navigate to weight tracking
        await page.click("text=⚖️ Weight Tracking")

        # Click "Log Weight" tab
        await page.click("button[role='tab']:has-text('📝 Log Weight')")

        # Fill weight form
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.fill("textarea[aria-label='Notes']", f"Day {day} - Cutting week {(day-1)//7 + 1}")

        # Submit weight entry
        await page.click("button:has-text('Log Weight')")

        # Verify success
        await expect(page.locator(f"text={weight:.1f} lbs")).to_be_visible()

        # Take screenshot every 7 days for debugging
        if day % 7 == 0:
            await page.screenshot(path=f"test-results/ben-day{day}-weight.png")


    # ===== DAYS 1-14: Food Logging =====
    for day in range(1, 15):
        # Navigate to nutrition tracking
        await page.click("text=🍽️ Nutrition Tracking")

        # Click "Add Food" tab
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")

        # Log daily meals (simulated as single entry)
        daily_calories = 2100 + random.randint(-100, 100)  # Realistic variance
        daily_protein = int(daily_calories * 0.10 / 4)  # ~10% protein

        await page.fill("input[aria-label='Food Name']", f"Day {day} Total Meals")
        await page.fill("input[aria-label='Calories']", str(daily_calories))
        await page.fill("input[aria-label='Protein (g)']", str(daily_protein))
        await page.fill("input[aria-label='Carbs (g)']", "200")
        await page.fill("input[aria-label='Fat (g)']", "70")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")

        # Select meal type
        await page.select_option("select[aria-label='Meal Type']", "dinner")

        # Add to log
        await page.click("button:has-text('Add to Log')")

        # Verify added
        await expect(page.locator(f"text={daily_calories} cal")).to_be_visible()


    # ===== DAY 14: Adaptive TDEE Analysis =====
    await page.click("text=🔬 Adaptive TDEE & Check-In")

    # Wait for analysis to load (should have 14 days of data)
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Extract Adaptive TDEE value
    adaptive_tdee_locator = page.locator('[data-testid="adaptive-tdee-value"]')
    await expect(adaptive_tdee_locator).to_be_visible()

    adaptive_tdee_text = await adaptive_tdee_locator.text_content()
    adaptive_tdee = int(adaptive_tdee_text.replace(",", "").replace(" cal", ""))

    # Assertion: TDEE should be 2550-2650 (accounting for EWMA lag)
    assert 2450 <= adaptive_tdee <= 2650, (
        f"Adaptive TDEE {adaptive_tdee} out of expected range 2450-2650. "
        f"Expected ~2600 cal based on 2100 intake + 2 lbs loss."
    )

    # Extract Formula TDEE for comparison
    formula_tdee_text = await page.locator('[data-testid="formula-tdee-value"]').text_content()
    formula_tdee = int(formula_tdee_text.replace(",", "").replace(" cal", ""))
    assert 2550 <= formula_tdee <= 2650, f"Formula TDEE {formula_tdee} unexpected"

    # Verify "On Track" status
    await expect(page.locator("text=✅ On track")).to_be_visible()
    await expect(page.locator("text=Keep doing what you're doing")).to_be_visible()

    # Verify no calorie adjustment recommended
    calorie_change_locator = page.locator('[data-testid="calorie-adjustment"]')
    calorie_change_text = await calorie_change_locator.text_content()
    assert "±0 cal" in calorie_change_text or "No change" in calorie_change_text, (
        f"Expected no adjustment, got: {calorie_change_text}"
    )

    # Verify weight trend chart exists
    await expect(page.locator("canvas")).to_be_visible()  # Plotly chart

    # Take final screenshot
    await page.screenshot(path="test-results/ben-day14-adaptive-tdee.png", full_page=True)

    # Success!
    print("✅ Scenario 1.1: Beginner Ben Cutting - PASSED")
```

---

#### **Scenario 1.2: Intermediate Ian - Bulking Journey**

**Profile**:
- Male, 28 years, 5'11", 185 lbs, Moderately Active
- Goal: Bulk to 195 lbs (+10 lbs)
- Experience: Intermediate (2+ years)

**14-Day Workflow**:
1. Create profile → Get initial macros (2900 cal, 180g protein)
2. Log daily weight: 185 → 186 lbs (+0.7 lb/week trend)
3. Log daily food: Average 2900 cal/day (±150 variance)
4. Day 14: View Adaptive TDEE → Expected: 2625 cal, "✅ On track"
5. Validate: No macro adjustment recommended

**Playwright Implementation**:
```python
@pytest.mark.tier1
@pytest.mark.asyncio
async def test_intermediate_ian_bulking_journey(page: Page, streamlit_ready):
    """
    Scenario 1.2: Complete 14-day bulking journey with on-track result.

    Validates:
    - Bulking phase macro calculation
    - Positive weight trend (muscle gain)
    - Higher calorie targets vs cutting
    - "On track" for bulking goals
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation
    await page.click("text=Create New Profile")
    await page.fill("input[aria-label='Name']", "Ian Intermediate")
    await page.fill("input[aria-label='Age']", "28")
    await page.select_option("select[aria-label='Sex']", "Male")
    await page.fill("input[aria-label='Weight (lbs)']", "185")
    await page.fill("input[aria-label='Height (inches)']", "71")  # 5'11"
    await page.select_option("select[aria-label='Activity Level']", "moderately_active")
    await page.fill("input[aria-label='Goal Weight (lbs)']", "195")
    await page.select_option("select[aria-label='Phase']", "bulk")
    await page.click("button:has-text('Create Profile')")

    # Verify bulking macros (higher calories)
    await page.click("text=📊 Your Nutrition Plan")
    calories_text = await page.locator('[data-testid="calories-value"]').text_content()
    calories = int(calories_text.replace(",", "").replace(" cal", ""))
    assert 2850 <= calories <= 2950, f"Expected ~2900 cal for bulk, got {calories}"

    # Log weight progression (185 → 186 lbs)
    weights = [185.0 + (i * 0.071) for i in range(14)]  # +1 lb total
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food intake (2900 cal/day average)
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        daily_calories = 2900 + random.randint(-150, 150)
        await page.fill("input[aria-label='Food Name']", f"Day {day} Bulk Meals")
        await page.fill("input[aria-label='Calories']", str(daily_calories))
        await page.fill("input[aria-label='Protein (g)']", "180")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Adaptive TDEE
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    adaptive_tdee_text = await page.locator('[data-testid="adaptive-tdee-value"]').text_content()
    adaptive_tdee = int(adaptive_tdee_text.replace(",", "").replace(" cal", ""))
    assert 2650 <= adaptive_tdee <= 2750, f"Adaptive TDEE {adaptive_tdee} unexpected for bulk"

    # Verify "On Track" for bulking
    await expect(page.locator("text=✅ On track")).to_be_visible()

    print("✅ Scenario 1.2: Intermediate Ian Bulking - PASSED")
```

---

#### **Scenario 1.3: Cutting Claire - Aggressive Fat Loss**

**Profile**:
- Female, 32 years, 5'6", 160 lbs, Very Active
- Goal: Cut to 145 lbs (-15 lbs)
- Experience: Advanced (4+ years)

**Implementation**:
```python
@pytest.mark.tier1
@pytest.mark.asyncio
async def test_cutting_claire_aggressive_fat_loss(page: Page, streamlit_ready):
    """Scenario 1.3: Aggressive cutting with very active lifestyle"""

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation
    await page.click("text=Create New Profile")
    await page.fill("input[aria-label='Name']", "Claire Cutting")
    await page.fill("input[aria-label='Age']", "32")
    await page.select_option("select[aria-label='Sex']", "Female")
    await page.fill("input[aria-label='Weight (lbs)']", "160")
    await page.fill("input[aria-label='Height (inches)']", "66")  # 5'6"
    await page.select_option("select[aria-label='Activity Level']", "very_active")
    await page.fill("input[aria-label='Goal Weight (lbs)']", "145")
    await page.select_option("select[aria-label='Phase']", "cut")
    await page.click("button:has-text('Create Profile')")

    # Verify aggressive deficit macros
    await page.click("text=📊 Your Nutrition Plan")
    calories_text = await page.locator('[data-testid="calories-value"]').text_content()
    calories = int(calories_text.replace(",", "").replace(" cal", ""))
    assert 1750 <= calories <= 1850, f"Expected ~1800 cal for aggressive cut, got {calories}"

    # Log weight progression (160 → 158.4 lbs, -1.2 lb/week)
    weights = [160.0 - (i * 0.114) for i in range(14)]  # -1.6 lbs total
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food intake (1800 cal/day, very consistent)
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", f"Day {day} Cut Meals")
        await page.fill("input[aria-label='Calories']", "1800")
        await page.fill("input[aria-label='Protein (g)']", "140")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Adaptive TDEE
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Should be on track or minimal adjustment
    await expect(page.locator("text=✅ On track")).to_be_visible()

    print("✅ Scenario 1.3: Cutting Claire Aggressive - PASSED")
```

---

#### **Scenario 1.4: Recomp Ryan - Body Recomposition**

```python
@pytest.mark.tier1
@pytest.mark.asyncio
async def test_recomp_ryan_body_recomp(page: Page, streamlit_ready):
    """Scenario 1.4: Recomposition (maintain weight, lose fat, gain muscle)"""

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation
    await page.click("text=Create New Profile")
    await page.fill("input[aria-label='Name']", "Ryan Recomp")
    await page.fill("input[aria-label='Age']", "35")
    await page.select_option("select[aria-label='Sex']", "Male")
    await page.fill("input[aria-label='Weight (lbs)']", "195")
    await page.fill("input[aria-label='Height (inches)']", "72")  # 6'0"
    await page.select_option("select[aria-label='Activity Level']", "moderately_active")
    await page.fill("input[aria-label='Goal Weight (lbs)']", "195")  # Same weight
    await page.select_option("select[aria-label='Phase']", "recomp")
    await page.click("button:has-text('Create Profile')")

    # Log weight progression (195 → 194.5 lbs, very slow loss)
    weights = [195.0 - (i * 0.036) for i in range(14)]  # -0.5 lbs total
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food (maintenance calories)
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", f"Day {day} Recomp")
        await page.fill("input[aria-label='Calories']", "2700")
        await page.fill("input[aria-label='Protein (g)']", "195")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Should show minimal change
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ On track")).to_be_visible()

    print("✅ Scenario 1.4: Recomp Ryan - PASSED")
```

---

#### **Scenario 1.5: Minimal Megan - Maintenance**

```python
@pytest.mark.tier1
@pytest.mark.asyncio
async def test_minimal_megan_maintenance(page: Page, streamlit_ready):
    """Scenario 1.5: Maintenance with minimal time commitment"""

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation
    await page.click("text=Create New Profile")
    await page.fill("input[aria-label='Name']", "Megan Minimal")
    await page.fill("input[aria-label='Age']", "29")
    await page.select_option("select[aria-label='Sex']", "Female")
    await page.fill("input[aria-label='Weight (lbs)']", "130")
    await page.fill("input[aria-label='Height (inches)']", "64")  # 5'4"
    await page.select_option("select[aria-label='Activity Level']", "lightly_active")
    await page.fill("input[aria-label='Goal Weight (lbs)']", "130")
    await page.select_option("select[aria-label='Phase']", "maintain")
    await page.click("button:has-text('Create Profile')")

    # Log weight (stable ±0.5 lbs)
    base_weight = 130.0
    weights = [base_weight + random.uniform(-0.5, 0.5) for _ in range(14)]
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food (maintenance with variance)
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        daily_cal = 1900 + random.randint(-200, 200)
        await page.fill("input[aria-label='Food Name']", f"Day {day} Meals")
        await page.fill("input[aria-label='Calories']", str(daily_cal))
        await page.fill("input[aria-label='Protein (g)']", "110")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Should show "Stable" status
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ Stable")).to_be_visible()

    print("✅ Scenario 1.5: Minimal Megan Maintenance - PASSED")
```

---

### Tier 2: Adaptive TDEE Edge Cases (8 scenarios)

#### **Scenario 2.1: Losing Too Fast (+100 cal adjustment)**

```python
@pytest.mark.tier2
@pytest.mark.asyncio
async def test_losing_too_fast_adjustment(page: Page, streamlit_ready, create_profile):
    """
    Scenario 2.1: Losing weight faster than planned, needs +100 cal increase.

    Setup: Beginner Ben cutting
    Expected: Lost 2 lbs in 14 days (goal: -1 lb/week)
    Actual: Lost 3 lbs in 14 days (actual: -1.5 lb/week, 50% faster)
    Recommendation: +100 cal increase
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile using helper
    await create_profile(page, {
        "name": "Ben FastCutting",
        "age": 30,
        "sex": "Male",
        "weight_lbs": 210,
        "height_inches": 70,
        "activity_level": "sedentary",
        "goal_weight_lbs": 190,
        "phase": "cut"
    })

    # Log weight: Lost 3 lbs in 14 days (210 → 207)
    weights = [210.0 - (i * 0.214) for i in range(14)]  # -3 lbs total
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food: 2100 cal/day (same as planned)
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", f"Day {day}")
        await page.fill("input[aria-label='Calories']", "2100")
        await page.fill("input[aria-label='Protein (g)']", "210")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Check recommendation
    await page.click("text=🔬 Adaptive TDEE & Check-In")

    # Assertions
    await expect(page.locator("text=⚠️")).to_be_visible()  # Warning icon
    await expect(page.locator("text=faster than planned")).to_be_visible()

    # Verify +100 cal adjustment
    adjustment_text = await page.locator('[data-testid="calorie-adjustment"]').text_content()
    assert "+100 cal" in adjustment_text, f"Expected +100 cal, got: {adjustment_text}"

    new_calories_text = await page.locator('[data-testid="new-calories"]').text_content()
    assert "2200" in new_calories_text, f"Expected 2200 cal, got: {new_calories_text}"

    # Verify reason
    reason_text = await page.locator('[data-testid="adjustment-reason"]').text_content()
    assert "losing_too_fast" in reason_text.lower()

    print("✅ Scenario 2.1: Losing Too Fast - PASSED")
```

---

#### **Scenario 2.2: Losing WAY Too Fast (+150 cal adjustment)**

```python
@pytest.mark.tier2
@pytest.mark.asyncio
async def test_losing_way_too_fast_large_adjustment(page: Page, streamlit_ready, create_profile):
    """
    Scenario 2.2: Losing weight MUCH faster than planned, needs +150 cal increase.

    Setup: Cutting Claire aggressive cut
    Expected: Lost 2.4 lbs in 14 days (goal: -1.2 lb/week)
    Actual: Lost 4 lbs in 14 days (actual: -2.0 lb/week, 67% faster)
    Recommendation: +150 cal increase (>50% threshold)
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    await create_profile(page, {
        "name": "Claire VeryFastCut",
        "age": 32,
        "sex": "Female",
        "weight_lbs": 160,
        "height_inches": 66,
        "activity_level": "very_active",
        "goal_weight_lbs": 145,
        "phase": "cut"
    })

    # Log weight: Lost 4 lbs in 14 days (160 → 156)
    weights = [160.0 - (i * 0.286) for i in range(14)]  # -4 lbs
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food: 1800 cal/day
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", f"Day {day}")
        await page.fill("input[aria-label='Calories']", "1800")
        await page.fill("input[aria-label='Protein (g)']", "140")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Check large adjustment
    await page.click("text=🔬 Adaptive TDEE & Check-In")

    # Verify +150 cal adjustment (>50% deviation)
    adjustment_text = await page.locator('[data-testid="calorie-adjustment"]').text_content()
    assert "+150 cal" in adjustment_text, f"Expected +150 cal, got: {adjustment_text}"

    new_calories_text = await page.locator('[data-testid="new-calories"]').text_content()
    assert "1950" in new_calories_text, f"Expected 1950 cal, got: {new_calories_text}"

    print("✅ Scenario 2.2: Losing WAY Too Fast - PASSED")
```

---

#### **Scenario 2.3: Losing Too Slow (-100 cal adjustment)**

```python
@pytest.mark.tier2
@pytest.mark.asyncio
async def test_losing_too_slow_plateau(page: Page, streamlit_ready, create_profile):
    """
    Scenario 2.3: Weight loss plateau, needs -100 cal decrease.

    Setup: Beginner Ben cutting
    Expected: Lost 2 lbs in 14 days (goal: -1 lb/week)
    Actual: Lost 1 lb in 14 days (actual: -0.5 lb/week, 50% slower)
    Recommendation: -100 cal decrease
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    await create_profile(page, {
        "name": "Ben SlowCutting",
        "age": 30,
        "sex": "Male",
        "weight_lbs": 210,
        "height_inches": 70,
        "activity_level": "sedentary",
        "goal_weight_lbs": 190,
        "phase": "cut"
    })

    # Log weight: Lost only 1 lb in 14 days (210 → 209)
    weights = [210.0 - (i * 0.071) for i in range(14)]  # -1 lb
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    # Log food: 2100 cal/day
    for day in range(1, 15):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", f"Day {day}")
        await page.fill("input[aria-label='Calories']", "2100")
        await page.fill("input[aria-label='Protein (g)']", "210")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Day 14: Check recommendation
    await page.click("text=🔬 Adaptive TDEE & Check-In")

    # Verify -100 cal adjustment
    await expect(page.locator("text=slower than expected")).to_be_visible()

    adjustment_text = await page.locator('[data-testid="calorie-adjustment"]').text_content()
    assert "-100 cal" in adjustment_text, f"Expected -100 cal, got: {adjustment_text}"

    new_calories_text = await page.locator('[data-testid="new-calories"]').text_content()
    assert "2000" in new_calories_text, f"Expected 2000 cal, got: {new_calories_text}"

    print("✅ Scenario 2.3: Losing Too Slow - PASSED")
```

---

#### **Scenario 2.4-2.8: Additional Edge Cases**

```python
@pytest.mark.tier2
@pytest.mark.asyncio
async def test_gaining_too_fast_bulk(page: Page, streamlit_ready, create_profile):
    """Scenario 2.4: Bulking too fast, needs -100 cal decrease"""
    # Implementation similar to above, but for bulking
    pass

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_gaining_too_slow_bulk(page: Page, streamlit_ready, create_profile):
    """Scenario 2.5: Bulking too slow, needs +150 cal increase"""
    pass

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_maintenance_unintended_loss(page: Page, streamlit_ready, create_profile):
    """Scenario 2.6: Maintenance but losing weight, needs +100 cal"""
    pass

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_maintenance_unintended_gain(page: Page, streamlit_ready, create_profile):
    """Scenario 2.7: Maintenance but gaining weight, needs -100 cal"""
    pass

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_insufficient_data_early_user(page: Page, streamlit_ready, create_profile):
    """
    Scenario 2.8: Insufficient data (<14 days), no adaptive TDEE yet.

    Validates:
    - Progress bar shows "7/14 days logged"
    - No adaptive TDEE calculated
    - Educational messaging displayed
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    await create_profile(page, {
        "name": "Ben EarlyUser",
        "age": 30,
        "sex": "Male",
        "weight_lbs": 210,
        "height_inches": 70,
        "activity_level": "sedentary",
        "goal_weight_lbs": 190,
        "phase": "cut"
    })

    # Log only 7 days of data
    weights = [210.0 - (i * 0.143) for i in range(7)]
    for day, weight in enumerate(weights, start=1):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Log Weight')")

    for day in range(1, 8):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", f"Day {day}")
        await page.fill("input[aria-label='Calories']", "2100")
        await page.fill("input[aria-label='Protein (g)']", "210")
        await page.fill("input[type='date']", f"2025-01-{day:02d}")
        await page.click("button:has-text('Add to Log')")

    # Navigate to Adaptive TDEE
    await page.click("text=🔬 Adaptive TDEE & Check-In")

    # Assertions
    await expect(page.locator("text=7/14 days logged")).to_be_visible()
    await expect(page.locator('[role="progressbar"]')).to_be_visible()
    await expect(page.locator("text=Log 7 more days")).to_be_visible()

    # Adaptive TDEE should NOT be shown
    await expect(page.locator('[data-testid="adaptive-tdee-value"]')).not_to_be_visible()

    # Formula TDEE should still be visible
    await expect(page.locator('[data-testid="formula-tdee-value"]')).to_be_visible()

    print("✅ Scenario 2.8: Insufficient Data - PASSED")
```

---

## 🔧 Helper Functions (conftest.py)

```python
# tests/browser/conftest.py
import pytest
import os
from playwright.async_api import async_playwright, Page
import asyncio

# Environment config
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
BROWSER_TYPE = os.getenv("BROWSER", "chromium")
SLOWMO = int(os.getenv("SLOWMO", "0"))
VIDEO_MODE = os.getenv("VIDEO", "on-failure")
TRACE_MODE = os.getenv("TRACE", "on-failure")


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "test-results/videos" if VIDEO_MODE != "off" else None,
        "record_video_size": {"width": 1920, "height": 1080}
    }


@pytest.fixture
async def streamlit_ready():
    """
    Helper to wait for Streamlit app to be fully loaded.

    Streamlit apps use iframes and have specific loading patterns.
    This fixture returns a function that waits for readiness.
    """
    async def wait_for_streamlit(page: Page, timeout: int = 10000):
        """Wait for Streamlit app to be ready"""
        # Wait for main app container
        await page.wait_for_selector('[data-testid="stApp"]', timeout=timeout)

        # Wait for any loading spinners to disappear
        try:
            await page.wait_for_selector(
                '[data-testid="stSpinner"]',
                state="hidden",
                timeout=5000
            )
        except:
            pass  # No spinners present

        # Small delay for JS to settle
        await asyncio.sleep(0.5)

    return wait_for_streamlit


@pytest.fixture
async def create_profile():
    """
    Helper to create user profile programmatically.

    Usage:
        await create_profile(page, {
            "name": "Ben Beginner",
            "age": 30,
            "sex": "Male",
            "weight_lbs": 210,
            "height_inches": 70,
            "activity_level": "sedentary",
            "goal_weight_lbs": 190,
            "phase": "cut"
        })
    """
    async def _create_profile(page: Page, profile_data: dict):
        await page.click("text=Create New Profile")

        await page.fill("input[aria-label='Name']", profile_data["name"])
        await page.fill("input[aria-label='Age']", str(profile_data["age"]))
        await page.select_option("select[aria-label='Sex']", profile_data["sex"])
        await page.fill("input[aria-label='Weight (lbs)']", str(profile_data["weight_lbs"]))
        await page.fill("input[aria-label='Height (inches)']", str(profile_data["height_inches"]))
        await page.select_option("select[aria-label='Activity Level']", profile_data["activity_level"])
        await page.fill("input[aria-label='Goal Weight (lbs)']", str(profile_data["goal_weight_lbs"]))
        await page.select_option("select[aria-label='Phase']", profile_data["phase"])

        await page.click("button:has-text('Create Profile')")
        await page.wait_for_selector("text=Profile created successfully")

    return _create_profile


@pytest.fixture
async def log_weight():
    """Helper to log daily weight"""
    async def _log_weight(page: Page, weight: float, date: str, notes: str = ""):
        await page.click("text=⚖️ Weight Tracking")
        await page.click("button[role='tab']:has-text('📝 Log Weight')")
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", date)
        if notes:
            await page.fill("textarea[aria-label='Notes']", notes)
        await page.click("button:has-text('Log Weight')")
        await page.wait_for_selector(f"text={weight:.1f} lbs")

    return _log_weight


@pytest.fixture
async def log_food():
    """Helper to log food entry"""
    async def _log_food(page: Page, name: str, calories: int, protein: int, date: str):
        await page.click("text=🍽️ Nutrition Tracking")
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")
        await page.fill("input[aria-label='Food Name']", name)
        await page.fill("input[aria-label='Calories']", str(calories))
        await page.fill("input[aria-label='Protein (g)']", str(protein))
        await page.fill("input[type='date']", date)
        await page.click("button:has-text('Add to Log')")
        await page.wait_for_selector(f"text={calories} cal")

    return _log_food


@pytest.fixture
async def mock_barcode_api():
    """
    Mock Open Food Facts API for barcode scanner tests.

    Usage:
        await mock_barcode_api(page, "012345678901", {
            "product_name": "Greek Yogurt",
            "nutriments": {"energy-kcal": 100, "proteins": 15}
        })
    """
    async def _mock_barcode(page: Page, upc: str, product_data: dict):
        await page.route(
            f"**/api.openfoodfacts.org/api/v0/product/{upc}.json",
            lambda route: route.fulfill(json={
                "status": 1,
                "product": product_data
            })
        )

    return _mock_barcode
```

---

## 🐳 Docker Setup

### docker-compose.test.yml
```yaml
version: '3.8'

services:
  # HealthRAG application under test
  healthrag:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ENABLE_CORS=false
      - STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 2s
      timeout: 3s
      retries: 30
      start_period: 10s
    networks:
      - test-network

  # Playwright test runner
  playwright-tests:
    build:
      context: .
      dockerfile: tests/Dockerfile.playwright
    environment:
      - BASE_URL=http://healthrag:8501
      - HEADLESS=${HEADLESS:-true}
      - BROWSER=${BROWSER:-chromium}
      - SLOWMO=${SLOWMO:-0}
      - VIDEO=${VIDEO:-on-failure}
      - TRACE=${TRACE:-on-failure}
    volumes:
      - ./test-results:/app/test-results
      - ./playwright-report:/app/playwright-report
      - ./trace-results:/app/trace-results
    depends_on:
      healthrag:
        condition: service_healthy
    networks:
      - test-network
    command: >
      sh -c "
        echo '=== Waiting for HealthRAG to be ready ===' &&
        sleep 5 &&
        echo '=== Running Playwright tests ===' &&
        pytest tests/browser/ -v
          --html=playwright-report/index.html
          --self-contained-html
          --tracing=on-failure
          --video=on-failure
      "

networks:
  test-network:
    driver: bridge
```

### tests/Dockerfile.playwright
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium firefox webkit

# Copy test code
COPY tests/ ./tests/
COPY src/ ./src/
COPY config/ ./config/

# Create output directories
RUN mkdir -p test-results playwright-report trace-results

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["pytest", "tests/browser/", "-v"]
```

---

## 🚀 Quick Start for Codex

### One-Command Execution
```bash
# Run all 50 scenarios
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# View results
open playwright-report/index.html

# View trace (if failures)
open trace-results/trace.zip
```

### Run Specific Tiers
```bash
# Tier 1: Core personas only
docker-compose -f docker-compose.test.yml run playwright-tests \
  pytest tests/browser/test_tier1_personas.py -v

# Tier 2: Adaptive TDEE edge cases
docker-compose -f docker-compose.test.yml run playwright-tests \
  pytest tests/browser/test_tier2_adaptive_tdee.py -v

# All tiers with cross-browser matrix
for browser in chromium firefox webkit; do
  BROWSER=$browser docker-compose -f docker-compose.test.yml up --abort-on-container-exit
done
```

### Debugging Options
```bash
# Headed mode (see browser)
HEADLESS=false docker-compose -f docker-compose.test.yml up

# Slow motion (500ms between actions)
SLOWMO=500 docker-compose -f docker-compose.test.yml up

# Always record video
VIDEO=always docker-compose -f docker-compose.test.yml up

# Always save trace
TRACE=always docker-compose -f docker-compose.test.yml up
```

---

## 📊 Expected Test Coverage

### Scenario Breakdown
- ✅ **Tier 1**: 5 core personas (complete workflows)
- ✅ **Tier 2**: 8 Adaptive TDEE edge cases (all thresholds)
- ✅ **Tier 3**: 7 exercise goal variations (strength, hypertrophy, endurance, etc.)
- ✅ **Tier 4**: 8 diet outcome edge cases (aggressive deficits, refeeds, variance)
- ✅ **Tier 5**: 12 multi-goal combinations (cut+strength, bulk+hypertrophy, etc.)
- ✅ **Tier 6**: 10 workflow integrations (barcode scanner, meal templates, exports)

**Total**: 50 automated scenarios

### Success Criteria
- All Tier 1 tests PASS (core functionality)
- ≥90% Tier 2-6 tests PASS (edge cases may reveal bugs)
- Test execution time: <25 minutes full suite
- HTML report generated with screenshots
- Video/trace artifacts available on failures

---

## 🎬 Implementation Notes for Codex

### Playwright Best Practices
1. **Auto-waiting**: Playwright automatically waits for elements, no explicit waits needed
2. **Locator strategy**: Use `data-testid` attributes (ask user to add to Streamlit components)
3. **Assertions**: Use `expect()` with auto-retry (better than bare `assert`)
4. **Screenshots**: Capture full page on failures for debugging
5. **Trace viewer**: Record browser traces for visual debugging

### Streamlit-Specific Handling
```python
# Wait for Streamlit to be ready
await page.wait_for_selector('[data-testid="stApp"]')

# Handle Streamlit spinners
await page.wait_for_selector('[data-testid="stSpinner"]', state="hidden")

# Streamlit uses iframes for some components
# If needed:
frame = page.frame_locator("iframe")
await frame.locator("button").click()
```

### Mock Strategies
```python
# Mock Open Food Facts API
await page.route(
    "**/api.openfoodfacts.org/**",
    lambda route: route.fulfill(json=mock_data)
)

# Mock camera/barcode scanner
await page.evaluate("""
    navigator.mediaDevices.getUserMedia = () =>
        Promise.resolve(mockVideoStream);
    window.BarcodeDetector = class {
        detect() { return Promise.resolve([{rawValue: '012345678901'}]); }
    };
""")
```

### Debugging Failed Tests
```bash
# View trace in Playwright Trace Viewer
playwright show-trace trace-results/trace.zip

# View video recording
open test-results/videos/test-name.webm

# View screenshot
open test-results/screenshots/test-name-failure.png
```

---

## ✅ Deliverables

After running this comprehensive test suite, Codex should generate:

1. **Test Report** (`playwright-report/index.html`)
   - PASS/FAIL status per scenario
   - Execution time per test
   - Summary statistics
   - Links to screenshots/videos

2. **Trace Files** (`trace-results/`)
   - DOM snapshots
   - Network requests
   - Console logs
   - Playwright actions timeline

3. **Videos** (`test-results/videos/`)
   - Browser recordings of failures
   - Helpful for debugging visual issues

4. **Bug Report** (if failures found)
   - Description of each failure
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshot evidence

---

## 🎯 Summary for Codex

**Primary Tool**: Playwright (auto-waiting, trace viewer, cross-browser)
**Execution**: Docker Compose (containerized, reproducible)
**Coverage**: 50 scenarios across 6 tiers
**Output**: HTML report + videos + traces

**To implement**:
1. Copy `conftest.py` fixtures to `tests/browser/`
2. Implement test functions following examples above
3. Add `data-testid` attributes to Streamlit components (ask user if needed)
4. Run via Docker Compose
5. Analyze results, report bugs

This framework gives Codex everything needed to implement production-grade browser testing for HealthRAG's Adaptive TDEE system! 🚀
