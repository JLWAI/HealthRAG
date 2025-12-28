# HealthRAG: Comprehensive Scenarios & Use Cases
**Production Development Guide for Phases 2-5**

---

## CORE PHILOSOPHY: DAILY AI COACH

**HealthRAG is NOT a static calculator or information retrieval system** - it's a **daily AI nutritional and exercise coach** that:
- Works with users daily to help reach their goals
- Tracks and analyzes results (weight, strength, body comp)
- Asks for data to provide intelligent coaching
- Adapts recommendations based on progress

**Every scenario in this document reflects this coaching mindset**:
- ❌ NOT: "Your TDEE is 2,600 calories" (static calculation)
- ✅ YES: "Based on your profile, your maintenance is ~2,600 cal. For cutting, I recommend 2,100 cal. We'll adjust based on your weekly weigh-ins." (coaching guidance)

**Daily Interactions**: Meal suggestions, workout logging, progress analysis, adjustment recommendations
**Weekly Check-Ins**: Weight trends, strength progression, body comp changes, calorie/volume adjustments
**Monthly Milestones**: Progress reports, program adjustments, phase transitions (cut → maintain, recomp → bulk)

---

## EXECUTIVE SUMMARY

This document defines 5 user personas, 12 core scenarios, 8 edge cases, and testing strategies to guide HealthRAG development from Phase 2 (current: Calculation Engine) through Phase 5 (Polish & Advanced Features). Each scenario is mapped to development phases with specific acceptance criteria, RAG citation requirements, and incremental testing checkpoints.

**Strategic Focus:**
- **Phase 2 (Current):** Profile-aware calculations (TDEE, macros) with RAG validation
- **Phase 3:** Template-based program generation using Jeff Nippard Tier List
- **Phase 4:** Progress tracking and adaptive adjustments
- **Phase 5:** Polish and user experience enhancements

**Reality Check:**
- Solo developer, 10-20 hours/week
- Must be testable incrementally
- Simple features first, valuable immediately
- 6-12 months to MVP with 50-100 users as success

---

## 1. USER PERSONAS

### PERSONA 1: "Beginner Ben" - The Newbie
**Demographics:**
- Age: 26, Male
- Weight: 210 lbs, Height: 5'11"
- Experience: 0 years training, complete beginner

**Goals:**
- Phase: Cut
- Target: 185 lbs in 24 weeks (1 lb/week)
- Primary Goal: Fat loss + learn proper training
- Timeline: 6 months

**Constraints:**
- Equipment: Home gym (dumbbells, bench, pull-up bar)
- Schedule: 3 days/week, 45-60 min/session
- Knowledge: Needs education on form, progression, nutrition basics
- Activity Level: Sedentary (desk job)

**Motivations:**
- Lost confidence, wants to look better
- Willing to learn but overwhelmed by information
- Needs simple, clear guidance
- Values evidence-based approach

**Phase Mapping:**
- **Phase 2:** Calculate TDEE (~2,600 → 2,100 cal deficit), macros (200g protein, 60g fat, rest carbs)
- **Phase 3:** Full-body 3x/week program using home gym equipment (A/B split recommended)
- **Phase 4:** Weekly weight tracking, adjust calories if rate < 0.75 lb/week
- **Phase 5:** Form video library, beginner education content

---

### PERSONA 2: "Intermediate Ian" - The Gym Regular
**Demographics:**
- Age: 32, Male
- Weight: 185 lbs, Height: 6'0"
- Experience: 5 years training (intermediate)

**Goals:**
- Phase: Bulk
- Target: 200 lbs in 20 weeks (0.75 lb/week)
- Primary Goal: Hypertrophy
- Timeline: 5 months

**Constraints:**
- Equipment: Commercial gym (full access)
- Schedule: 4 days/week, 60-75 min/session
- Knowledge: Understands basics, wants optimization
- Activity Level: Moderately active

**Motivations:**
- Plateau'd on generic programs
- Wants evidence-based programming
- Needs periodization and progression strategy
- Values efficiency (time-constrained professional)

**Phase Mapping:**
- **Phase 2:** Calculate TDEE (~2,800 → 3,175 cal surplus), macros (175g protein, 90g fat, rest carbs)
- **Phase 3:** Upper/Lower 4x/week using Min-Max 4X template, S/A-tier exercises
- **Phase 4:** Track performance (reps/weight), increase volume if no progression for 2 weeks
- **Phase 5:** Exercise substitution suggestions, deload recommendations

---

### PERSONA 3: "Cutting Claire" - The Female Lifter
**Demographics:**
- Age: 28, Female
- Weight: 145 lbs, Height: 5'5"
- Experience: 3 years training (intermediate)

**Goals:**
- Phase: Cut
- Target: 135 lbs in 16 weeks (0.625 lb/week)
- Primary Goal: Fat loss while maintaining strength
- Timeline: 4 months

**Constraints:**
- Equipment: Commercial gym (full access)
- Schedule: 5 days/week, 60 min/session
- Knowledge: Experienced, wants optimization for cutting
- Activity Level: Very active (trains 5x/week + cardio)

**Motivations:**
- Previous cuts lost too much muscle
- Wants to preserve strength during deficit
- Needs high protein, lower volume approach
- Values hunger management strategies

**Phase Mapping:**
- **Phase 2:** Calculate TDEE (~2,200 → 1,900 cal deficit), macros (135g protein, 50g fat, rest carbs), cite RP female-specific recommendations
- **Phase 3:** PPL 5x/week using Min-Max 5X template, reduced volume for deficit (-20% from maintenance)
- **Phase 4:** Track strength metrics, increase calories if strength drops >10%, refeed protocol
- **Phase 5:** Hunger management tips from RP, cardio integration

---

### PERSONA 4: "Recomp Ryan" - The Lean Gainer
**Demographics:**
- Age: 24, Male
- Weight: 165 lbs, Height: 5'10"
- Experience: 2 years training (intermediate)

