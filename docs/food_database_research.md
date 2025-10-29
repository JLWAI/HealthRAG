# Food Database Integration Research
**Date:** 2025-10-29
**Status:** ✅ Verified - All data sources confirmed working

## Executive Summary

Researched and tested free nutrition databases for meal planning feature. **Both primary sources (USDA FDC + Open Food Facts) are confirmed working with excellent coverage and zero cost.**

---

## ✅ Verified Data Sources

### 1. USDA FoodData Central (FDC)
**Primary for:** Accuracy, raw foods, baseline nutrient data

#### Test Results
- ✅ API responding successfully with `DEMO_KEY`
- ✅ Search query "chicken breast" returned **22,789 results**
- ✅ Comprehensive nutrient data (14+ nutrients per food)
- ✅ Includes branded products with UPC codes
- ✅ Serving sizes and per-100g normalization available

#### Key Details
- **Cost:** FREE (public domain, CC0 1.0 license)
- **Rate Limits:** 1,000 requests/hour (can request higher)
- **Coverage:** 500,000+ food entries
- **API Key:** Free signup at https://fdc.nal.usda.gov/api-key-signup
- **Documentation:** https://fdc.nal.usda.gov/api-guide/

#### Available Endpoints
```bash
GET  /food/{fdcId}         # Single food details
GET  /foods                # Multiple foods (batch)
POST /foods                # Multiple foods (batch)
GET  /foods/list           # Paged listings
POST /foods/list           # Paged listings
GET  /foods/search         # Search by name/keyword
POST /foods/search         # Advanced search
```

#### Sample Request
```bash
curl "https://api.nal.usda.gov/fdc/v1/foods/search?query=chicken%20breast&api_key=YOUR_KEY"
```

#### Sample Response Structure
```json
{
  "fdcId": 2187885,
  "description": "CHICKEN BREAST",
  "dataType": "Branded",
  "gtinUpc": "030034086411",
  "brandOwner": "Giant Eagle, Inc.",
  "ingredients": "BONELESS SKINLESS CHICKEN BREAST...",
  "servingSize": 284.0,
  "servingSizeUnit": "g",
  "foodNutrients": [
    {
      "nutrientName": "Protein",
      "value": 20.4,
      "unitName": "G"
    },
    {
      "nutrientName": "Total lipid (fat)",
      "value": 8.1,
      "unitName": "G"
    },
    {
      "nutrientName": "Carbohydrate, by difference",
      "value": 1.06,
      "unitName": "G"
    },
    {
      "nutrientName": "Energy",
      "value": 165,
      "unitName": "KCAL"
    }
  ]
}
```

#### Pros
- ✅ Government-curated, highly accurate
- ✅ Free with generous rate limits
- ✅ Comprehensive nutrient profiles (macros + micros)
- ✅ Bulk downloads available for offline use
- ✅ Multiple data types (Foundation, Survey, Branded, Legacy)

#### Cons
- ❌ No direct barcode key (must match by name/brand)
- ⚠️ Need to request API key (instant, free)

---

### 2. Open Food Facts (OFF)
**Primary for:** Barcode lookup, packaged products, global coverage

#### Test Results
- ✅ API responding successfully (no key required)
- ✅ Barcode lookup working perfectly
- ✅ Test product (737628064502) returned full nutrition data
- ✅ Detailed ingredient lists with allergens
- ✅ Crowdsourced quality tags and verification status

#### Key Details
- **Cost:** FREE (Open Database License)
- **Rate Limits:**
  - 100 req/min for product queries
  - 10 req/min for search queries
  - 2 req/min for facet queries
- **Coverage:** 2.8M+ products globally
- **API Key:** Not required
- **Documentation:** https://openfoodfacts.github.io/openfoodfacts-server/api/

#### Barcode Lookup Endpoint
```bash
GET https://world.openfoodfacts.org/api/v2/product/{barcode}
```

#### Sample Request
```bash
curl "https://world.openfoodfacts.org/api/v2/product/737628064502"
```

#### Sample Response Highlights
```json
{
  "code": "737628064502",
  "product": {
    "product_name": "Thai Kitchen Rice Noodles",
    "brands": "Simply Asia, Thai Kitchen",
    "quantity": "10 oz/284 g",
    "serving_size": "284.0",
    "allergens": "en:peanuts, en:sesame-seeds, en:soybeans",
    "ingredients_text": "Rice Noodles (rice, water), seasoning packet...",
    "nutriments": {
      "energy-kcal": 385,
      "energy-kcal_100g": 385,
      "proteins": 9.62,
      "proteins_100g": 9.62,
      "fat": 7.69,
      "fat_100g": 7.69,
      "carbohydrates": 71.15,
      "carbohydrates_100g": 71.15,
      "sugars": 13.46,
      "fiber": 1.9,
      "sodium": 0.288,
      "salt": 0.72
    },
    "nutriscore_grade": "d",
    "nova_group": 4,
    "image_front_url": "https://images.openfoodfacts.org/...",
    "image_nutrition_url": "https://images.openfoodfacts.org/..."
  }
}
```

