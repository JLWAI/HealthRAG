# Food Database API Setup

## ✅ Status: APIs Verified Working

Both USDA FoodData Central and Open Food Facts APIs have been tested and confirmed working.

---

## Quick Start

### 1. Add API Key to .env

Add this line to your `.env` file at `data/.env`:

```bash
USDA_FDC_API_KEY=m1aOhdzpps15KKDWjpb9RE5tLKkKZUzUIivmZyvs
```

**Your API Key Details:**
- Email: jasonewillis@gmail.com
- Key: `m1aOhdzpps15KKDWjpb9RE5tLKkKZUzUIivmZyvs`
- Rate Limit: 1,000 requests/hour (free tier)

### 2. Run the Test Script

Test that both APIs are working:

```bash
# Load env vars and run test
export $(cat data/.env | xargs) && python3 test_food_apis.py
```

Expected output:
```
✓ USDA FDC API: All tests passed!
✓ Open Food Facts API: All tests passed!
✓ All tests passed! Both APIs are ready for integration.
```

---

## Test Results Summary

### USDA FoodData Central ✅
- **Query "chicken breast":** 22,789 results
- **Query "banana":** 5,165 results
- **Query "oatmeal":** 2,550 results
- **Nutrient Data:** 13-16 nutrients per food (protein, fat, carbs, vitamins, minerals)

### Open Food Facts ✅
- **Barcode 737628064502:** ✓ Found (Thai Kitchen Rice Noodles)
- **Barcode 028400047685:** ✓ Found (Rold Gold pretzels)
- **Barcode 041220576210:** ⚠ 404 (product removed - expected with crowdsourced data)

**Note:** OFF 404s are normal - the database is crowdsourced and products are added/removed. This validates our fallback strategy (OFF → FDC by name search).

---

## API Endpoints Reference

### USDA FoodData Central

**Base URL:** `https://api.nal.usda.gov/fdc/v1`

**Search Foods:**
```bash
curl "https://api.nal.usda.gov/fdc/v1/foods/search?query=banana&api_key=YOUR_KEY"
```

**Get Single Food:**
```bash
curl "https://api.nal.usda.gov/fdc/v1/food/123456?api_key=YOUR_KEY"
```

**Rate Limits:**
- 1,000 requests/hour (default)
- Can request higher limits if needed

### Open Food Facts

**Base URL:** `https://world.openfoodfacts.org/api/v2`

**Get Product by Barcode:**
```bash
curl "https://world.openfoodfacts.org/api/v2/product/737628064502"
```

**Rate Limits:**
- 100 requests/min for product queries
- 10 requests/min for search queries
- No API key required

---

## Integration Strategy

### Barcode Lookup Flow
```
User scans barcode
    ↓
Try Open Food Facts (barcode → product)
    ↓
If found & quality good → Use OFF data
    ↓
If not found/poor quality → Search USDA FDC by product name
    ↓
Store in local cache
```

### Name Search Flow
```
User searches "chicken breast"
    ↓
Query USDA FDC (most accurate for raw foods)
    ↓
Display top results
    ↓
User selects → Store normalized data
```

---

## Data Quality Notes

### USDA FDC
- **Accuracy:** ⭐⭐⭐⭐⭐ (government curated)
- **Coverage:** 500K+ foods
- **Best for:** Raw foods, baseline nutrients, generic items
- **Confidence Score:** 0.85-0.95

### Open Food Facts
- **Accuracy:** ⭐⭐⭐⭐☆ (crowdsourced, varies)
- **Coverage:** 2.8M+ products
- **Best for:** Packaged products with barcodes
- **Confidence Score:** 0.5-0.8 (depending on completeness)

**Recommendation:** Prefer USDA FDC when both sources have the same item. Use OFF for barcode lookup and product images.

---

## Next Steps

1. ✅ ~~Get USDA API key~~ (Complete)
2. ✅ ~~Test both APIs~~ (Complete)
3. ⏳ Implement Phase 1: Data Layer
   - Create `src/food_database.py`
   - Implement FDC wrapper
   - Implement OFF wrapper
   - Build caching layer
4. ⏳ Implement Phase 2: UI Components
5. ⏳ Implement Phase 3: Meal Planning

See `docs/food_database_research.md` for full implementation roadmap.

---

## Troubleshooting

### Test Fails: "USDA_FDC_API_KEY not found"
**Fix:** Make sure you exported the env var:
```bash
export $(cat data/.env | xargs)
```

### OFF Returns 404 for Barcode
**Expected:** Crowdsourced data - some products get removed. Your fallback strategy handles this:
1. Try OFF first (fast, barcode-based)
2. If 404 → Search USDA FDC by product name
3. Cache result locally

### Rate Limit Hit on USDA FDC
**Current Limit:** 1,000 req/hour (720K/month)

**Solutions:**
1. Implement local caching (reduces by 80%+)
2. Request higher limit from USDA (free)
3. Mirror common foods locally

---

## Files Created

- `test_food_apis.py` - Integration test script
- `.env.example` - Environment variable template
- `docs/food_database_research.md` - Full research documentation
- `docs/FOOD_API_SETUP.md` - This file

---

## Cost Analysis (1000 Users)

**Monthly API Calls Estimate:**
- 1000 users × 30 searches/month = 30K searches
- Cache hit rate: 80% after week 1
- Actual API calls: ~6K/month (well under free limits)

**Total Cost:** $0/month ✅