**Goals:**
- Phase: Recomp
- Target: Maintain ~165 lbs, gain muscle, lose fat simultaneously
- Primary Goal: Body recomposition
- Timeline: 12+ weeks (long-term goal)

**Constraints:**
- Equipment: Home gym (barbell, dumbbells, rack, bench)
- Schedule: 4 days/week, 75 min/session
- Knowledge: Understands training, confused about recomp nutrition
- Activity Level: Moderately active

**Motivations:**
- "Skinny-fat," wants to look athletic
- Doesn't want to bulk/cut cycle
- Needs high volume, maintenance calories
- Values body composition over scale weight

**Phase Mapping:**
- **Phase 2:** Calculate TDEE (~2,600 maintenance), macros (165g protein, 70g fat, rest carbs), cite Jeff Nippard recomp guide
- **Phase 3:** Upper/Lower 4x/week, high volume (maintenance + 10%), emphasize progressive overload
- **Phase 4:** Track body composition (photos, measurements), adjust volume if no visual changes in 4 weeks
- **Phase 5:** Body composition estimation, progress photo comparison

---

### PERSONA 5: "Minimal Megan" - The Time-Crunched Professional
**Demographics:**
- Age: 35, Female
- Weight: 128 lbs, Height: 5'4"
- Experience: 1 year training (beginner+)

**Goals:**
- Phase: Maintain
- Target: Maintain current weight, general fitness
- Primary Goal: General fitness, stress management
- Timeline: Ongoing

**Constraints:**
- Equipment: Minimal (resistance bands, dumbbells only)
- Schedule: 2 days/week, 30-45 min/session (extremely limited)
- Knowledge: Knows basics, needs efficiency
- Activity Level: Lightly active

**Motivations:**
- High-stress job, limited time
- Wants to maintain health, not compete
- Needs minimalist approach that works
- Values consistency over intensity

**Phase Mapping:**
- **Phase 2:** Calculate TDEE (~1,850 maintenance), macros (105g protein, 50g fat, rest carbs)
- **Phase 3:** Full-body 2x/week, compound movements only, minimal equipment substitutions
- **Phase 4:** Track adherence (did workout happen?), adjust difficulty if too demanding
- **Phase 5:** Quick workout generator, time-saving supersets

---

## 2. CORE SCENARIOS

### SCENARIO 1: First-Time Profile Creation (All Personas)
**Phase:** 2 (Current)

**User Journey:**
1. User opens HealthRAG, sees "Create Your Profile" form
2. Enters personal info: weight, height, age, sex, activity level
3. Selects goals: phase (cut/bulk/maintain/recomp), target weight, timeline
4. Chooses equipment preset (minimal/home_gym/commercial_gym)
5. Sets schedule: days/week, minutes/session, preferred split
6. Clicks "Create Profile"

**System Response:**
```
✅ Profile created successfully!

=== YOUR PROFILE ===
Weight: 185 lbs
Height: 6'0"
Phase: Bulk
Equipment: Commercial Gym
Schedule: 4 days/week, 60 min/session
```

**Acceptance Criteria:**
- Profile saved to `/data/user_profile.json`
- All fields validated (weight 50-500 lbs, height 48-84 inches, age 13-100)
- Equipment preset applied correctly
- Timestamps (created_at, updated_at) added
- Profile loads on next visit

**RAG Citations:** None (pure data entry)

**Test Data:**
```python
# Beginner Ben
{
    'weight_lbs': 210, 'height_inches': 71, 'age': 26, 'sex': 'male',
    'phase': 'cut', 'target_weight_lbs': 185, 'timeline_weeks': 24,
    'equipment': EQUIPMENT_PRESETS['home_gym'], 'days_per_week': 3
}

# Intermediate Ian
{
    'weight_lbs': 185, 'height_inches': 72, 'age': 32, 'sex': 'male',
    'phase': 'bulk', 'target_weight_lbs': 200, 'timeline_weeks': 20,
    'equipment': EQUIPMENT_PRESETS['commercial_gym'], 'days_per_week': 4
}
```

---

### SCENARIO 2: Calculate TDEE & Macros ✅ IMPLEMENTED
**Phase:** 2 (Week 2 - COMPLETED)

**Implementation Status:** ✅ Complete (Week 2 Deliverable)
- ✅ src/calculations.py created with coaching-style guidance
- ✅ 25/25 tests passing in tests/test_calculations.py
- ✅ Integrated into src/main.py chat interface
- ✅ All 5 personas validated (Beginner Ben, Intermediate Ian, Cutting Claire, Recomp Ryan, Minimal Megan)
- ✅ Coaching mindset: Sets expectations, promises adaptation, cites RP sources

**User Query:** "What are my calories and macros for cutting?"

