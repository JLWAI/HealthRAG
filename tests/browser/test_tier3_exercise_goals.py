"""
Tier 3: Exercise Goal Variations - Browser Tests

7 scenarios covering different exercise goals and their interaction with diet outcomes.

Scenarios:
- 3.1: Strength-focused cutting (preserve strength on deficit)
- 3.2: Hypertrophy-focused bulking (maximize muscle on surplus)
- 3.3: Powerlifting recomp (strength gains while staying in weight class)
- 3.4: Endurance athlete cutting (runner/cyclist cutting for performance)
- 3.5: Bodybuilding contest prep (extreme fat loss for show, 12 weeks out)
- 3.6: CrossFit maintenance (performance + aesthetics maintenance)
- 3.7: Minimal time commitment (busy professional, 2-3x/week training)

Testing focus:
- Exercise goal impacts macro recommendations
- Coaching messages reference training style
- TDEE adjustments account for training volume
- Volume landmarks appropriate for experience level
"""

import pytest
import os
import random
import sys
from typing import Any

try:
    from playwright.async_api import Page, expect
    HAS_PLAYWRIGHT = True
except ImportError:
    Page = Any  # type: ignore
    expect = None  # type: ignore
    HAS_PLAYWRIGHT = False

pytestmark = pytest.mark.skipif(
    not HAS_PLAYWRIGHT or "pytest_playwright" not in sys.modules,
    reason="pytest-playwright plugin required for browser E2E tests"
)

# Environment configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")


# ===== Scenario 3.1: Strength-Focused Cutting =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_strength_focused_cutting(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.1: Strength preservation during cut

    Profile:
    - Male, 28 years, 6'0", 220 lbs, Moderately Active
    - Goal: Cut to 200 lbs (-20 lbs) while maintaining strength
    - Exercise: Powerlifting-style, 4x/week
    - Priority: Strength PRs over weight loss speed

    Expected behavior:
    - Moderate deficit (-500 cal, 1 lb/week)
    - High protein (1g/lb minimum)
    - Coaching emphasizes strength metrics over scale weight
    - Volume recommendations: MEV range (12-14 sets/muscle/week)
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with strength focus
    await create_profile(page, {
        "name": "Steve Strongman",
        "age": 28,
        "sex": "Male",
        "weight_lbs": 220,
        "height_inches": 72,  # 6'0"
        "activity_level": "moderately_active",
        "goal_weight_lbs": 200,
        "phase": "cut"
    })

    # Log 14 days of weight (220 → 218 lbs, -2 lbs total = -1 lb/week rate)
    weights = [220.0 - (i * 0.143) for i in range(14)]  # -0.143 lbs/day
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (deficit for cutting, high protein)
    # TDEE ~2,900 cal (220 lbs, moderately active)
    # Deficit: -500 cal = 2,400 cal target
    # Protein: 220g (1g/lb)
    await log_food_series(page, avg_calories=2400, avg_protein=220, num_days=14, start_date="2025-01-01")

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    # Weight loss rate should be on-track (-1 lb/week)
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Adaptive TDEE should be calculated
    adaptive_tdee = await page.locator('[data-testid="adaptive-tdee-value"]').text_content()
    adaptive_tdee_num = int(adaptive_tdee.replace(",", "").replace(" cal", ""))
    assert 2800 <= adaptive_tdee_num <= 3000, f"Adaptive TDEE out of range: {adaptive_tdee_num}"

    # Coaching should reference strength preservation
    coaching_text = await page.locator('[data-testid="coaching-message"]').text_content()
    assert any(keyword in coaching_text.lower() for keyword in ["strength", "performance", "pr", "lift"]), \
        f"Coaching message doesn't mention strength focus: {coaching_text}"

    # Protein recommendation should be high
    protein_rec = await page.locator('[data-testid="protein-recommendation"]').text_content()
    assert "220" in protein_rec or "1.0" in protein_rec, f"Protein recommendation too low: {protein_rec}"

    print("✅ Scenario 3.1: Strength-Focused Cutting - PASSED")


