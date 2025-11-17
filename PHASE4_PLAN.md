# Phase 4: Nutrition Tracking & Adaptive TDEE
**Goal:** Build MacroFactor-quality nutrition tracking ($11.99/month value) using 100% free data

**Timeline:** 6 weeks (10-20 hours/week)
**Total Effort:** ~60-90 hours
**Value Created:** $144/year in subscription savings + integrated training

---

## Week 9: Food Database Foundation (15-20 hours)

### Day 1-2: Database Schema & Core Architecture (5-6 hours)
**Tasks:**
- [x] Create `src/nutrition_database.py` with SQLite schema
- [x] Define normalized food data model (FDC, OFF, custom foods)
- [x] Add full-text search indexes
- [x] Create migration scripts
- [x] Write validation tests

**Deliverable:** Empty database with proper schema, ready for import

**Files Created:**
- `src/nutrition_database.py` - Database schema and core queries
- `src/food_models.py` - Data models (Food, FoodEntry, DailyNutrition)
- `tests/test_nutrition_database.py` - Schema validation tests

### Day 3-4: USDA FDC Integration (4-5 hours)
**Tasks:**
- [ ] Download FDC bulk data (~2GB)
  - Foundation Foods: ~1,000 core items
  - SR Legacy: ~8,000 items
  - Branded Foods: ~400,000 items
- [ ] Create ETL script `scripts/import_fdc_data.py`
- [ ] Parse JSON → SQLite with proper normalization
- [ ] Build FDC search function (name, brand, category)
- [ ] Validate 30 items against USDA website

**Deliverable:** ~400K USDA foods searchable in local database

**Download URLs:**
```bash
# Foundation Foods (core reference data)
wget https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2024-10-31.zip

# SR Legacy (legacy standard reference)
wget https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2024-10-31.zip

# Branded Foods (packaged products)
wget https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_branded_food_json_2024-10-31.zip
```

### Day 5-7: Open Food Facts Integration (6-8 hours)
**Tasks:**
- [ ] Download OFF bulk dump (~30GB compressed → ~100GB uncompressed)
- [ ] Create ETL script `scripts/import_off_data.py`
- [ ] Parse JSONL → SQLite (barcode, name, nutrition)
- [ ] Build barcode lookup function
- [ ] Build name search function
- [ ] Validate 30 barcodes against OFF website

**Deliverable:** ~2.8M products with barcode lookup capability

**Download Strategy:**
```bash
# Option 1: Full dump (30GB compressed)
wget https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz

# Option 2: Smaller subset for testing (recommended for MVP)
# Download only complete, verified products
# Filter: nutrition_grade exists, completeness > 0.8
# Result: ~500K high-quality products instead of 2.8M
```

**Time-Saving Strategy:** Start with 500K high-quality products instead of full 2.8M dump. Can always expand later.

### Week 9 Deliverables:
✅ SQLite database with normalized schema
✅ ~400K USDA foods (FDC)
✅ ~500K packaged products with barcodes (OFF)
✅ Search functions: by name, brand, barcode, category
✅ Full-text search working
✅ 60-item validation test passing

---

## Week 10: Food Logging UI (12-15 hours)

### Day 1-2: Core Food Search UI (4-5 hours)
**Tasks:**
- [ ] Create `src/food_search.py` with search logic
- [ ] Add Streamlit food search interface
- [ ] Autocomplete dropdown (top 20 results)
- [ ] Display: name, brand, calories, protein per serving
- [ ] Quick-add button → log to database
- [ ] Search history (recent searches)

**UI Mock:**
```python
st.text_input("Search food...", key="food_search")
# Shows results as you type
# Click → Add serving size → Log
```

### Day 3-4: Barcode Scan + Manual Entry (4-5 hours)
**Tasks:**
- [ ] Add camera input for barcode scan
- [ ] Decode barcode using `pyzbar` library
- [ ] Lookup barcode in local database
- [ ] Fallback to OFF live API if not found
- [ ] Manual entry form for unlisted foods
- [ ] Save custom foods to user database

**Libraries Needed:**
```bash
pip install pyzbar pillow opencv-python
```

**UI Flow:**
```
1. User scans barcode with camera
2. Decode barcode → 737628064502
3. Search local DB → Found! "Quest Bar - Chocolate Chip"
4. Show nutrition → User confirms serving size → Log
```

### Day 5-7: Daily Log View + Macro Totals (4-5 hours)
**Tasks:**
- [ ] Daily food log interface (meal-based)
  - Breakfast / Lunch / Dinner / Snacks
- [ ] Display logged foods with macros
- [ ] Running totals (calories, protein, carbs, fat)
- [ ] Target vs. actual comparison
- [ ] Edit/delete logged entries
- [ ] Copy yesterday's meals (quick re-log)

