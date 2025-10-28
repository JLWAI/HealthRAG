# HealthRAG: Intake Form Design
**Capturing Realistic Equipment & Gym Access**

---

## 🎯 THE PROBLEM

**Current System (TOO SIMPLE):**
```
Equipment: [dumbbells, bench, pull-up bar]
```

**Reality (COMPLEX):**
- User has access to MULTIPLE gyms with DIFFERENT equipment
- Convenience/distance varies (home gym vs 30 min drive)
- Program needs to prioritize convenient options
- Some equipment is available at multiple locations

---

## 📋 UPDATED INTAKE FORM

### Section 1: Personal Information
*(Already implemented in Week 1)*

- Name (e.g., "Jason")
- Weight, Height, Age, Sex
- Activity Level

---

### Section 2: Goals
*(Already implemented in Week 1)*

- Phase (cut, bulk, maintain, recomp)
- Target weight and timeline
- Primary goal

---

### Section 3: Training Schedule
*(Already implemented in Week 1)*

- Days per week (3-6)
- Minutes per session (30-120)
- Preferred split (full body, upper/lower, PPL, etc.)

---

### Section 4: **GYM ACCESS & EQUIPMENT** (NEW - EXPANDED)

This is where the magic happens - capturing REALISTIC gym access.

#### **Multi-Location Gym Access**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏋️ GYM ACCESS & EQUIPMENT

Where do you have access to train?