# ===== Scenario 3.2: Hypertrophy-Focused Bulking =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_hypertrophy_focused_bulking(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.2: Maximum muscle growth during bulk

    Profile:
    - Male, 25 years, 5'10", 165 lbs, Very Active
    - Goal: Bulk to 185 lbs (+20 lbs)
    - Exercise: Hypertrophy focus, 5x/week PPL split
    - Priority: Muscle size over strength

    Expected behavior:
    - Moderate surplus (+300-400 cal, 0.75 lb/week gain)
    - Volume recommendations: MAV range (18-22 sets/muscle/week)
    - Coaching emphasizes progressive overload and volume
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with hypertrophy focus
    await create_profile(page, {
        "name": "Henry Hypertrophy",
        "age": 25,
        "sex": "Male",
        "weight_lbs": 165,
        "height_inches": 70,  # 5'10"
        "activity_level": "very_active",
        "goal_weight_lbs": 185,
        "phase": "bulk",
        "exercise_goal": "hypertrophy",
        "training_frequency": 5,
        "experience_level": "intermediate"
    })

    # Log 14 days of weight (165 → 166.5 lbs, +1.5 lbs total = +0.75 lb/week rate)
    weights = [165.0 + (i * 0.107) for i in range(14)]  # +0.107 lbs/day
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (surplus for bulking)
    # TDEE ~2,700 cal (165 lbs, very active)
    # Surplus: +350 cal = 3,050 cal target
    # Protein: 165g (1g/lb)
    for day in range(1, 15):
        await log_food_series(page, [
            {"name": f"Day {day} Bulk", "calories": 3050, "protein": 165, "date": f"2025-01-{day:02d}"}
        ])

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Adaptive TDEE calculation
    adaptive_tdee = await page.locator('[data-testid="adaptive-tdee-value"]').text_content()
    adaptive_tdee_num = int(adaptive_tdee.replace(",", "").replace(" cal", ""))
    assert 2600 <= adaptive_tdee_num <= 2800, f"Adaptive TDEE out of range: {adaptive_tdee_num}"

    # Coaching should reference volume and hypertrophy
    coaching_text = await page.locator('[data-testid="coaching-message"]').text_content()
    assert any(keyword in coaching_text.lower() for keyword in ["volume", "hypertrophy", "muscle", "growth", "size"]), \
        f"Coaching message doesn't mention hypertrophy focus: {coaching_text}"

    print("✅ Scenario 3.2: Hypertrophy-Focused Bulking - PASSED")


# ===== Scenario 3.3: Powerlifting Recomp =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_powerlifting_recomp(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.3: Strength gains while maintaining weight class

    Profile:
    - Male, 32 years, 5'9", 198 lbs, Moderately Active
    - Goal: Recomp at 198 lbs (stay in 198 lb weight class)
    - Exercise: Powerlifting (squat, bench, deadlift focus)
    - Priority: Increase total while staying in weight class

    Expected behavior:
    - Maintenance calories (minimal net weight change)
    - High protein for body recomposition
    - Coaching emphasizes strength gains, not scale weight
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with powerlifting focus
    await create_profile(page, {
        "name": "Paul Powerlifter",
        "age": 32,
        "sex": "Male",
        "weight_lbs": 198,
        "height_inches": 69,  # 5'9"
        "activity_level": "moderately_active",
        "goal_weight_lbs": 198,
        "phase": "recomp",
        "exercise_goal": "powerlifting",
        "training_frequency": 4,
        "experience_level": "advanced"
    })

    # Log 14 days of weight (198 → 197.5 lbs, minimal change)
    base_weight = 198.0
    weights = [base_weight - (i * 0.036) for i in range(14)]  # -0.5 lbs total
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (maintenance calories)
    # TDEE ~2,750 cal (198 lbs, moderately active)
    # Protein: 200g (1g/lb for recomp)
    for day in range(1, 15):
        await log_food_series(page, [
            {"name": f"Day {day} Maintenance", "calories": 2750, "protein": 200, "date": f"2025-01-{day:02d}"}
        ])

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Weight should be stable (±0.5 lbs)
    weight_change = await page.locator('[data-testid="weight-change"]').text_content()
    assert "-0.5" in weight_change or "-1" in weight_change, f"Weight change not minimal: {weight_change}"

    # Coaching should reference strength and weight class
    coaching_text = await page.locator('[data-testid="coaching-message"]').text_content()
    assert any(keyword in coaching_text.lower() for keyword in ["recomp", "strength", "weight class", "total"]), \
        f"Coaching message doesn't mention recomp/powerlifting: {coaching_text}"

    print("✅ Scenario 3.3: Powerlifting Recomp - PASSED")


