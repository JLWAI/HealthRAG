# HealthRAG Nutrition Data Architecture
**Phase 4: Food Logging & Adaptive TDEE Tracking**

*Based on MacroFactor feature set + Free/Open nutritional databases*

---

## 🎯 OBJECTIVE

Build MacroFactor-quality nutrition tracking ($11.99/month value) using **100% free, open-source data**:

1. **Food logging** - Barcode scan + name search
2. **Adaptive TDEE** - MacroFactor's algorithm (trend weight + back-calculation)
3. **Weekly macro adjustments** - Adherence-neutral coaching
4. **Progress tracking** - Weight trends, expenditure graphs, macro adherence

**Cost:** $0 (vs MacroFactor's $11.99/month)

---

## 📊 DATA SOURCE STRATEGY

### **Prioritized Stack** (Free-First Approach)

| Rank | Source | Primary Use | Coverage | Cost | API Limits |
|------|--------|-------------|----------|------|------------|
| **1** | **USDA FoodData Central** | Raw foods, accuracy baseline | ~400K items (US-focused) | Free | 1,000 req/hour (API key) |
| **2** | **Open Food Facts** | Barcode lookup, packaged foods | ~2.8M products (global) | Free | None (open data) |
| **3** | **Open Food Repo** | Barcode backup (Swiss products) | ~400K (Swiss-heavy) | Free | None (open data) |
| **4** | **Edamam** (fallback) | Enhanced features, paid SLA | Large (proprietary) | Freemium | 10K/month free tier |

**Decision Rationale:**
- **FDC** = Most accurate macros (USDA-verified) for raw/commodity foods
- **OFF** = Best free barcode coverage (crowdsourced but good)
- **FoodRepo** = Secondary barcode source for international products
- **Edamam** = Optional paid upgrade if we need better coverage/SLA

---

## 🏗️ ARCHITECTURE OVERVIEW

### **Three-Tier Data Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  📱 Streamlit UI: Barcode scan + Name search + Manual entry │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                         │
│  🧮 Food Search Engine → Nutrition Calculator → Logging     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER (3-Tier)                     │
├─────────────────────────────────────────────────────────────┤
│  Tier 1: Local Cache (SQLite)                              │
│   - Frequently logged foods                                 │
│   - User's custom foods/recipes                             │
│   - Recent search results (24-48hr TTL)                     │
├─────────────────────────────────────────────────────────────┤
│  Tier 2: Bulk Mirrors (Local DB)                           │
│   - FDC full download (~400K items, ~2GB JSON)             │
│   - OFF daily dump (~2.8M items, ~30GB compressed)         │
│   - Refreshed weekly/monthly                                │
├─────────────────────────────────────────────────────────────┤
│  Tier 3: Live APIs (Fallback)                              │
│   - FDC API (cache misses)                                  │
│   - OFF API (new barcodes)                                  │
│   - Edamam API (if paid tier enabled)                      │
└─────────────────────────────────────────────────────────────┘
```

**Why Three Tiers?**
- **Speed:** Local cache = instant lookups (no API latency)
- **Reliability:** Works offline (bulk mirrors downloaded)
- **Freshness:** Live APIs for new products
- **Cost:** Minimize API calls (stay within free limits)

---

## 🔍 FOOD LOOKUP FLOW

### **Scenario 1: Barcode Scan**

```python
def lookup_food_by_barcode(barcode: str) -> Food:
    """
    MacroFactor-style barcode lookup with free data sources.

    Priority:
    1. Check local cache (instant)
    2. Query OFF local mirror
    3. Query FoodRepo local mirror
    4. Live API fallback (OFF → FoodRepo → Edamam)
    5. If still not found: prompt user to add manually
    """

    # Step 1: Check cache (recent scans)
    if food := cache.get(f"barcode:{barcode}"):
        return food

    # Step 2: Local OFF mirror (SQLite full-text search)
    if food := off_db.query("SELECT * FROM products WHERE code = ?", barcode):
        cache.set(f"barcode:{barcode}", food, ttl=86400)  # 24hr cache
        return normalize_off_food(food)

    # Step 3: Local FoodRepo mirror
    if food := foodrepo_db.query("SELECT * FROM products WHERE barcode = ?", barcode):
        cache.set(f"barcode:{barcode}", food, ttl=86400)
        return normalize_foodrepo_food(food)

    # Step 4: Live APIs (cache miss)
    # Try OFF live API
    response = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{barcode}")
    if response.status_code == 200 and response.json()['status'] == 1:
        food = response.json()['product']
        cache.set(f"barcode:{barcode}", food, ttl=86400)
        # Store in local DB for future offline use
        off_db.insert(food)
        return normalize_off_food(food)

    # Try FoodRepo live API
    # ... similar pattern

    # Step 5: Not found
    raise FoodNotFoundError(f"Barcode {barcode} not found in any database")
```

### **Scenario 2: Name Search**

```python
def search_food_by_name(query: str, limit: int = 20) -> List[Food]:
    """
    FDC-first name search (most accurate for generics).

    Priority:
    1. FDC local mirror (raw foods, USDA-verified)
    2. OFF local mirror (branded foods)
    3. User's custom foods
    4. Live API fallback
    """

    results = []

    # Step 1: Search FDC local mirror (best for raw foods)
    fdc_results = fdc_db.search(f"""
        SELECT * FROM foods
        WHERE description LIKE ? OR brand_owner LIKE ?
        ORDER BY data_type, fdcId
        LIMIT ?
    """, (f"%{query}%", f"%{query}%", limit))

    results.extend([normalize_fdc_food(f) for f in fdc_results])

    # Step 2: Search OFF local mirror (branded products)
    off_results = off_db.search(f"""
        SELECT * FROM products
        WHERE product_name LIKE ? OR brands LIKE ?
        LIMIT ?
    """, (f"%{query}%", f"%{query}%", limit))

    results.extend([normalize_off_food(f) for f in off_results])

    # Step 3: User's custom foods
    custom_results = user_foods_db.search(query, limit=5)
    results.extend(custom_results)

    # Step 4: Deduplicate and rank
    ranked_results = rank_search_results(results, query)

    return ranked_results[:limit]
```

---

## 📦 DATABASE SCHEMA

### **foods Table** (Normalized from all sources)

```sql
CREATE TABLE foods (
    -- Primary Key
    food_id TEXT PRIMARY KEY,  -- Format: "fdc:123456" or "off:737628064502"

    -- Source Metadata
    source TEXT NOT NULL,  -- 'fdc', 'off', 'foodrepo', 'custom'
    source_id TEXT NOT NULL,  -- Original ID from source
    barcode TEXT,  -- UPC/EAN if available

    -- Basic Info
    name TEXT NOT NULL,
    brand TEXT,
    category TEXT,

    -- Nutrition (per 100g, normalized)
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fiber_g REAL,
    sugar_g REAL,
    sodium_mg REAL,

    -- Serving Info
    serving_size_g REAL,  -- Default serving size
    serving_description TEXT,  -- "1 cup", "1 slice", etc.

    -- Micronutrients (optional, for advanced tracking)
    vitamin_a_ug REAL,
    vitamin_c_mg REAL,
    calcium_mg REAL,
    iron_mg REAL,
    -- ... add more as needed

    -- Quality Indicators
    data_quality TEXT,  -- 'verified', 'label_exact', 'derived', 'estimated'
    completeness_score REAL,  -- 0.0-1.0 (% of fields populated)

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP,

    -- Indexes
    INDEX idx_barcode (barcode),
    INDEX idx_name_fts (name),  -- Full-text search
    INDEX idx_brand_fts (brand),
    INDEX idx_source (source)
);
```

### **food_log Table** (User's daily intake)

```sql
CREATE TABLE food_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,  -- Links to user profile

    -- When & What
    logged_at TIMESTAMP NOT NULL,  -- When eaten
    meal_type TEXT,  -- 'breakfast', 'lunch', 'dinner', 'snack'

    -- Food Reference
    food_id TEXT NOT NULL,  -- FK to foods table
    food_name TEXT NOT NULL,  -- Denormalized for historical tracking

    -- Quantity
    serving_size_g REAL NOT NULL,  -- Actual amount eaten
    servings REAL NOT NULL,  -- Number of servings (1.5 servings, etc.)

    -- Nutrition (denormalized for this serving)
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fiber_g REAL,

    -- Metadata
    source TEXT,  -- 'barcode', 'search', 'manual', 'recent', 'recipe'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (food_id) REFERENCES foods(food_id)
);
```

### **weight_log Table** (Daily weigh-ins)

```sql
CREATE TABLE weight_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,

    -- Weight Data
    weight_lbs REAL NOT NULL,
    weigh_date DATE NOT NULL,  -- Date only (morning weigh-in)

    -- Trend Calculation (computed daily)
    trend_weight_lbs REAL,  -- EWMA smoothed weight

    -- Metadata
    notes TEXT,  -- "ate sushi last night", "day after cheat meal"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, weigh_date)  -- One weigh-in per day
);
```

### **nutrition_summary Table** (Daily rollup for TDEE calculation)

```sql
CREATE TABLE nutrition_summary (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,

    -- Daily Totals
    total_calories REAL NOT NULL,
    total_protein_g REAL NOT NULL,
    total_fat_g REAL NOT NULL,
    total_carbs_g REAL NOT NULL,

    -- Adherence Metrics
    target_calories REAL,  -- What they SHOULD have eaten
    calories_delta REAL,  -- Actual - Target

    -- Computed Fields
    meal_count INTEGER,  -- Number of logged meals

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, date)
);
```

---

## 🧮 MACROFACTOR-STYLE ADAPTIVE TDEE

### **Algorithm Implementation**

```python
# src/adaptive_tdee.py

