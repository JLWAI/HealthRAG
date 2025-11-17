# Target Apps Analysis: RP Hypertrophy + MacroFactor
**Complete Feature Breakdown for HealthRAG Clone**

*Research Date: January 2025*

---

## 🎯 OVERVIEW

We're building HealthRAG to combine the best of:

1. **RP Hypertrophy App** (Training) - $34.99/month
2. **MacroFactor** (Nutrition) - $11.99/month

**Total Cost if Buying Both:** $46.98/month ($563.76/year)

**HealthRAG Goal:** Free, local, integrated alternative with improvements

---

# PART 1: MACROFACTOR (NUTRITION)

## 📊 Core Features

### 1. **Adaptive Energy Expenditure Algorithm**

**How It Works:**
```
Actual TDEE = (Weight Change × 3500 cal/lb) ÷ Days + Average Calories Consumed
```

**Process:**
1. User logs weight daily
2. User logs food/calories daily
3. App calculates "Trend Weight" (smoothed average, not daily fluctuations)
4. App compares trend weight change to calories consumed
5. App back-calculates actual TDEE
6. **Adapts to metabolic changes automatically**

**Example:**
```
Week 1-2 Data:
- Starting weight: 210 lbs (trend)
- Ending weight: 208 lbs (trend) → -2 lbs in 14 days
- Average calories: 1,800/day

Calculation:
- Weight change: -2 lbs × 3500 cal/lb = -7,000 cal deficit
- Deficit per day: -7,000 ÷ 14 = -500 cal/day
- TDEE = 1,800 cal eaten + 500 cal deficit = 2,300 cal/day

Week 3-4 Data:
- Starting weight: 208 lbs (trend)
- Ending weight: 207 lbs (trend) → -1 lb in 14 days (slowing down!)
- Average calories: 1,800/day (same)

Calculation:
- Weight change: -1 lb × 3500 cal/lb = -3,500 cal deficit
- Deficit per day: -3,500 ÷ 14 = -250 cal/day
- TDEE = 1,800 cal eaten + 250 cal deficit = 2,050 cal/day

Metabolic Adaptation Detected!
- TDEE dropped from 2,300 → 2,050 (-250 cal)
- Algorithm adjusts targets for next week
```

**Accuracy:**
- MacroFactor's adaptive approach is **3x more accurate** than static TDEE formulas
- Accounts for metabolic adaptation, NEAT changes, hormonal shifts

### 2. **Adherence-Neutral Coaching**

**Philosophy:** "We don't care if you hit your targets - we care about YOUR DATA"

**How It Works:**
- Algorithm calculates TDEE based on **what you actually ate**, not what you were "supposed" to eat
- No shame/guilt for exceeding macros
- No "red" days or negative feedback
- Adjustments based on REALITY, not adherence

**Example:**
```
Target: 1,800 cal/day for weight loss

Week 1 Reality:
Mon: 1,600 cal
Tue: 2,200 cal (over by 400!)
Wed: 1,500 cal
Thu: 1,900 cal
Fri: 2,500 cal (way over!)
Sat: 1,700 cal
Sun: 1,800 cal

Average: 1,886 cal/day
Weight change: -1.5 lbs

MacroFactor Response:
"Your TDEE is ~2,500 cal/day based on actual intake and weight change.
Next week target: 1,850 cal/day (adjusted based on YOUR reality)"

Other Apps Response:
"You exceeded your target 2 days this week! ❌ Try harder!"
```

**Why This Matters:**
- Sustainable long-term adherence
- No perfectionism required
- Real-world flexibility (eating out, social events)
- Algorithm LEARNS from your actual behavior

### 3. **Trend Weight Calculation**

**Problem:** Daily weight fluctuates due to water, sodium, carbs, digestion

**Solution:** Exponentially weighted moving average (EWMA)

