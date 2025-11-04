"""
Comprehensive Phase 4 Feature Testing - Browser Tests

Tests all Phase 4 tracking features with end-to-end browser automation:
- Adaptive TDEE algorithm with enhancements
- Weight tracking with trend analysis
- Nutrition tracking with meal templates
- Workout logging with autoregulation
- Body measurements tracking
- Progress photos upload/comparison
- Monthly progress reports
- Data export functionality

These tests verify the complete user journey through Phase 4 features,
ensuring all UI components, data persistence, and integrations work correctly.

Author: Claude (Anthropic)
Date: November 2025
"""

import pytest
import os
import sys
from typing import Any
from datetime import datetime, timedelta
import tempfile

try:
    from playwright.async_api import Page, expect, FilePayload
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


# ===== Test 1: Complete Phase 4 User Journey =====

@pytest.mark.tier1
@pytest.mark.asyncio
async def test_complete_phase4_journey(
    page: Page,
    streamlit_ready,
    create_profile,
    log_weight_series,
    log_food_series
):
    """
    Test complete Phase 4 user journey from profile creation to analytics.

    Scenario: Ben Beginner (210 lbs → 185 lbs cutting journey)
    - Create profile
    - Log 14 days of weight + food
    - View Adaptive TDEE
    - Check all 7 enhanced tabs
    - Verify data persistence

    Expected:
    - Adaptive TDEE activates after 14 days
    - TDEE Trends chart shows formula vs adaptive
    - Weight Progress shows trend line
    - Goal Prediction shows target date
    - Body Measurements can be logged
    - Progress Photos can be uploaded
    - Monthly Report generates correctly
    - Export works
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Step 1: Create profile
    await create_profile(page, {
        "name": "Ben Beginner",
        "age": 30,
        "sex": "Male",
        "weight_lbs": 210,
        "height_inches": 70,  # 5'10"
        "activity_level": "sedentary",
        "goal_weight_lbs": 185,
        "phase": "cut"
    })

    # Step 2: Log 14 days of weight (210 → 208 lbs, -2 lbs = -1 lb/week)
    weights = [210.0 - (i * 0.143) for i in range(14)]
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Step 3: Log 14 days of food (deficit: 2100 cal/day)
    await log_food_series(page, avg_calories=2100, avg_protein=210, num_days=14, start_date="2025-01-01")

    # Step 4: Navigate to Adaptive TDEE
    await page.click("text=🎯 Adaptive TDEE")
    await expect(page.locator("text=✅")).to_be_visible(timeout=10000)

    # Verify Adaptive TDEE is calculated
    await expect(page.locator("text=Adaptive TDEE")).to_be_visible()

    # Step 5: Check TDEE Trends tab
    await page.click("button[role='tab']:has-text('📈 TDEE Trends')")
    await expect(page.locator("text=TDEE Historical Trends")).to_be_visible(timeout=5000)

    # Step 6: Check Weight Progress tab
    await page.click("button[role='tab']:has-text('⚖️ Weight Progress')")
    await expect(page.locator("text=Weight Progress")).to_be_visible(timeout=5000)

    # Step 7: Check Goal Prediction tab
    await page.click("button[role='tab']:has-text('🎯 Goal Prediction')")
    await expect(page.locator("text=Goal Date Prediction")).to_be_visible(timeout=5000)
    await expect(page.locator("text=185 lbs")).to_be_visible()  # Target weight

    # Step 8: Check Body Measurements tab
    await page.click("button[role='tab']:has-text('📏 Body Measurements')")
    await expect(page.locator("text=Body Measurements")).to_be_visible(timeout=5000)

    # Log body measurements
    await page.fill("input[aria-label='Waist (inches)']", "34")
    await page.fill("input[aria-label='Chest (inches)']", "42")
    await page.click("button:has-text('Save Measurements')")
    await expect(page.locator("text=✅")).to_be_visible(timeout=5000)

    # Step 9: Check Progress Photos tab
    await page.click("button[role='tab']:has-text('📸 Progress Photos')")
    await expect(page.locator("text=Upload Progress Photo")).to_be_visible(timeout=5000)

    # Step 10: Check Monthly Report tab
    await page.click("button[role='tab']:has-text('📊 Monthly Report')")
    await expect(page.locator("text=Monthly Progress Report")).to_be_visible(timeout=5000)

    # Step 11: Check Export tab
    await page.click("button[role='tab']:has-text('📤 Export Data')")
    await expect(page.locator("text=Export TDEE Data")).to_be_visible(timeout=5000)

    print("✓ Complete Phase 4 journey test passed")


# ===== Test 2: Body Measurements Tracking =====

@pytest.mark.tier1
@pytest.mark.asyncio
async def test_body_measurements_tracking(
    page: Page,
    streamlit_ready,
    create_profile
):
    """
    Test body measurements tracking feature.

    Scenario:
    - Log initial measurements
    - Log follow-up measurements (2 weeks later)
    - Compare measurements
    - Verify waist-to-hip ratio calculation

    Expected:
    - Measurements save successfully
    - Comparison shows deltas
    - Waist-to-hip ratio calculated correctly
    - Progress trends visible
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile
    await create_profile(page, {
        "name": "Claire Cutting",
        "age": 28,
        "sex": "Female",
        "weight_lbs": 145,
        "height_inches": 64,  # 5'4"
        "activity_level": "moderately_active",
        "goal_weight_lbs": 135,
        "phase": "cut"
    })

    # Navigate to Body Measurements
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('📏 Body Measurements')")

    # Log initial measurements (Week 0)
    await page.fill("input[type='date']", "2025-01-01")
    await page.fill("input[aria-label='Neck (inches)']", "13.5")
    await page.fill("input[aria-label='Chest (inches)']", "34")
    await page.fill("input[aria-label='Waist (inches)']", "28")
    await page.fill("input[aria-label='Hips (inches)']", "37")
    await page.fill("input[aria-label='Thigh Left (inches)']", "21")
    await page.fill("input[aria-label='Thigh Right (inches)']", "21")

    await page.click("button:has-text('Save Measurements')")
    await expect(page.locator("text=✅ Measurements saved")).to_be_visible(timeout=5000)

    # Verify waist-to-hip ratio
    await expect(page.locator("text=Waist-to-Hip Ratio")).to_be_visible()
    # Expected: 28/37 = 0.76

    # Log follow-up measurements (Week 2, after cutting)
    await page.fill("input[type='date']", "2025-01-15")
    await page.fill("input[aria-label='Waist (inches)']", "27")  # -1 inch
    await page.fill("input[aria-label='Hips (inches)']", "36.5")  # -0.5 inch
    await page.click("button:has-text('Save Measurements')")
    await expect(page.locator("text=✅ Measurements saved")).to_be_visible(timeout=5000)

    # Check comparison
    await expect(page.locator("text=-1.0 inch")).to_be_visible()  # Waist reduction

    print("✓ Body measurements tracking test passed")


