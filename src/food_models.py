"""
Food Data Models for HealthRAG Nutrition System

Normalized data models for:
- Foods from multiple sources (FDC, OFF, custom)
- Food log entries
- Daily nutrition summaries
- Weight tracking for TDEE calculation
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import date, datetime
from enum import Enum


class FoodSource(Enum):
    """Source of food data"""
    FDC = "fdc"  # USDA FoodData Central
    OFF = "off"  # Open Food Facts
    FOODREPO = "foodrepo"  # Open Food Repo
    CUSTOM = "custom"  # User-created
    EDAMAM = "edamam"  # Edamam API (optional paid tier)


class DataQuality(Enum):
    """Data quality indicators"""
    VERIFIED = "verified"  # USDA-verified or label-exact
    LABEL_EXACT = "label_exact"  # Scanned from product label
    DERIVED = "derived"  # Calculated from ingredients
    ESTIMATED = "estimated"  # Approximated
    UNKNOWN = "unknown"  # Quality not known


@dataclass
class Food:
    """
    Normalized food item from any source.

    All nutrition values are per 100g for consistency.
    Serving sizes stored separately.
    """
    # Primary Key
    food_id: str  # Format: "fdc:123456" or "off:737628064502"

    # Source Metadata
    source: FoodSource
    source_id: str  # Original ID from source database
    barcode: Optional[str] = None  # UPC/EAN if available

    # Basic Info
    name: str = ""
    brand: Optional[str] = None
    category: Optional[str] = None

    # Macronutrients (per 100g)
    calories: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    sodium_mg: Optional[float] = None

    # Serving Info
    serving_size_g: Optional[float] = None  # Default serving size in grams
    serving_description: Optional[str] = None  # "1 cup", "1 slice", "100g"

    # Micronutrients (optional, for advanced tracking)
    vitamin_a_ug: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    potassium_mg: Optional[float] = None

    # Quality Indicators
    data_quality: DataQuality = DataQuality.UNKNOWN
    completeness_score: float = 0.0  # 0.0-1.0 (% of fields populated)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_synced: Optional[datetime] = None

    def get_nutrition_per_serving(self) -> Dict[str, float]:
        """Calculate nutrition for default serving size"""
        if not self.serving_size_g:
            # Default to 100g if no serving size specified
            serving_g = 100.0
        else:
            serving_g = self.serving_size_g

        multiplier = serving_g / 100.0

        return {
            'calories': self.calories * multiplier,
            'protein_g': self.protein_g * multiplier,
            'fat_g': self.fat_g * multiplier,
            'carbs_g': self.carbs_g * multiplier,
            'fiber_g': self.fiber_g * multiplier if self.fiber_g else None,
            'sugar_g': self.sugar_g * multiplier if self.sugar_g else None,
            'serving_size_g': serving_g,
            'serving_description': self.serving_description or f"{serving_g}g"
        }

    def calculate_completeness_score(self) -> float:
        """
        Score data completeness (0.0-1.0).

        Required fields (50%): name, calories, protein, fat, carbs
        Important fields (30%): fiber, sugar, sodium, serving_size
        Nice-to-have (20%): micronutrients, brand, category
        """
        score = 0.0

        # Required (10 points each = 50 points)
        if self.name: score += 10
        if self.calories > 0: score += 10
        if self.protein_g >= 0: score += 10
        if self.fat_g >= 0: score += 10
        if self.carbs_g >= 0: score += 10

        # Important (7.5 points each = 30 points)
        if self.fiber_g is not None: score += 7.5
        if self.sugar_g is not None: score += 7.5
        if self.sodium_mg is not None: score += 7.5
        if self.serving_size_g is not None: score += 7.5

        # Nice-to-have (5 points each = 20 points)
        if self.vitamin_a_ug is not None: score += 5
        if self.vitamin_c_mg is not None: score += 5
        if self.brand: score += 5
        if self.category: score += 5

        return score / 100.0


@dataclass
class FoodEntry:
    """
    Single food log entry (user ate this food).

    Denormalizes food data for historical tracking
    (if food data changes later, log remains accurate).
    """
    # Required fields (no defaults)
    user_id: str
    logged_at: datetime  # When eaten
    food_id: str  # FK to foods table
    food_name: str  # Denormalized for history

    # Optional fields (with defaults)
    entry_id: Optional[int] = None
    meal_type: Optional[str] = None  # 'breakfast', 'lunch', 'dinner', 'snack'
    brand: Optional[str] = None  # Denormalized

    # Quantity
    serving_size_g: float = 100.0  # Actual amount eaten
    servings: float = 1.0  # Number of servings (1.5 servings, etc.)

    # Nutrition (denormalized for this serving)
    calories: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None

    # Metadata
    source: str = "search"  # 'barcode', 'search', 'manual', 'recent', 'recipe'
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class DailyNutrition:
    """
    Daily nutrition summary (rollup of all food entries for a day).

    Used for TDEE calculation and adherence tracking.
    """
    # Required fields (no defaults)
    user_id: str
    date: date

    # Optional fields (with defaults)
    summary_id: Optional[int] = None

    # Daily Totals (actual intake)
    total_calories: float = 0.0
    total_protein_g: float = 0.0
    total_fat_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fiber_g: Optional[float] = None

    # Targets (what they SHOULD eat)
    target_calories: Optional[float] = None
    target_protein_g: Optional[float] = None
    target_fat_g: Optional[float] = None
    target_carbs_g: Optional[float] = None

    # Adherence Metrics
    calories_delta: Optional[float] = None  # Actual - Target
    adherence_pct: Optional[float] = None  # Actual / Target * 100

    # Computed Fields
    meal_count: int = 0  # Number of logged meals
    entry_count: int = 0  # Number of food entries

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def calculate_adherence(self):
        """Calculate adherence metrics"""
        if self.target_calories and self.target_calories > 0:
            self.calories_delta = self.total_calories - self.target_calories
            self.adherence_pct = (self.total_calories / self.target_calories) * 100
        else:
            self.calories_delta = None
            self.adherence_pct = None


@dataclass
class WeightEntry:
    """
    Daily weight log entry.

    Used for trend weight calculation and TDEE.
    """
    # Required fields (no defaults)
    user_id: str
    weight_lbs: float
    weigh_date: date  # Date only (AM weigh-in)

    # Optional fields (with defaults)
    log_id: Optional[int] = None

    # Trend Calculation (computed via EWMA)
    trend_weight_lbs: Optional[float] = None  # Smoothed weight

    # Metadata
    notes: Optional[str] = None  # "ate sushi last night", "day after cheat meal"
    created_at: Optional[datetime] = None


@dataclass
class BodyMeasurement:
    """
    Body measurements (waist, chest, arms, etc.).

    Critical for recomp tracking (waist decrease = fat loss proof).
    """
    # Required fields (no defaults)
    user_id: str
    measurement_date: date

    # Optional fields (with defaults)
    measurement_id: Optional[int] = None

    # Common Measurements (inches)
    waist_inches: Optional[float] = None  # At navel (PRIMARY for recomp)
    chest_inches: Optional[float] = None  # At nipple line
    arm_left_inches: Optional[float] = None  # At peak (flexed)
    arm_right_inches: Optional[float] = None
    thigh_left_inches: Optional[float] = None  # At mid-thigh
    thigh_right_inches: Optional[float] = None
    hip_inches: Optional[float] = None  # At widest point

    # Calculated Metrics
    waist_to_height_ratio: Optional[float] = None  # Health indicator

    # Metadata
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class UserMacroTargets:
    """
    User's current macro targets.

    Updated weekly based on adaptive TDEE algorithm.
    """
    # Required fields (no defaults)
    user_id: str
    start_date: date

    # Optional fields (with defaults)
    target_id: Optional[int] = None
    end_date: Optional[date] = None  # None = current target

    # Calorie Targets
    target_calories: float = 2000.0

    # Macro Targets (grams)
    target_protein_g: float = 150.0
    target_fat_g: float = 65.0
    target_carbs_g: float = 200.0

    # Goal Context
    phase: str = "maintain"  # 'cut', 'bulk', 'maintain', 'recomp'
    goal_rate_lbs_per_week: float = 0.0  # -1.0 for cut, +0.75 for bulk, 0 for maintain/recomp

    # Metadata
    notes: Optional[str] = None  # "Week 8 adjustment: -100 cal (losing too slow)"
    created_at: Optional[datetime] = None


# Helper Functions

def create_food_from_fdc(fdc_data: Dict) -> Food:
    """
    Convert FDC JSON data to normalized Food model.

    FDC data structure:
    {
      "fdcId": 171477,
      "description": "Chicken, broilers or fryers, breast, meat only, raw",
      "brandOwner": null,
      "foodNutrients": [
        {"nutrientId": 1008, "value": 120},  # Energy (kcal)
        {"nutrientId": 1003, "value": 23.0},  # Protein
        ...
      ]
    }
    """
    # Implementation will be in src/nutrition_database.py
    # This is a placeholder showing the interface
    pass


def create_food_from_off(off_data: Dict) -> Food:
    """
    Convert Open Food Facts JSON to normalized Food model.

    OFF data structure:
    {
      "code": "737628064502",
      "product_name": "Quest Bar - Chocolate Chip Cookie Dough",
      "brands": "Quest Nutrition",
      "nutriments": {
        "energy-kcal_100g": 350,
        "proteins_100g": 21,
        ...
      }
    }
    """
    # Implementation will be in src/nutrition_database.py
    # This is a placeholder showing the interface
    pass


if __name__ == "__main__":
    # Example usage
    print("=== Food Data Models Test ===\n")

    # Test Food model
    chicken = Food(
        food_id="fdc:171477",
        source=FoodSource.FDC,
        source_id="171477",
        name="Chicken breast, raw",
        calories=120,
        protein_g=23.0,
        fat_g=1.2,
        carbs_g=0.0,
        serving_size_g=113.4,  # 4 oz
        serving_description="4 oz (113g)",
        data_quality=DataQuality.VERIFIED
    )

    # Calculate completeness
    chicken.completeness_score = chicken.calculate_completeness_score()
    print(f"Food: {chicken.name}")
    print(f"Completeness: {chicken.completeness_score:.1%}")

    # Get nutrition per serving
    serving_nutrition = chicken.get_nutrition_per_serving()
    print(f"\nPer Serving ({serving_nutrition['serving_description']}):")
    print(f"  Calories: {serving_nutrition['calories']:.0f}")
    print(f"  Protein: {serving_nutrition['protein_g']:.1f}g")
    print(f"  Fat: {serving_nutrition['fat_g']:.1f}g")
    print(f"  Carbs: {serving_nutrition['carbs_g']:.1f}g")

    # Test FoodEntry
    entry = FoodEntry(
        user_id="default_user",
        logged_at=datetime.now(),
        food_id="fdc:171477",
        food_name="Chicken breast, raw",
        meal_type="lunch",
        serving_size_g=226.8,  # 8 oz
        servings=2.0,
        calories=240,
        protein_g=46.0,
        fat_g=2.4,
        carbs_g=0.0,
        source="search"
    )

    print(f"\n\nFood Entry:")
    print(f"  Meal: {entry.meal_type}")
    print(f"  Food: {entry.food_name}")
    print(f"  Amount: {entry.servings} servings ({entry.serving_size_g}g)")
    print(f"  Calories: {entry.calories:.0f}")
    print(f"  Protein: {entry.protein_g:.1f}g")

    # Test DailyNutrition
    daily = DailyNutrition(
        user_id="default_user",
        date=date.today(),
        total_calories=1850,
        total_protein_g=175,
        total_fat_g=60,
        total_carbs_g=180,
        target_calories=1800,
        target_protein_g=180,
        meal_count=4,
        entry_count=12
    )

    daily.calculate_adherence()

    print(f"\n\nDaily Summary:")
    print(f"  Date: {daily.date}")
    print(f"  Calories: {daily.total_calories:.0f} / {daily.target_calories:.0f} ({daily.adherence_pct:.0f}%)")
    print(f"  Protein: {daily.total_protein_g:.0f}g / {daily.target_protein_g:.0f}g")
    print(f"  Delta: {daily.calories_delta:+.0f} calories")
    print(f"  Meals logged: {daily.meal_count}")