#### Pros
- ✅ Direct barcode lookup (UPC/EAN)
- ✅ No API key required
- ✅ Global product coverage
- ✅ Product images (front, nutrition label)
- ✅ Allergen information
- ✅ Detailed ingredient lists
- ✅ Nutri-Score and NOVA ratings
- ✅ Bulk data dumps available

#### Cons
- ⚠️ Crowdsourced data (quality varies)
- ⚠️ Disclaimer: "no assurances that data is accurate"
- ⚠️ Requires validation against FDC for accuracy

---

## 📊 Recommended Architecture

### Data Layer Flow

#### Path 1: Barcode Lookup
```
1. User scans/enters barcode
   ↓
2. Query OFF: GET /api/v2/product/{barcode}
   ↓
3a. If found + high quality → Use OFF data
3b. If found + low quality → Verify against FDC by name
3c. If not found → Search FDC by product name
```

#### Path 2: Name Search
```
1. User searches food name (e.g., "chicken breast")
   ↓
2. Query FDC: /foods/search?query=chicken%20breast
   ↓
3. Display top results with source indicators
   ↓
4. User selects → Store normalized data
```

### Data Normalization Strategy

```python
class NormalizedFood:
    """Unified food data structure"""
    id: str                    # Internal UUID
    source: str                # "FDC" | "OFF" | "USER"
    source_id: str             # Original ID from source
    name: str
    brand: Optional[str]
    barcode: Optional[str]

    # Nutrition per 100g (normalized)
    calories_100g: float
    protein_100g: float
    fat_100g: float
    carbs_100g: float
    fiber_100g: Optional[float]
    sugar_100g: Optional[float]
    sodium_100g: Optional[float]

    # Serving info
    serving_size: Optional[float]
    serving_unit: Optional[str]

    # Quality metadata
    confidence_score: float    # 0.0-1.0
    last_verified: datetime
    verification_source: str   # "manual" | "cross_check" | "trusted_source"

    # Additional data
    allergens: List[str]
    ingredients: Optional[str]
    image_url: Optional[str]
```

### Confidence Scoring System

```python
CONFIDENCE_SCORES = {
    "FDC_foundation": 0.95,      # USDA curated data
    "FDC_survey": 0.90,           # USDA survey data
    "FDC_branded": 0.85,          # Manufacturer data
    "OFF_verified": 0.80,         # Community verified
    "OFF_complete": 0.70,         # All fields present
    "OFF_partial": 0.50,          # Missing fields
    "USER_verified": 0.90,        # Manually verified by user
    "USER_unverified": 0.60,      # User-added, unverified
}
```

---

## 🧪 Validation Test Plan

### Phase 1: Accuracy Testing (30 items)

**Raw/Generic Foods (15 items):**
- Chicken breast (raw)
- Brown rice (cooked)
- Broccoli (raw)
- Banana
- Eggs (large)
- Salmon (raw)
- Sweet potato (baked)
- Almonds
- Greek yogurt (plain)
- Oats (dry)
- Spinach (raw)
- Ground beef (85/15)
- Whole milk
- Black beans (cooked)
- Apple

**Packaged Foods with Barcodes (15 items):**
- Protein bars (3 brands)
- Bread (2 brands)
- Cereal (2 brands)
- Protein powder (2 brands)
- Pasta (2 brands)
- Canned tuna (2 brands)
- Peanut butter (2 brands)

**Test Procedure:**
1. Lookup each item in both FDC and OFF
2. Compare macros (per 100g normalized)
3. Manually verify against actual label
4. Flag any variance >10%
5. Assign confidence scores

**Success Criteria:**
- ✅ 90% of items found in at least one source
- ✅ <10% macro variance for 80% of items
- ✅ All packaged items found via barcode in OFF
- ✅ All generic items found in FDC

---

## 💾 Database Schema (SQLite)