**Example:**
```
Daily Weigh-Ins:
Mon: 210.2 lbs
Tue: 211.4 lbs (+1.2 lbs - ate sushi, high sodium)
Wed: 209.8 lbs (-1.6 lbs - whoosh effect)
Thu: 210.5 lbs
Fri: 210.1 lbs

Trend Weight (smoothed):
Mon: 210.0 lbs
Tue: 210.2 lbs (only slight increase, ignoring water spike)
Wed: 210.0 lbs (steady downward trend)
Thu: 209.9 lbs
Fri: 209.8 lbs (-0.2 lbs actual fat loss detected)

Conclusion: You lost ~0.2 lbs of actual body mass this week
```

**Benefits:**
- Reduces anxiety from daily fluctuations
- More accurate progress tracking
- Better coaching decisions

### 4. **Weekly Macro Adjustments**

**Check-In Day:** User selects preferred day (e.g., every Monday)

**Adjustment Logic:**
```python
if rate_of_change > goal_rate:
    # Losing too fast (>1.5 lb/week when goal is 1.0 lb/week)
    new_target = current_calories + 100-150
elif rate_of_change < goal_rate:
    # Losing too slow (<0.5 lb/week when goal is 1.0 lb/week)
    new_target = current_calories - 100-150
else:
    # On track
    new_target = current_calories  # No change
```

**Example:**
```
Goal: Lose 1.0 lb/week
Current Target: 1,800 cal/day

Week 1-2: Lost 2.5 lbs (1.25 lb/week) → Too fast!
Adjustment: +150 cal → New target: 1,950 cal/day

Week 3-4: Lost 1.0 lbs (0.5 lb/week) → Too slow!
Adjustment: -100 cal → New target: 1,850 cal/day

Week 5-6: Lost 2.0 lbs (1.0 lb/week) → Perfect!
Adjustment: No change → Target: 1,850 cal/day
```

### 5. **Food Logging Features**

**Speed:** Fastest food logging on the market (fewer taps than any competitor)

**Input Methods:**
1. **Barcode Scanning** - Instant food recognition
2. **AI Describe** - Voice/text: "chicken breast with broccoli and rice" → Auto-populated
3. **Verified Food Database** - Premium database (not user-generated like MyFitnessPal)
4. **Custom Recipes** - Save multi-ingredient meals
5. **Manual Entry** - For unlisted foods
6. **Recent Foods** - Quick access to frequently logged items

**Example AI Describe:**
```
User: "Large pepperoni pizza, 3 slices"
MacroFactor:
→ Papa John's Large Pepperoni Pizza (3 slices)
→ 840 calories, 36g protein, 96g carbs, 30g fat
→ Confirm? [Yes] [Edit] [Different Food]
```

### 6. **Progress Tracking**

**Visualizations:**
- **Trend Weight Graph** (smoothed weight over time)
- **Energy Expenditure Graph** (TDEE over time, shows metabolic adaptation)
- **Nutrition Intake Graph** (calories, macros over time)
- **Macro Ratio Pie Chart** (protein/fat/carbs %)
- **Micronutrient Tracking** (vitamins, minerals, fiber)

**Additional Tracking:**
- Body measurements (waist, chest, arms, etc.)
- Progress photos (compare side-by-side)
- Custom habits (water intake, steps, sleep)
- Period tracking (for females)

**Example Expenditure Graph:**
```
TDEE Over Time (Cut Phase):

2,800 cal ┤
         │
2,600 cal ┤  ●
         │   ╲
2,400 cal ┤    ●─●
         │        ╲
2,200 cal ┤         ●─●──●  ← Metabolic adaptation
         │
2,000 cal ┤
         └─────────────────────
         Week 1  Week 4  Week 8

Insight: TDEE dropped 600 cal over 8 weeks (expected during cut)
Action: Algorithm adjusted targets to maintain 1 lb/week loss
```

### 7. **Macro Customization**

**Presets:**
- Balanced (40/30/30 - carbs/protein/fat)
- Low-carb (20/40/40)
- Keto (5/30/65)
- High-carb (50/30/20)