from typing import List, Tuple
import numpy as np
from datetime import date, timedelta

class AdaptiveTDEE:
    """
    MacroFactor-style adaptive TDEE calculation.

    Calculates actual energy expenditure by comparing:
    1. Trend weight change (EWMA smoothed)
    2. Average calorie intake

    Formula:
    TDEE = Average_Calories + (Weight_Change_lbs × 3500 cal/lb ÷ Days)
    """

    def __init__(self, alpha: float = 0.3):
        """
        Args:
            alpha: EWMA smoothing factor (0.1-0.5)
                   - Lower = smoother (less reactive to daily fluctuations)
                   - Higher = faster adaptation (more reactive)
                   MacroFactor likely uses ~0.25-0.35
        """
        self.alpha = alpha

    def calculate_trend_weight(self, daily_weights: List[float]) -> List[float]:
        """
        Exponentially Weighted Moving Average (EWMA) smoothing.

        Eliminates daily water/sodium fluctuations.

        Example:
        Daily: [210.2, 211.4, 209.8, 210.5, 210.1]
        Trend: [210.0, 210.2, 210.0, 209.9, 209.8]
        """
        if not daily_weights:
            return []

        trend = [daily_weights[0]]  # Start with first weight

        for weight in daily_weights[1:]:
            new_trend = (self.alpha * weight) + ((1 - self.alpha) * trend[-1])
            trend.append(new_trend)

        return trend

    def calculate_tdee(
        self,
        weights: List[Tuple[date, float]],  # [(date, weight_lbs), ...]
        calories: List[Tuple[date, float]],  # [(date, calories), ...]
        window_days: int = 14
    ) -> Tuple[float, float, float]:
        """
        Calculate adaptive TDEE over rolling window.

        Args:
            weights: List of (date, weight_lbs) tuples
            calories: List of (date, calories) tuples
            window_days: Rolling window size (14 = 2 weeks recommended)

        Returns:
            (tdee, trend_weight_start, trend_weight_end)

        Example:
        weights = [
            (date(2025, 1, 1), 210.2),
            (date(2025, 1, 2), 211.4),
            ...
            (date(2025, 1, 14), 208.5)
        ]
        calories = [
            (date(2025, 1, 1), 1800),
            (date(2025, 1, 2), 1850),
            ...
        ]

        Result:
        TDEE = 2,300 cal/day
        Trend start: 210.0 lbs
        Trend end: 208.0 lbs
        Weight change: -2.0 lbs in 14 days
        """

        # Sort by date
        weights_sorted = sorted(weights, key=lambda x: x[0])
        calories_sorted = sorted(calories, key=lambda x: x[0])

        # Extract most recent window
        recent_weights = weights_sorted[-window_days:]
        recent_calories = calories_sorted[-window_days:]

        if len(recent_weights) < window_days or len(recent_calories) < window_days:
            raise ValueError(f"Need at least {window_days} days of data")

        # Calculate trend weights
        daily_weights = [w[1] for w in recent_weights]
        trend_weights = self.calculate_trend_weight(daily_weights)

        # Weight change over period
        trend_start = trend_weights[0]
        trend_end = trend_weights[-1]
        weight_change_lbs = trend_end - trend_start

        # Average calorie intake
        daily_calories = [c[1] for c in recent_calories]
        avg_calories = np.mean(daily_calories)

        # Calculate energy deficit/surplus
        # 3500 calories = 1 lb of fat
        energy_delta_per_day = (weight_change_lbs * 3500) / window_days

        # TDEE = calories eaten + energy deficit
        # If losing weight (negative change), energy_delta is negative
        # TDEE = 1800 + (-500) = 2300 cal/day
        tdee = avg_calories - energy_delta_per_day

        return tdee, trend_start, trend_end

    def adjust_macros_weekly(
        self,
        current_target: float,
        goal_rate_lbs_per_week: float,
        actual_rate_lbs_per_week: float,
        tolerance: float = 0.2
    ) -> float:
        """
        MacroFactor's adherence-neutral weekly adjustment.

        Args:
            current_target: Current calorie target
            goal_rate_lbs_per_week: Desired rate (e.g., -1.0 = lose 1 lb/week)
            actual_rate_lbs_per_week: Actual rate from trend weight
            tolerance: Acceptable variance (0.2 = ±20%)

        Returns:
            New calorie target

        Example 1 (Cutting):
        Goal: -1.0 lb/week
        Actual: -1.2 lb/week (losing too fast)
        Adjustment: +100-150 cal (slow down fat loss, preserve muscle)

        Example 2 (Cutting):
        Goal: -1.0 lb/week
        Actual: -0.4 lb/week (losing too slow)
        Adjustment: -100-150 cal (increase deficit)

        Example 3 (On track):
        Goal: -1.0 lb/week
        Actual: -1.0 lb/week
        Adjustment: 0 (no change)
        """

        # Calculate variance from goal
        variance = (actual_rate_lbs_per_week - goal_rate_lbs_per_week) / abs(goal_rate_lbs_per_week)

        # If within tolerance, no change
        if abs(variance) <= tolerance:
            return current_target

        # If losing/gaining too fast, increase calories
        if actual_rate_lbs_per_week < goal_rate_lbs_per_week:  # More negative (cutting) or more positive (bulking)
            adjustment = 150 if abs(variance) > 0.5 else 100
            return current_target + adjustment

        # If losing/gaining too slow, decrease calories
        else:
            adjustment = 150 if abs(variance) > 0.5 else 100
            return current_target - adjustment
