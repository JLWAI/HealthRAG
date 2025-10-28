# HealthRAG: Comprehensive Data Collection & Measurement Strategy
**Phase 4 Planning: Progress Tracking & Adaptive Coaching**

---

## EXECUTIVE SUMMARY

HealthRAG's adaptive coaching system requires systematic data collection across body metrics, performance, nutrition, recovery, and subjective feedback. This strategy prioritizes **minimum viable tracking** (Phase 4 Week 10-12) with incremental expansion to full adaptive coaching (Week 13-14) and advanced features (Phase 5).

**Core Philosophy**: Daily AI coach that tracks, analyzes, and adapts. Not a static calculator.

**Key Principles**:
- Start simple: Weight + workout logging only (Week 10)
- Add gradually: Measurements, nutrition, recovery (Weeks 11-14)
- Minimize friction: Quick entry, smart defaults, optional fields
- Evidence-based thresholds: RP and Jeff Nippard guidelines for adjustments
- Local-first: SQLite database, works offline, no cloud dependencies

**Success Criteria**:
- Week 10: Basic weight tracking + 7-day moving average
- Week 12: Workout logging + volume trend analysis
- Week 14: Adaptive recommendations (calories, volume adjustments)

---

## 1. DATA COLLECTION MATRIX

| Data Category | What to Measure | Why It Matters | Frequency | Required/Optional | Phase-Specific | Input Method | Storage |
|---------------|-----------------|----------------|-----------|-------------------|----------------|--------------|---------|
| **BODY METRICS** |
| Body Weight | Weight in lbs | Primary progress indicator for cut/bulk/maintain | Daily (AM, fasted) | **REQUIRED** for cut/bulk/recomp | Cut/Bulk: CRITICAL, Recomp: Maintain ±2 lbs | Number input | `daily_weights` table |
| Waist | Inches at navel | Fat loss indicator (better than scale for recomp) | Weekly | **REQUIRED for recomp**, Optional for cut/bulk | Recomp: PRIMARY metric, Cut: Validates fat loss | Number input | `measurements` table |
| Chest | Inches at nipple line | Muscle gain indicator | Weekly or Biweekly | OPTIONAL | Bulk/Recomp: Useful for muscle tracking | Number input | `measurements` table |
| Arms/Legs | Inches at peak | Muscle gain indicators | Biweekly | OPTIONAL | Bulk: Growth indicators | Number input | `measurements` table |
| **PERFORMANCE METRICS** |
| Exercise Performance | Weight × Reps × Sets | PRIMARY muscle gain indicator | Per workout | **REQUIRED** | All phases: CRITICAL for progressive overload | Quick log interface | `workout_logs` table |
| Volume Load | Total kg lifted per session | Training volume tracking | Per workout (auto-calculated) | Auto-calculated | All phases: Track volume trends | Calculated field | `workout_logs` |
| RPE (Rate of Perceived Exertion) | 1-10 scale per set | Fatigue management, autoregulation | Per set (optional) | OPTIONAL (advanced) | All phases: Detect overtraining | Dropdown (1-10) | `workout_logs` |
| **NUTRITION COMPLIANCE** |
| Daily Calories | Total calories consumed | Primary diet adherence metric | Daily | **REQUIRED for cut/bulk/recomp** | Cut/Bulk/Recomp: CRITICAL | Number input | `nutrition_logs` table |
| Protein (g) | Grams of protein | Muscle preservation/growth | Daily | **REQUIRED for cut/bulk/recomp** | All phases: Most important macro | Number input | `nutrition_logs` table |
| **RECOVERY INDICATORS** |
| Sleep Duration | Hours slept | PRIMARY recovery factor | Daily | **REQUIRED** | All phases: Affects everything | Number input (hours) | `recovery_logs` table |
| Sleep Quality | 1-10 subjective | Recovery quality | Daily | OPTIONAL | All phases: Useful correlation | Dropdown (1-10) | `recovery_logs` table |
| Fatigue Level | 1-10 overall energy | Training readiness | Daily | OPTIONAL | All phases: Autoregulation input | Dropdown (1-10) | `recovery_logs` table |
| **SUBJECTIVE FEEDBACK** |
| Workout Feel | "Great/Good/Okay/Bad/Terrible" | Training quality | Per workout | OPTIONAL | All phases: Quick sentiment | 5-option dropdown | `workout_logs` table |
| Hunger Level | 1-10 scale | Diet sustainability (cut) | Daily | **REQUIRED for cut** | Cut: Early warning of aggressive deficit | Dropdown (1-10) | `nutrition_logs` table |
| **PROGRESS PHOTOS** |
| Front/Side/Back Photos | Visual body comp | Best recomp/cut progress indicator | Weekly or Biweekly | **REQUIRED for recomp** | Recomp: PRIMARY metric | File upload | `progress_photos` table |

---

## 2. USER EXPERIENCE DESIGN