**Custom Ratios:**
- Set exact protein: 1.0g/lb bodyweight
- Set exact fat: 0.35g/lb bodyweight
- Remainder = carbs

**Dynamic Adjustments:**
- Protein increases during cuts (preserve muscle)
- Carbs increase during bulk (fuel training)

---

## 💪 MacroFactor Strengths

1. **Adaptive Algorithm** - No other app calculates TDEE this accurately
2. **Adherence-Neutral** - No guilt, just data
3. **Trend Weight** - Eliminates daily fluctuation anxiety
4. **Verified Database** - Premium food data (not user-generated errors)
5. **Micronutrient Tracking** - Vitamins, minerals, fiber
6. **Expenditure Visualization** - SEE your metabolism adapting
7. **Evidence-Based** - Created by Stronger by Science (Greg Nuckols, Eric Trexler)
8. **Affordable** - $6-12/month (cheaper than competitors)

---

## 🚨 MacroFactor Limitations

1. **Requires Daily Consistency**
   - Must log food daily (even cheat days)
   - Must weigh daily (algorithm needs data)
   - 2+ week data before accurate TDEE

2. **Mobile App Only**
   - No desktop version
   - Must log on phone (inconvenient for some)

3. **No Training Integration**
   - Nutrition-only (no workout tracking)
   - Separate app needed for training

4. **Minimal Coaching Explanations**
   - Doesn't explain WHY macros are set
   - No educational content in-app

5. **Early Bulking Issues**
   - Underestimated calories for skinny users initially
   - Users report needing +100-200 cal above recommendations

6. **Micronutrient Data Gaps**
   - Not all foods have complete vitamin/mineral data
   - Depends on food label completeness

---

# PART 2: RP HYPERTROPHY APP (TRAINING)

## 🏋️ Core Features

### 1. **Mesocycle Builder**

**Templates:** 45+ pre-selected programs
- Upper Body 4x per week
- Lower Body 4x per week
- Push/Pull/Legs (PPL) 6x per week
- Full Body 3x per week
- Bro Split 5x per week
- Body part specialization (arms, shoulders, back, etc.)

**Custom Building:**
- Select muscles to emphasize (growth focus)
- Select muscles for maintenance (sustain current size)
- Select muscles to ignore (minimal volume)

**2025 Update: Meso Builder (Beta)**
- Complete flexibility in muscle selection
- "Mr. Nick Shaw" template (6x/week, arms/shoulders emphasis)

### 2. **Volume Progression System**

**RP Volume Concepts:**
- **MEV** (Minimum Effective Volume) - Lowest sets per week to grow
- **MAV** (Maximum Adaptive Volume) - Optimal sets per week for growth
- **MRV** (Maximum Recoverable Volume) - Maximum sets before overtraining
- **MV** (Maintenance Volume) - Sets to maintain muscle

**Example (Chest):**
```
MEV: 10 sets/week (minimum to grow)
MAV: 16 sets/week (optimal for most people)
MRV: 22 sets/week (max before overtraining)
MV: 6 sets/week (maintain current size)

Mesocycle Progression:
Week 1: 12 sets (start above MEV)
Week 2: 14 sets
Week 3: 16 sets (approaching MAV)
Week 4: 18 sets (peak week)
Week 5: 10 sets (deload - 50% reduction)
```

**Primary Method:** Set accumulation (add sets weekly)
**Secondary:** Weight progression (increase load)
**Tertiary:** RIR progression (3 RIR → 0 RIR)

### 3. **Autoregulation via Feedback**

**After Each Workout, User Reports:**

1. **Pump Quality** (low/moderate/extreme)
   - Low → Need more volume
   - Moderate → Good volume
   - Extreme → Too much volume

2. **Soreness** (when did it heal?)
   - Healed on time → Good volume
   - Still sore → Too much volume
   - No soreness → Possibly too little volume

3. **Disruption** (general fatigue/strength loss)
   - Low → Can handle more volume
   - Moderate → Good volume
   - High → Reduce volume