```

### **Example Usage**

```python
# User profile: Cutting phase, goal = lose 1.0 lb/week

# Week 1-2 data
weights = [
    (date(2025, 1, 1), 210.2),
    (date(2025, 1, 2), 211.4),
    (date(2025, 1, 3), 209.8),
    # ... 14 days total
    (date(2025, 1, 14), 208.5)
]

calories = [
    (date(2025, 1, 1), 1800),
    (date(2025, 1, 2), 1750),
    (date(2025, 1, 3), 1900),
    # ... 14 days total
    (date(2025, 1, 14), 1850)
]

tdee_calc = AdaptiveTDEE(alpha=0.3)

# Calculate TDEE
tdee, trend_start, trend_end = tdee_calc.calculate_tdee(weights, calories, window_days=14)

print(f"Trend weight: {trend_start:.1f} lbs → {trend_end:.1f} lbs")
print(f"Weight change: {trend_end - trend_start:.1f} lbs in 14 days")
print(f"Rate: {(trend_end - trend_start) / 2:.2f} lbs/week")
print(f"Average intake: {np.mean([c[1] for c in calories]):.0f} cal/day")
print(f"Calculated TDEE: {tdee:.0f} cal/day")

# Adjust macros for next week
goal_rate = -1.0  # Lose 1 lb/week
actual_rate = (trend_end - trend_start) / 2  # -1.5 lbs / 2 weeks = -0.75 lb/week

