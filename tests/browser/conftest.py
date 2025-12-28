"""
Playwright Test Fixtures and Helpers for HealthRAG Browser Testing

This module provides reusable fixtures and helper functions for Playwright-based
end-to-end testing of the HealthRAG Streamlit application.

Fixtures:
- browser_context_args: Browser configuration
- streamlit_ready: Wait for Streamlit to be fully loaded
- create_profile: Programmatically create user profiles
- log_weight: Helper to log daily weights
- log_food: Helper to log food entries
- log_workout: Helper to log workout sessions
- mock_barcode_api: Mock Open Food Facts API responses

Environment Variables:
- BASE_URL: HealthRAG application URL (default: http://localhost:8501)
- HEADLESS: Run browser in headless mode (default: true)
- BROWSER: Browser to use (chromium, firefox, webkit; default: chromium)
- SLOWMO: Slow down operations by N milliseconds (default: 0)
- VIDEO: Video recording mode (always, on-failure, off; default: on-failure)
- TRACE: Trace recording mode (always, on-failure, off; default: on-failure)
"""

import pytest
import os
import asyncio
from playwright.async_api import Page, BrowserContext
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta


# ===== Environment Configuration =====

BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
BROWSER_TYPE = os.getenv("BROWSER", "chromium")
SLOWMO = int(os.getenv("SLOWMO", "0"))
VIDEO_MODE = os.getenv("VIDEO", "on-failure")
TRACE_MODE = os.getenv("TRACE", "on-failure")


# ===== Browser Configuration =====

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Configure browser context for all tests.

    Sets viewport size, video recording, and other browser options.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "test-results/videos" if VIDEO_MODE != "off" else None,
        "record_video_size": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


# ===== Streamlit-Specific Helpers =====

@pytest.fixture
async def streamlit_ready():
    """
    Wait for Streamlit application to be fully loaded and interactive.

    Streamlit apps have specific loading patterns:
    1. Main app container renders
    2. Loading spinners appear/disappear
    3. Components become interactive

    Usage:
        await streamlit_ready(page)
    """
    async def wait_for_streamlit(page: Page, timeout: int = 10000):
        """
        Wait for Streamlit to be ready.

        Args:
            page: Playwright page instance
            timeout: Maximum time to wait in milliseconds
        """
        # Wait for main Streamlit app container
        try:
            await page.wait_for_selector(
                '[data-testid="stApp"]',
                timeout=timeout,
                state="visible"
            )
        except Exception as e:
            # Fallback: wait for any Streamlit element
            await page.wait_for_selector("div.main", timeout=timeout)

        # Wait for loading spinners to disappear
        try:
            await page.wait_for_selector(
                '[data-testid="stSpinner"]',
                state="hidden",
                timeout=5000
            )
        except:
            pass  # No spinners present

        # Wait for any status messages to appear/stabilize
        try:
            await page.wait_for_selector(
                '[data-testid="stStatusWidget"]',
                timeout=2000
            )
            await asyncio.sleep(0.5)
        except:
            pass  # No status widgets

        # Give JS time to settle
        await asyncio.sleep(0.5)

        print(f"✓ Streamlit ready at {BASE_URL}")

    return wait_for_streamlit


# ===== Profile Management Helpers =====

@pytest.fixture
async def create_profile():
    """
    Create user profile programmatically.

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

    Returns:
        Async function that creates profile and waits for success
    """
    async def _create_profile(page: Page, profile_data: Dict):
        """
        Fill and submit profile creation form.

        Args:
            page: Playwright page instance
            profile_data: Dictionary with profile fields
        """
        # Click "Create New Profile" button
        await page.click("text=Create New Profile")

        # Wait for form to appear
        await page.wait_for_selector("input[aria-label='Name']")

        # Fill form fields
        await page.fill("input[aria-label='Name']", profile_data["name"])
        await page.fill("input[aria-label='Age']", str(profile_data["age"]))
        await page.select_option("select[aria-label='Sex']", profile_data["sex"])
        await page.fill("input[aria-label='Weight (lbs)']", str(profile_data["weight_lbs"]))
        await page.fill("input[aria-label='Height (inches)']", str(profile_data["height_inches"]))
        await page.select_option("select[aria-label='Activity Level']", profile_data["activity_level"])
        await page.fill("input[aria-label='Goal Weight (lbs)']", str(profile_data["goal_weight_lbs"]))
        await page.select_option("select[aria-label='Phase']", profile_data["phase"])

        # Submit profile
        await page.click("button:has-text('Create Profile')")

        # Wait for success message
        await page.wait_for_selector("text=Profile created successfully", timeout=5000)

        print(f"✓ Profile created: {profile_data['name']} ({profile_data['phase']})")

    return _create_profile