4. **Joint Pain**
   - None → Exercise selection good
   - Mild → Monitor
   - Moderate/Severe → Replace exercise

5. **Performance** (strength progression)
   - Increased weight/reps → Working!
   - Plateaued → May need more volume
   - Decreased → Overtraining, reduce volume

**Algorithm Response:**
```python
if pump == 'low' and soreness == 'healed early':
    next_week_sets += 2  # Need more volume
elif pump == 'extreme' and soreness == 'still sore':
    next_week_sets -= 1  # Too much volume
else:
    next_week_sets += 1  # Normal progression
```

### 4. **Exercise Selection**

**Two Options:**

1. **Manual Selection**
   - Dropdown menu with extensive database
   - User chooses exercises
   - **Limitation:** User must know what to pick

2. **Auto-Fill**
   - Algorithm generates exercise selection
   - **MAJOR CRITICISM:**
     - Random exercise selection
     - Repeats same exercises
     - Places biomechanically similar movements consecutively
     - Unpredictable changes

**Notable Gap:** No equipment-based filtering, no tier recommendations

### 5. **Mesocycle Structure**

**Typical 6-Week Mesocycle:**

| Week | Sets | RIR | Load | Notes |
|------|------|-----|------|-------|
| 1 | 12 | 3 | Start | Base volume |
| 2 | 14 | 2 | +2.5-5% | Progressive overload |
| 3 | 16 | 2 | +2.5-5% | Approaching MAV |
| 4 | 18 | 1 | +2.5-5% | Peak volume |
| 5 | 20 | 0 | Same | Maximum stimulus |
| 6 | 10 | 3 | -20% | Deload (50% volume) |

**After Deload:** Start new mesocycle (potentially different split/exercises)

### 6. **Workout Execution**

**During Training:**
- See prescribed sets × reps × weight
- Track actual performance
- Enter feedback (pump, soreness, etc.)

**Missing Features:**
- ❌ No rest period timers
- ❌ No prescribed rest periods
- ❌ No exercise form videos/cues

### 7. **Progressive Overload Mechanisms**

1. **Set Accumulation** (primary)
   - Add 1-2 sets per week
   - Most reliable hypertrophy driver

2. **Load Progression**
   - Increase weight 2.5-5% when RIR drops
   - "Last week: 3 RIR @ 185 lbs → This week: 2 RIR @ 190 lbs"

3. **RIR Progression**
   - Start: 3 RIR (3 reps left in tank)
   - End: 0 RIR (taken to failure)

**Example:**
```
Exercise: Barbell Bench Press

Week 1: 3 sets × 8 reps @ 185 lbs, 3 RIR
Week 2: 4 sets × 8 reps @ 185 lbs, 2 RIR
Week 3: 4 sets × 8 reps @ 190 lbs, 2 RIR
Week 4: 5 sets × 8 reps @ 190 lbs, 1 RIR
Week 5: 5 sets × 8 reps @ 195 lbs, 0 RIR
Week 6: 2 sets × 8 reps @ 175 lbs, 3 RIR (deload)
```

---

## 💪 RP Hypertrophy Strengths

1. **Evidence-Based Science** - Dr. Mike Israetel's research
2. **Autoregulation** - Adjusts to YOUR recovery
3. **Volume Optimization** - Finds your MEV/MAV/MRV
4. **Deload Built-In** - Prevents overtraining
5. **Specialization** - Emphasize specific muscle groups
6. **Progressive Overload** - Clear progression scheme
7. **45+ Templates** - Variety for different goals

---

## 🚨 RP Hypertrophy Limitations

1. **❌ No Exercise Selection Guidance**
   - User must know which exercises to choose
   - Auto-fill is poor quality

2. **❌ No Equipment Customization**
   - Doesn't adapt to available equipment
   - No home gym vs commercial gym

3. **❌ No Rest Period Guidance**
   - No prescribed rest times
   - No timer widget

4. **❌ Web-Based Only**
   - Requires internet connection
   - No offline mode

5. **❌ Short Mesocycles**
   - 4-6 weeks may be insufficient
   - Some users manually extend