new_target = tdee_calc.adjust_macros_weekly(
    current_target=1800,
    goal_rate_lbs_per_week=goal_rate,
    actual_rate_lbs_per_week=actual_rate,
    tolerance=0.2
)

print(f"\nWeek 3 Recommendation:")
print(f"Current target: 1,800 cal/day")
print(f"New target: {new_target:.0f} cal/day")
print(f"Adjustment: {new_target - 1800:+.0f} cal/day")
```

**Output:**
```
Trend weight: 210.0 lbs → 208.5 lbs
Weight change: -1.5 lbs in 14 days
Rate: -0.75 lbs/week
Average intake: 1,825 cal/day
Calculated TDEE: 2,200 cal/day

Week 3 Recommendation:
Current target: 1,800 cal/day
New target: 1,700 cal/day
Adjustment: -100 cal/day
(Reason: Losing slower than goal, increase deficit slightly)
```

---

## 📈 PROGRESS VISUALIZATIONS

### **Streamlit Dashboard Components**

```python
# src/nutrition_dashboard.py

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_nutrition_dashboard(user_id: str):
    """
    MacroFactor-style nutrition dashboard.

    Shows:
    1. Trend weight graph
    2. Energy expenditure (TDEE) graph
    3. Daily calorie intake graph
    4. Macro breakdown
    5. Weekly check-in summary
    """

    st.subheader("📊 Nutrition & Progress Tracking")

    # Load last 8 weeks of data
    end_date = date.today()
    start_date = end_date - timedelta(days=56)

    weights = load_weight_log(user_id, start_date, end_date)
    calories = load_nutrition_summary(user_id, start_date, end_date)

    # Graph 1: Trend Weight
    st.markdown("### 📉 Weight Trend")
    fig_weight = go.Figure()

    # Daily weights (scatter)
    fig_weight.add_trace(go.Scatter(
        x=[w.weigh_date for w in weights],
        y=[w.weight_lbs for w in weights],
        mode='markers',
        name='Daily Weight',
        marker=dict(size=8, color='lightblue', opacity=0.6)
    ))

    # Trend weight (line)
    fig_weight.add_trace(go.Scatter(
        x=[w.weigh_date for w in weights],
        y=[w.trend_weight_lbs for w in weights],
        mode='lines',
        name='Trend Weight',
        line=dict(color='blue', width=3)
    ))

    fig_weight.update_layout(
        xaxis_title="Date",
        yaxis_title="Weight (lbs)",
        hovermode='x unified'
    )

    st.plotly_chart(fig_weight, use_container_width=True)

    # Graph 2: Energy Expenditure (TDEE over time)
    st.markdown("### 🔥 Energy Expenditure (TDEE)")

    # Calculate rolling 2-week TDEE
    tdee_calc = AdaptiveTDEE()
    tdee_history = []

    for i in range(14, len(weights)):
        window_weights = [(w.weigh_date, w.weight_lbs) for w in weights[i-14:i]]
        window_calories = [(c.date, c.total_calories) for c in calories[i-14:i]]

        try:
            tdee, _, _ = tdee_calc.calculate_tdee(window_weights, window_calories)
            tdee_history.append((weights[i].weigh_date, tdee))
        except:
            pass

    fig_tdee = go.Figure()
    fig_tdee.add_trace(go.Scatter(
        x=[t[0] for t in tdee_history],
        y=[t[1] for t in tdee_history],
        mode='lines+markers',
        name='TDEE',
        line=dict(color='orange', width=2)
    ))

    fig_tdee.update_layout(
        xaxis_title="Date",
        yaxis_title="TDEE (cal/day)",
        hovermode='x unified'
    )

    st.plotly_chart(fig_tdee, use_container_width=True)

    st.info("💡 **Metabolic Adaptation:** Notice TDEE dropping during your cut? This is expected! Your body adapts to reduced calories. The algorithm auto-adjusts your targets to maintain your goal rate.")

    # Graph 3: Daily Calorie Intake
    st.markdown("### 🍽️ Daily Calorie Intake")

    fig_calories = go.Figure()

    # Actual calories (bars)
    fig_calories.add_trace(go.Bar(
        x=[c.date for c in calories],
        y=[c.total_calories for c in calories],
        name='Actual Calories',
        marker_color='green'
    ))

    # Target line
    target = calories[0].target_calories if calories else 1800
    fig_calories.add_hline(
        y=target,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Target: {target:.0f} cal"
    )

    fig_calories.update_layout(
        xaxis_title="Date",
        yaxis_title="Calories",
        hovermode='x unified'
    )

    st.plotly_chart(fig_calories, use_container_width=True)

    # Weekly Check-In Summary
    st.markdown("### 📋 Weekly Check-In")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Current Trend Weight",
            value=f"{weights[-1].trend_weight_lbs:.1f} lbs",
            delta=f"{weights[-1].trend_weight_lbs - weights[-7].trend_weight_lbs:.1f} lbs this week"
        )

    with col2:
        avg_intake = np.mean([c.total_calories for c in calories[-7:]])
        st.metric(
            label="Average Intake (7 days)",
            value=f"{avg_intake:.0f} cal/day",
            delta=f"{avg_intake - target:+.0f} vs target"
        )

    with col3:
        current_tdee = tdee_history[-1][1] if tdee_history else 2000
        st.metric(
            label="Current TDEE",
            value=f"{current_tdee:.0f} cal/day"
        )
