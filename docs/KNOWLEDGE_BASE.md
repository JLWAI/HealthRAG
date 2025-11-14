# HealthRAG Knowledge Base Summary

**For Claude Web/Cloud**: This document summarizes the content of 28 PDFs (310MB) that are stored locally and gitignored for privacy/copyright reasons.

**Last Updated**: 2025-11-04

---

## 📚 Document Inventory

### Renaissance Periodization (RP) - Nutrition & Training
- **EBOOK_Renaissance_Diet_2.0.pdf** (10 MB) - Comprehensive diet manual
- **EBOOK_Simply_RP.pdf** (8.9 MB) - Simplified RP nutrition
- **EBOOK_Time_To_Eat.pdf** (7.1 MB) - Meal timing strategies
- **November 7th, 2023, The Diet Adjustments Manual v.3.0.9..pdf** (70 MB) - Latest diet adjustments
- **RP_6_Month_Hypertrophy_App-Fat_Loss.pdf** (845 KB) - 6-month cutting program
- **RP_6_Month_Hypertrophy_App-Muscle_Gain.pdf** (737 KB) - 6-month bulking program

### Jeff Nippard - Exercise Science
- **Jeff Nippard's Tier List.pdf** (50 KB) - S/A/B/C exercise rankings (KEY RESOURCE)
- **S Tier Exercises.rtf** - Top exercises by muscle group (see `EXERCISE_TIERS.json`)
- **Fundamentals_Hypertrophy_Program.pdf** (12 MB) - Complete program with tracking
- **THE_MUSCLE_LADDER_-_EBOOK_-_07_-_10.11.24.pdf** (10 MB) - Advanced training strategies

### RP Training Science
- **Ebook_Scientific_Principles_of_Hypertrophy_Training.pdf** (4.7 MB) - Science-based training
- **Ebook_An_Intro_To_Volume_Landmarks.pdf** (10 MB) - MEV/MAV/MRV concepts (CRITICAL)
- **Ebook_Recovering_From_Training.pdf** (19 MB) - Recovery protocols

### Program Templates
- **The_Min-Max_Program__4X.pdf** (57 MB) - 4-day split
- **The_Min-Max_Program__5X.pdf** (67 MB) - 5-day split
- **Min-Max_Program_4x.xlsx** (113 KB) - Excel tracking
- **Min-Max_Program_5x.xlsx** (131 KB) - Excel tracking
- **Fundamentals_Hypertrophy_Program_Excel_Tracking_Sheet.xlsx** (251 KB)

### Body For Life Movement (BFFM) - Old School Bodybuilding
- **BFFM_2012_Version.pdf** (2.2 MB)
- **bffm2003-2.pdf** (2.0 MB)
- **The_Ultimate_Guide_to_Body_Recomposition.pdf** (20 MB)

### Nutrition Guides
- **abfood.pdf** (862 KB), **food1.pdf** (669 KB), **food2.pdf** (864 KB)
- **bodyfat.pdf** (853 KB), **selfimage.pdf** (769 KB)
- **Download-Weekly-Shopping-List1.pdf** (58 KB)
- **shopping-list.pdf** (339 KB)
- **paleo-quick-start-guide.pdf** (38 KB)
- **whole9-seasonal-produce-2012.pdf** (3.0 MB)

### Personal Health
- **Primary Care Note 10-06-2025.pdf** (29 KB) - Medical records
- **6_Month_Diet_App_Challenge_Pack-FatLoss.pdf** (1.4 MB)

---

## 🏋️ Exercise Tier List (Jeff Nippard)

**Source**: S Tier Exercises.rtf, Jeff Nippard's Tier List.pdf

**Tier System**: S+ (best of the best) > S (excellent) > A (great) > B (good) > C (acceptable)