6. **❌ No Nutrition Integration**
   - Diet app sold separately (+$35/month!)

7. **❌ Expensive**
   - $34.99/month or $299.99/year

8. **❌ Complexity**
   - MEV/MAV/MRV overwhelming for beginners

---

# PART 3: HEALTHRAG IMPLEMENTATION PLAN

## 🎯 Competitive Advantages

| Feature | MacroFactor | RP Hypertrophy | HealthRAG |
|---------|-------------|----------------|-----------|
| **Adaptive TDEE** | ✅ Best-in-class | ❌ Not applicable | ✅ Planned (Phase 4) |
| **Nutrition Tracking** | ✅ Excellent | ❌ Separate app | ✅ Built-in (Week 2-3) |
| **Training Programs** | ❌ Not applicable | ✅ 45+ templates | 🔄 Planned (Phase 3) |
| **Equipment Awareness** | ❌ N/A | ❌ None | ✅ **Built** (Week 2) |
| **Exercise Tier Guidance** | ❌ N/A | ❌ None | ✅ **Planned** (Jeff Nippard) |
| **Integrated Coach** | ❌ Nutrition only | ❌ Training only | ✅ **Both!** |
| **Offline Mode** | ❌ Mobile app | ❌ Web-based | ✅ **Local MLX** |
| **Cost** | $12/month | $35/month | ✅ **Free** |
| **Proactive Dashboard** | ⚠️ Limited | ⚠️ Limited | ✅ **Built** (Week 3) |
| **Rest Period Timers** | ❌ N/A | ❌ None | 📋 Planned |
| **Adherence-Neutral** | ✅ Excellent | ⚠️ Not applicable | 📋 Planned (Phase 4) |

---

## 📋 Phase-by-Phase Implementation

### ✅ **PHASE 1: Foundation (Week 0-1) - COMPLETE**
- RAG system with RP + Jeff Nippard PDFs
- LLM backend (Ollama + MLX)
- Basic Q&A

### ✅ **PHASE 2: User Profile & Nutrition (Week 2-3) - COMPLETE**

**MacroFactor-Inspired Features Implemented:**
- ✅ User profile (weight, height, age, sex, activity)
- ✅ TDEE calculation (Mifflin-St Jeor BMR formula)
- ✅ Macro calculation (phase-aware: cut/bulk/recomp)
- ✅ Proactive dashboard (auto-show nutrition plan)
- ✅ Personalized coaching guidance

**Still Missing from MacroFactor:**
- ❌ Adaptive TDEE (trend weight + calories → recalculate TDEE)
- ❌ Adherence-neutral coaching
- ❌ Food logging
- ❌ Weekly macro adjustments

### 🔄 **PHASE 3: Program Generation (Week 5-8) - NEXT**

**RP Hypertrophy-Inspired Features to Build:**

**Week 5-6: Exercise Database + Selection Engine**
```python
# src/exercise_database.py

S_PLUS_TIER = {
    'glutes': ['walking_lunge'],
    'quads': ['hack_squat'],
    'triceps': ['overhead_cable_extension'],
    'back': ['chest_supported_row'],
    'biceps': ['face_away_beian_cable_curl'],
    'shoulders': ['cable_lateral_raise']
}

S_TIER = {
    'chest': [
        'barbell_bench_press',
        'incline_dumbbell_press',
        'machine_chest_press',
        'cable_crossover'
    ],
    'back': [
        'wide_grip_lat_pulldown',
        'neutral_grip_lat_pulldown',
        'cable_row',
        'chest_supported_row',
        'reverse_pec_deck'
    ],
    # ... etc for all muscle groups
}

EQUIPMENT_REQUIREMENTS = {
    'barbell_bench_press': ['barbell', 'bench', 'rack'],
    'dumbbell_bench_press': ['dumbbells', 'bench'],
    'cable_crossover': ['cables'],
    'walking_lunge': ['dumbbells', 'bodyweight'],
    # ... etc
}

def select_exercises(muscle_group, user_equipment):
    """
    HEALTHRAG ADVANTAGE OVER RP:
    - Filter by equipment (RP doesn't do this!)
    - Prioritize S/S+ tier (RP doesn't do this!)
    - Provide intelligent substitutions within tier
    """
    available = []

    # Check S+ tier first
    for ex in S_PLUS_TIER.get(muscle_group, []):
        if has_equipment(ex, user_equipment):
            available.append({'name': ex, 'tier': 'S+'})

    # Then S tier
    for ex in S_TIER.get(muscle_group, []):
        if has_equipment(ex, user_equipment):
            available.append({'name': ex, 'tier': 'S'})

    return available
```