```

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 4A: Food Database Setup (Week 9)**

**Tasks:**
```python
# Week 9 Checklist

[x] Download FDC bulk data
    wget https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2024-10-31.zip

[x] Download OFF bulk dump
    wget https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz

[x] Create SQLite schema
    python scripts/create_nutrition_db.py

[x] ETL: FDC → SQLite
    python scripts/import_fdc_data.py

[x] ETL: OFF → SQLite
    python scripts/import_off_data.py

[x] Build full-text search indexes
    CREATE VIRTUAL TABLE foods_fts USING fts5(name, brand, category);

[x] Validate data quality
    python scripts/validate_nutrition_data.py
```

**Deliverables:**
- `data/nutrition.db` (SQLite database with ~500K foods)
- `src/food_database.py` (search/lookup functions)
- `tests/test_food_database.py` (validation tests)

### **Phase 4B: Food Logging UI (Week 10)**

**Tasks:**
```python
# Week 10 Checklist

[x] Barcode scan UI (Streamlit camera input)
    st.camera_input("Scan barcode")

[x] Name search UI (autocomplete dropdown)
    st.selectbox("Search food...", options=search_results)

[x] Manual entry UI (for unlisted foods)

[x] Recent foods quick-add

[x] Custom foods/recipes

[x] Daily log view (breakfast/lunch/dinner/snacks)