### Daily Morning Check-In (30 seconds)

```
🌅 DAILY CHECK-IN
─────────────────────────────────
Today: Monday, October 28, 2025

⚖️ WEIGHT ENTRY (REQUIRED)
   [____] lbs
   📊 7-day average: 183.2 lbs (-0.8 lbs this week)

😴 SLEEP (REQUIRED)
   [____] hours

[Submit Check-In]
```

### Post-Workout Logging (3-5 minutes)

```
💪 WORKOUT LOG - Upper Day 1
─────────────────────────────────

1. Barbell Bench Press
   Set 1: [225] lbs × [8] reps
   Set 2: [225] lbs × [7] reps
   Set 3: [225] lbs × [7] reps
   Set 4: [225] lbs × [6] reps

   📊 Last week: 220 lbs × 8,7,7,6 → +5 lbs! 🎉

[Copy Last Week] [Exercise Complete ✓]

How did this workout feel?
[💪 Great] [👍 Good] [😐 Okay] [👎 Bad] [😩 Terrible]

[Save Workout]
```

### Weekly Check-In (5 minutes)

```
📊 WEEKLY CHECK-IN - Week 8
─────────────────────────────────

📏 BODY MEASUREMENTS (Required for Recomp/Cut)
   Waist (at navel): [__.__] inches
   Chest (optional): [__.__] inches

   📊 Last week: Waist 33.5" → Suggests 33.0" 🎉

📸 PROGRESS PHOTO (Recommended)
   [📷 Take Front Photo] [Skip]

🎯 TRAINING REVIEW
   Workouts Completed: 4/4 ✅

[Complete Check-In]
```

---

## 3. ANALYSIS CAPABILITIES

### Weight Trend Analysis

```python
def analyze_weight_trend(user_id, phase, weeks=2):
    """
    Calculate 7-day moving average and rate of change.
    Detect if adjustments needed based on phase.
    """
    # Phase-specific thresholds
    thresholds = {
        'cut': {'target': -1.0, 'min': -1.5, 'max': -0.5},
        'bulk': {'target': 0.75, 'min': 0.5, 'max': 1.25},
        'recomp': {'target': 0.0, 'min': -0.5, 'max': 0.5}
    }

    # Return: "too_slow", "too_fast", or "on_track"
```

**Thresholds for Action**:
- **Cut**: Weight loss < 0.5 lb/week for 2+ weeks → Reduce calories 100-200
- **Cut**: Weight loss > 1.5 lb/week for 2+ weeks → Increase calories 100-150
- **Bulk**: Weight gain < 0.5 lb/week for 2+ weeks → Increase calories 150-200
- **Recomp**: Weight changes > ±2 lbs over 2 weeks → Adjust calories ±100-150

### Strength Progression Analysis

**Plateau Detection** (no progress for 2+ weeks) → Recommend:
1. Add 1-2 sets per muscle group (volume increase)
2. Deload week (reduce volume 50%, maintain intensity)
3. Check nutrition (are they in too deep of a deficit?)

**Regression** (strength decreasing) → Recommend:
1. **If cutting**: Acceptable if < 10% strength loss
2. **If bulking**: RED FLAG - increase calories immediately
3. **If recomp**: Check sleep, stress, recovery factors

---

## 4. MINIMUM VIABLE DATASET (MVP)

### Phase 4 Week 10-12: BASIC TRACKING

**Critical Data Only**:
1. **Body Weight** (daily) - Primary progress indicator
2. **Workout Performance** (per workout) - Strength progression = muscle gain proof
3. **Sleep Duration** (daily) - PRIMARY recovery factor

**UI Flow**:
- Morning: Weight + Sleep (30 seconds)
- Post-Workout: Log exercises (3-5 minutes)

**Adaptive Coaching Enabled**:
- ✅ Calorie adjustment if weight trend wrong
- ✅ Volume adjustment if strength plateaus
- ✅ Deload recommendation if insufficient sleep

### Phase 4 Week 13-14: ENHANCED TRACKING

**Add**:
4. **Daily Calories & Protein** - Validate adherence
5. **Weekly Waist Measurement** - Recomp users
6. **Workout Feel** - Quick quality indicator

**Adaptive Coaching Enhanced**:
- ✅ Detect low adherence → Simplify meal plan
- ✅ Waist decreasing + scale stable → Confirm recomp working

### Phase 5: ADVANCED TRACKING

**Add**:
7. Progress Photos (weekly)
8. Chest/Arms/Legs Measurements (biweekly)
9. RPE per set (autoregulation)
10. Hunger/Energy/Motivation Levels
11. Cycle Tracking (females)

---

## 5. DATABASE SCHEMA (SQLite)

### Table: `daily_weights`

```sql
CREATE TABLE daily_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    date DATE NOT NULL,
    weight_lbs REAL NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_daily_weights_user_date ON daily_weights(user_id, date DESC);
```