**Week 7: Mesocycle Templates**
```python
# src/mesocycle_templates.py

TEMPLATES = {
    'upper_lower_4x': {
        'name': 'Upper/Lower 4x per Week',
        'days_per_week': 4,
        'split': {
            'day_1': 'upper',
            'day_2': 'lower',
            'day_3': 'upper',
            'day_4': 'lower'
        },
        'muscle_groups': {
            'upper': ['chest', 'back', 'shoulders', 'biceps', 'triceps'],
            'lower': ['quads', 'hamstrings', 'glutes', 'calves']
        },
        'volume_per_muscle': {
            'chest': 12,  # sets per week (starting volume)
            'back': 14,
            'quads': 14,
            'glutes': 10,
            # ... etc
        }
    },
    'ppl_6x': {
        'name': 'Push/Pull/Legs 6x per Week',
        # ... etc
    }
}
```

**Week 8: Volume Prescription + Progressive Overload**
```python
# src/volume_prescription.py

VOLUME_LANDMARKS = {
    'chest': {'MEV': 10, 'MAV': 16, 'MRV': 22},
    'back': {'MEV': 12, 'MAV': 18, 'MRV': 25},
    'quads': {'MEV': 12, 'MAV': 18, 'MRV': 24},
    # ... etc
}

def generate_mesocycle_progression(muscle_group, training_level, weeks=6):
    """
    HEALTHRAG = RP's volume progression approach
    """
    mev = VOLUME_LANDMARKS[muscle_group]['MEV']
    mav = VOLUME_LANDMARKS[muscle_group]['MAV']

    # Beginners start at MEV, advanced start near MAV
    if training_level == 'beginner':
        start_volume = mev
    elif training_level == 'intermediate':
        start_volume = (mev + mav) // 2
    else:  # advanced
        start_volume = mav - 2

    weekly_volumes = []
    for week in range(1, weeks + 1):
        if week == weeks:  # Deload week
            sets = int(start_volume * 0.5)
            rir = 3
        else:
            sets = start_volume + ((week - 1) * 2)  # Add 2 sets/week
            rir = 4 - week  # 3 RIR → 0 RIR

        weekly_volumes.append({
            'week': week,
            'sets': sets,
            'rir': max(0, rir)
        })

    return weekly_volumes
```

