# USDA FoodData Central Integration

## Overview

Integrate USDA FoodData Central API to provide comprehensive food database for HealthRAG's nutrition tracking.

**API Documentation**: https://fdc.nal.usda.gov/api-guide.html

---

## API Access

### API Key
- **Free**: Signup required at https://fdc.nal.usda.gov/api-key-signup.html
- **Rate Limit**: 1000 requests/hour (free tier)
- **Cost**: Free forever

### Base URL
```
https://api.nal.usda.gov/fdc/v1/
```

---

## Key Endpoints

### 1. Search Foods
```http
GET /foods/search?api_key={key}&query=chicken%20breast&pageSize=25
```

**Response:**
```json
{
  "totalHits": 156,
  "currentPage": 1,
  "totalPages": 7,
  "foods": [
    {
      "fdcId": 171477,
      "description": "Chicken, broilers or fryers, breast, meat only, raw",
      "dataType": "SR Legacy",
      "brandName": null,
      "foodCategory": "Poultry Products",
      "foodNutrients": [
        {
          "nutrientId": 1008,
          "nutrientName": "Energy",
          "nutrientNumber": "208",
          "unitName": "kcal",
          "value": 165
        },
        {
          "nutrientId": 1003,
          "nutrientName": "Protein",
          "unitName": "g",
          "value": 31.0
        }
      ]
    }
  ]
}
```

### 2. Get Food by FDC ID
```http
GET /food/{fdcId}?api_key={key}
```

**Use Case:** Fetch detailed nutritional info after search

### 3. Get Multiple Foods
```http
GET /foods?fdcIds=171477,171478&api_key={key}
```

**Use Case:** Batch fetch for caching

---

## Nutrient IDs Reference

Key nutrients we track:

| Nutrient | ID | Unit | Field Name |
|----------|----|----|------------|
| Energy (Calories) | 1008 | kcal | calories |
| Protein | 1003 | g | protein_g |
| Carbohydrate | 1005 | g | carbs_g |
| Total Fat | 1004 | g | fat_g |
| Fiber | 1079 | g | fiber_g |
| Sugars | 2000 | g | sugar_g |
| Sodium | 1093 | mg | sodium_mg |
| Potassium | 1092 | mg | potassium_mg |
| Calcium | 1087 | mg | calcium_mg |
| Iron | 1089 | mg | iron_mg |
| Vitamin A | 1106 | mcg | vitamin_a_mcg |
| Vitamin C | 1162 | mg | vitamin_c_mg |
| Vitamin D | 1114 | mcg | vitamin_d_mcg |

---

## Integration Strategy

### Phase 1: Direct API Calls (MVP)
```
User Search → USDA API → Parse Response → Display Results
```

**Pros:** Simple, always up-to-date
**Cons:** Requires internet, rate limits, slower

### Phase 2: Local Cache (Stage 2)
```
User Search → Check SQLite Cache → If miss: USDA API → Cache Result → Display
```

**Pros:** Faster, works offline for cached foods
**Cons:** Stale data for rarely-used foods

### Phase 3: Hybrid (Stage 3)
```
Popular Foods: Pre-cached in SQLite (top 10,000 foods)
Rare Foods: Fetch from API on-demand
User Foods: Always in SQLite
```

**Recommended for production**

---

## Implementation

### Service Class Structure