# ===== Weight Tracking Helpers =====

@pytest.fixture
async def log_weight():
    """
    Log daily weight entry.

    Usage:
        await log_weight(page, 210.5, "2025-01-15", "Feeling good")
    """
    async def _log_weight(
        page: Page,
        weight: float,
        date: str,
        notes: str = ""
    ):
        """
        Create weight log entry.

        Args:
            page: Playwright page instance
            weight: Weight in pounds
            date: Date string (YYYY-MM-DD)
            notes: Optional notes
        """
        # Navigate to weight tracking
        await page.click("text=⚖️ Weight Tracking")

        # Switch to "Log Weight" tab
        await page.click("button[role='tab']:has-text('📝 Log Weight')")

        # Fill form
        await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
        await page.fill("input[type='date']", date)

        if notes:
            await page.fill("textarea[aria-label='Notes']", notes)

        # Submit
        await page.click("button:has-text('Log Weight')")

        # Verify entry appears
        await page.wait_for_selector(f"text={weight:.1f} lbs", timeout=3000)

        print(f"✓ Weight logged: {weight:.1f} lbs on {date}")

    return _log_weight


@pytest.fixture
async def log_weight_series():
    """
    Log series of weight entries (useful for 14-day scenarios).

    Usage:
        weights = [210.0 - (i * 0.143) for i in range(14)]  # 210 → 208
        await log_weight_series(page, weights, start_date="2025-01-01")
    """
    async def _log_weight_series(
        page: Page,
        weights: List[float],
        start_date: str = None
    ):
        """
        Log multiple weight entries.

        Args:
            page: Playwright page instance
            weights: List of weights (lbs) to log
            start_date: Starting date (YYYY-MM-DD), defaults to today
        """
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")

        start = datetime.strptime(start_date, "%Y-%m-%d")

        for day, weight in enumerate(weights):
            date = (start + timedelta(days=day)).strftime("%Y-%m-%d")

            await page.click("text=⚖️ Weight Tracking")
            await page.click("button[role='tab']:has-text('📝 Log Weight')")
            await page.fill("input[aria-label='Weight (lbs)']", f"{weight:.1f}")
            await page.fill("input[type='date']", date)
            await page.click("button:has-text('Log Weight')")
            await page.wait_for_selector(f"text={weight:.1f} lbs", timeout=3000)

        print(f"✓ Logged {len(weights)} weight entries")

    return _log_weight_series


# ===== Nutrition Tracking Helpers =====

@pytest.fixture
async def log_food():
    """
    Log food entry.

    Usage:
        await log_food(page, "Chicken Breast", 200, 40, "2025-01-15")
    """
    async def _log_food(
        page: Page,
        name: str,
        calories: int,
        protein: int,
        date: str,
        carbs: int = 0,
        fat: int = 0,
        meal_type: str = "lunch"
    ):
        """
        Create food log entry.

        Args:
            page: Playwright page instance
            name: Food/meal name
            calories: Total calories
            protein: Protein in grams
            date: Date string (YYYY-MM-DD)
            carbs: Carbs in grams (optional)
            fat: Fat in grams (optional)
            meal_type: Meal type (breakfast, lunch, dinner, snack)
        """
        # Navigate to nutrition tracking
        await page.click("text=🍽️ Nutrition Tracking")

        # Switch to "Add Food" tab
        await page.click("button[role='tab']:has-text('🔍 Search & Add')")

        # Fill form
        await page.fill("input[aria-label='Food Name']", name)
        await page.fill("input[aria-label='Calories']", str(calories))
        await page.fill("input[aria-label='Protein (g)']", str(protein))

        if carbs > 0:
            await page.fill("input[aria-label='Carbs (g)']", str(carbs))
        if fat > 0:
            await page.fill("input[aria-label='Fat (g)']", str(fat))

        await page.fill("input[type='date']", date)
        await page.select_option("select[aria-label='Meal Type']", meal_type)

        # Submit
        await page.click("button:has-text('Add to Log')")

        # Verify entry appears
        await page.wait_for_selector(f"text={calories} cal", timeout=3000)

        print(f"✓ Food logged: {name} ({calories} cal) on {date}")

    return _log_food