### **Glutes**
- **S+ Tier**: Walking lunge
- **S Tier**: Machine hip abductions (also #1 for upper glutes), Walking lunges, Elevated front foot lunges, 45° back extension

### **Quads**
- **S+ Tier**: Hack squat (alternate: High bar barbell back squat)
- **S Tier**: Barbell back squat, Hack squat, Pendulum squat, Smith machine squat, Bulgarian split squats

### **Triceps**
- **S+ Tier**: Overhead cable tricep extension
- **S Tier**: Overhead cable triceps extension, Skull crushers

### **Back**
- **S+ Tier**: Chest supported row
- **S Tier**: Wide grip lat pulldowns, Neutral grip lat pulldowns, Half kneeling one arm lat pulldowns, Chest supported rows, Cable rows, Wide grip cable rows, Reverse pec deck (sitting sideways)

### **Biceps**
- **S+ Tier**: Face away Bayesian cable curl (alternate: 45° preacher curl)
- **S Tier**: Preacher curl, Machine preacher curl, Face away Bayesian cable curl

### **Shoulders**
- **S+ Tier**: Cable lateral raise (for overall shoulder development)
- **S Tier**: Cable lateral raise, Cable Y raise, Behind the back cuffed lateral raise, Reverse cable crossover (#1 rear delt builder)
- **Front Delts #1**: Machine shoulder press
- **Side Delts #1**: Cable lateral raise

**Note**: Full exercise database with 200+ exercises stored in `src/exercise_database.py` with tier rankings, equipment requirements, and muscle group targets.

---

## 🎛️ Equipment Profiles

**Source**: `src/exercise_alternatives.py`, `src/profile.py`, PDF programs

See `EQUIPMENT_INVENTORY.json` for complete machine-readable data.

### **Jason's Home Gym** (24 items, ~85% exercise coverage)
**Barbell Setup**: Barbell, J-hooks, Squat rack
**Smith Machine**: Smith machine, Smith squat rack, Smith bench press (rare for home gym!)
**Dumbbells**: Full dumbbell set
**Benches**: Flat bench, Incline bench, Decline bench
**Machines**: Leg extension, Leg curl, Lat pulldown, Cable row, Chest press, Lateral raise
**Cable System**: Dual cable/functional trainer
**Other**: Pull-up bar, Landmine, Treadmill, Rowing machine, Elliptical

**Key Strengths**: Free barbell compound lifts, Smith machine for safety, complete leg machines, dual cable system

### **Planet Fitness** (28 items, ~75% exercise coverage)
**Machines**: Smith machine, Leg press, Hack squat, Chest press, Shoulder press, Pec deck
**Isolation**: Leg extension, Leg curl, Lat pulldown, Seated row, Bicep curl, Tricep extension, Lateral raise, Rear delt
**Dumbbells**: Dumbbells, Kettlebells
**Functional**: TRX, Battle ropes, Medicine balls, BOSU balls, Functional trainer
**Cardio**: Treadmill, Elliptical, Rowing machine

**Limitations**: ❌ No barbell, ❌ No free squat rack, ❌ No pull-up bar (has assisted machine)

### **Shared Equipment** (13 items)
Dumbbells, Smith machine, Cables, Functional trainer, Leg extension, Leg curl, Chest press, Lateral raise, Lat pulldown, Treadmill, Elliptical, Rowing machine, Bodyweight

### **Equipment Presets** (from `src/profile.py`)
- `minimal` (3): Bodyweight, Resistance bands, Dumbbells
- `home_gym_basic` (5): Dumbbells, Bench, Pull-up bar, Bands, Bodyweight
- `home_gym_advanced` (23): Jason's full home gym
- `planet_fitness` (27): Planet Fitness equipment
- `home_gym_plus_pf` (33): Combined (best of both worlds)
- `commercial_gym` (34): Full commercial gym (maximum coverage)

---

## 📊 Volume Landmarks (RP)

**Source**: Ebook_An_Intro_To_Volume_Landmarks.pdf

**Key Concepts**:
- **MV (Maintenance Volume)**: Sets needed to maintain muscle mass
- **MEV (Minimum Effective Volume)**: Sets needed to make gains
- **MAV (Maximum Adaptive Volume)**: Optimal sets for most gains
- **MRV (Maximum Recoverable Volume)**: Max sustainable sets before overtraining

**General Guidelines** (sets per muscle group per week):

| Muscle Group | MEV | MAV | MRV | Notes |
|--------------|-----|-----|-----|-------|
| **Chest** | 8-10 | 12-16 | 18-22 | Responds well to frequency |
| **Back** | 10-14 | 16-20 | 22-28 | Can handle high volume |
| **Shoulders** | 8-12 | 14-18 | 20-26 | Anterior delts recover faster |
| **Biceps** | 6-8 | 10-14 | 16-20 | Small muscle, lower volume |
| **Triceps** | 6-10 | 12-16 | 18-22 | Gets work from pressing |
| **Quads** | 8-10 | 12-16 | 18-24 | High work capacity |
| **Hamstrings** | 6-8 | 10-14 | 16-20 | Lower than quads |
| **Glutes** | 6-8 | 10-14 | 16-22 | Responds to hip thrusts |
| **Calves** | 8-10 | 12-16 | 18-24 | High frequency helpful |
| **Abs** | 10-14 | 16-20 | 24-30 | Daily work tolerated |

**Experience Level Adjustments**:
- **Beginner**: Start at MEV, progress slowly
- **Intermediate**: Work in MEV-MAV range
- **Advanced**: Can approach MAV-MRV temporarily

**Deload Guidelines**:
- Every 4-8 weeks (individual variability)
- Reduce volume to 40-50% of MRV
- Maintain intensity (weight on bar)
- 1 week duration typical

---

## 🍽️ Nutrition Guidelines (RP)

**Sources**: EBOOK_Renaissance_Diet_2.0.pdf, EBOOK_Simply_RP.pdf, The Diet Adjustments Manual v.3.0.9

### **Protein Recommendations** (g/lb bodyweight)

| Phase | Protein | Rationale |
|-------|---------|-----------|
| **Cutting** | 1.0-1.2 g/lb | Preserve muscle in deficit |
| **Maintenance** | 0.8-1.0 g/lb | Sustain muscle mass |
| **Bulking** | 0.8-1.0 g/lb | Build muscle in surplus |
| **Recomp** | 1.0-1.2 g/lb | High protein aids fat loss |

### **Fat Recommendations**

| Phase | Fat % of Calories | Fat g/lb | Notes |
|-------|------------------|----------|-------|
| **Cutting** | 20-30% | 0.3-0.4 g/lb | Lower end for faster loss |
| **Maintenance** | 25-35% | 0.4-0.5 g/lb | Hormonal health |
| **Bulking** | 20-30% | 0.3-0.4 g/lb | More carbs for training |

### **Carb Recommendations**
- **Remainder calories** after protein and fat
- **Cutting**: Lower carbs (150-250g typical)
- **Bulking**: Higher carbs (300-500g+ typical)
- **Timing**: Prioritize around training

### **TDEE Calculation** (Mifflin-St Jeor)

**Males**:
```
BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
TDEE = BMR × Activity Factor
```

**Females**:
```
BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161
TDEE = BMR × Activity Factor
```

**Activity Factors**:
- Sedentary (1.2): Little/no exercise
- Light (1.375): 1-3 days/week
- Moderate (1.55): 3-5 days/week
- Active (1.725): 6-7 days/week
- Very Active (1.9): 2x/day training

### **Calorie Adjustments by Phase**

| Phase | TDEE Adjustment | Weekly Change | Notes |
|-------|----------------|---------------|-------|
| **Cutting** | -500 cal | -1 lb/week | Aggressive |
| **Cutting (Slow)** | -250 cal | -0.5 lb/week | Sustainable |
| **Maintenance** | 0 cal | 0 lb/week | Body recomp possible |
| **Lean Bulk** | +300 cal | +0.5 lb/week | Minimize fat gain |
| **Aggressive Bulk** | +500 cal | +1 lb/week | Faster muscle, more fat |

### **Meal Frequency & Timing** (RP)
- **3-5 meals per day** optimal for muscle protein synthesis
- **Pre-workout** (1-3 hours): Protein + carbs
- **Post-workout** (0-2 hours): Protein + carbs (anabolic window overblown but helpful)
- **Evening meal**: Can be higher fat (training day dependent)

### **Diet Adjustments** (from The Diet Adjustments Manual v.3.0.9)
- **Week 1-2**: Assess baseline (weight, energy, hunger, cravings, gym performance)
- **Week 3+**: Adjust every 7-14 days based on rate of weight change
- **Adherence-neutral adjustments**: Change calories based on actual vs. target rate
- **Thresholds**: ±20% variance = no change, ±50% = ±150 cal, otherwise ±100 cal

**MacroFactor-Style Adaptive TDEE** (RP-aligned):
- Track weight daily, calculate EWMA (Exponential Weighted Moving Average, α=0.3)
- Back-calculate TDEE: `TDEE = Avg_Calories + (Weight_Change × 3500 / Days)`
- Adjust macros weekly based on trend

---

## 🏋️ Program Templates

### **The Min-Max Program** (4x/week or 5x/week)

**Source**: The_Min-Max_Program__4X.pdf, The_Min-Max_Program__5X.pdf

**Training Split**:
- **4x/week**: Upper/Lower/Upper/Lower
- **5x/week**: Upper/Lower/Push/Pull/Legs

**Progression Scheme**:
- 6-week mesocycles
- Week 1-2: 10-12 reps, RIR 3-4
- Week 3-4: 8-10 reps, RIR 2-3
- Week 5: 6-8 reps, RIR 1-2
- Week 6: Deload (50% volume)

**Volume**: 12-18 sets per muscle group per week (MAV range)

**Equipment Flexibility**: "I based the program on equipment you'll find in most commercial gyms. But if your gym doesn't have a specific machine or apparatus, or you train at home with limited options, just make the appropriate substitution."

### **Fundamentals Hypertrophy Program** (Jeff Nippard)

**Source**: Fundamentals_Hypertrophy_Program.pdf

**Training Split**: Upper/Lower 4x/week
**Duration**: 6 weeks
**Progression**: Linear progression with RIR-based autoregulation
**Volume**: 10-14 sets per muscle group per week (MEV-MAV)
**Target Audience**: Beginners to early intermediates

**Key Features**:
- 30+ exercise alternatives provided
- Equipment substitution guide (pages 33-36)
- Emphasis on form over load
- Progressive overload via weight/reps/RIR

### **RP 6-Month Hypertrophy App Programs**

**Sources**: RP_6_Month_Hypertrophy_App-Fat_Loss.pdf, RP_6_Month_Hypertrophy_App-Muscle_Gain.pdf

**Structure**:
- 6 months / 24 weeks
- 4-week mesocycles with 1-week deloads
- Progressive volume accumulation
- App-based tracking and autoregulation

**Fat Loss**: Higher frequency (5-6x/week), MEV-MAV volume, emphasis on metabolic work
**Muscle Gain**: 4-5x/week, MAV-MRV volume, focus on progressive overload

---

## 📈 Progressive Overload Strategies

**Source**: Ebook_Scientific_Principles_of_Hypertrophy_Training.pdf

**Progression Hierarchy** (in order of preference):
1. **Add reps** (within target range, e.g., 8-12 reps)
2. **Add weight** (when top of rep range achieved)
3. **Add sets** (if volume still in MEV-MAV range)
4. **Improve technique** (better muscle engagement)
5. **Increase ROM** (range of motion)
6. **Decrease rest** (advanced technique)

**RIR-Based Progression** (Reps in Reserve):
- **RIR 4**: Could do 4 more reps (far from failure)
- **RIR 2-3**: Ideal for hypertrophy (most sets)
- **RIR 1**: Very close to failure (occasional)
- **RIR 0**: Absolute failure (rare, risky)

**Weekly Progression Example**:
- Week 1: 3×10 @ 135 lbs, RIR 3
- Week 2: 3×11 @ 135 lbs, RIR 2.5
- Week 3: 3×12 @ 135 lbs, RIR 2
- Week 4: 3×10 @ 140 lbs, RIR 3 ← Add weight, reset reps

---

## 🩺 Recovery & Deload Principles

**Source**: Ebook_Recovering_From_Training.pdf

**Signs You Need a Deload**:
- Strength plateau/regression for 2+ weeks
- Persistent soreness (>48 hours)
- Poor sleep quality
- Elevated resting heart rate
- Loss of motivation/gym enthusiasm
- Joint pain (not DOMS)

**Deload Methods**:
1. **Volume Deload** (recommended): 40-50% normal volume, maintain weight
2. **Intensity Deload**: Normal volume, reduce weight 10-20%
3. **Active Rest**: Light cardio, mobility work, no heavy lifting

**Deload Frequency**:
- **Beginners**: Every 8-12 weeks
- **Intermediates**: Every 6-8 weeks
- **Advanced**: Every 4-6 weeks
- **During cuts**: Every 4 weeks (faster fatigue accumulation)

---

## 🎯 Current Implementation Status

**What's Already Built** (See `src/` directory):
- ✅ Exercise database (`exercise_database.py`) - 200+ exercises with tier rankings
- ✅ Volume prescription (`volume_prescription.py`) - MEV/MAV/MRV by muscle/experience
- ✅ Progressive overload (`progressive_overload.py`) - RIR-based progression
- ✅ Exercise alternatives (`exercise_alternatives.py`) - Equipment-aware substitutions
- ✅ Program generator (`program_generator.py`) - 6-week mesocycle generation
- ✅ Workout tracking (`workout_logger.py`, `workout_database.py`) - SQLite logging
- ✅ Nutrition tracking (`food_logger.py`, `meal_templates.py`) - Meal logging with templates
- ✅ USDA FDC integration (`food_api_fdc.py`) - 400K foods
- ✅ Open Food Facts (`food_api_off.py`) - 2.8M products, barcode scanning

**What's Missing** (Phase 4 Priority):
- ❌ Adaptive TDEE algorithm (MacroFactor-style EWMA + back-calculation)
- ❌ Weekly macro adjustments (adherence-neutral recommendations)
- ❌ Body measurements tracking
- ❌ Progress photos
- ❌ Monthly progress reports

---

## 📝 How to Use This Knowledge Base

**For Claude Web/Cloud**:
1. **Exercise Selection**: Reference `EXERCISE_TIERS.json` for S/A/B tier rankings
2. **Equipment Constraints**: Check `EQUIPMENT_INVENTORY.json` for home vs. PF availability
3. **Volume Prescription**: Use MEV/MAV/MRV tables above for program design
4. **Nutrition Calculations**: Apply RP formulas (protein 1.0-1.2 g/lb, fat 0.3-0.5 g/lb)
5. **Program Structure**: Follow 6-week mesocycle template with weekly RIR progression

**For Local Development**:
- All data structures already implemented in `src/` Python modules
- JSON files provide machine-readable data for API/UI consumption
- PDFs remain local for RAG queries via ChromaDB vectorstore

---

**Last Updated**: 2025-11-04
**Total Documents**: 28 PDFs (310 MB)
**Total Structured Data Files**: 3 JSON + 1 Markdown