**HealthRAG Advantages Over RP:**
1. ✅ Equipment-aware exercise selection (RP doesn't have this!)
2. ✅ S/S+ tier prioritization (RP's auto-fill is poor)
3. ✅ Integrated nutrition (RP requires separate $35/month app)
4. ✅ Local/offline (RP is web-only)

### 📋 **PHASE 4: Tracking & Autoregulation (Week 9-12+)**

**MacroFactor-Inspired Features to Build:**

```python
# src/tracking.py

class NutritionTracker:
    """MacroFactor-style adaptive TDEE calculation"""

    def calculate_adaptive_tdee(self, weight_log, food_log, days=14):
        """
        HEALTHRAG = MacroFactor's adaptive algorithm

        1. Calculate trend weight (EWMA smoothing)
        2. Calculate weight change over period
        3. Calculate average calories over period
        4. Back-calculate TDEE from weight change + calories
        """
        trend_weights = self.calculate_trend_weight(weight_log)
        weight_change = trend_weights[-1] - trend_weights[0]  # lbs

        avg_calories = sum(food_log) / len(food_log)

        # Energy deficit/surplus in calories
        energy_delta = weight_change * 3500 / days  # 3500 cal = 1 lb

        # Actual TDEE = calories eaten + energy deficit
        tdee = avg_calories + energy_delta

        return tdee

    def calculate_trend_weight(self, daily_weights):
        """Exponentially weighted moving average (EWMA)"""
        alpha = 0.3  # Smoothing factor
        trend = [daily_weights[0]]

        for weight in daily_weights[1:]:
            new_trend = (alpha * weight) + ((1 - alpha) * trend[-1])
            trend.append(new_trend)

        return trend

    def adjust_macros_weekly(self, goal_rate, actual_rate, current_calories):
        """
        HEALTHRAG = MacroFactor's adherence-neutral adjustments

        Adjusts based on ACTUAL results, not adherence
        """
        if actual_rate > goal_rate * 1.2:  # Too fast
            return current_calories + 150
        elif actual_rate < goal_rate * 0.8:  # Too slow
            return current_calories - 100
        else:  # On track
            return current_calories
```

**RP Hypertrophy-Inspired Features to Build:**

```python
# src/workout_tracking.py

class WorkoutTracker:
    """RP-style feedback collection + autoregulation"""

    def collect_workout_feedback(self, muscle_group):
        """
        HEALTHRAG = RP's autoregulation system
        """
        feedback = {
            'pump': input("Pump quality (low/moderate/extreme): "),
            'soreness': input("Soreness healing (early/on-time/late): "),
            'disruption': input("Fatigue level (low/moderate/high): "),
            'joint_pain': input("Joint pain (none/mild/moderate/severe): "),
            'performance': input("Strength (increased/same/decreased): ")
        }

        return feedback

    def adjust_next_week_volume(self, current_sets, feedback):
        """
        HEALTHRAG = RP's volume adjustment logic
        """
        if feedback['pump'] == 'low' and feedback['soreness'] == 'early':
            return current_sets + 2  # Need more volume
        elif feedback['pump'] == 'extreme' and feedback['soreness'] == 'late':
            return current_sets - 1  # Too much volume
        elif feedback['joint_pain'] in ['moderate', 'severe']:
            return current_sets - 2  # Reduce volume, modify exercises
        else:
            return current_sets + 1  # Normal progression
```

**Additional Tracking (Beyond MacroFactor + RP):**

```python
# src/additional_tracking.py

- [ ] Body measurements (waist, chest, arms)
- [ ] Progress photos
- [ ] 10,000 steps/day tracking
- [ ] Sleep tracking
- [ ] Hydration tracking
- [ ] Period tracking (females)
- [ ] Custom habit tracking
```

### 📋 **PHASE 5: Advanced Features (Future)**

**HealthRAG-Specific Improvements:**

1. **Better Exercise Selection UI**
   - Show tier labels (S+/S/A/B)
   - Show equipment required
   - Show substitutions within tier
   - Exercise form videos/cues

2. **Rest Period Timers**
   - Evidence-based rest periods:
     - Compounds: 2-3 minutes
     - Isolation: 1-2 minutes
   - In-app timer widget

3. **Home Workout Modifications**
   - Substitute barbell → dumbbell/bodyweight
   - "Training at home today? Here are alternatives..."

4. **Injury Accommodation**
   - "Shoulder hurts? Avoid overhead pressing, try..."
   - Joint-friendly exercise substitutions

5. **Cardio Integration**
   - LISS/HIIT prescription
   - Integrate with 10K steps goal

6. **Recovery Metrics**
   - HRV tracking (if user has device)
   - Sleep quality integration
   - Readiness score

---

## 🎯 SUCCESS CRITERIA

**HealthRAG will surpass MacroFactor + RP when:**

### Nutrition (vs MacroFactor):
- ✅ TDEE calculation (basic - complete)
- 📋 Adaptive TDEE (trend weight + back-calculation - Phase 4)
- 📋 Adherence-neutral coaching (Phase 4)
- 📋 Food logging (Phase 4)
- 📋 Weekly macro adjustments (Phase 4)
- ✅ **ADVANTAGE:** Integrated with training (MacroFactor is nutrition-only)

### Training (vs RP Hypertrophy):
- 🔄 Exercise database (Phase 3, Week 5-6)
- 🔄 Mesocycle builder (Phase 3, Week 7-8)
- 🔄 Volume progression (Phase 3, Week 8)
- 📋 Autoregulation feedback (Phase 4)
- ✅ **ADVANTAGE:** Equipment-aware selection (RP doesn't have this)
- ✅ **ADVANTAGE:** S/S+ tier priority (RP's auto-fill is poor)
- ✅ **ADVANTAGE:** Integrated nutrition (RP requires separate app)

### Overall:
- ✅ **Free** (vs $47/month for both apps)
- ✅ **Local/offline** (vs web/mobile-only)
- ✅ **Integrated coach** (vs separate apps)
- ✅ **Equipment-first** (neither app has this)
- ✅ **Proactive UX** (dashboard shows plan automatically)

---

## 📚 REFERENCES

**MacroFactor:**
- Official Site: https://macrofactorapp.com/
- Algorithm Philosophy: https://macrofactorapp.com/macrofactors-algorithms-and-core-philosophy/
- Adherence-Neutral Explained: https://macrofactorapp.com/adherence-neutral/
- Dr. Muscle Review (2025): https://dr-muscle.com/macrofactor-app-review/
- Outlift Review: https://outlift.com/macrofactor-review/

**RP Hypertrophy App:**
- Official Site: https://rpstrength.com/pages/hypertrophy-app
- Dr. Muscle Review (2025): https://dr-muscle.com/rp-hypertrophy-app-review/
- Dr. Muscle Critique: https://dr-muscle.com/rp-hypertrophy-app-critique/

**HealthRAG Documentation:**
- WEEK3_PROGRESS.md (current implementation status)
- TIER_LIST_COVERAGE_ANALYSIS.md (95-100% S/S+ tier coverage)
- UX_VISION.md (dashboard mockup)

---

## 💡 IMMEDIATE NEXT ACTIONS

### 1. **Update Todo List for Phase 3**
Create new branch: `feat/phase3-program-generation`

### 2. **Week 5 Task: Exercise Database**
Create `src/exercise_database.py` with:
- S+ tier exercises (6 total from Jeff Nippard)
- S tier exercises (~27 total)
- Equipment requirements mapping
- Exercise selection logic (equipment-aware + tier-prioritized)

### 3. **Week 6 Task: Exercise Selection Engine**
Create `src/exercise_selection.py` with:
- `select_exercises(muscle_group, user_equipment, tier_priority)`
- `get_substitutions(exercise, user_equipment, same_tier=True)`
- Integration with user profile equipment list

### 4. **Week 7 Task: Mesocycle Templates**
Create `src/mesocycle_templates.py` with:
- Upper/Lower 4x template
- PPL 6x template
- Full Body 3x template
- Volume prescription per muscle group

### 5. **Week 8 Task: Progressive Overload**
Create `src/progression.py` with:
- `generate_mesocycle_progression(muscle, level, weeks=6)`
- Set accumulation logic
- RIR progression (3 → 0)
- Deload week (50% volume)

---

## 🎯 BOTTOM LINE

**We're building TWO $35/month apps into ONE free local app.**

**Total Market Value:** $563.76/year
**HealthRAG Cost:** $0

**Key Differentiators:**
1. ✅ Integrated (not separate nutrition + training apps)
2. ✅ Equipment-aware (neither competitor has this)
3. ✅ S/S+ tier exercise priority (RP's auto-fill is poor)
4. ✅ Local/offline (both competitors require internet)
5. ✅ Free (vs $47/month combined)

**Next Step:** Begin Phase 3 implementation (Exercise Database + Mesocycle Builder)