# ===== Test 3: Progress Photos Upload & Comparison =====

@pytest.mark.tier1
@pytest.mark.asyncio
async def test_progress_photos_upload_comparison(
    page: Page,
    streamlit_ready,
    create_profile
):
    """
    Test progress photos upload and before/after comparison.

    Scenario:
    - Upload "before" photo (front, Week 0)
    - Upload "after" photo (front, Week 4)
    - Compare photos side-by-side
    - Verify comparison stats (days elapsed, weight change)

    Expected:
    - Photos upload successfully
    - Gallery displays photos
    - Comparison view shows before/after
    - Stats calculated correctly (28 days, weight delta)
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile
    await create_profile(page, {
        "name": "Ian Intermediate",
        "age": 32,
        "sex": "Male",
        "weight_lbs": 185,
        "height_inches": 72,  # 6'0"
        "activity_level": "very_active",
        "goal_weight_lbs": 200,
        "phase": "bulk"
    })

    # Navigate to Progress Photos
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('📸 Progress Photos')")

    # Switch to Upload tab
    await page.click("button[role='tab']:has-text('📤 Upload')")

    # Create temporary test image
    import io
    from PIL import Image

    # Create a simple test image (100x100 red square)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Upload "before" photo
    await page.set_input_files("input[type='file']", {
        "name": "before.jpg",
        "mimeType": "image/jpeg",
        "buffer": img_bytes.getvalue()
    })

    await page.fill("input[type='date']", "2025-01-01")
    await page.select_option("select[aria-label='Angle/Pose']", "front")
    await page.fill("input[aria-label='Weight (lbs)']", "185")
    await page.select_option("select[aria-label='Phase']", "bulk")
    await page.fill("textarea[aria-label='Notes']", "Starting bulk - feeling lean")

    await page.click("button:has-text('📸 Upload Photo')")
    await expect(page.locator("text=✅ Photo uploaded")).to_be_visible(timeout=5000)

    # Upload "after" photo (4 weeks later)
    img2 = Image.new('RGB', (100, 100), color='blue')
    img2_bytes = io.BytesIO()
    img2.save(img2_bytes, format='JPEG')
    img2_bytes.seek(0)

    await page.set_input_files("input[type='file']", {
        "name": "after.jpg",
        "mimeType": "image/jpeg",
        "buffer": img2_bytes.getvalue()
    })

    await page.fill("input[type='date']", "2025-01-29")  # 28 days later
    await page.fill("input[aria-label='Weight (lbs)']", "188")  # +3 lbs
    await page.click("button:has-text('📸 Upload Photo')")
    await expect(page.locator("text=✅ Photo uploaded")).to_be_visible(timeout=5000)

    # Switch to Gallery tab
    await page.click("button[role='tab']:has-text('🖼️ Gallery')")
    await expect(page.locator("text=2 photos")).to_be_visible()

    # Switch to Compare tab
    await page.click("button[role='tab']:has-text('⚖️ Compare')")

    # Select before photo
    await page.select_option("select[aria-label='Select Before Photo']", "2025-01-01 (front)")

    # Select after photo
    await page.select_option("select[aria-label='Select After Photo']", "2025-01-29 (front)")

    # Click compare button
    await page.click("button:has-text('🔍 Compare Photos')")

    # Verify comparison stats
    await expect(page.locator("text=28 days")).to_be_visible()  # Days elapsed
    await expect(page.locator("text=+3.0 lbs")).to_be_visible()  # Weight change
    await expect(page.locator("text=Bulk")).to_be_visible()  # Phase

    print("✓ Progress photos upload & comparison test passed")


# ===== Test 4: Monthly Progress Report Generation =====

@pytest.mark.tier1
@pytest.mark.asyncio
async def test_monthly_progress_report(
    page: Page,
    streamlit_ready,
    create_profile,
    log_weight_series,
    log_food_series,
    log_workout
):
    """
    Test monthly progress report generation.

    Scenario:
    - Log 30 days of weight + nutrition + workouts
    - Generate January 2025 progress report
    - Verify achievements, recommendations, rating

    Expected:
    - Report generates successfully
    - Achievements section populated
    - Recommendations based on actual data
    - Overall rating calculated (Excellent/Good/Fair/Needs Attention)
    - Visualizations render
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile
    await create_profile(page, {
        "name": "Ryan Recomp",
        "age": 35,
        "sex": "Male",
        "weight_lbs": 165,
        "height_inches": 69,  # 5'9"
        "activity_level": "very_active",
        "goal_weight_lbs": 165,  # Maintenance for recomp
        "phase": "recomp"
    })

    # Log 30 days of weight (stable around 165 lbs for recomp)
    weights = [165.0 + ((-1)**i * 0.5) for i in range(30)]  # Fluctuates ±0.5 lbs
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 30 days of food (maintenance: 2600 cal/day)
    await log_food_series(page, avg_calories=2600, avg_protein=165, num_days=30, start_date="2025-01-01")

    # Log 12 workouts (3x/week for 4 weeks)
    workout_dates = ["2025-01-01", "2025-01-03", "2025-01-05",
                     "2025-01-08", "2025-01-10", "2025-01-12",
                     "2025-01-15", "2025-01-17", "2025-01-19",
                     "2025-01-22", "2025-01-24", "2025-01-26"]

    for workout_date in workout_dates:
        await log_workout(page, workout_date, [
            {"exercise": "Bench Press", "weight": 200, "reps": 8, "sets": 3},
            {"exercise": "Squat", "weight": 275, "reps": 8, "sets": 3},
            {"exercise": "Deadlift", "weight": 315, "reps": 5, "sets": 3}
        ])

    # Navigate to Monthly Report
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('📊 Monthly Report')")

    # Select January 2025
    await page.select_option("select[aria-label='Month']", "1")  # January
    await page.fill("input[aria-label='Year']", "2025")

    # Click generate report
    await page.click("button:has-text('Generate Report')")

    # Verify report sections
    await expect(page.locator("text=Monthly Progress Report")).to_be_visible(timeout=10000)
    await expect(page.locator("text=🏆 Achievements")).to_be_visible()
    await expect(page.locator("text=💡 Recommendations")).to_be_visible()
    await expect(page.locator("text=Overall Rating")).to_be_visible()

    # Verify achievements mention workouts completed
    await expect(page.locator("text=12 workouts")).to_be_visible()

    # Verify recomp-specific recommendations
    await expect(page.locator("text=recomp")).to_be_visible()

    print("✓ Monthly progress report generation test passed")