```python
# src/services/usda_service.py

import os
import requests
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config.settings import USDA_API_KEY, USDA_BASE_URL
from src.models import Food, FoodAPICache

class USDAService:
    """USDA FoodData Central API integration"""

    def __init__(self, db_session: Session):
        self.api_key = USDA_API_KEY
        self.base_url = USDA_BASE_URL
        self.db = db_session
        self.cache_ttl_hours = 168  # 1 week cache

    def search_foods(
        self,
        query: str,
        page_size: int = 25,
        page_number: int = 1,
        use_cache: bool = True
    ) -> Dict:
        """Search foods via USDA API with caching"""

        # Check cache first
        if use_cache:
            cached = self._get_cached_search(query, page_number)
            if cached:
                return cached

        # Make API request
        url = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "pageNumber": page_number,
            "dataType": ["Survey (FNDDS)", "SR Legacy", "Branded"]
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Cache the result
        if use_cache:
            self._cache_search_result(query, page_number, data)

        # Parse and return
        return self._parse_search_results(data)

    def get_food_details(self, fdc_id: int) -> Optional[Food]:
        """Get detailed food info by FDC ID"""

        # Check if already in our database
        existing = self.db.query(Food).filter_by(fdc_id=fdc_id).first()
        if existing:
            return existing

        # Fetch from API
        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Parse and save to database
        food = self._parse_food_details(data)
        self.db.add(food)
        self.db.commit()

        return food

    def _parse_search_results(self, data: Dict) -> Dict:
        """Parse USDA search response into our format"""

        foods = []
        for item in data.get("foods", []):
            nutrients = {n["nutrientName"]: n["value"]
                        for n in item.get("foodNutrients", [])}

            foods.append({
                "fdc_id": item["fdcId"],
                "name": item["description"],
                "brand": item.get("brandName"),
                "calories": nutrients.get("Energy", 0),
                "protein_g": nutrients.get("Protein", 0),
                "carbs_g": nutrients.get("Carbohydrate, by difference", 0),
                "fat_g": nutrients.get("Total lipid (fat)", 0),
                "serving_size_g": 100,  # USDA data is per 100g
                "data_source": "usda"
            })

        return {
            "total": data["totalHits"],
            "page": data["currentPage"],
            "total_pages": data["totalPages"],
            "results": foods
        }

    def _parse_food_details(self, data: Dict) -> Food:
        """Parse detailed food data into Food model"""

        nutrients = {}
        for nutrient in data.get("foodNutrients", []):
            nutrients[nutrient["nutrient"]["id"]] = nutrient.get("amount", 0)

        return Food(
            fdc_id=data["fdcId"],
            name=data["description"],
            brand=data.get("brandName"),
            calories=nutrients.get(1008, 0),  # Energy
            protein_g=nutrients.get(1003, 0),
            carbs_g=nutrients.get(1005, 0),
            fat_g=nutrients.get(1004, 0),
            fiber_g=nutrients.get(1079, 0),
            sugar_g=nutrients.get(2000, 0),
            sodium_mg=nutrients.get(1093, 0),
            potassium_mg=nutrients.get(1092, 0),
            calcium_mg=nutrients.get(1087, 0),
            iron_mg=nutrients.get(1089, 0),
            vitamin_a_mcg=nutrients.get(1106, 0),
            vitamin_c_mg=nutrients.get(1162, 0),
            vitamin_d_mcg=nutrients.get(1114, 0),
            serving_size_g=100,
            serving_size_unit="g",
            data_source="usda",
            is_verified=True
        )

    def _get_cached_search(self, query: str, page: int) -> Optional[Dict]:
        """Check cache for search results"""

        cache_key = f"search:{query}:page:{page}"

        cache_entry = self.db.query(FoodAPICache).filter_by(
            cache_key=cache_key
        ).first()

        if cache_entry and cache_entry.expires_at > datetime.utcnow():
            return cache_entry.response_data

        return None

    def _cache_search_result(self, query: str, page: int, data: Dict):
        """Cache search results"""

        cache_key = f"search:{query}:page:{page}"

        expires_at = datetime.utcnow() + timedelta(hours=self.cache_ttl_hours)

        cache_entry = FoodAPICache(
            cache_key=cache_key,
            cache_type="search_result",
            response_data=data,
            expires_at=expires_at
        )

        self.db.merge(cache_entry)
        self.db.commit()

    def bulk_import_popular_foods(self, fdc_ids: List[int]):
        """Pre-populate database with popular foods"""

        for fdc_id in fdc_ids:
            try:
                self.get_food_details(fdc_id)
                print(f"Imported FDC {fdc_id}")
            except Exception as e:
                print(f"Failed to import FDC {fdc_id}: {e}")
```

---

## OpenFoodFacts Integration (Barcode Lookup)

### Overview
OpenFoodFacts is a free, open database of food products with barcode support.

**API Documentation**: https://world.openfoodfacts.org/data

### Barcode Lookup
```http
GET https://world.openfoodfacts.org/api/v2/product/{barcode}.json
```

**Example:**
```http
GET https://world.openfoodfacts.org/api/v2/product/038000845406.json
```