**System Process:**
1. Load user profile (Beginner Ben: 210 lbs, 5'11", 26, male, sedentary)
2. Calculate BMR using Mifflin-St Jeor equation
3. Apply activity multiplier (sedentary = 1.2)
4. Apply phase adjustment (cut = -500 cal)
5. Calculate macros (protein: 1g/lb, fat: 0.3-0.4g/lb, carbs: remainder)
6. Query RAG for validation/recommendations from RP diet guides

**Expected Output:**
```
Based on your profile (210 lbs, 5'11", 26, male, sedentary), here are your cutting macros:

**Maintenance TDEE:** ~2,600 calories
(BMR: ~2,170 cal × sedentary multiplier 1.2)

**Cutting Target:** ~2,100 calories (-500 cal deficit, ~1 lb/week loss)

**Macro Breakdown:**
- Protein: 210g (840 cal) - 40%
- Fat: 65g (585 cal) - 28%
- Carbs: 169g (675 cal) - 32%

**Source References:**
According to Renaissance Periodization's Diet 2.0 (Chapter 3), protein intake should be 1.0-1.2g per lb bodyweight during a cut to preserve muscle mass. Fat intake at 0.3-0.4g per lb supports hormone production while maximizing carbs for training performance.

For a 1 lb/week fat loss rate, a 500 calorie daily deficit is appropriate. RP recommends starting conservatively and adjusting based on weekly weigh-ins (Diet Adjustments Manual, p. 12).
```

**Acceptance Criteria:**
- TDEE calculation within 5% of standard formulas
- Protein: 0.8-1.2g per lb bodyweight (cite RP)
- Fat: 0.3-0.5g per lb bodyweight
- Carbs: Remainder after protein/fat
- Must cite specific PDF sources (RP Diet 2.0, Diet Adjustments Manual)
- Adjust for phase (cut: -500, bulk: +300-500, maintain: 0, recomp: 0)

**RAG Citations Required:**
- Renaissance Periodization Diet 2.0 (protein recommendations)
- RP Diet Adjustments Manual (deficit/surplus amounts)
- Jeff Nippard Fundamentals guide (macro ranges validation)

**Test Cases:**
```python
# Test 1: Male cutting
profile = {'weight_lbs': 210, 'height_inches': 71, 'age': 26, 'sex': 'male',
           'activity_level': 'sedentary', 'phase': 'cut'}
expected_tdee = 2100  # ±100 cal
expected_protein = 189-231  # 0.9-1.1g/lb

# Test 2: Female bulking
profile = {'weight_lbs': 135, 'height_inches': 65, 'age': 28, 'sex': 'female',
           'activity_level': 'very_active', 'phase': 'bulk'}
expected_tdee = 2600  # ±100 cal
expected_protein = 122-149  # 0.9-1.1g/lb

# Test 3: Male recomp
profile = {'weight_lbs': 165, 'height_inches': 70, 'age': 24, 'sex': 'male',
           'activity_level': 'moderately_active', 'phase': 'recomp'}
expected_tdee = 2600  # ±100 cal (maintenance)
expected_protein = 149-182  # 0.9-1.1g/lb
```

**Phase 2 Week 2 Deliverable:** This scenario must be fully implemented this week.

---

### SCENARIO 3: Query Training Principles (Phase 2)
**Phase:** 2 (Validates RAG system with profile context)

**User Query:** "How much volume do I need per week for muscle growth?"

**Expected Output:**
```
Based on your intermediate training level, here's what Renaissance Periodization recommends for weekly volume:

**Volume Landmarks (sets per muscle group per week):**
- **Maintenance Volume (MV):** 6-8 sets
- **Minimum Effective Volume (MEV):** 10-12 sets
- **Maximum Adaptive Volume (MAV):** 15-20 sets
- **Maximum Recoverable Volume (MRV):** 22-25 sets

As an intermediate lifter training 4 days per week, you should aim for 12-18 sets per muscle group per week initially, starting closer to MEV and progressing toward MAV over a training block.

**Source:** RP Hypertrophy Training Principles (Volume Landmarks chapter), Scientific Principles of Hypertrophy Training ebook.

**Your Program Recommendation:**
With 4 days/week and 60-75 min per session, an Upper/Lower split would allow approximately 14-16 sets per muscle group per week, falling in the optimal range for growth.
```

**Acceptance Criteria:**
- Must cite RP Volume Landmarks ebook
- Must contextualize based on user experience level (beginner: lower volume, advanced: higher volume)
- Must consider schedule constraints (days/week)
- Must differentiate between MV, MEV, MAV, MRV definitions

---

### SCENARIO 4: Program Template Selection (Phase 3, Week 5-6)
**Phase:** 3 (Weeks 5-6)

**User Request:** "Generate a training program for me"

**Expected Output:**
```
Based on your profile (4 days/week, 60-75 min/session, commercial gym access, intermediate level), I recommend:

**Program Template:** Jeff Nippard Min-Max 4X Program
**Split:** Upper/Lower (2 upper, 2 lower per week)
**Duration:** 4-6 week blocks with deload every 4-5 weeks

This template is optimized for:
- Time efficiency (60-75 min sessions)
- Hypertrophy focus (your goal: bulk)
- Intermediate volume (~14-16 sets per muscle/week)
- Compound movement emphasis

**Next Step:** I'll customize this template with S/A-tier exercises based on your equipment and generate your 4-week program.

Would you like to proceed with program generation?
```

**Acceptance Criteria:**
- Correct template match based on days/week
- Validate split compatibility (3 days = full body, 4 days = upper/lower, 5-6 days = PPL)
- Reference actual template files (Min-Max 4X.xlsx)
- Explain why template was chosen

---

### SCENARIO 5: Exercise Selection from Tier List (Phase 3, Week 7)
**Phase:** 3 (Week 7)

**User Profile:** Beginner Ben (home gym: dumbbells, bench, pull-up bar)

**Query:** "What are the best chest exercises I can do with my home gym?"

**Expected Output:**
```
Based on your equipment (dumbbells, bench, pull-up bar) and Jeff Nippard's Exercise Tier List:

**S-Tier Chest Exercises (Available to You):**
1. **Dumbbell Bench Press** - Primary chest builder
   - Alternative: Incline Dumbbell Bench Press (upper chest emphasis)

2. **Dumbbell Flyes** - Stretch and isolation
   - Alternative: Incline Dumbbell Flyes (upper chest)

**A-Tier Chest Exercises (Available):**
3. **Push-ups** - Bodyweight compound
   - Variations: Decline push-ups (weighted with backpack)

**B-Tier Options:**
4. **Squeeze Press** - Inner chest focus with dumbbells

**Not Available (S/A-Tier):**
- Barbell Bench Press (requires barbell) - S-Tier
- Cable Flyes (requires cables) - A-Tier
- Dips (requires dip station) - A-Tier

**Recommendation:** For a home gym chest workout, prioritize dumbbell bench press and flyes, supplemented with push-up variations. These will provide excellent chest development despite limited equipment.

**Source:** Jeff Nippard's Exercise Tier List (Chest section)
```

**Acceptance Criteria:**
- Filter exercises by user's available equipment
- Prioritize S-tier, then A-tier, then B-tier
- Provide alternatives within same tier
- Explain what's missing and why (S/A-tier exercises not available)
- Must cite Jeff Nippard Tier List

---

### SCENARIO 6: Complete Body Recomposition Journey (Phases 2-4)
**Phase:** 2-4 (Multi-phase scenario: Nutrition + Training + Tracking)

**User Profile:** Recomp Ryan (165 lbs, 5'10", 24, male, intermediate, "skinny-fat")

**User Goal:** "I want to build muscle and lose fat at the same time. I don't want to bulk and get fatter, and I don't want to cut and lose the little muscle I have. Is body recomposition possible for me?"

---

#### PART 1: Initial Assessment & Eligibility (Phase 2)

**System Response:**
```
Let me assess if body recomposition is appropriate for you.

**Body Recomposition Overview:**
Building muscle while losing fat simultaneously is possible, but it's NOT for everyone. It works best for specific populations and requires patience.

**Your Profile Analysis:**
- Weight: 165 lbs, Height: 5'10" (BMI: 23.7 - normal range)
- Training Experience: 2 years (intermediate)
- Current Phase: Not overweight, not underweight
- Goal: Improve body composition without weight change

**Who Recomp Works For (According to RP & Jeff Nippard):**
✅ **Complete beginners** (<6 months training) - newbie gains allow muscle growth in deficit
✅ **Returning after long layoff** (>6 months off) - muscle memory accelerates regrowth
✅ **Overweight individuals** (BMI >27) with minimal muscle - fat provides energy for muscle growth
❓ **Intermediate lifters** (1-3 years training) - possible but VERY slow progress

**Your Situation:**
You're an intermediate lifter (2 years training), which means recomp WILL work, but expect:
- **Slower progress** than bulk/cut cycles (3-6 months to see noticeable changes)
- **High training volume required** (push toward MAV - Maximum Adaptive Volume)
- **Strict adherence needed** (no calorie/macro flexibility)
- **Progress tracking via body comp** (photos, measurements) not scale weight

**Alternative Approaches:**
1. **Mini-Cut → Lean Bulk** (Recommended for faster results)
   - 6-8 week cut to 155 lbs (lose fat, reveal muscle)
   - 16-20 week bulk to 170 lbs (build muscle with minimal fat gain)
   - Net result: More muscle, leaner, in 6 months

2. **Body Recomposition** (Slower but no weight gain)
   - Maintain 165 lbs for 6-12 months
   - Gradual muscle gain, gradual fat loss
   - Net result: Same weight, better body comp, in 12 months

**Question:** Would you like to proceed with body recomposition (slower, no weight change) or try a mini-cut → lean bulk approach (faster, more effective)?

**Source:** Renaissance Periodization Diet 2.0 (Recomposition chapter), Jeff Nippard "Can You Build Muscle and Lose Fat?" video content
```

**User Response:** "I want to try recomp. I don't want to gain any weight right now."

---

#### PART 2: Nutrition Setup - Maintenance Calories & Macros (Phase 2, Week 2)

**System Process:**
1. Calculate TDEE at maintenance (no deficit/surplus)
2. Set macros: High protein, moderate fat, rest carbs
3. Explain recomp-specific nutrition principles

**System Response:**
```
Perfect! Let's set up your body recomposition nutrition plan.

**Your Maintenance TDEE:**
- BMR: ~1,800 cal (Mifflin-St Jeor formula)
- Activity Level: Moderately active (4 days/week training)
- TDEE: ~2,700 calories/day (maintenance)

**Body Recomp Calories:** 2,700 cal/day
- **No deficit** - eating below maintenance will prioritize fat loss over muscle gain
- **No surplus** - eating above maintenance will add fat faster than muscle
- **Exact maintenance** - creates optimal environment for slow recomp

**Macro Breakdown:**
- **Protein:** 180g (720 cal) - 27%
  - **Higher than bulk/cut:** 1.1g per lb bodyweight (recomp needs max protein)
  - Supports muscle protein synthesis despite no calorie surplus

- **Fat:** 75g (675 cal) - 25%
  - 0.45g per lb - supports hormone production

- **Carbs:** 330g (1,320 cal) - 48%
  - High carbs fuel intense training volume required for recomp

**Recomp-Specific Nutrition Principles:**

1. **Protein Timing Matters MORE:**
   - Distribute evenly across 4 meals (~45g per meal)
   - Pre/post-workout protein critical (muscle protein synthesis window)
   - Source: RP Diet 2.0 recommends 0.4-0.5g/kg per meal for recomp

2. **Carb Cycling Optional:**
   - Higher carbs on training days (350g)
   - Lower carbs on rest days (310g)
   - Maintains weekly average of 2,700 cal

3. **STRICT Adherence Required:**
   - ±50 calorie tolerance (not ±200 like bulk/cut)
   - Track daily, weigh food initially
   - Recomp is unforgiving - small errors stall progress

4. **No Cheat Meals:**
   - Even one weekly cheat meal can erase your small surplus/deficit
   - Save cheat meals for bulk/cut phases

**Tracking:**
- Weigh daily, track weekly average (should stay 164-166 lbs)
- If weight increases >2 lbs over 2 weeks: Reduce calories 100-150
- If weight decreases >2 lbs over 2 weeks: Increase calories 100-150

**Expected Timeline:**
- Weeks 1-4: No visible changes (body adapting)
- Weeks 5-8: Slight strength gains, minor visual changes
- Weeks 9-12: Noticeable body comp improvement (clothes fit differently)
- Months 4-6: Clear muscle definition, lost 1-2% body fat, gained 2-4 lbs muscle

**Source:** Renaissance Periodization Diet 2.0 (Recomposition Nutrition), RP Time To Eat (Protein Timing), Jeff Nippard Fundamentals (Recomp Macros)

Ready to see your training program?
```

---

#### PART 3: Training Approach - High Volume for Recomp (Phase 3, Week 8)

**User Query:** "Generate my recomp training program"

**System Process:**
1. Load Min-Max 4X template (4 days/week, Upper/Lower)
2. Increase volume by 10-15% over standard intermediate volume
3. Emphasize progressive overload (strength gains = muscle gains)
4. Select exercises prioritizing S/A-tier compounds

**System Response:**
```
=== YOUR BODY RECOMPOSITION TRAINING PROGRAM ===

**Program:** Modified Min-Max 4X (High Volume for Recomp)
**Split:** Upper/Lower, 4 days/week
**Volume:** 18-20 sets per muscle group per week (higher than standard 14-16)
**Focus:** Progressive overload, compound movements, high training density

**Why High Volume for Recomp?**
According to RP Volume Landmarks, body recomposition requires training stimulus ABOVE what's needed for maintenance. You'll train closer to MAV (Maximum Adaptive Volume) to signal muscle growth despite no calorie surplus.

---

**WEEK 1-4 PROGRAM:**

**UPPER DAY 1 (Monday) - STRENGTH FOCUS**
1. Barbell Bench Press: 4 sets × 6-8 reps (S-Tier)
2. Barbell Rows: 4 sets × 6-8 reps (S-Tier)
3. Overhead Press: 4 sets × 8-10 reps (A-Tier) ⬅️ +1 set vs standard
4. Pull-ups (Weighted): 4 sets × 6-10 reps (S-Tier) ⬅️ +1 set
5. Incline Dumbbell Press: 3 sets × 10-12 reps (S-Tier)
6. Cable Rows: 3 sets × 10-12 reps (A-Tier)
7. Lateral Raises: 3 sets × 12-15 reps (A-Tier)

**Volume:** Chest 10 sets, Back 11 sets, Shoulders 10 sets

---

**LOWER DAY 1 (Tuesday) - STRENGTH FOCUS**
1. Barbell Squat: 4 sets × 6-8 reps (S-Tier)
2. Romanian Deadlift: 4 sets × 8-10 reps (S-Tier)
3. Bulgarian Split Squat: 3 sets × 8-12 reps each leg (S-Tier)
4. Leg Curls: 3 sets × 10-12 reps (A-Tier)
5. Leg Press: 3 sets × 12-15 reps (A-Tier) ⬅️ Added for volume
6. Calf Raises: 4 sets × 12-15 reps (A-Tier)

**Volume:** Quads 14 sets, Hamstrings 10 sets, Calves 4 sets

---

**UPPER DAY 2 (Thursday) - HYPERTROPHY FOCUS**
1. Incline Barbell Press: 4 sets × 8-10 reps (S-Tier)
2. Lat Pulldown: 4 sets × 10-12 reps (A-Tier)
3. Dips: 3 sets × 8-12 reps (A-Tier)
4. Dumbbell Rows: 4 sets × 10-12 reps (S-Tier) ⬅️ +1 set
5. Dumbbell Flyes: 3 sets × 12-15 reps (A-Tier)
6. Face Pulls: 3 sets × 15-20 reps (A-Tier)
7. Barbell Curls: 3 sets × 10-12 reps (A-Tier)
8. Overhead Tricep Extension: 3 sets × 10-12 reps (A-Tier)

**Volume:** Chest 10 sets, Back 11 sets, Shoulders 6 sets, Arms 6 sets

---

**LOWER DAY 2 (Saturday) - HYPERTROPHY FOCUS**
1. Deadlift: 4 sets × 5-8 reps (S-Tier)
2. Front Squat or Hack Squat: 3 sets × 8-12 reps (A-Tier)
3. Walking Lunges: 3 sets × 12-15 reps each leg (A-Tier)
4. Nordic Curls: 3 sets × 6-10 reps (S-Tier)
5. Leg Extensions: 3 sets × 12-15 reps (B-Tier) ⬅️ Added for volume
6. Seated Calf Raises: 4 sets × 15-20 reps (A-Tier)

**Volume:** Quads 13 sets, Hamstrings 10 sets, Calves 4 sets

---

**WEEKLY VOLUME TOTALS:**
- Chest: 20 sets (vs 14-16 standard intermediate) ⬆️
- Back: 22 sets (vs 14-16) ⬆️
- Shoulders: 16 sets (vs 12-14) ⬆️
- Quads: 27 sets (vs 18-20) ⬆️
- Hamstrings: 20 sets (vs 14-16) ⬆️
- Arms: 6 sets direct work + indirect volume

**Progressive Overload Protocol (CRITICAL for Recomp):**

Since you're at maintenance calories, you MUST track performance to confirm muscle growth:

**Week 1-2:** Establish baseline (track all weights/reps)
**Week 3-4:** Add 1-2 reps per set OR add 5-10 lbs
**Week 5-6:** Continue progression, should hit top of rep range
**Week 7:** Deload week (50% volume, maintain intensity)
**Week 8+:** New block, increase baseline weights 5-10 lbs

**If progression stalls for 2 weeks:**
- Option 1: Add 1-2 sets per muscle group (increase volume)
- Option 2: Check nutrition (are you truly at maintenance?)
- Option 3: Take deload week early

**Recomp Training Rules:**

1. **Strength MUST increase** - this is your proof of muscle growth
   - Track every workout (weight × reps × sets)
   - If strength plateaus >2 weeks, something is wrong

2. **Recovery is harder** - no calorie surplus to fuel recovery
   - Sleep 8+ hours
   - Manage stress
   - Consider deload every 4-5 weeks (not 6-8 weeks like bulk)

3. **Cardio is optional** - but don't overdo it
   - Max 2-3 sessions/week, 20-30 min low intensity
   - Too much cardio impairs recovery for recomp

**Source:** RP Hypertrophy Training Principles (Volume for Recomp), Jeff Nippard Min-Max Program (template structure), Scientific Principles of Hypertrophy (Progressive Overload)

Would you like me to export this as an Excel tracking sheet?
```

---

#### PART 4: Progress Tracking & Adjustments (Phase 4, Week 10-12)

**User Action (Week 8):** "I've been doing recomp for 8 weeks. My weight is the same (165 lbs), but I'm not sure if it's working."

**System Process:**
1. Analyze progress data (weight, strength, body comp)
2. Assess if recomp is working or if pivot needed
3. Recommend adjustments or phase change

**System Response:**
```
=== WEEK 8 RECOMP PROGRESS CHECK ===

**Weight Trend:**
- Week 1: 165 lbs
- Week 4: 166 lbs
- Week 8: 165 lbs
- **Average:** 165.3 lbs ✅ (maintaining weight as intended)

**Strength Progress:**
Let me review your logged workouts...

**Bench Press:**
- Week 1: 185 lbs × 8 reps × 4 sets
- Week 8: 200 lbs × 8 reps × 4 sets
- **Progress:** +15 lbs ✅ EXCELLENT

**Squat:**
- Week 1: 225 lbs × 8 reps
- Week 8: 245 lbs × 8 reps
- **Progress:** +20 lbs ✅ EXCELLENT

**Deadlift:**
- Week 1: 275 lbs × 8 reps
- Week 8: 295 lbs × 8 reps
- **Progress:** +20 lbs ✅ EXCELLENT

**Body Composition (Self-Reported):**
- Week 1 Photos: Soft midsection, minimal muscle definition
- Week 8 Photos: Slight ab visibility, more shoulder/arm definition
- Waist measurement: 34" → 32.5" (-1.5 inches) ✅
- Chest measurement: 38" → 39" (+1 inch) ✅

---

**ANALYSIS: RECOMP IS WORKING! ✅**

**Evidence:**
1. ✅ Weight maintained (165 lbs average)
2. ✅ Strength increased significantly (+15-20 lbs on major lifts)
3. ✅ Waist decreased (fat loss indicator)
4. ✅ Chest increased (muscle gain indicator)
5. ✅ Visual changes in photos (more definition)

**What This Means:**
You've likely gained **2-3 lbs of muscle** and lost **2-3 lbs of fat** in 8 weeks. This is EXCELLENT progress for body recomposition!

**Expected Rate:**
- Recomp muscle gain: 0.25-0.5 lbs/week (1-2 lbs/month)
- Recomp fat loss: 0.25-0.5 lbs/week (1-2 lbs/month)
- You're on the faster end of this range ✅

---

**RECOMMENDATIONS FOR NEXT 8 WEEKS:**

**Option 1: Continue Recomp (Recommended)**
- You're making great progress
- Keep calories at 2,700/day
- Maintain current program, continue progressive overload
- Reassess at Week 16

**Option 2: Transition to Lean Bulk**
- If you want FASTER muscle gain
- Increase calories to 2,900-3,000/day (+200-300 surplus)
- Accept small fat gain (worth it for faster muscle growth)
- Bulk for 12-16 weeks, then mini-cut

**Option 3: Take Diet Break**
- If you're feeling fatigued or hungry
- Increase calories to 2,850/day (small surplus) for 1-2 weeks
- Then return to 2,700 maintenance
- Helps reset hormones, improve recovery

**My Suggestion:**
Since recomp is working well, **continue for another 8 weeks** (total 16 weeks). At Week 16, reassess:
- If still making progress → Continue recomp
- If progress stalls → Switch to lean bulk
- If happy with body comp → Switch to maintenance (lower volume training)

**When to Pivot to Bulk/Cut:**

**Pivot to Bulk if:**
- Strength plateaus for 3+ weeks despite deloads
- You want faster muscle gain (accept small fat gain)
- You're very lean already (<12% body fat estimated)

**Pivot to Cut if:**
- You're still "too fat" for your liking
- Fat loss has stalled but muscle gain continues
- You want to reveal the muscle you've built

**Source:** RP Diet Adjustments Manual (Recomp Progress), Jeff Nippard "When to Stop Recomping" guidelines, Renaissance Periodization Body Recomposition Strategies

Great work! Keep going - you're doing this right. 💪
```

---

**Acceptance Criteria for Scenario 6:**

**Phase 2 (Nutrition):**
- [ ] Detect recomp phase in profile
- [ ] Calculate maintenance TDEE (no deficit/surplus)
- [ ] Set high protein macros (1.0-1.2g per lb)
- [ ] Explain recomp eligibility (works best for beginners, returning lifters, overweight)
- [ ] Set realistic expectations (slow progress, 6-12 months)
- [ ] Cite RP Diet 2.0 Recomposition chapter

**Phase 3 (Training):**
- [ ] Generate high-volume program (18-22 sets per muscle/week)
- [ ] Emphasize progressive overload tracking
- [ ] Select compound S/A-tier exercises
- [ ] Include deload protocol (every 4-5 weeks)
- [ ] Cite RP Volume Landmarks for recomp volume recommendations

**Phase 4 (Tracking):**
- [ ] Track weight (should maintain ±2 lbs)
- [ ] Track strength progression (proof of muscle gain)
- [ ] Track body composition (waist/chest measurements, photos)
- [ ] Recommend adjustments if progress stalls
- [ ] Provide pivot strategy (when to bulk/cut instead)

**Test Cases:**
```python
# Test 1: Recomp TDEE (maintenance, no adjustment)
profile = {'weight_lbs': 165, 'phase': 'recomp', 'activity_level': 'moderately_active'}
tdee = calculate_tdee(profile)
assert tdee == calculate_bmr(profile) * 1.5  # No +/- adjustment

# Test 2: Recomp macros (high protein)
macros = calculate_macros(profile, tdee=2700)
assert 165 * 1.0 <= macros['protein_g'] <= 165 * 1.2  # 1.0-1.2g per lb

# Test 3: Recomp program volume
program = generate_program(profile, phase='recomp')
assert 18 <= program.weekly_volume['chest'] <= 22  # High volume
assert 18 <= program.weekly_volume['back'] <= 22
```

---

## 3. EDGE CASES & VARIATIONS

### EDGE CASE 1: Unrealistic Goal Timeline
**Scenario:** User wants to lose 50 lbs in 8 weeks (6.25 lb/week)

**System Response:**
```
⚠️ UNREALISTIC GOAL DETECTED

**Your Goal:** Lose 50 lbs in 8 weeks (6.25 lb/week)
**Safe Rate:** 1-2 lb/week maximum (1% bodyweight/week)

**Why This is Concerning:**
According to Renaissance Periodization Diet 2.0, losing more than 1.5-2% bodyweight per week (3.3-4.4 lbs for you) leads to:
- Significant muscle loss
- Metabolic adaptation
- Hormonal disruption
- Increased hunger and fatigue
- Unsustainable results

**Recommended Timeline:**
- **Conservative:** 50 lbs at 1 lb/week = **50 weeks** (~12 months)
- **Aggressive:** 50 lbs at 1.5 lb/week = **33 weeks** (~8 months)

Would you like me to set a more realistic timeline? (Recommended: 40-50 weeks for 50 lb loss)
```

**Acceptance Criteria:**
- Detect unrealistic rate (>2 lb/week for cut, >1 lb/week for bulk)
- Calculate healthy rate based on current weight
- Explain risks of aggressive dieting
- Cite RP diet guidelines
- Offer realistic alternative timeline

---

### EDGE CASE 2: Conflicting Goals (Bulk in Deficit)
**Scenario:** User wants to bulk but sets calorie deficit

**System Response:**
```
🔍 CONFLICTING GOALS DETECTED

**Your Profile:**
- Phase: Bulk (gain muscle)
- Target: 165 lbs → 175 lbs (+10 lbs)
- But you also indicated: "Cut" phase

**Issue:** You can't bulk (gain weight) while in a cutting (deficit) phase. These are opposite goals.

**Let's Clarify Your Goal:**
1. **Build Muscle + Gain Weight?** → Bulking phase (+300-500 cal surplus)
2. **Lose Fat + Maintain Muscle?** → Cutting phase (-300-500 cal deficit)
3. **Build Muscle + Lose Fat simultaneously?** → Body Recomposition (maintenance calories)

Based on your profile (intermediate, 165 lbs, 2 years training), I recommend:
- **Bulk first** (12-16 weeks, +10-15 lbs) → **Then cut** (12-16 weeks, -5-10 lbs)
- Or **Cut first** (if currently overfat) → **Then bulk**

Which approach would you prefer? I'll recalculate your macros accordingly.
```

---

### EDGE CASE 3: Minimal Time/Equipment (2 Days/Week, Bodyweight Only)
**Scenario:** Minimal Megan (2 days/week, 30 min/session, bodyweight only)

**Expected Output:**
```
=== MINIMAL TRAINING PROGRAM ===

**Your Constraints:**
- 2 days per week
- 30-45 minutes per session
- Bodyweight only (no equipment)

**Your 2-Day Full-Body Program:**

**Day 1 & Day 2 (same workout, 2x per week):**
1. Push-ups: 3-4 sets × 8-15 reps
2. Bodyweight Squats: 3-4 sets × 15-20 reps
3. Inverted Rows (table edge): 3-4 sets × 8-12 reps
4. Lunges: 3 sets × 10-12 reps each leg
5. Plank: 3 sets × 30-60 seconds

**Session Duration:** 30-40 minutes (minimal rest needed)

**Reality Check:**
This program will:
- ✅ Maintain general fitness
- ✅ Build strength (if beginner)
- ✅ Support weight maintenance/loss
- ❌ NOT optimal for hypertrophy
- ❌ Limited progression potential

**Source:** RP Volume Landmarks (minimum effective volume), Jeff Nippard Fundamentals (bodyweight training)
```

---

## 4. ACCEPTANCE CRITERIA MATRIX

### Phase 2: User Profile & Calculations (CURRENT - Weeks 1-4)

| Feature | Must Have | Should Have | Nice to Have | Status |
|---------|-----------|-------------|--------------|--------|
| **Profile Creation** | ✅ Save/load JSON | Validation rules | Export as PDF | ✅ Done |
| **Profile Updates** | ✅ Weight updates | Bulk updates | History tracking | ✅ Done |
| **TDEE Calculation** | ✅ Mifflin-St Jeor BMR | Activity multipliers | Custom formulas | 🔄 Week 2 |
| **Macro Calculation** | ✅ Protein/Fat/Carb split | Phase adjustments | Meal timing | 🔄 Week 2 |
| **RAG Citations** | ✅ Cite RP sources | Page numbers | Confidence scores | 🔄 Week 2 |
| **Profile UI** | ✅ Streamlit forms | Quick updates | Profile history | ✅ Done |

### Phase 3: Program Generation (Weeks 5-9)

| Feature | Must Have | Should Have | Nice to Have | Status |
|---------|-----------|-------------|--------------|--------|
| **Excel Parser** | Parse 3 templates | Extract structure | Auto-detect format | ⏸️ Week 5 |
| **Tier List Parser** | Convert RTF→JSON | All muscle groups | Exercise variations | ⏸️ Week 7 |
| **Exercise Selection** | Filter by equipment | Tier prioritization | User preferences | ⏸️ Week 7 |
| **Program Generation** | 4-week program | Template matching | Periodization | ⏸️ Week 8 |
| **Volume Calculation** | Sets per muscle/week | Experience adjustments | Volume landmarks | ⏸️ Week 8 |
| **Progression Scheme** | Linear progression | Deload weeks | Autoregulation | ⏸️ Week 8 |
| **Program Export** | PDF export | Excel tracking sheet | Print-friendly | ⏸️ Week 9 |

### Phase 4: Adaptive Coaching (Weeks 10-14)

| Feature | Must Have | Should Have | Nice to Have | Status |
|---------|-----------|-------------|--------------|--------|
| **Progress Tracking** | Weight logging | Performance logging | Body measurements | ⏸️ Week 10 |
| **Diet Adjustments** | Calorie adjustments | Macro adjustments | Refeed protocols | ⏸️ Week 10 |
| **Training Adjustments** | Volume adjustments | Deload recommendations | Exercise substitutions | ⏸️ Week 11 |
| **Progress Analysis** | Weekly summaries | Trend detection | Plateau detection | ⏸️ Week 12 |

---

## 5. TESTING SCENARIOS & VALIDATION

### Phase 2 Testing (Current Focus)

**Test Suite 1: TDEE Calculation Accuracy**
```python
def test_tdee_male_sedentary():
    """Test TDEE calculation for sedentary male"""
    profile = {
        'weight_lbs': 185,
        'height_inches': 72,
        'age': 30,
        'sex': 'male',
        'activity_level': 'sedentary'
    }
    tdee = calculate_tdee(profile)
    assert 2200 <= tdee <= 2400  # Expected range

def test_tdee_female_active():
    """Test TDEE calculation for active female"""
    profile = {
        'weight_lbs': 140,
        'height_inches': 65,
        'age': 28,
        'sex': 'female',
        'activity_level': 'very_active'
    }
    tdee = calculate_tdee(profile)
    assert 2100 <= tdee <= 2300  # Expected range
```

**Test Suite 2: Macro Calculation Validation**
```python
def test_macros_cutting():
    """Test macro split for cutting phase"""
    profile = {'weight_lbs': 185, 'phase': 'cut'}
    calories = 2000
    macros = calculate_macros(profile, calories)

    # Protein: 0.9-1.1g per lb
    assert 167 <= macros['protein_g'] <= 204

    # Fat: 0.3-0.4g per lb
    assert 56 <= macros['fat_g'] <= 74
```

---

## 6. PRODUCTION ROADMAP

### Phase 2 (Weeks 1-4) - CURRENT PHASE

**Week 1: Profile System** ✅ COMPLETE

**Week 2: Calculation Engine** ✅ COMPLETE
- ✅ TDEE calculation (Mifflin-St Jeor)
- ✅ Activity multipliers
- ✅ Phase adjustments (cut/bulk/maintain/recomp)
- ✅ Macro calculation (protein/fat/carbs)
- ✅ Coaching-style guidance generation
- ✅ Testing suite (25 tests passing)

**Deliverable Week 2:**
```python
# User can ask:
"What are my cutting macros?"

# System responds with:
# - Calculated TDEE
# - Phase-adjusted calories
# - Macro breakdown (g and %)
# - RP citation for recommendations
```

**Week 3: Profile-Aware RAG Queries**
- Profile context injection into RAG queries
- User-specific recommendations
- Citation improvements

**Week 4: Phase 2 Polish & Testing**
- Comprehensive test suite (all personas)
- Edge case handling
- Documentation

---

### Phase 3 (Weeks 5-9) - Program Generation

**Week 5-6:** Template Parsing
**Week 7:** Tier List Integration
**Week 8:** Program Generation Core
**Week 9:** Program Export & Polish

**Milestone:** User can generate a complete, customized 4-week training program.

---

### Phase 4 (Weeks 10-14) - Adaptive Coaching

**Week 10:** Weight Tracking & Diet Adjustments
**Week 11-12:** Training Progress Tracking
**Week 13-14:** Adaptive Adjustments

**Milestone:** System adapts program and diet based on user progress.

---

### Phase 5 (Weeks 15+) - Polish & Advanced Features

**Week 15-16:** UI/UX Polish
**Week 17:** Meal Planning
**Week 18:** Exercise Library
**Week 19:** Export & Integrations

**Milestone:** Polished MVP ready for 50-100 users.

---

## 7. PRIORITIZATION & FOCUS

### Must Build (Critical Path)

1. **Phase 2 Week 2:** TDEE & Macro Calculation with RAG citations
2. **Phase 3 Week 7:** Tier List parsing and exercise selection
3. **Phase 3 Week 8:** Program generation from templates
4. **Phase 4 Week 10:** Weight tracking and diet adjustments

### Should Build (High Value)

1. Training progress tracking (Phase 4)
2. Adaptive volume adjustments (Phase 4)
3. Progress charts (Phase 5)
4. Exercise library (Phase 5)

### Nice to Have (Later)

1. Meal planning integration
2. Google Sheets sync
3. Dark mode UI

### Can Skip (Out of Scope for MVP)

1. Social features
2. Custom template builder
3. AI form analysis
4. Nutrition tracking app integration

---

## SUMMARY & NEXT STEPS

**Week 2 Status:** ✅ COMPLETE

1. ✅ **Implement TDEE Calculation** (Scenario 2) - DONE
2. ✅ **Implement Macro Calculation** (Scenario 2) - DONE
3. ✅ **Coaching-Style Guidance** (Scenario 2) - DONE
4. ✅ **Testing** (Test Suite 1-3) - DONE (25/25 passing)

**Testing Checkpoints:** ✅ ALL PASSED
Run tests with all 5 personas:
- ✅ Beginner Ben (cut, home gym)
- ✅ Intermediate Ian (bulk, commercial gym)
- ✅ Cutting Claire (cut, female, commercial gym)
- ✅ Recomp Ryan (recomp, home gym)
- ✅ Minimal Megan (maintain, minimal equipment)

**Success Criteria for Week 2:** ✅ ALL COMPLETE
- [x] User can query "What are my cutting macros?" and receive calculated TDEE + macros
- [x] Response cites RP Diet 2.0 or Diet Adjustments Manual
- [x] TDEE within 5% of manual calculation
- [x] Macros within recommended ranges (protein 0.8-1.2g/lb, etc.)
- [x] All 5 personas tested successfully
- [x] Coaching mindset implemented (sets expectations, promises adaptation)