[Add Gym Location] ← User can add multiple

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 LOCATION 1 - Home Gym [Edit] [Remove]

   Location Name: Home Gym
   Type: [Home Gym] [Commercial Gym] [Other]

   Convenience:
   • [●] Primary (Use most often)
   • [ ] Secondary (Use occasionally)
   • [ ] Tertiary (Use rarely/special occasions)

   Distance: [At home ▼] (at home, 5 min, 10 min, 15 min, 30+ min)

   Available Equipment:

   ☑️ Free Weights
      ☑️ Dumbbells (5-75 lbs)
      ☐ Barbell
      ☐ Bumper Plates
      ☑️ Adjustable Bench
      ☑️ Flat Bench
      ☐ Squat Rack / Power Rack

   ☑️ Bodyweight
      ☑️ Pull-up Bar
      ☐ Dip Station
      ☑️ Resistance Bands

   ☐ Machines
      ☐ Cable Crossover
      ☐ Leg Press
      ☐ Leg Curl / Leg Extension
      ☐ Smith Machine
      ☐ Chest Press Machine
      ☐ Lat Pulldown Machine

   ☐ Specialty Equipment
      ☐ Trap Bar
      ☐ Safety Squat Bar
      ☐ Landmine
      ☐ Sled

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 LOCATION 2 - Planet Fitness [Edit] [Remove]

   Location Name: Planet Fitness
   Type: [Commercial Gym]

   Convenience:
   • [ ] Primary (Use most often)
   • [●] Secondary (Use occasionally)
   • [ ] Tertiary (Use rarely/special occasions)

   Distance: [10 min drive ▼]

   Available Equipment:

   ☑️ Free Weights
      ☑️ Dumbbells (5-75 lbs only)
      ☐ Barbell (Planet Fitness doesn't have free barbells)
      ☐ Bumper Plates
      ☑️ Adjustable Bench

   ☐ Bodyweight
      ☑️ Pull-up Bar (assisted)
      ☐ Dip Station

   ☑️ Machines
      ☑️ Smith Machine
      ☑️ Cable Crossover
      ☑️ Leg Press
      ☑️ Leg Curl / Leg Extension
      ☑️ Chest Press Machine
      ☑️ Lat Pulldown Machine

   Notes: "No free barbell, no squat rack - but great for machine work"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 LOCATION 3 - Air Force Base Gym [Edit] [Remove]

   Location Name: Air Force Base Gym
   Type: [Military/Government Gym]

   Convenience:
   • [ ] Primary (Use most often)
   • [ ] Secondary (Use occasionally)
   • [●] Tertiary (Use rarely/special occasions)

   Distance: [30+ min drive ▼]

   Available Equipment:

   ☑️ Free Weights
      ☑️ Dumbbells (5-150 lbs)
      ☑️ Barbell (multiple)
      ☑️ Bumper Plates
      ☑️ Competition Bench
      ☑️ Squat Rack / Power Rack (multiple)

   ☑️ Bodyweight
      ☑️ Pull-up Bar
      ☑️ Dip Station

   ☑️ Machines
      ☑️ Cable Crossover
      ☑️ Leg Press
      ☑️ All machines

   ☑️ Specialty Equipment
      ☑️ Deadlift Platform
      ☑️ Trap Bar
      ☑️ Safety Squat Bar
      ☑️ Landmine
      ☑️ Sled

   Notes: "Full powerlifting setup - great for heavy barbell work, but 30 min drive each way. Use for optional Saturday heavy day."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[+ Add Another Gym Location]

[Save Profile]
```

---

## 🗄️ DATA STRUCTURE

### Updated `profile.json`:

```json
{
  "personal_info": {
    "name": "Jason",
    "weight_lbs": 210,
    "height_inches": 71,
    "age": 26,
    "sex": "male",
    "activity_level": "sedentary"
  },
  "goals": {
    "phase": "cut",
    "target_weight_lbs": 185,
    "timeline_weeks": 24,
    "primary_goal": "fat_loss"
  },
  "schedule": {
    "days_per_week": 3,
    "minutes_per_session": 60,
    "preferred_split": "full_body"
  },
  "gym_locations": [
    {
      "id": "home_gym",
      "name": "Home Gym",
      "type": "home",
      "priority": "primary",
      "distance_minutes": 0,
      "equipment": {
        "free_weights": {
          "dumbbells": {"available": true, "range": "5-75 lbs"},
          "barbell": {"available": false},
          "adjustable_bench": {"available": true},
          "squat_rack": {"available": false}
        },
        "bodyweight": {
          "pull_up_bar": {"available": true},
          "dip_station": {"available": false},
          "resistance_bands": {"available": true}
        },
        "machines": {
          "cables": {"available": false},
          "leg_press": {"available": false}
        }
      },
      "notes": "Most convenient, use for majority of workouts"
    },
    {
      "id": "planet_fitness",
      "name": "Planet Fitness",
      "type": "commercial",
      "priority": "secondary",
      "distance_minutes": 10,
      "equipment": {
        "free_weights": {
          "dumbbells": {"available": true, "range": "5-75 lbs"},
          "barbell": {"available": false},
          "adjustable_bench": {"available": true}
        },
        "machines": {
          "smith_machine": {"available": true},
          "cables": {"available": true},
          "leg_press": {"available": true},
          "leg_curl": {"available": true},
          "chest_press_machine": {"available": true}
        }
      },
      "notes": "No free barbell, no squat rack - but great for machine work"
    },
    {
      "id": "af_base_gym",
      "name": "Air Force Base Gym",
      "type": "military",
      "priority": "tertiary",
      "distance_minutes": 30,
      "equipment": {
        "free_weights": {
          "dumbbells": {"available": true, "range": "5-150 lbs"},
          "barbell": {"available": true, "count": "multiple"},
          "bumper_plates": {"available": true},
          "competition_bench": {"available": true},
          "squat_rack": {"available": true, "count": "multiple"}
        },
        "bodyweight": {
          "pull_up_bar": {"available": true},
          "dip_station": {"available": true}
        },
        "machines": {
          "cables": {"available": true},
          "leg_press": {"available": true},
          "all_standard_machines": {"available": true}
        },
        "specialty": {
          "deadlift_platform": {"available": true},
          "trap_bar": {"available": true},
          "safety_squat_bar": {"available": true},
          "sled": {"available": true}
        }
      },
      "notes": "Full powerlifting setup - use for optional Saturday heavy barbell day"
    }
  ],
  "created_at": "2025-10-28T10:00:00Z",
  "updated_at": "2025-10-28T10:00:00Z"
}
```

---

## 🏋️ HOW THIS AFFECTS PROGRAM GENERATION (Phase 3)

### Program Generation Logic:

```python
def generate_weekly_program(profile: UserProfile) -> WeeklyProgram:
    """
    Generate program prioritizing primary gym, with secondary/tertiary options.
    """

    # Get gym locations sorted by priority
    primary_gym = profile.get_gym_by_priority('primary')
    secondary_gym = profile.get_gym_by_priority('secondary')
    tertiary_gym = profile.get_gym_by_priority('tertiary')

    days_per_week = profile.schedule.days_per_week

    # Strategy: Use primary gym for most workouts
    program = WeeklyProgram()

    if days_per_week == 3:
        # Full Body 3x/week - ALL at primary gym (home gym)
        program.add_workout('Monday', 'Full Body A', gym=primary_gym)
        program.add_workout('Wednesday', 'Full Body B', gym=primary_gym)
        program.add_workout('Friday', 'Full Body A', gym=primary_gym)

    elif days_per_week == 4:
        # Upper/Lower - Mix primary + secondary if needed
        program.add_workout('Monday', 'Upper A', gym=primary_gym)

        # If primary gym lacks leg equipment, suggest secondary
        if not primary_gym.has_leg_equipment():
            program.add_workout('Tuesday', 'Lower A', gym=secondary_gym,
                              reason="Planet Fitness has leg press/leg curl machines you don't have at home")
        else:
            program.add_workout('Tuesday', 'Lower A', gym=primary_gym)

        program.add_workout('Thursday', 'Upper B', gym=primary_gym)
        program.add_workout('Saturday', 'Lower B', gym=primary_gym)

    # Add optional tertiary gym workout (e.g., Air Force base)
    if tertiary_gym and tertiary_gym.has_equipment('squat_rack', 'barbell'):
        program.add_optional_workout('Saturday', 'Heavy Barbell Day', gym=tertiary_gym,
                                    reason="Optional: Use Air Force base for heavy squats/deadlifts if you have time (30 min drive)")

    return program
```

### Example Program Output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 JASON'S WEEKLY PROGRAM - Week 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 MONDAY - Upper Body A (Home Gym)
   Duration: 45-60 min
   Location: Home Gym (most convenient)

   1. Dumbbell Bench Press: 4 sets × 8-10 reps @ 50 lbs
   2. Dumbbell Rows: 4 sets × 8-10 reps @ 60 lbs
   3. Overhead Press: 3 sets × 10-12 reps @ 30 lbs
   4. Pull-ups: 3 sets × 6-10 reps (bodyweight or band-assisted)
   5. Dumbbell Curls: 2 sets × 12-15 reps @ 25 lbs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 WEDNESDAY - Lower Body (Planet Fitness - 10 min drive)
   Duration: 60 min
   Location: Planet Fitness
   Why here? You don't have leg press/leg curl at home

   1. Leg Press: 4 sets × 12-15 reps
   2. Leg Curl: 3 sets × 12-15 reps
   3. Goblet Squat (dumbbells): 4 sets × 12-15 reps @ 60 lbs
   4. Smith Machine RDLs: 3 sets × 10-12 reps
   5. Calf Raises: 4 sets × 15-20 reps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 FRIDAY - Upper Body B (Home Gym)
   Duration: 45-60 min
   Location: Home Gym (most convenient)

   1. Incline Dumbbell Press: 4 sets × 8-10 reps @ 45 lbs
   2. Single-Arm Dumbbell Rows: 4 sets × 10-12 reps @ 55 lbs each
   3. Lateral Raises: 3 sets × 12-15 reps @ 15 lbs
   4. Resistance Band Face Pulls: 3 sets × 15-20 reps
   5. Dumbbell Tricep Extensions: 2 sets × 12-15 reps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 SATURDAY (OPTIONAL) - Heavy Barbell Day (Air Force Base - 30 min drive)
   Duration: 60-75 min
   Location: Air Force Base Gym
   Why here? Full powerlifting setup for heavy barbell work

   Do this IF you have time and want to work on heavy barbell strength:

   1. Barbell Back Squat: 5 sets × 5 reps (heavy)
   2. Barbell Deadlift: 4 sets × 5 reps (heavy)
   3. Barbell Bench Press: 5 sets × 5 reps
   4. Barbell Rows: 4 sets × 8 reps

   Skip this if: You're busy, weather is bad, or you're feeling fatigued.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 KEY BENEFITS

### 1. **Realistic Convenience**
- Most workouts at home gym (most convenient)
- Planet Fitness for leg day (you lack leg equipment at home)
- Air Force base is optional (30 min drive, only if you have time)

### 2. **Smart Equipment Matching**
- Program knows what's available at each gym
- Only recommends exercises you can actually do
- Suggests location swaps when beneficial ("Planet Fitness has leg press you don't have at home")

### 3. **Flexible Optional Workouts**
- Air Force base barbell day is marked OPTIONAL
- "Skip this if you're busy or fatigued"
- Not required for progress, just a bonus

### 4. **Trackable & Location-Aware**
- Each workout shows location
- Shows drive time
- Shows why that location was chosen

---

## 📋 IMPLEMENTATION PHASES

### Phase 2 Week 3 (Now): Update Profile System
- [ ] Add `name` field to profile
- [ ] Add `gym_locations` array to profile
- [ ] Update intake form with multi-location gym access
- [ ] Create equipment checklist UI

### Phase 3 Weeks 5-8: Program Generation
- [ ] `generate_weekly_program(profile)` uses gym priority
- [ ] Exercise selection filters by location equipment
- [ ] Display location per workout ("Monday - Home Gym")
- [ ] Add "Why this location?" explanations

### Phase 4 Weeks 10-14: Progress Tracking
- [ ] Log which gym you actually used
- [ ] Track adherence per location
- [ ] Adjust if user consistently skips tertiary gym

---

## ✅ ACCEPTANCE CRITERIA

### Intake Form:
1. ✅ User can add multiple gym locations
2. ✅ Each location has priority (primary, secondary, tertiary)
3. ✅ Each location has distance/convenience
4. ✅ Each location has equipment checklist
5. ✅ User can add notes per location

### Program Generation (Phase 3):
1. ✅ Program prioritizes primary gym for most workouts
2. ✅ Program suggests secondary gym when beneficial (e.g., better equipment)
3. ✅ Program marks tertiary gym workouts as OPTIONAL
4. ✅ Each workout shows location and reason why
5. ✅ Only recommends exercises available at that gym

### User Experience:
1. ✅ Jason sees: "Monday - Home Gym (most convenient)"
2. ✅ Jason sees: "Wednesday - Planet Fitness (10 min drive) - you don't have leg press at home"
3. ✅ Jason sees: "Saturday (OPTIONAL) - Air Force Base (30 min) - heavy barbell work"
4. ✅ Jason can skip optional workouts without guilt

---

## 🎯 SUMMARY

**The user is RIGHT:** The app needs to know:
- What equipment you have access to
- WHERE that equipment is located
- How CONVENIENT each location is
- What exercises are REALISTIC at each location

This enables **realistic program generation** that:
- Prioritizes convenience (home gym 3-4x/week)
- Suggests secondary gyms strategically (Planet Fitness for leg day)
- Marks inconvenient gyms as optional (Air Force base for heavy barbell work)

**Next Steps:**
1. Add multi-location gym access to intake form (Week 3)
2. Use this data for program generation (Phase 3, Weeks 5-8)
3. Track actual gym usage (Phase 4, Weeks 10-14)

This is a GREAT insight! 💪