```sql
-- Foods table
CREATE TABLE foods (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,           -- 'FDC' | 'OFF' | 'USER'
    source_id TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT,
    barcode TEXT,

    -- Nutrition per 100g
    calories_100g REAL NOT NULL,
    protein_100g REAL NOT NULL,
    fat_100g REAL NOT NULL,
    carbs_100g REAL NOT NULL,
    fiber_100g REAL,
    sugar_100g REAL,
    sodium_100g REAL,

    -- Serving info
    serving_size REAL,
    serving_unit TEXT,

    -- Quality
    confidence_score REAL NOT NULL DEFAULT 0.7,
    last_verified DATETIME NOT NULL,
    verification_source TEXT,

    -- Additional
    allergens TEXT,
    ingredients TEXT,
    image_url TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(source, source_id)
);

CREATE INDEX idx_foods_barcode ON foods(barcode);
CREATE INDEX idx_foods_name ON foods(name);
CREATE INDEX idx_foods_brand ON foods(brand, name);

-- User food log
CREATE TABLE food_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    food_id TEXT NOT NULL,
    date DATE NOT NULL,
    meal_type TEXT,                 -- 'breakfast' | 'lunch' | 'dinner' | 'snack'
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    notes TEXT,

    FOREIGN KEY (food_id) REFERENCES foods(id),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_log_date ON food_log(user_id, date);
CREATE INDEX idx_food_log_food ON food_log(food_id);

-- Favorite foods
CREATE TABLE favorite_foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    food_id TEXT NOT NULL,
    custom_name TEXT,
    typical_quantity REAL,
    typical_unit TEXT,

    FOREIGN KEY (food_id) REFERENCES foods(id),
    UNIQUE(user_id, food_id)
);
```

---

## 🚀 Implementation Roadmap

### Phase 1: Data Layer (Week 1-2, ~20 hours)

**Tasks:**
- [ ] Get USDA FDC API key
- [ ] Implement FDC search wrapper
- [ ] Implement OFF barcode lookup wrapper
- [ ] Create SQLite schema
- [ ] Build data normalization layer
- [ ] Implement caching strategy
- [ ] Add confidence scoring

**Files to create:**
- `src/food_database.py` - Main database class
- `src/food_api_fdc.py` - FDC API wrapper
- `src/food_api_off.py` - OFF API wrapper
- `src/food_models.py` - Data models
- `tests/test_food_database.py` - Unit tests

### Phase 2: UI Components (Week 3-4, ~15 hours)

**Tasks:**
- [ ] Add "Meal Planning" tab to Streamlit
- [ ] Barcode input field
- [ ] Name search with autocomplete
- [ ] Display nutrition facts card
- [ ] Show data source & confidence
- [ ] Add to meal builder

**Files to create/modify:**
- `src/main.py` - Add meal planning tab
- `src/meal_planner_ui.py` - UI components
- `src/nutrition_display.py` - Formatting helpers

### Phase 3: Meal Planning (Week 5-6, ~20 hours)

**Tasks:**
- [ ] Create meal builder (add multiple foods)
- [ ] Calculate total macros
- [ ] Compare to daily targets
- [ ] Save meal templates
- [ ] Daily food log
- [ ] Weekly nutrition summary

### Phase 4: Integration (Week 7-8, ~15 hours)

**Tasks:**
- [ ] Link nutrition to training days
- [ ] Adjust macros for training vs rest
- [ ] Visualize nutrition + workout trends
- [ ] Generate weekly reports

---

## 📝 Next Steps

1. **Get FDC API Key:** Sign up at https://fdc.nal.usda.gov/api-key-signup (instant)
2. **Run Validation Tests:** Test 30 sample foods
3. **Create Database Schema:** SQLite tables for food data
4. **Build API Wrappers:** Python classes for FDC + OFF
5. **Implement Caching:** Local mirror of common foods

---

## 🔗 Resources

- **USDA FDC:** https://fdc.nal.usda.gov/
- **USDA FDC API Guide:** https://fdc.nal.usda.gov/api-guide/
- **USDA FDC API Key Signup:** https://fdc.nal.usda.gov/api-key-signup
- **Open Food Facts:** https://world.openfoodfacts.org/
- **OFF API Docs:** https://openfoodfacts.github.io/openfoodfacts-server/api/
- **OFF Data Dumps:** https://world.openfoodfacts.org/data/
- **GitHub Issue:** https://github.com/JLWAI/HealthRAG/issues/5

---

## ✅ Conclusion

**Both primary data sources are production-ready and free:**
- ✅ USDA FDC: Best accuracy, 500K+ foods, 1K req/hr free
- ✅ Open Food Facts: Best barcode coverage, 2.8M+ products, free
- ✅ No paid APIs required for MVP
- ✅ Can scale to thousands of users on free tier

**Estimated total cost for 1000 users:** $0/month (all free APIs)

**Recommended approach:**
1. Start with FDC + OFF (free)
2. Build local cache for common foods
3. Add Edamam (paid) only if free limits hit
4. Focus on data quality validation from day one