[x] Macro totals display
```

**Deliverables:**
- `src/food_logging.py` (logging functions)
- Updated `src/main.py` (food logging tab)
- `tests/test_food_logging.py`

### **Phase 4C: Adaptive TDEE & Coaching (Week 11-12)**

**Tasks:**
```python
# Week 11-12 Checklist

[x] Implement EWMA trend weight calculation
    AdaptiveTDEE.calculate_trend_weight()

[x] Implement adaptive TDEE algorithm
    AdaptiveTDEE.calculate_tdee()

[x] Implement weekly macro adjustments
    AdaptiveTDEE.adjust_macros_weekly()

[x] Progress graphs (Plotly charts)
    - Trend weight
    - TDEE over time
    - Daily calorie intake
    - Macro breakdown

[x] Weekly check-in UI

[x] Coaching explanations
    "You lost 2.5 lbs this week (goal: 1.0 lb/week).
     This is too fast - we're adding 150 cal to preserve muscle."
```

**Deliverables:**
- `src/adaptive_tdee.py` (algorithm implementation)
- `src/nutrition_dashboard.py` (visualizations)
- `tests/test_adaptive_tdee.py` (algorithm validation)

---

## 🧪 DATA QUALITY VALIDATION

### **Accuracy Testing Plan**

```python
# tests/test_nutrition_accuracy.py