**Response:**
```json
{
  "code": "038000845406",
  "product": {
    "product_name": "Cheerios",
    "brands": "General Mills",
    "nutriments": {
      "energy-kcal_100g": 367,
      "proteins_100g": 10,
      "carbohydrates_100g": 73,
      "fat_100g": 6.7,
      "fiber_100g": 10,
      "sodium_100g": 0.75
    },
    "serving_size": "28 g"
  }
}
```

### Integration
```python
# src/services/barcode_service.py

class BarcodeService:
    """OpenFoodFacts barcode lookup"""

    def lookup_barcode(self, barcode: str) -> Optional[Dict]:
        """Look up food by barcode"""

        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

        response = requests.get(url)
        if response.status_code != 200:
            return None

        data = response.json()

        if data["status"] != 1:
            return None

        product = data["product"]
        nutrients = product.get("nutriments", {})

        return {
            "barcode": barcode,
            "name": product.get("product_name"),
            "brand": product.get("brands"),
            "calories": nutrients.get("energy-kcal_100g", 0),
            "protein_g": nutrients.get("proteins_100g", 0),
            "carbs_g": nutrients.get("carbohydrates_100g", 0),
            "fat_g": nutrients.get("fat_100g", 0),
            "fiber_g": nutrients.get("fiber_100g", 0),
            "serving_size_g": 100,
            "data_source": "openfoodfacts"
        }
```

---

## Popular Foods Pre-Population

### Top 1000 Foods List

Create a curated list of most commonly tracked foods:

**Categories:**
- Proteins: Chicken breast, eggs, salmon, tuna, beef, etc.
- Carbs: Rice, oats, bread, pasta, potatoes, etc.
- Vegetables: Broccoli, spinach, carrots, etc.
- Fruits: Banana, apple, berries, etc.
- Dairy: Milk, yogurt, cheese, etc.
- Fats: Olive oil, nuts, avocado, etc.

**Script:**
```python
# scripts/populate_popular_foods.py

from src.services.usda_service import USDAService
from src.database import get_db

# Top 1000 FDC IDs (curated list)
POPULAR_FOODS = [
    171477,  # Chicken breast
    173424,  # Eggs
    175167,  # White rice
    # ... 997 more
]

def populate_foods():
    db = next(get_db())
    service = USDAService(db)

    print(f"Importing {len(POPULAR_FOODS)} popular foods...")
    service.bulk_import_popular_foods(POPULAR_FOODS)
    print("Done!")

if __name__ == "__main__":
    populate_foods()
```

---

## Configuration

### Environment Variables

```bash
# config/settings.py or .env

USDA_API_KEY=your_api_key_here
USDA_BASE_URL=https://api.nal.usda.gov/fdc/v1
USDA_RATE_LIMIT=1000  # requests per hour
USDA_CACHE_TTL_HOURS=168  # 1 week
```

---

## Error Handling

### Rate Limiting
```python
import time
from functools import wraps

def rate_limit_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(e.response.headers.get("Retry-After", 60))
                print(f"Rate limit hit. Retrying after {retry_after}s")
                time.sleep(retry_after)
                return func(*args, **kwargs)
            raise
    return wrapper
```

### Fallback Strategy
1. Try USDA API
2. If fails, try OpenFoodFacts (for branded foods)
3. If fails, allow user to create custom food entry

---

## Testing

### Mock API Responses
```python
# tests/test_usda_service.py

import pytest
from unittest.mock import Mock, patch
from src.services.usda_service import USDAService

def test_search_foods():
    mock_response = {
        "totalHits": 1,
        "currentPage": 1,
        "foods": [{
            "fdcId": 171477,
            "description": "Chicken, breast",
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 165}
            ]
        }]
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response

        service = USDAService(mock_db)
        results = service.search_foods("chicken breast")

        assert results["total"] == 1
        assert results["results"][0]["name"] == "Chicken, breast"
```

---

## Next Steps

1. Sign up for USDA API key
2. Implement `USDAService` class
3. Implement `BarcodeService` class
4. Create popular foods list
5. Add FastAPI endpoints that use these services
6. Build Streamlit UI for food search
7. Add caching layer
8. Create pre-population script

---

## Resources

- **USDA FoodData Central**: https://fdc.nal.usda.gov/
- **API Docs**: https://fdc.nal.usda.gov/api-guide.html
- **OpenFoodFacts**: https://world.openfoodfacts.org/
- **Nutrient Database**: https://fdc.nal.usda.gov/download-datasets.html