# ===== Scenario 3.4: Endurance Athlete Cutting =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_endurance_athlete_cutting(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.4: Runner/cyclist cutting for performance

    Profile:
    - Female, 30 years, 5'6", 145 lbs, Very Active
    - Goal: Cut to 135 lbs (-10 lbs) for race performance
    - Exercise: Running/cycling, 5-6x/week
    - Priority: Maintain endurance performance, minimize muscle loss

    Expected behavior:
    - Moderate deficit (-300 cal, 0.6 lb/week)
    - Lower protein needs vs strength athletes (0.8-1.0g/lb)
    - Higher carb emphasis for endurance performance
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with endurance focus
    await create_profile(page, {
        "name": "Emma Endurance",
        "age": 30,
        "sex": "Female",
        "weight_lbs": 145,
        "height_inches": 66,  # 5'6"
        "activity_level": "very_active",
        "goal_weight_lbs": 135,
        "phase": "cut",
        "exercise_goal": "endurance",
        "training_frequency": 5,
        "experience_level": "intermediate"
    })

    # Log 14 days of weight (145 → 143.8 lbs, -1.2 lbs total = -0.6 lb/week rate)
    weights = [145.0 - (i * 0.086) for i in range(14)]  # -0.086 lbs/day
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (moderate deficit, endurance focus)
    # TDEE ~2,300 cal (145 lbs female, very active)
    # Deficit: -300 cal = 2,000 cal target
    # Protein: 130g (0.9g/lb, lower than strength athletes)
    for day in range(1, 15):
        await log_food_series(page, [
            {"name": f"Day {day} Endurance", "calories": 2000, "protein": 130, "date": f"2025-01-{day:02d}"}
        ])

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Coaching should reference endurance performance
    coaching_text = await page.locator('[data-testid="coaching-message"]').text_content()
    assert any(keyword in coaching_text.lower() for keyword in ["endurance", "performance", "cardio", "running", "aerobic"]), \
        f"Coaching message doesn't mention endurance focus: {coaching_text}"

    print("✅ Scenario 3.4: Endurance Athlete Cutting - PASSED")


# ===== Scenario 3.5: Bodybuilding Contest Prep =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_bodybuilding_contest_prep(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.5: Extreme fat loss for bodybuilding show (12 weeks out)

    Profile:
    - Male, 28 years, 5'10", 190 lbs, Very Active
    - Goal: Cut to 165 lbs (-25 lbs) for show
    - Exercise: Bodybuilding split, 6x/week + cardio
    - Priority: Maximum muscle retention, aesthetics

    Expected behavior:
    - Aggressive deficit (-750 cal, 1.5 lb/week initially)
    - Very high protein (1.2g/lb minimum)
    - Weekly adjustments expected as metabolic adaptation occurs
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with bodybuilding focus
    await create_profile(page, {
        "name": "Brad Bodybuilder",
        "age": 28,
        "sex": "Male",
        "weight_lbs": 190,
        "height_inches": 70,  # 5'10"
        "activity_level": "very_active",
        "goal_weight_lbs": 165,
        "phase": "cut",
        "exercise_goal": "bodybuilding",
        "training_frequency": 6,
        "experience_level": "advanced"
    })

    # Log 14 days of weight (190 → 187 lbs, -3 lbs total = -1.5 lb/week rate)
    weights = [190.0 - (i * 0.214) for i in range(14)]  # -0.214 lbs/day
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (aggressive deficit, very high protein)
    # TDEE ~3,000 cal (190 lbs, very active with training)
    # Deficit: -750 cal = 2,250 cal target
    # Protein: 230g (1.2g/lb for muscle retention)
    for day in range(1, 15):
        await log_food_series(page, [
            {"name": f"Day {day} Contest Prep", "calories": 2250, "protein": 230, "date": f"2025-01-{day:02d}"}
        ])

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    # Aggressive cut should be on-track
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Very high protein recommendation
    protein_rec = await page.locator('[data-testid="protein-recommendation"]').text_content()
    assert any(value in protein_rec for value in ["230", "1.2", "220"]), f"Protein not high enough for contest prep: {protein_rec}"

    # Coaching should warn about aggressive deficit
    coaching_text = await page.locator('[data-testid="coaching-message"]').text_content()
    assert any(keyword in coaching_text.lower() for keyword in ["contest", "aggressive", "muscle retention", "monitoring"]), \
        f"Coaching message doesn't address contest prep challenges: {coaching_text}"

    print("✅ Scenario 3.5: Bodybuilding Contest Prep - PASSED")