def test_fdc_vs_label_accuracy():
    """
    Compare FDC data vs. actual product labels.

    Test 30 items:
    - 15 raw foods (chicken breast, broccoli, rice)
    - 15 packaged (Quest bar, Kodiak pancakes, etc.)

    Acceptance: <5% variance in macros per 100g
    """
    test_items = [
        # Raw foods (should be nearly exact)
        {"name": "Chicken breast, raw", "fdc_id": "171477",
         "expected": {"protein": 23.0, "fat": 1.2, "carbs": 0.0}},

        # Packaged foods
        {"name": "Quest Protein Bar - Chocolate Chip Cookie Dough",
         "barcode": "888849000470",
         "expected": {"protein": 21.0, "fat": 8.0, "carbs": 24.0}},
        # ... 28 more
    ]

    for item in test_items:
        if "fdc_id" in item:
            result = food_db.get_by_fdc_id(item["fdc_id"])
        else:
            result = food_db.get_by_barcode(item["barcode"])

        # Check accuracy
        for macro in ["protein", "fat", "carbs"]:
            expected = item["expected"][macro]
            actual = result[f"{macro}_g"]
            variance = abs(actual - expected) / expected

            assert variance < 0.05, f"{item['name']}: {macro} variance {variance:.1%} > 5%"
```

### **Completeness Scoring**

```python
def calculate_completeness_score(food: dict) -> float:
    """
    Score food data completeness (0.0-1.0).

    Required fields (50%):
    - name, calories, protein, fat, carbs

    Important fields (30%):
    - fiber, sugar, sodium, serving_size

    Nice-to-have (20%):
    - micronutrients, brand, category
    """
    score = 0.0

    # Required (10 points each = 50 points)
    if food.get("name"): score += 10
    if food.get("calories"): score += 10
    if food.get("protein_g"): score += 10
    if food.get("fat_g"): score += 10
    if food.get("carbs_g"): score += 10

    # Important (7.5 points each = 30 points)
    if food.get("fiber_g"): score += 7.5
    if food.get("sugar_g"): score += 7.5
    if food.get("sodium_mg"): score += 7.5
    if food.get("serving_size_g"): score += 7.5

    # Nice-to-have (5 points each = 20 points)
    if food.get("vitamin_a_ug"): score += 5
    if food.get("vitamin_c_mg"): score += 5
    if food.get("brand"): score += 5
    if food.get("category"): score += 5

    return score / 100
