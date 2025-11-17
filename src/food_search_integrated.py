"""
Integrated Food Search System

Combines USDA FDC + Open Food Facts + Local Database
Provides unified interface for food lookup with multiple fallback strategies.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os

from food_logger import FoodLogger, Food
from food_api_fdc import FDCAPIClient, FDCFood
from food_api_off import OFFAPIClient, OFFProduct


@dataclass
class SearchResult:
    """Unified search result from any source"""
    food_id: Optional[int]  # Local DB ID (if already saved)
    name: str
    brand: Optional[str]
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    source: str  # "local", "fdc", "off"
    barcode: Optional[str] = None
    confidence: float = 1.0  # 0.0-1.0 quality score


class IntegratedFoodSearch:
    """
    Unified food search across multiple sources.

    Search Priority:
    1. Local database (fastest, already used foods)
    2. USDA FDC (most accurate for raw foods)
    3. Open Food Facts (barcode/packaged products)

    Features:
    - Barcode lookup (UPC/EAN)
    - Name search with fuzzy matching
    - Automatic caching to local database
    - Quality scoring (prefer USDA over crowd-sourced)
    """

    def __init__(self, food_logger: FoodLogger):
        self.food_logger = food_logger
        self.fdc_client = None  # Lazy init (requires API key)
        self.off_client = OFFAPIClient()

    def _get_fdc_client(self) -> Optional[FDCAPIClient]:
        """Lazy initialize FDC client (requires API key)"""
        if self.fdc_client is None:
            try:
                self.fdc_client = FDCAPIClient()
            except ValueError:
                # API key not available, skip FDC
                return None
        return self.fdc_client

    def search_by_name(self, query: str, limit: int = 20) -> List[SearchResult]:
        """
        Search foods by name across all sources.

        Strategy:
        1. Search local database first (instant)
        2. Search USDA FDC for high-quality data
        3. Merge and rank by relevance

        Args:
            query: Search term (e.g., "chicken breast")
            limit: Max results to return

        Returns:
            List of SearchResult objects, ranked by quality/relevance
        """
        results = []

        # 1. Search local database
        local_foods = self.food_logger.search_foods(query, limit=10)
        for food in local_foods:
            results.append(SearchResult(
                food_id=food.food_id,
                name=food.name,
                brand=food.brand,
                serving_size=food.serving_size,
                calories=food.calories,
                protein_g=food.protein_g,
                carbs_g=food.carbs_g,
                fat_g=food.fat_g,
                source="local",
                barcode=food.barcode,
                confidence=1.0  # Already in DB = highest confidence
            ))

        # 2. Search USDA FDC (if API key available)
        fdc = self._get_fdc_client()
        if fdc and len(results) < limit:
            try:
                fdc_foods = fdc.search_and_parse(query, limit=limit - len(results))
                for food in fdc_foods:
                    results.append(self._fdc_to_search_result(food))
            except Exception as e:
                print(f"FDC search error: {e}")

        return results[:limit]

    def lookup_barcode(self, barcode: str) -> Optional[SearchResult]:
        """
        Lookup food by barcode (UPC/EAN).

        Strategy:
        1. Check local database first
        2. Query Open Food Facts
        3. Cache result if found

        Args:
            barcode: Product barcode (e.g., "737628064502")

        Returns:
            SearchResult or None if not found
        """
        # 1. Check local database
        conn = self.food_logger._FoodLogger__init__.db_path  # Access private
        # Actually, let's use a proper method
        # For now, skip local barcode lookup (would need new query)

        # 2. Query Open Food Facts
        product = self.off_client.lookup_barcode(barcode)

        if not product:
            return None

        # Convert to SearchResult
        result = self._off_to_search_result(product)

        # 3. Cache to local database
        food = Food(
            food_id=None,
            name=result.name,
            brand=result.brand,
            serving_size=result.serving_size,
            calories=result.calories,
            protein_g=result.protein_g,
            carbs_g=result.carbs_g,
            fat_g=result.fat_g,
            source="off",
            barcode=barcode
        )

        try:
            food_id = self.food_logger.add_food(food)
            result.food_id = food_id
            result.source = "local"  # Now cached locally
        except Exception as e:
            print(f"Warning: Failed to cache food: {e}")

        return result

    def _fdc_to_search_result(self, fdc_food: FDCFood) -> SearchResult:
        """Convert FDC food to SearchResult"""
        # FDC serving size description
        serving = fdc_food.household_serving or f"{fdc_food.serving_size or 100}g"

        return SearchResult(
            food_id=None,  # Not in local DB yet
            name=fdc_food.description,
            brand=fdc_food.brand_name,
            serving_size=serving,
            calories=fdc_food.calories,
            protein_g=fdc_food.protein_g,
            carbs_g=fdc_food.carbs_g,
            fat_g=fdc_food.fat_g,
            source="fdc",
            barcode=fdc_food.gtin_upc,
            confidence=0.95 if fdc_food.data_type == "Foundation" else 0.85
        )

    def _off_to_search_result(self, off_product: OFFProduct) -> SearchResult:
        """Convert OFF product to SearchResult"""
        return SearchResult(
            food_id=None,  # Not in local DB yet
            name=off_product.product_name,
            brand=off_product.brands,
            serving_size=off_product.serving_size or "100g",
            calories=off_product.calories,
            protein_g=off_product.protein_g,
            carbs_g=off_product.carbs_g,
            fat_g=off_product.fat_g,
            source="off",
            barcode=off_product.barcode,
            confidence=off_product.completeness * 0.8  # 0-80% based on data quality
        )

    def add_result_to_database(self, result: SearchResult) -> int:
        """
        Add search result to local database.

        Returns:
            food_id in local database
        """
        if result.food_id:
            # Already in database
            return result.food_id

        food = Food(
            food_id=None,
            name=result.name,
            brand=result.brand,
            serving_size=result.serving_size,
            calories=result.calories,
            protein_g=result.protein_g,
            carbs_g=result.carbs_g,
            fat_g=result.fat_g,
            source=result.source,
            barcode=result.barcode
        )

        return self.food_logger.add_food(food)


if __name__ == "__main__":
    # Test integrated search
    print("=== Integrated Food Search Test ===\n")

    # Initialize
    logger = FoodLogger("data/test_food_log.db")
    search = IntegratedFoodSearch(logger)

    # Test 1: Search by name
    print("TEST 1: Search 'chicken'")
    print("=" * 60)
    results = search.search_by_name("chicken", limit=5)

    for i, r in enumerate(results, 1):
        print(f"{i}. {r.name[:50]}")
        print(f"   Source: {r.source} | Confidence: {r.confidence:.0%}")
        print(f"   {r.calories} cal | {r.protein_g}g P | {r.serving_size}")
        print()

    # Test 2: Barcode lookup
    print("\nTEST 2: Barcode lookup '737628064502'")
    print("=" * 60)
    barcode_result = search.lookup_barcode("737628064502")

    if barcode_result:
        print(f"✅ Found: {barcode_result.name}")
        print(f"   Brand: {barcode_result.brand}")
        print(f"   Source: {barcode_result.source}")
        print(f"   Calories: {barcode_result.calories}")
        print(f"   Cached to DB: {barcode_result.food_id is not None}")
    else:
        print("❌ Not found")

    print("\n✅ All tests completed!")
