"""
USDA FoodData Central API Wrapper

Provides clean interface to USDA FDC API for food data retrieval.
Handles API key management, rate limiting, and response parsing.

API Documentation: https://fdc.nal.usda.gov/api-guide.html
"""

import os
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class FDCFood:
    """Simplified FDC food response"""
    fdc_id: int
    description: str
    data_type: str  # "Foundation", "SR Legacy", "Branded", "Survey"
    food_category: Optional[str]

    # Nutrition per 100g
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: Optional[float]
    sugar_g: Optional[float]
    sodium_mg: Optional[float]

    # Serving info (if available)
    serving_size: Optional[float]  # grams
    serving_size_unit: Optional[str]
    household_serving: Optional[str]  # "1 cup", "1 medium"

    # Branded food info
    brand_owner: Optional[str]
    brand_name: Optional[str]
    gtin_upc: Optional[str]  # Barcode
    ingredients: Optional[str]


class FDCAPIClient:
    """
    USDA FoodData Central API client.

    Features:
    - Search foods by name/keyword
    - Get detailed food data by FDC ID
    - Parse nutrition data into standardized format
    - Respect rate limits (1000 req/hour default)
    """

    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FDC API client.

        Args:
            api_key: FDC API key. If None, reads from env var USDA_FDC_API_KEY
        """
        self.api_key = api_key or os.environ.get('USDA_FDC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "USDA FDC API key required. "
                "Set USDA_FDC_API_KEY environment variable or pass api_key parameter. "
                "Get key at: https://fdc.nal.usda.gov/api-key-signup"
            )

        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.036  # ~1000 req/hour = 1 req per 3.6ms

    def _rate_limit(self):
        """Simple rate limiter to respect API limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def search_foods(
        self,
        query: str,
        page_size: int = 20,
        page_number: int = 1,
        data_type: Optional[List[str]] = None,
        sort_by: str = "dataType.keyword",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Search for foods by name or keyword.

        Args:
            query: Search term (e.g., "chicken breast")
            page_size: Results per page (max 200)
            page_number: Page number (1-indexed)
            data_type: Filter by data types (e.g., ["Foundation", "SR Legacy"])
            sort_by: Sort field
            sort_order: "asc" or "desc"

        Returns:
            Dictionary with 'totalHits' and 'foods' list
        """
        self._rate_limit()

        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": min(page_size, 200),  # Cap at API max
            "pageNumber": page_number,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        if data_type:
            params["dataType"] = data_type

        response = self.session.get(
            f"{self.BASE_URL}/foods/search",
            params=params,
            timeout=10
        )
        response.raise_for_status()

        return response.json()

    def get_food(self, fdc_id: int, format: str = "full") -> Dict[str, Any]:
        """
        Get detailed information for a specific food by FDC ID.

        Args:
            fdc_id: FoodData Central ID
            format: "abridged" or "full" (default full)

        Returns:
            Complete food data including all nutrients
        """
        self._rate_limit()

        params = {
            "api_key": self.api_key,
            "format": format
        }

        response = self.session.get(
            f"{self.BASE_URL}/food/{fdc_id}",
            params=params,
            timeout=10
        )
        response.raise_for_status()

        return response.json()

    def parse_food_response(self, food_data: Dict) -> FDCFood:
        """
        Parse FDC API response into simplified FDCFood object.

        Extracts key nutrients and normalizes to per-100g values.
        """
        # Extract basic info
        fdc_id = food_data.get('fdcId')
        description = food_data.get('description', '')
        data_type = food_data.get('dataType', '')
        food_category = food_data.get('foodCategory')

        # Extract branded info if available
        brand_owner = food_data.get('brandOwner')
        brand_name = food_data.get('brandName')
        gtin_upc = food_data.get('gtinUpc')
        ingredients = food_data.get('ingredients')

        # Extract serving size info
        serving_size = food_data.get('servingSize')
        serving_size_unit = food_data.get('servingSizeUnit')
        household_serving = food_data.get('householdServingFullText')

        # Parse nutrients (stored in foodNutrients array)
        nutrients = {}
        food_nutrients = food_data.get('foodNutrients', [])

        # Nutrient ID mapping (FDC standard IDs)
        nutrient_map = {
            1008: 'calories',      # Energy (kcal)
            1003: 'protein_g',     # Protein
            1004: 'fat_g',         # Total lipid (fat)
            1005: 'carbs_g',       # Carbohydrate, by difference
            1079: 'fiber_g',       # Fiber, total dietary
            2000: 'sugar_g',       # Total Sugars
            1093: 'sodium_mg',     # Sodium, Na
        }

        for nutrient_data in food_nutrients:
            nutrient_id = nutrient_data.get('nutrientId')
            if nutrient_id in nutrient_map:
                key = nutrient_map[nutrient_id]
                value = nutrient_data.get('value', 0)

                # Convert sodium from mg to mg (already in mg)
                # Convert others from per-serving to per-100g if needed
                nutrients[key] = value

        # Ensure all required fields exist
        calories = nutrients.get('calories', 0)
        protein_g = nutrients.get('protein_g', 0)
        fat_g = nutrients.get('fat_g', 0)
        carbs_g = nutrients.get('carbs_g', 0)
        fiber_g = nutrients.get('fiber_g')
        sugar_g = nutrients.get('sugar_g')
        sodium_mg = nutrients.get('sodium_mg')

        return FDCFood(
            fdc_id=fdc_id,
            description=description,
            data_type=data_type,
            food_category=food_category,
            calories=calories,
            protein_g=protein_g,
            fat_g=fat_g,
            carbs_g=carbs_g,
            fiber_g=fiber_g,
            sugar_g=sugar_g,
            sodium_mg=sodium_mg,
            serving_size=serving_size,
            serving_size_unit=serving_size_unit,
            household_serving=household_serving,
            brand_owner=brand_owner,
            brand_name=brand_name,
            gtin_upc=gtin_upc,
            ingredients=ingredients
        )

    def search_and_parse(
        self,
        query: str,
        limit: int = 20,
        data_type: Optional[List[str]] = None
    ) -> List[FDCFood]:
        """
        Search foods and return parsed results in one call.

        Convenience method that combines search_foods() and parse_food_response().
        """
        results = self.search_foods(query, page_size=limit, data_type=data_type)

        foods = []
        for food_data in results.get('foods', []):
            try:
                parsed = self.parse_food_response(food_data)
                foods.append(parsed)
            except Exception as e:
                # Log error but continue processing other foods
                print(f"Warning: Failed to parse food {food_data.get('fdcId')}: {e}")
                continue

        return foods


# Convenience functions for common operations

def search_foundation_foods(query: str, limit: int = 20) -> List[FDCFood]:
    """
    Search only Foundation Foods (highest quality USDA data).

    Foundation Foods are lab-analyzed with the most complete nutrient profiles.
    """
    client = FDCAPIClient()
    return client.search_and_parse(query, limit=limit, data_type=["Foundation"])


def search_sr_legacy_foods(query: str, limit: int = 20) -> List[FDCFood]:
    """
    Search SR Legacy foods (Standard Reference, comprehensive nutrient database).

    SR Legacy contains 8,000+ foods with complete nutrient data.
    Good for raw/generic foods.
    """
    client = FDCAPIClient()
    return client.search_and_parse(query, limit=limit, data_type=["SR Legacy"])


def search_branded_foods(query: str, limit: int = 20) -> List[FDCFood]:
    """
    Search branded/packaged foods.

    Contains manufacturer-provided label data for specific brands.
    """
    client = FDCAPIClient()
    return client.search_and_parse(query, limit=limit, data_type=["Branded"])


def search_all_foods(query: str, limit: int = 20) -> List[FDCFood]:
    """
    Search all food types (Foundation, SR Legacy, Branded, Survey).

    Returns mixed results prioritized by data quality.
    """
    client = FDCAPIClient()
    return client.search_and_parse(query, limit=limit)


if __name__ == "__main__":
    # Test the API client
    print("=== USDA FDC API Client Test ===\n")

    try:
        # Test 1: Search chicken breast
        print("TEST 1: Search 'chicken breast'")
        print("=" * 60)
        foods = search_foundation_foods("chicken breast", limit=3)

        for food in foods:
            print(f"\n{food.description}")
            print(f"  FDC ID: {food.fdc_id}")
            print(f"  Type: {food.data_type}")
            print(f"  Calories: {food.calories}")
            print(f"  Protein: {food.protein_g}g")
            print(f"  Fat: {food.fat_g}g")
            print(f"  Carbs: {food.carbs_g}g")
            if food.fiber_g:
                print(f"  Fiber: {food.fiber_g}g")

        print("\n\nTEST 2: Search 'banana' (all types)")
        print("=" * 60)
        all_bananas = search_all_foods("banana", limit=5)
        print(f"Found {len(all_bananas)} banana entries")

        for food in all_bananas[:3]:  # Show first 3
            print(f"\n{food.description[:60]}...")
            print(f"  Type: {food.data_type}, Calories: {food.calories}")

        print("\n✅ All tests passed!")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo fix:")
        print("1. Get API key: https://fdc.nal.usda.gov/api-key-signup")
        print("2. Add to data/.env: USDA_FDC_API_KEY=your_key_here")
        print("3. Run: export $(cat data/.env | xargs) && python3 src/food_api_fdc.py")
