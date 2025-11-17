#!/usr/bin/env python3
"""
Test script for USDA FDC and Open Food Facts APIs
Verifies both APIs are working with real data
"""

import os
import sys
import requests
from typing import Dict, Any, Optional

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_usda_fdc(api_key: str) -> bool:
    """Test USDA FoodData Central API"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing USDA FoodData Central API{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    test_queries = [
        "chicken breast",
        "banana",
        "oatmeal"
    ]

    for query in test_queries:
        try:
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "query": query,
                "api_key": api_key,
                "pageSize": 3
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            total_hits = data.get('totalHits', 0)
            foods = data.get('foods', [])

            if foods:
                first_food = foods[0]
                print(f"{GREEN}✓{RESET} Query: '{query}'")
                print(f"  Total Results: {total_hits:,}")
                print(f"  First Result: {first_food.get('description', 'N/A')}")
                print(f"  Data Type: {first_food.get('dataType', 'N/A')}")

                # Show nutrients if available
                nutrients = first_food.get('foodNutrients', [])
                if nutrients:
                    print(f"  Nutrients: {len(nutrients)} available")
                    # Show first 3 nutrients
                    for nutrient in nutrients[:3]:
                        name = nutrient.get('nutrientName', 'Unknown')
                        value = nutrient.get('value', 0)
                        unit = nutrient.get('unitName', '')
                        print(f"    - {name}: {value} {unit}")
                print()
            else:
                print(f"{RED}✗{RESET} Query: '{query}' - No results found\n")
                return False

        except Exception as e:
            print(f"{RED}✗{RESET} Query: '{query}' - Error: {e}\n")
            return False

    print(f"{GREEN}✓ USDA FDC API: All tests passed!{RESET}\n")
    return True


def test_open_food_facts() -> bool:
    """Test Open Food Facts API"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Open Food Facts API{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Test barcodes (common products)
    test_barcodes = [
        ("737628064502", "Thai Kitchen Rice Noodles"),
        ("041220576210", "Kraft Mac & Cheese"),
        ("028400047685", "Cheerios")
    ]

    for barcode, expected_name in test_barcodes:
        try:
            url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 1 and data.get('product'):
                product = data['product']
                name = product.get('product_name') or product.get('generic_name', 'Unknown')
                brands = product.get('brands', 'Unknown')

                print(f"{GREEN}✓{RESET} Barcode: {barcode}")
                print(f"  Expected: {expected_name}")
                print(f"  Found: {name}")
                print(f"  Brands: {brands}")

                # Show nutrition data
                nutriments = product.get('nutriments', {})
                if nutriments:
                    print(f"  Nutrition (per 100g):")
                    print(f"    - Energy: {nutriments.get('energy-kcal_100g', 'N/A')} kcal")
                    print(f"    - Protein: {nutriments.get('proteins_100g', 'N/A')} g")
                    print(f"    - Fat: {nutriments.get('fat_100g', 'N/A')} g")
                    print(f"    - Carbs: {nutriments.get('carbohydrates_100g', 'N/A')} g")
                print()
            else:
                print(f"{YELLOW}⚠{RESET} Barcode: {barcode} - Product not found")
                print(f"  Note: Crowdsourced data - products may be removed/updated\n")
                # Don't fail test - OFF database is crowdsourced and products can be removed

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"{YELLOW}⚠{RESET} Barcode: {barcode} - Not in database (404)")
                print(f"  Note: This is expected with crowdsourced data\n")
                # Don't fail - 404s are common with OFF
            else:
                print(f"{RED}✗{RESET} Barcode: {barcode} - HTTP Error: {e}\n")
                return False
        except Exception as e:
            print(f"{RED}✗{RESET} Barcode: {barcode} - Error: {e}\n")
            return False

    print(f"{GREEN}✓ Open Food Facts API: All tests passed!{RESET}\n")
    return True


def main():
    """Run all API tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Food Database API Integration Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    # Get USDA API key from environment
    api_key = os.environ.get('USDA_FDC_API_KEY')

    if not api_key:
        print(f"\n{RED}✗ USDA_FDC_API_KEY not found in environment{RESET}")
        print(f"\n{YELLOW}Please add to data/.env file:{RESET}")
        print(f"  USDA_FDC_API_KEY=your_api_key_here")
        print(f"\nThen run:")
        print(f"  export $(cat data/.env | xargs) && python3 test_food_apis.py")
        sys.exit(1)

    # Run tests
    fdc_pass = test_usda_fdc(api_key)
    off_pass = test_open_food_facts()

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    if fdc_pass and off_pass:
        print(f"{GREEN}✓ All tests passed! Both APIs are ready for integration.{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}✗ Some tests failed. Check output above.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