**UI Mock:**
```
📅 Today: October 28, 2025

🍳 BREAKFAST (450 cal, 35g protein)
- Eggs (3 large): 210 cal, 18g protein
- Oatmeal (1 cup): 150 cal, 5g protein
- Protein shake: 90 cal, 12g protein
[+ Add Food]

🥗 LUNCH (0 cal, 0g protein)
[+ Add Food]

📊 DAILY TOTALS
Calories: 450 / 2,000 (23%)
Protein: 35g / 180g (19%)
Carbs: 45g / 200g
Fat: 15g / 65g
```

### Week 10 Deliverables:
✅ Food search UI (name search + autocomplete)
✅ Barcode scanning working
✅ Manual food entry for unlisted items
✅ Daily food log with meal breakdown
✅ Macro totals display
✅ Recent foods quick-add
✅ Custom foods saved to user database

---

## Week 11-12: Adaptive TDEE Algorithm (16-20 hours)

### Week 11 Day 1-3: EWMA Trend Weight (6-8 hours)
**Tasks:**
- [ ] Create `src/adaptive_tdee.py` with AdaptiveTDEE class
- [ ] Implement EWMA smoothing algorithm
  - Alpha = 0.3 (MacroFactor-style)
- [ ] Daily weight logging UI
- [ ] 7-day moving average calculation
- [ ] Weight trend graph (Plotly)
  - Daily weights (scatter)
  - Trend weight (smoothed line)
- [ ] Validate algorithm against MacroFactor sample data

**Algorithm:**
```python
def calculate_trend_weight(daily_weights: List[float]) -> List[float]:
    """
    Exponentially Weighted Moving Average.

    MacroFactor uses alpha ≈ 0.25-0.35
    Lower = smoother (less reactive)
    Higher = faster adaptation
    """
    alpha = 0.3
    trend = [daily_weights[0]]

    for weight in daily_weights[1:]:
        new_trend = (alpha * weight) + ((1 - alpha) * trend[-1])
        trend.append(new_trend)

    return trend
```

### Week 11 Day 4-7: TDEE Calculation (6-8 hours)
**Tasks:**
- [ ] Implement back-calculation TDEE algorithm
- [ ] Formula: `TDEE = Avg_Calories + (Weight_Change × 3500 / Days)`
- [ ] Rolling 14-day window
- [ ] TDEE trend graph
- [ ] Validate against known examples
- [ ] Write comprehensive tests

**Example Calculation:**
```python
# 14-day window
# Trend weight: 210.0 → 208.5 lbs (-1.5 lbs)
# Average intake: 1,825 cal/day

weight_change_lbs = -1.5
energy_delta_per_day = (weight_change_lbs * 3500) / 14
# = -375 cal/day deficit

tdee = avg_calories - energy_delta_per_day
# = 1825 - (-375) = 2,200 cal/day
```

### Week 12 Day 1-4: Weekly Macro Adjustments (4-6 hours)
**Tasks:**
- [ ] Implement adherence-neutral adjustment logic
- [ ] Compare actual vs. goal rate of change
- [ ] Adjustment thresholds:
  - Within ±20% → No change
  - Outside ±50% → ±150 cal adjustment
  - Otherwise → ±100 cal adjustment
- [ ] Weekly check-in UI
- [ ] Coaching explanations
- [ ] Test with multiple scenarios (cutting, bulking, recomp)

**Logic:**
```python
def adjust_macros_weekly(
    current_target: float,
    goal_rate_lbs_per_week: float,
    actual_rate_lbs_per_week: float,
    tolerance: float = 0.2
) -> Tuple[float, str]:
    """
    MacroFactor-style adherence-neutral adjustment.

    Example:
    Goal: -1.0 lb/week (cutting)
    Actual: -0.4 lb/week (too slow)
    Result: -100 cal (increase deficit)
    """
    variance = (actual_rate - goal_rate) / abs(goal_rate)

    if abs(variance) <= tolerance:
        return current_target, "On track! No changes needed."

    if actual_rate < goal_rate:  # Losing/gaining too fast
        adjustment = 150 if abs(variance) > 0.5 else 100
        return current_target + adjustment, f"Add {adjustment} cal to slow down"
    else:  # Losing/gaining too slow
        adjustment = 150 if abs(variance) > 0.5 else 100
        return current_target - adjustment, f"Cut {adjustment} cal to speed up"
```

### Week 11-12 Deliverables:
✅ Daily weight logging + trend calculation
✅ Weight graph (daily + trend line)
✅ TDEE calculation (14-day rolling window)
✅ TDEE trend graph
✅ Weekly macro adjustment algorithm
✅ Weekly check-in UI with recommendations
✅ Coaching explanations for adjustments

---

## Week 13-14: Adaptive Coaching System (12-15 hours)

### Week 13: Proactive Recommendations (6-8 hours)
**Tasks:**
- [ ] Create `src/coaching_engine.py`
- [ ] Detect scenarios:
  - Weight plateau (2+ weeks no change)
  - Losing too fast (>1.5 lb/week on cut)
  - Gaining too slow (<0.5 lb/week on bulk)
  - Adherence issues (actual < 80% of target)