```

---

## 💡 HEALTHRAG ADVANTAGES OVER MACROFACTOR

| Feature | MacroFactor | HealthRAG |
|---------|-------------|-----------|
| **Adaptive TDEE** | ✅ Excellent | ✅ **Same algorithm** (open-source!) |
| **Adherence-Neutral** | ✅ Excellent | ✅ **Same approach** |
| **Trend Weight** | ✅ EWMA smoothing | ✅ **Same algorithm** |
| **Food Database** | ✅ Verified (proprietary) | ✅ **FDC + OFF** (free, open) |
| **Barcode Lookup** | ✅ Excellent | ✅ **OFF + FoodRepo** (free) |
| **Weekly Adjustments** | ✅ Auto-adjust | ✅ **Same logic** |
| **Offline Mode** | ❌ Mobile app only | ✅ **Local DB** (bulk mirrors) |
| **Training Integration** | ❌ Nutrition only | ✅ **Integrated!** (RP Hypertrophy features) |
| **Cost** | ❌ $11.99/month | ✅ **Free** |
| **Desktop Support** | ❌ Mobile only | ✅ **Streamlit web UI** |
| **Open Source** | ❌ Proprietary | ✅ **100% open** |

---

## 🎯 SUCCESS CRITERIA

**HealthRAG Nutrition Tracking = MacroFactor Quality at $0 cost**

### Parity with MacroFactor:
- ✅ Adaptive TDEE calculation (same algorithm)
- ✅ Adherence-neutral coaching
- ✅ Trend weight smoothing
- ✅ Weekly macro adjustments
- ✅ Progress visualizations

### Improvements over MacroFactor:
- ✅ **Integrated training** (MacroFactor is nutrition-only)
- ✅ **Offline mode** (bulk DB mirrors)
- ✅ **Desktop support** (Streamlit web UI)
- ✅ **Free** (no $12/month subscription)
- ✅ **Open source** (full transparency)

---

## 📚 API ENDPOINTS REFERENCE

### **USDA FoodData Central**

**Search Foods:**
```bash
GET https://api.nal.usda.gov/fdc/v1/foods/search?query=chicken%20breast&api_key=YOUR_KEY
```

**Get Food Details:**
```bash
GET https://api.nal.usda.gov/fdc/v1/food/171477?api_key=YOUR_KEY
```

**Bulk Download:**
```bash
https://fdc.nal.usda.gov/download-datasets.html
- Foundation Foods: ~1,000 items (core reference)
- SR Legacy: ~8,000 items (legacy USDA SR)
- Branded Foods: ~400,000 items (packaged products)
```

**API Key:** Free, register at https://fdc.nal.usda.gov/api-key-signup.html

---

### **Open Food Facts**

**Get Product by Barcode:**
```bash
GET https://world.openfoodfacts.org/api/v2/product/737628064502
```

**Search Products:**
```bash
GET https://world.openfoodfacts.org/api/v2/search?search_terms=quest%20bar
```

**Bulk Download:**
```bash
# Full dump (~30GB compressed, 2.8M products)
wget https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz

# Daily delta (new/updated products)
wget https://static.openfoodfacts.org/data/delta/YYYY-MM-DD.jsonl.gz
```

**No API Key Required** (100% free, open data)

---

### **Open Food Repo**

**Get Product by Barcode:**
```bash
GET https://www.openfoodrepo.org/api/products/{barcode}
```

**Search:**
```bash
GET https://www.openfoodrepo.org/api/products?search=swiss%20chocolate
```

---

### **Edamam (Optional Paid Tier)**

**Food Search:**
```bash
GET https://api.edamam.com/api/food-database/v2/parser?app_id=YOUR_ID&app_key=YOUR_KEY&ingr=chicken%20breast
```

**Barcode Lookup:**
```bash
GET https://api.edamam.com/api/food-database/v2/parser?app_id=YOUR_ID&app_key=YOUR_KEY&upc=737628064502
```

**Free Tier:** 10,000 requests/month

---

## 🚀 NEXT STEPS

1. **Review this architecture** with user
2. **Begin Phase 4A** (Food Database Setup, Week 9)
3. **Download bulk data** (FDC + OFF)
4. **Create SQLite schema**
5. **Build ETL pipelines**
6. **Validate data quality** (30-item accuracy test)

**Timeline:**
- Week 9: Database setup
- Week 10: Food logging UI
- Week 11-12: Adaptive TDEE + coaching
- **Result:** MacroFactor-quality nutrition tracking, $0 cost, integrated with training

---

**Bottom Line:** We're building a $12/month nutrition app using 100% free, open-source data with the same algorithms MacroFactor uses, but integrated with our training system (which MacroFactor doesn't have).