@pytest.fixture
async def log_food_series():
    """
    Log series of food entries (useful for 14-day scenarios).

    Usage:
        await log_food_series(page, 2100, 210, 14, start_date="2025-01-01")
    """
    async def _log_food_series(
        page: Page,
        avg_calories: int,
        avg_protein: int,
        num_days: int,
        start_date: str = None,
        variance: int = 100
    ):
        """
        Log multiple food entries with realistic variance.

        Args:
            page: Playwright page instance
            avg_calories: Average daily calories
            avg_protein: Average daily protein (g)
            num_days: Number of days to log
            start_date: Starting date (YYYY-MM-DD)
            variance: ± calorie variance (default: 100)
        """
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")

        start = datetime.strptime(start_date, "%Y-%m-%d")

        for day in range(num_days):
            date = (start + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_cal = avg_calories + random.randint(-variance, variance)
            daily_protein = int(avg_protein * (daily_cal / avg_calories))

            await page.click("text=🍽️ Nutrition Tracking")
            await page.click("button[role='tab']:has-text('🔍 Search & Add')")
            await page.fill("input[aria-label='Food Name']", f"Day {day+1} Meals")
            await page.fill("input[aria-label='Calories']", str(daily_cal))
            await page.fill("input[aria-label='Protein (g)']", str(daily_protein))
            await page.fill("input[type='date']", date)
            await page.click("button:has-text('Add to Log')")
            await page.wait_for_selector(f"text={daily_cal} cal", timeout=3000)

        print(f"✓ Logged {num_days} food entries (avg {avg_calories} cal)")

    return _log_food_series


# ===== Workout Logging Helpers =====

@pytest.fixture
async def log_workout():
    """
    Log workout session.

    Usage:
        await log_workout(page, "2025-01-15", [
            {"exercise": "Bench Press", "weight": 200, "reps": 8, "sets": 3},
            {"exercise": "Squat", "weight": 275, "reps": 5, "sets": 3}
        ])
    """
    async def _log_workout(page: Page, date: str, exercises: List[Dict]):
        """
        Create workout log entry.

        Args:
            page: Playwright page instance
            date: Date string (YYYY-MM-DD)
            exercises: List of exercise dictionaries with:
                - exercise: Exercise name
                - weight: Weight in lbs
                - reps: Number of reps
                - sets: Number of sets
        """
        # Navigate to workout logging
        await page.click("text=💪 Workout Logging")

        # Fill date
        await page.fill("input[type='date']", date)

        # Log each exercise
        for ex in exercises:
            await page.fill("input[aria-label='Exercise']", ex["exercise"])
            await page.fill("input[aria-label='Weight (lbs)']", str(ex["weight"]))
            await page.fill("input[aria-label='Reps']", str(ex["reps"]))
            await page.fill("input[aria-label='Sets']", str(ex["sets"]))
            await page.click("button:has-text('Add Exercise')")

        # Save workout
        await page.click("button:has-text('Save Workout')")

        print(f"✓ Workout logged: {len(exercises)} exercises on {date}")

    return _log_workout


# ===== API Mocking Helpers =====

@pytest.fixture
async def mock_barcode_api():
    """
    Mock Open Food Facts API for barcode scanner tests.

    Usage:
        await mock_barcode_api(page, "012345678901", {
            "product_name": "Greek Yogurt",
            "nutriments": {
                "energy-kcal": 100,
                "proteins": 15,
                "carbohydrates": 10,
                "fat": 0.5
            }
        })
    """
    async def _mock_barcode(page: Page, upc: str, product_data: Dict):
        """
        Intercept Open Food Facts API and return mock data.

        Args:
            page: Playwright page instance
            upc: UPC barcode string
            product_data: Mock product data
        """
        await page.route(
            f"**/api.openfoodfacts.org/api/v0/product/{upc}.json",
            lambda route: route.fulfill(
                status=200,
                json={
                    "status": 1,
                    "product": product_data
                }
            )
        )

        print(f"✓ Mocked Open Food Facts API for UPC: {upc}")

    return _mock_barcode


@pytest.fixture
async def mock_camera():
    """
    Mock camera/webcam for barcode scanning tests.

    Usage:
        await mock_camera(page, "012345678901")  # Mock barcode scan
    """
    async def _mock_camera(page: Page, barcode: str):
        """
        Mock camera and barcode detector.

        Args:
            page: Playwright page instance
            barcode: Barcode value to return from mock detector
        """
        await page.evaluate(f"""
            // Mock getUserMedia (camera access)
            navigator.mediaDevices.getUserMedia = () => {{
                return Promise.resolve({{
                    getTracks: () => [{{stop: () => {{}}}}]
                }});
            }};

            // Mock BarcodeDetector
            window.BarcodeDetector = class {{
                detect() {{
                    return Promise.resolve([{{
                        rawValue: '{barcode}',
                        format: 'upc_a'
                    }}]);
                }}
            }};
        """)

        print(f"✓ Mocked camera with barcode: {barcode}")

    return _mock_camera


# ===== Assertion Helpers =====

async def assert_adaptive_tdee_in_range(
    page: Page,
    min_tdee: int,
    max_tdee: int,
    message: str = ""
):
    """
    Assert Adaptive TDEE is within expected range.

    Args:
        page: Playwright page instance
        min_tdee: Minimum expected TDEE
        max_tdee: Maximum expected TDEE
        message: Optional error message
    """
    tdee_text = await page.locator('[data-testid="adaptive-tdee-value"]').text_content()
    tdee = int(tdee_text.replace(",", "").replace(" cal", ""))

    assert min_tdee <= tdee <= max_tdee, (
        f"Adaptive TDEE {tdee} out of range [{min_tdee}, {max_tdee}]. {message}"
    )

    print(f"✓ Adaptive TDEE: {tdee} cal (expected {min_tdee}-{max_tdee})")


async def assert_calorie_adjustment(
    page: Page,
    expected_change: int,
    expected_reason: str
):
    """
    Assert calorie adjustment matches expected values.

    Args:
        page: Playwright page instance
        expected_change: Expected calorie change (±100, ±150, 0)
        expected_reason: Expected adjustment reason
    """
    adjustment_text = await page.locator('[data-testid="calorie-adjustment"]').text_content()

    if expected_change > 0:
        assert f"+{expected_change} cal" in adjustment_text
    elif expected_change < 0:
        assert f"{expected_change} cal" in adjustment_text
    else:
        assert "±0 cal" in adjustment_text or "No change" in adjustment_text

    reason_text = await page.locator('[data-testid="adjustment-reason"]').text_content()
    assert expected_reason in reason_text.lower()

    print(f"✓ Adjustment: {expected_change:+d} cal (reason: {expected_reason})")


# ===== pytest Configuration =====

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "tier1: Core persona scenarios")
    config.addinivalue_line("markers", "tier2: Adaptive TDEE edge cases")
    config.addinivalue_line("markers", "tier3: Exercise goal variations")
    config.addinivalue_line("markers", "tier4: Diet outcome edge cases")
    config.addinivalue_line("markers", "tier5: Multi-goal combinations")
    config.addinivalue_line("markers", "tier6: Workflow integrations")
    config.addinivalue_line("markers", "slow: Slow-running tests (>30s)")