### Table: `workout_logs`

```sql
CREATE TABLE workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    date DATE NOT NULL,
    workout_name TEXT,
    exercise TEXT NOT NULL,
    set_number INTEGER NOT NULL,
    weight_lbs REAL,
    reps INTEGER,
    rpe INTEGER,
    is_pr BOOLEAN DEFAULT 0,
    workout_feel TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_logs_user_date ON workout_logs(user_id, date DESC);
CREATE INDEX idx_workout_logs_user_exercise ON workout_logs(user_id, exercise, date DESC);
```

### Table: `nutrition_logs`

```sql
CREATE TABLE nutrition_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    date DATE NOT NULL,
    calories INTEGER,
    protein_g INTEGER,
    hunger_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
```

### Table: `recovery_logs`

```sql
CREATE TABLE recovery_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    date DATE NOT NULL,
    sleep_hours REAL,
    sleep_quality INTEGER,
    fatigue_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
```

### Table: `measurements`

```sql
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    date DATE NOT NULL,
    measurement_type TEXT NOT NULL,
    value_inches REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date, measurement_type)
);
```

---

## 6. PHASE-SPECIFIC TRACKING STRATEGIES

### CUTTING PHASE

**Critical Data**:
- Body Weight (daily) - PRIMARY metric
- Waist Measurement (weekly) - Validates fat loss
- Strength Performance (per workout) - Preserve muscle
- Daily Calories & Protein - Adherence tracking
- Hunger Level (daily) - Sustainability indicator
- Sleep Duration (daily) - Recovery critical on deficit

**Adjustment Triggers**:
- Weight loss too slow (< 0.5 lb/week for 2 weeks) → -100-200 cal
- Weight loss too fast (> 1.5 lb/week for 2 weeks) → +100-150 cal
- Strength dropping >10% → Increase calories
- Hunger >8/10 for 3+ days → Refeed day

### BULKING PHASE

**Critical Data**:
- Body Weight (daily) - Target 0.5-1.0 lb/week gain
- Strength Performance (per workout) - PRIMARY muscle gain indicator
- Waist Measurement (weekly) - Prevent excessive fat gain
- Daily Calories & Protein - Adherence tracking

**Adjustment Triggers**:
- Weight gain too slow (< 0.5 lb/week for 2 weeks) → +150-200 cal
- Weight gain too fast (> 1.0 lb/week for 2 weeks) → -100-150 cal
- Strength not progressing for 2 weeks → Increase volume
- Waist increasing >1.5"/month → Reduce surplus

### RECOMP PHASE

**Critical Data**:
- Waist Measurement (weekly) - PRIMARY metric (not scale weight!)
- Chest Measurement (weekly) - Muscle gain indicator
- Strength Performance (per workout) - PROOF of muscle gain
- Progress Photos (weekly) - Visual changes > scale
- Body Weight (daily) - Should maintain ±2 lbs

**Adjustment Triggers**:
- Weight increasing >2 lbs over 2 weeks → -100-150 cal
- Weight decreasing >2 lbs over 2 weeks → +100-150 cal
- Strength plateau >3 weeks → Increase volume
- No visual changes after 12 weeks → Pivot to cut or bulk

---

## 7. IMPLEMENTATION ROADMAP

### Phase 4 Week 10: BASIC TRACKING MVP

**Build**:
- `daily_weights` table + UI
- `workout_logs` table + UI
- `recovery_logs` table (sleep only)
- Basic analysis: 7-day weight MA, volume load trends

**Deliverable**: User can track weight, workouts, sleep. See basic trends.

### Phase 4 Week 11-12: ENHANCED TRACKING

**Add**:
- `nutrition_logs` table + UI
- `measurements` table + UI
- Enhanced analysis: Adherence %, body comp trends, plateau detection

**Deliverable**: Full tracking system operational.

### Phase 4 Week 13-14: ADAPTIVE COACHING

**Add**:
- Decision trees (weight adjustment, volume adjustment)
- Proactive recommendations
- Monthly progress reports

**Deliverable**: FULL ADAPTIVE COACHING OPERATIONAL.

### Phase 5: ADVANCED FEATURES

**Add**:
- Progress photos + comparison
- RPE-based autoregulation
- Cycle tracking (females)
- Voice input
- Export reports

---

## SUMMARY

This data strategy enables HealthRAG to function as a true **daily AI coach** that:
- Tracks progress across multiple dimensions (weight, strength, body comp, nutrition, recovery)
- Analyzes trends to detect plateaus, regressions, or excessive progress
- Adapts recommendations based on data (calories, volume, deloads, diet breaks)
- Provides evidence-based guidance grounded in RP and Jeff Nippard principles
- Minimizes user friction while maximizing coaching intelligence

**Next Steps**: Implement Phase 2 (Week 2) calculation engine, then build toward Phase 4 (Week 10-14) adaptive coaching system.