# ===== Scenario 3.6: CrossFit Maintenance =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_crossfit_maintenance(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.6: CrossFit athlete maintaining performance + aesthetics

    Profile:
    - Female, 27 years, 5'7", 150 lbs, Very Active
    - Goal: Maintain at 150 lbs
    - Exercise: CrossFit, 4-5x/week (mix of strength + conditioning)
    - Priority: Performance across multiple domains, maintain physique

    Expected behavior:
    - Maintenance calories (stable weight)
    - Balanced macros (protein + carbs for mixed training)
    - Coaching references CrossFit-specific metrics
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with CrossFit focus
    await create_profile(page, {
        "name": "Cara CrossFit",
        "age": 27,
        "sex": "Female",
        "weight_lbs": 150,
        "height_inches": 67,  # 5'7"
        "activity_level": "very_active",
        "goal_weight_lbs": 150,
        "phase": "maintain",
        "exercise_goal": "crossfit",
        "training_frequency": 4,
        "experience_level": "intermediate"
    })

    # Log 14 days of weight (150 ± 0.5 lbs, stable maintenance)
    base_weight = 150.0
    weights = [base_weight + random.uniform(-0.5, 0.5) for _ in range(14)]
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (maintenance calories, balanced macros)
    # TDEE ~2,400 cal (150 lbs female, very active)
    # Protein: 150g (1g/lb)
    for day in range(1, 15):
        await log_food_series(page, [
            {"name": f"Day {day} CrossFit", "calories": 2400, "protein": 150, "date": f"2025-01-{day:02d}"}
        ])

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Weight should be stable
    weight_change = await page.locator('[data-testid="weight-change"]').text_content()
    weight_change_num = float(weight_change.replace("lbs", "").replace("+", "").replace("-", "").strip())
    assert weight_change_num <= 1.0, f"Weight not stable for maintenance: {weight_change}"

    print("✅ Scenario 3.6: CrossFit Maintenance - PASSED")


# ===== Scenario 3.7: Minimal Time Commitment =====

@pytest.mark.tier3
@pytest.mark.asyncio
async def test_minimal_time_commitment(page: Page, streamlit_ready, create_profile, log_weight_series, log_food_series):
    """
    Scenario 3.7: Busy professional with minimal training time

    Profile:
    - Male, 35 years, 5'11", 185 lbs, Lightly Active
    - Goal: Maintain muscle, lose some fat (recomp to 180 lbs)
    - Exercise: Full body workouts, 2-3x/week
    - Priority: Time efficiency, sustainable routine

    Expected behavior:
    - Small deficit (-200 cal, 0.4 lb/week)
    - Volume recommendations: MEV range (10-12 sets/muscle/week)
    - Coaching emphasizes adherence and sustainability
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Profile creation with minimal time focus
    await create_profile(page, {
        "name": "Mike Minimal",
        "age": 35,
        "sex": "Male",
        "weight_lbs": 185,
        "height_inches": 71,  # 5'11"
        "activity_level": "lightly_active",
        "goal_weight_lbs": 180,
        "phase": "recomp",
        "exercise_goal": "general_fitness",
        "training_frequency": 3,
        "experience_level": "beginner"
    })

    # Log 14 days of weight (185 → 184.2 lbs, -0.8 lbs total = -0.4 lb/week rate)
    weights = [185.0 - (i * 0.057) for i in range(14)]  # -0.057 lbs/day
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 14 days of food (small deficit, sustainable)
    # TDEE ~2,450 cal (185 lbs, lightly active)
    # Deficit: -200 cal = 2,250 cal target
    # Protein: 165g (0.9g/lb)
    for day in range(1, 15):
        await log_food_series(page, [
            {"name": f"Day {day} Busy Professional", "calories": 2250, "protein": 165, "date": f"2025-01-{day:02d}"}
        ])

    # Navigate to Adaptive TDEE Check-In
    await page.click("text=🔬 Adaptive TDEE & Check-In")
    await expect(page.locator("text=✅ 14 days of data")).to_be_visible()

    # Assertions
    await expect(page.locator("text=✅ On track")).to_be_visible()

    # Coaching should emphasize sustainability
    coaching_text = await page.locator('[data-testid="coaching-message"]').text_content()
    assert any(keyword in coaching_text.lower() for keyword in ["sustainable", "consistent", "adherence", "realistic"]), \
        f"Coaching message doesn't emphasize sustainability: {coaching_text}"

    print("✅ Scenario 3.7: Minimal Time Commitment - PASSED")