- [ ] Generate contextual recommendations
- [ ] Weekly summary reports
- [ ] Progress milestones (10 lbs lost, etc.)

**Coaching Examples:**
```
🎯 WEEKLY CHECK-IN - Week 8

📊 WEIGHT PROGRESS
Trend: 185.2 lbs → 184.1 lbs (-1.1 lbs this week)
Goal: -1.0 lb/week
Status: ✅ ON TRACK!

💡 RECOMMENDATION
Great work! Your weight loss rate is perfect.
No changes needed this week. Keep doing what you're doing!

🍽️ NUTRITION ADHERENCE
Average intake: 1,847 cal/day (target: 1,800)
Adherence: 97% ✅

💪 STRENGTH PROGRESS
Bench Press: +5 lbs this week 🎉
You're maintaining strength while cutting - excellent!
```

### Week 14: Advanced Features (6-7 hours)
**Tasks:**
- [ ] Add body measurement tracking (waist, chest, arms)
- [ ] Body composition estimates (waist-to-height ratio)
- [ ] Progress photos upload
- [ ] Monthly progress reports
- [ ] Export nutrition data (CSV, Excel)
- [ ] Diet break recommendations (after 8-12 weeks cutting)

### Week 13-14 Deliverables:
✅ Proactive coaching system operational
✅ Weekly check-in summaries
✅ Automatic macro adjustments
✅ Scenario detection (plateau, too fast, too slow)
✅ Body measurement tracking
✅ Progress reports
✅ Export functionality

---

## Success Metrics

**By End of Week 14:**

### Features Complete:
- ✅ Food database: ~900K foods (400K FDC + 500K OFF)
- ✅ Search: Name, brand, barcode, category
- ✅ Logging: Daily meals, macros, quick-add
- ✅ TDEE: Adaptive calculation (MacroFactor algorithm)
- ✅ Coaching: Weekly check-ins, auto-adjustments
- ✅ Graphs: Weight trend, TDEE, calories, macros

### Quality Checks:
- [ ] Food search returns results in <500ms
- [ ] Barcode lookup works for 95%+ of common products
- [ ] TDEE calculation matches MacroFactor within ±50 cal
- [ ] Weekly adjustments are accurate and helpful
- [ ] UI is responsive and intuitive

### User Experience:
- Daily logging takes <2 minutes
- Weekly check-in takes <5 minutes
- Coaching feels personalized and helpful
- No confusion about what to do next

---

## Time Budget Breakdown

| Week | Focus | Hours | Cumulative |
|------|-------|-------|------------|
| Week 9 | Database setup | 15-20 | 15-20 |
| Week 10 | Food logging UI | 12-15 | 27-35 |
| Week 11 | TDEE algorithm | 8-10 | 35-45 |
| Week 12 | Macro adjustments | 8-10 | 43-55 |
| Week 13 | Coaching system | 6-8 | 49-63 |
| Week 14 | Polish & testing | 6-7 | 55-70 |

**Total: 55-70 hours over 6 weeks**
**Average: 9-12 hours/week (fits your 10-20 hr/week schedule)**

---

## Risk Mitigation

### Risk 1: OFF Data Too Large (30GB)
**Mitigation:** Start with 500K high-quality subset instead of full 2.8M dump

### Risk 2: Barcode Scanning Doesn't Work Well
**Mitigation:** Manual entry + name search as primary, barcode as "nice-to-have"

### Risk 3: TDEE Algorithm Too Complex
**Mitigation:** Use proven MacroFactor algorithm from NUTRITION_DATA_ARCHITECTURE.md

### Risk 4: Takes Longer Than 6 Weeks
**Mitigation:** MVP approach - core features first, polish later

---

## MVP vs. Full Feature Set

### MVP (Weeks 9-12) - 40 hours
**Core Features:**
- ✅ Food search (name only, no barcode)
- ✅ Manual logging
- ✅ Daily macro totals
- ✅ Weight tracking + trend
- ✅ Basic TDEE calculation
- ✅ Manual macro adjustments

**Value:** Replaces MyFitnessPal + basic TDEE tracking

### Full (Weeks 9-14) - 70 hours
**Everything Above Plus:**
- ✅ Barcode scanning
- ✅ Automatic TDEE calculation
- ✅ Weekly coaching recommendations
- ✅ Body measurements
- ✅ Progress reports

**Value:** Replaces MacroFactor ($144/year) + integrated training

---

## Next Steps

1. **Review this plan** - Any questions or adjustments?
2. **Start Week 9 Day 1-2** - Create database schema
3. **Daily progress updates** - Commit code daily for momentum
4. **Weekly check-ins** - Review progress, adjust timeline if needed

**Ready to start?** I'll create the database schema and kick off Week 9 Day 1.