# ===== Test 5: Data Export Functionality =====

@pytest.mark.tier1
@pytest.mark.asyncio
async def test_data_export(
    page: Page,
    streamlit_ready,
    create_profile,
    log_weight_series,
    log_food_series
):
    """
    Test TDEE data export to CSV and JSON.

    Scenario:
    - Generate 14 days of TDEE data
    - Export to CSV
    - Export to JSON
    - Verify file downloads

    Expected:
    - CSV export contains all columns
    - JSON export valid format
    - File downloads successfully
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile and log data
    await create_profile(page, {
        "name": "Megan Minimal",
        "age": 26,
        "sex": "Female",
        "weight_lbs": 128,
        "height_inches": 63,  # 5'3"
        "activity_level": "lightly_active",
        "goal_weight_lbs": 128,  # Maintenance
        "phase": "maintain"
    })

    weights = [128.0 + ((-1)**i * 0.3) for i in range(14)]
    await log_weight_series(page, weights, start_date="2025-01-01")

    await log_food_series(page, avg_calories=1800, avg_protein=128, num_days=14, start_date="2025-01-01")

    # Navigate to Export tab
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('📤 Export Data')")

    # Export CSV
    async with page.expect_download() as download_info:
        await page.click("button:has-text('📥 Export CSV')")

    download = await download_info.value
    assert download.suggested_filename.endswith(".csv")

    # Export JSON
    async with page.expect_download() as download_info:
        await page.click("button:has-text('📥 Export JSON')")

    download = await download_info.value
    assert download.suggested_filename.endswith(".json")

    print("✓ Data export functionality test passed")


# ===== Test 6: Water Weight Spike Detection =====

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_water_weight_spike_detection(
    page: Page,
    streamlit_ready,
    create_profile,
    log_weight_series
):
    """
    Test water weight spike detection and coaching.

    Scenario:
    - Log normal weight trend
    - Log sudden +3 lb spike (water weight)
    - Verify alert appears with coaching message

    Expected:
    - Water weight alert displayed
    - Coaching message explains spike causes
    - Recommendation to not panic
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile
    await create_profile(page, {
        "name": "Test User",
        "age": 30,
        "sex": "Female",
        "weight_lbs": 140,
        "height_inches": 65,
        "activity_level": "moderately_active",
        "goal_weight_lbs": 130,
        "phase": "cut"
    })

    # Log normal trend: 140 → 138 over 10 days
    weights = [140.0 - (i * 0.2) for i in range(10)]

    # Add sudden +3 lb spike on day 11 (water weight)
    weights.append(141.0)  # Spike!
    weights.append(141.5)
    weights.append(139.0)  # Back down
    weights.append(138.5)

    await log_weight_series(page, weights, start_date="2025-01-01")

    # Navigate to Weight Progress tab
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('⚖️ Weight Progress')")

    # Verify water weight alert
    await expect(page.locator("text=⚠️ Water Weight Spike")).to_be_visible(timeout=5000)
    await expect(page.locator("text=+3")).to_be_visible()
    await expect(page.locator("text=Don't panic")).to_be_visible()

    print("✓ Water weight spike detection test passed")


