"""
Open Food Facts API Wrapper

Provides clean interface to Open Food Facts API for barcode-based food lookup.
Handles product search, barcode lookup, and nutrition data parsing.

API Documentation: https://openfoodfacts.github.io/openfoodfacts-server/api/
"""

import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class OFFProduct:
    """Simplified Open Food Facts product"""
    barcode: str
    product_name: str
    brands: Optional[str]
    quantity: Optional[str]  # "10 oz", "284 g"

    # Nutrition per 100g (normalized)
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: Optional[float]
    sugar_g: Optional[float]
    sodium_mg: Optional[float]
    saturated_fat_g: Optional[float]

    # Serving info (if available)
    serving_size: Optional[str]

    # Additional info
    categories: Optional[str]
    ingredients_text: Optional[str]
    allergens: Optional[str]
    nutriscore_grade: Optional[str]  # a, b, c, d, e
    nova_group: Optional[int]  # 1-4 (processing level)

    # Images
    image_url: Optional[str]
    image_nutrition_url: Optional[str]

    # Quality indicators
    completeness: float  # 0.0-1.0 (how complete the data is)
    data_quality_tags: List[str]


class OFFAPIClient:
    """
    Open Food Facts API client.

    Features:
    - Lookup products by barcode (UPC/EAN)
    - Search products by name
    - Parse nutrition data into standardized format
    - No API key required (free, open database)

    Rate Limits:
    - 100 requests/min for product queries
    - 10 requests/min for search queries
    """

    BASE_URL = "https://world.openfoodfacts.org/api/v2"

    def __init__(self):
        """Initialize Open Food Facts API client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HealthRAG/1.0 (Nutrition Tracking App)'
        })
        self.last_request_time = 0
        self.min_request_interval = 0.6  # 100 req/min = 1 req per 0.6s

    def _rate_limit(self):
        """Simple rate limiter to respect API limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Get product by barcode (UPC/EAN).

        Args:
            barcode: Product barcode (e.g., "737628064502")

        Returns:
            Product data dictionary or None if not found
        """
        self._rate_limit()

        # Clean barcode (remove spaces, dashes)
        barcode = barcode.replace(' ', '').replace('-', '')

        try:
            response = self.session.get(
                f"{self.BASE_URL}/product/{barcode}",
                timeout=10
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            # Check if product found
            if data.get('status') != 1:
                return None

            return data.get('product')

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def search_products(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "popularity"
    ) -> Dict[str, Any]:
        """
        Search products by name.

        Args:
            query: Search term (e.g., "greek yogurt")
            page: Page number (1-indexed)
            page_size: Results per page (max 100)
            sort_by: "popularity", "product_name", "created_t"

        Returns:
            Dictionary with 'products' list and pagination info
        """
        self._rate_limit()

        params = {
            "search_terms": query,
            "page": page,
            "page_size": min(page_size, 100),
            "sort_by": sort_by
        }

        response = self.session.get(
            f"{self.BASE_URL}/search",
            params=params,
            timeout=10
        )
        response.raise_for_status()

        return response.json()

    def parse_product_response(self, product_data: Dict) -> OFFProduct:
        """
        Parse Open Food Facts API response into simplified OFFProduct object.

        Extracts nutrition data and normalizes to per-100g values.
        """
        # Basic info
        barcode = product_data.get('code', '')
        product_name = product_data.get('product_name') or product_data.get('generic_name', 'Unknown')
        brands = product_data.get('brands')
        quantity = product_data.get('quantity')

        # Categories and ingredients
        categories = product_data.get('categories')
        ingredients_text = product_data.get('ingredients_text')
        allergens = product_data.get('allergens')

        # Quality scores
        nutriscore_grade = product_data.get('nutriscore_grade')
        nova_group = product_data.get('nova_group')

        # Images
        image_url = product_data.get('image_url')
        image_nutrition_url = product_data.get('image_nutrition_url')

        # Extract nutrition data (per 100g)
        nutriments = product_data.get('nutriments', {})

        # Get nutrition values (OFF uses _100g suffix)
        calories = nutriments.get('energy-kcal_100g', 0) or nutriments.get('energy_100g', 0) / 4.184  # kJ to kcal
        protein_g = nutriments.get('proteins_100g', 0)
        fat_g = nutriments.get('fat_100g', 0)
        carbs_g = nutriments.get('carbohydrates_100g', 0)
        fiber_g = nutriments.get('fiber_100g')
        sugar_g = nutriments.get('sugars_100g')
        sodium_mg = nutriments.get('sodium_100g', 0) * 1000 if nutriments.get('sodium_100g') else None  # g to mg
        saturated_fat_g = nutriments.get('saturated-fat_100g')

        # Serving size
        serving_size = product_data.get('serving_size')

        # Calculate completeness score
        completeness = self._calculate_completeness(product_data)

        # Extract quality tags
        data_quality_tags = product_data.get('data_quality_tags', [])

        return OFFProduct(
            barcode=barcode,
            product_name=product_name,
            brands=brands,
            quantity=quantity,
            calories=calories,
            protein_g=protein_g,
            fat_g=fat_g,
            carbs_g=carbs_g,
            fiber_g=fiber_g,
            sugar_g=sugar_g,
            sodium_mg=sodium_mg,
            saturated_fat_g=saturated_fat_g,
            serving_size=serving_size,
            categories=categories,
            ingredients_text=ingredients_text,
            allergens=allergens,
            nutriscore_grade=nutriscore_grade,
            nova_group=nova_group,
            image_url=image_url,
            image_nutrition_url=image_nutrition_url,
            completeness=completeness,
            data_quality_tags=data_quality_tags
        )

    def _calculate_completeness(self, product_data: Dict) -> float:
        """
        Calculate data completeness score (0.0-1.0).

        Based on presence of key fields.
        """
        score = 0.0
        nutriments = product_data.get('nutriments', {})

        # Required fields (20 points each = 100 points)
        if product_data.get('product_name') or product_data.get('generic_name'):
            score += 20
        if nutriments.get('energy-kcal_100g') or nutriments.get('energy_100g'):
            score += 20
        if nutriments.get('proteins_100g') is not None:
            score += 20
        if nutriments.get('fat_100g') is not None:
            score += 20
        if nutriments.get('carbohydrates_100g') is not None:
            score += 20

        return score / 100.0

    def lookup_barcode(self, barcode: str) -> Optional[OFFProduct]:
        """
        Convenience method: Lookup and parse barcode in one call.

        Returns:
            OFFProduct or None if not found
        """
        product_data = self.get_product_by_barcode(barcode)

        if not product_data:
            return None

        try:
            return self.parse_product_response(product_data)
        except Exception as e:
            print(f"Warning: Failed to parse product {barcode}: {e}")
            return None

    def search_and_parse(self, query: str, limit: int = 20) -> List[OFFProduct]:
        """
        Search products and return parsed results in one call.

        Returns:
            List of OFFProduct objects
        """
        results = self.search_products(query, page_size=limit)

        products = []
        for product_data in results.get('products', []):
            try:
                parsed = self.parse_product_response(product_data)
                products.append(parsed)
            except Exception as e:
                # Log error but continue processing other products
                print(f"Warning: Failed to parse product {product_data.get('code')}: {e}")
                continue

        return products


# Convenience functions

def lookup_barcode(barcode: str) -> Optional[OFFProduct]:
    """
    Quick barcode lookup.

    Example:
        product = lookup_barcode("737628064502")
        if product:
            print(f"{product.product_name}: {product.calories} cal")
    """
    client = OFFAPIClient()
    return client.lookup_barcode(barcode)


def search_products(query: str, limit: int = 20) -> List[OFFProduct]:
    """
    Quick product search.

    Example:
        products = search_products("greek yogurt")
        for p in products:
            print(f"{p.product_name} ({p.brands})")
    """
    client = OFFAPIClient()
    return client.search_and_parse(query, limit=limit)


if __name__ == "__main__":
    # Test the API client
    print("=== Open Food Facts API Client Test ===\n")

    # Test 1: Lookup known barcode
    print("TEST 1: Lookup barcode '737628064502' (Thai Kitchen Rice Noodles)")
    print("=" * 60)

    product = lookup_barcode("737628064502")

    if product:
        print(f"✅ Product found!")
        print(f"Name: {product.product_name}")
        print(f"Brands: {product.brands}")
        print(f"Quantity: {product.quantity}")
        print(f"\nNutrition (per 100g):")
        print(f"  Calories: {product.calories}")
        print(f"  Protein: {product.protein_g}g")
        print(f"  Fat: {product.fat_g}g")
        print(f"  Carbs: {product.carbs_g}g")
        if product.fiber_g:
            print(f"  Fiber: {product.fiber_g}g")
        if product.sugar_g:
            print(f"  Sugar: {product.sugar_g}g")
        print(f"\nCompleteness: {product.completeness:.0%}")
        print(f"Nutri-Score: {product.nutriscore_grade or 'N/A'}")
        print(f"NOVA Group: {product.nova_group or 'N/A'}")
    else:
        print("❌ Product not found")

    # Test 2: Search products
    print("\n\nTEST 2: Search 'greek yogurt'")
    print("=" * 60)

    products = search_products("greek yogurt", limit=3)
    print(f"Found {len(products)} products\n")

    for i, p in enumerate(products, 1):
        print(f"{i}. {p.product_name}")
        print(f"   Brands: {p.brands or 'Unknown'}")
        print(f"   Calories: {p.calories} | Protein: {p.protein_g}g")
        print()

    # Test 3: Test 404 (product not in database)
    print("TEST 3: Lookup non-existent barcode '000000000000'")
    print("=" * 60)

    not_found = lookup_barcode("000000000000")
    if not_found:
        print("❌ Unexpectedly found product")
    else:
        print("✅ Correctly returned None for missing product")

    print("\n✅ All tests completed!")