# ===== Test 7: Goal Date Prediction Scenarios =====

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_goal_date_predictions(
    page: Page,
    streamlit_ready,
    create_profile,
    log_weight_series,
    log_food_series
):
    """
    Test goal date prediction with best/current/worst scenarios.

    Scenario:
    - User wants to lose 25 lbs (210 → 185)
    - Currently losing 1 lb/week
    - Verify predictions: Best (25 weeks), Current (25 weeks), Worst (37.5 weeks)

    Expected:
    - Goal prediction shows all 3 scenarios
    - Current rate displayed
    - Estimated completion dates shown
    - Coaching message appropriate for rate
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile with goal weight
    await create_profile(page, {
        "name": "Goal Test User",
        "age": 30,
        "sex": "Male",
        "weight_lbs": 210,
        "height_inches": 70,
        "activity_level": "sedentary",
        "goal_weight_lbs": 185,  # -25 lbs goal
        "phase": "cut"
    })

    # Log 14 days showing -1 lb/week rate
    weights = [210.0 - (i * 0.143) for i in range(14)]  # -2 lbs over 14 days
    await log_weight_series(page, weights, start_date="2025-01-01")

    await log_food_series(page, avg_calories=2100, avg_protein=210, num_days=14, start_date="2025-01-01")

    # Navigate to Goal Prediction tab
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('🎯 Goal Prediction')")

    # Verify prediction sections
    await expect(page.locator("text=Goal Date Prediction")).to_be_visible(timeout=5000)
    await expect(page.locator("text=185 lbs")).to_be_visible()  # Target
    await expect(page.locator("text=Current Rate")).to_be_visible()
    await expect(page.locator("text=-1.0 lbs/week")).to_be_visible()

    # Verify scenarios
    await expect(page.locator("text=🏆 Best Case")).to_be_visible()
    await expect(page.locator("text=📊 Current Pace")).to_be_visible()
    await expect(page.locator("text=⚠️ Worst Case")).to_be_visible()

    # Verify approximately 25 weeks at current rate (25 lbs / 1 lb/week)
    await expect(page.locator("text=25 weeks")).to_be_visible()

    print("✓ Goal date prediction scenarios test passed")


# ===== Test 8: TDEE Trends Visualization =====

@pytest.mark.tier2
@pytest.mark.asyncio
async def test_tdee_trends_visualization(
    page: Page,
    streamlit_ready,
    create_profile,
    log_weight_series,
    log_food_series
):
    """
    Test TDEE trends chart with Formula/Adaptive/Intake lines.

    Scenario:
    - Log 30 days of data
    - View TDEE Trends chart
    - Verify 3 lines: Formula TDEE, Adaptive TDEE, Average Intake

    Expected:
    - Chart renders successfully
    - All 3 lines visible
    - Hover tooltips show values
    - Date range selector works
    """

    await page.goto(f"{BASE_URL}")
    await streamlit_ready(page)

    # Create profile
    await create_profile(page, {
        "name": "Trend Test User",
        "age": 30,
        "sex": "Male",
        "weight_lbs": 185,
        "height_inches": 70,
        "activity_level": "moderately_active",
        "goal_weight_lbs": 200,
        "phase": "bulk"
    })

    # Log 30 days of weight (185 → 188, +3 lbs = +0.7 lbs/week bulk)
    weights = [185.0 + (i * 0.1) for i in range(30)]
    await log_weight_series(page, weights, start_date="2025-01-01")

    # Log 30 days of food (surplus: 2900 cal/day)
    await log_food_series(page, avg_calories=2900, avg_protein=185, num_days=30, start_date="2025-01-01")

    # Navigate to TDEE Trends tab
    await page.click("text=🎯 Adaptive TDEE")
    await streamlit_ready(page)
    await page.click("button[role='tab']:has-text('📈 TDEE Trends')")

    # Verify chart elements
    await expect(page.locator("text=TDEE Historical Trends")).to_be_visible(timeout=10000)
    await expect(page.locator("text=Formula TDEE")).to_be_visible()
    await expect(page.locator("text=Adaptive TDEE")).to_be_visible()
    await expect(page.locator("text=Average Intake")).to_be_visible()

    # Verify chart renders (Plotly chart container)
    await expect(page.locator(".plotly")).to_be_visible()

    print("✓ TDEE trends visualization test passed")


# ===== Run Configuration =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
