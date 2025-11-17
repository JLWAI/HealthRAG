# RP Hypertrophy App Feature Analysis
**Target App to Mimic/Clone for HealthRAG**

*Research Date: January 2025*

---

## 🎯 OVERVIEW

**Renaissance Periodization Hypertrophy App**
- **Creator:** Renaissance Periodization (Dr. Mike Israetel, Nick Shaw)
- **Type:** Web-based training application (browser-based, not native mobile app)
- **Price:** $34.99/month or $299.99/year
- **Focus:** Evidence-based hypertrophy training with autoregulation
- **Separate App:** RP Diet Coach (nutrition/macro tracking) is sold separately

---

## 🏋️ CORE FEATURES

### 1. **Mesocycle Builder**
- **45+ pre-selected templates** (Upper Body 4x, Lower Body 4x, PPL, Full Body, etc.)
- **Custom mesocycle creation** - Build your own from scratch
- **New 2025 Feature:** Meso Builder (beta) - Complete flexibility to:
  - Select which muscles to emphasize
  - Which muscles to put on maintenance
  - Which muscles to ignore entirely
- **Named Templates:** "Mr. Nick Shaw" (6 days/week, arms + shoulders emphasis, pre-loaded exercises)

### 2. **Volume Progression System**

**Primary Method:** Set accumulation (adding sets over time)
- Gradual volume increase over 4-6 week mesocycle
- Weight progression (increase load)
- RIR progression (Reps in Reserve: 3 RIR → 0 RIR over mesocycle)
- **Deload phase** after each mesocycle

**RP Volume Concepts:**
- **MEV** (Minimum Effective Volume) - Lowest volume to make gains
- **MV** (Maintenance Volume) - Volume to maintain muscle
- **MAV** (Maximum Adaptive Volume) - Optimal volume for growth
- **MRV** (Maximum Recoverable Volume) - Maximum volume before overtraining

### 3. **Autoregulation via Feedback**

**User Reports After Each Workout:**
1. **Pump Quality** (low/moderate/extreme)
   - Low pump → Need more volume
   - Moderate pump → Good volume
   - Extreme pump → Too much volume
2. **Soreness** (when did soreness heal?)
3. **Disruption** (general fatigue and strength loss)
4. **Joint Pain** (direct pain assessment)
5. **Performance** (strength progression tracking)

**Algorithm Response:**
- Adjusts next week's training based on feedback
- Adds/removes sets dynamically
- Prevents overtraining while maximizing growth

### 4. **Exercise Selection**

**Two Options:**
1. **Manual Selection** - User chooses from dropdown menu
   - Extensive exercise database
   - User must know what exercise they want

2. **Auto-Fill Feature** (LIMITATION)
   - Generates random exercises
   - **Criticism:** Repeats exercises, places similar movements consecutively, unpredictable
   - Reviewers suggest manual selection preferred

**Notable Gap:** No personalized exercise recommendations based on equipment

### 5. **Workout Execution**

**During Training:**
- See exact weight and reps to hit each week
- Track sets, reps, weight
- Enter feedback (pump, soreness, etc.)

**Missing Features:**
- ❌ No rest period timers
- ❌ No prescribed rest periods
- ❌ No home workout modifications
- ❌ Requires internet connection (web-based, no offline mode)

### 6. **Program Structure**

**Typical Mesocycle:**
- **Week 1:** Base volume, 3 RIR
- **Week 2:** +volume, 2 RIR
- **Week 3:** +volume, 1 RIR
- **Week 4:** Peak volume, 0 RIR
- **Week 5 (optional):** Further progression
- **Week 6:** Deload (reduce volume 50%)

**Split Options:**
- Full body (3x/week)
- Upper/Lower (4x/week)
- Push/Pull/Legs (6x/week)
- Bro split (5x/week)
- Body part specialization programs

---

## 💪 STRENGTHS (What Makes It Great)

1. **Evidence-Based Science** - Built on Dr. Mike Israetel's research
2. **Autoregulation** - Adjusts to YOUR recovery, not a generic plan
3. **Volume Optimization** - Finds your personal MEV/MAV/MRV sweet spot
4. **Flexibility** - 45+ templates + custom building
5. **Progressive Overload** - Clear progression scheme (sets, weight, RIR)
6. **Specialization** - Can emphasize specific muscle groups
7. **Deload Built-In** - Prevents overtraining systematically

---

## 🚨 LIMITATIONS (Opportunities for HealthRAG to Improve)

### Critical Gaps:
1. **❌ No Exercise Selection Guidance**
   - User must know which exercises to choose
   - Auto-fill is poor quality (random, repetitive)
   - **HealthRAG Opportunity:** Use Jeff Nippard S/S+ tier list to recommend best exercises

2. **❌ No Equipment-Based Customization**
   - Doesn't adapt program to available equipment
   - No home gym vs commercial gym differentiation
   - **HealthRAG Opportunity:** Equipment-first approach (we're already doing this!)

3. **❌ No Rest Period Guidance**
   - Doesn't prescribe rest times
   - No timer functionality
   - **HealthRAG Opportunity:** Evidence-based rest periods (2-3 min compounds, 1-2 min isolation)

4. **❌ Web-Only (No Offline)**
   - Requires internet connection
   - Can't train in basement/areas without signal
   - **HealthRAG Opportunity:** Local-first architecture with MLX

5. **❌ Short Mesocycles**
   - 4-6 weeks may be too short for some users
   - Some users manually extend programs
   - **HealthRAG Opportunity:** Flexible mesocycle lengths (4-12 weeks)

6. **❌ No Nutrition Integration**
   - Diet app sold separately ($34.99/month additional!)
   - No unified coaching experience
   - **HealthRAG Opportunity:** Integrated nutrition + training (we're already doing this!)

7. **❌ Expensive**
   - $34.99/month or $299.99/year
   - + $34.99/month for Diet app = $70/month total!
   - **HealthRAG Opportunity:** Free/open-source local app

8. **❌ Complexity for Beginners**
   - MEV/MAV/MRV terminology overwhelming
   - Requires understanding of RP principles
   - **HealthRAG Opportunity:** Simpler onboarding for beginners

---

## 🎯 HEALTHRAG FEATURE COMPARISON

| Feature | RP Hypertrophy App | HealthRAG Status |
|---------|-------------------|------------------|
| **Mesocycle Builder** | ✅ 45+ templates + custom | 🔄 Phase 3 (Weeks 5-8) |
| **Volume Progression** | ✅ Set accumulation + RIR | 🔄 Phase 3 (planned) |
| **Autoregulation Feedback** | ✅ Pump/soreness/disruption | 📋 Phase 4+ (future) |
| **Exercise Database** | ✅ Extensive dropdown | 🔄 Phase 3 (Jeff Nippard tier list) |
| **Equipment Customization** | ❌ No equipment awareness | ✅ **Already built!** (Week 2) |
| **Nutrition Integration** | ❌ Separate app ($35/mo) | ✅ **Already built!** (Week 2-3) |
| **Exercise Selection Help** | ❌ Auto-fill poor quality | ✅ **Planned** (S/S+ tier priority) |
| **Rest Period Guidance** | ❌ Not provided | 📋 Phase 3+ (planned) |
| **Offline Mode** | ❌ Web-based only | ✅ **Local-first** (MLX backend) |
| **Cost** | ❌ $35/month | ✅ **Free** (self-hosted) |
| **Proactive Dashboard** | ❌ Not mentioned | ✅ **Already built!** (Week 3) |
| **Personalization** | ⚠️ Templates only | ✅ **Name + custom profile** (Week 3) |

**Legend:**
- ✅ = Fully implemented
- 🔄 = In progress / planned soon
- 📋 = Future phase
- ❌ = Not available
- ⚠️ = Limited implementation

---

## 📝 HEALTHRAG IMPLEMENTATION ROADMAP

### ✅ **PHASE 1: Foundation (Weeks 0-1) - COMPLETE**
- RAG system with RP Diet 2.0 + Jeff Nippard PDFs
- LLM backend (Ollama + MLX)
- Basic Q&A functionality

### ✅ **PHASE 2: User Profile & Nutrition (Weeks 2-3) - COMPLETE**
- User profile system (weight, height, age, sex, activity, **name**)
- Equipment inventory (home gym + Planet Fitness)
- TDEE & macro calculations
- **Proactive dashboard** (auto-show nutrition plan)
- Personalized coaching guidance

### 🔄 **PHASE 3: Program Generation (Weeks 5-8) - IN PROGRESS**

**Week 5-6: Exercise Selection Engine**
- [ ] Jeff Nippard S/S+ tier exercise database
- [ ] Equipment-based exercise filtering
- [ ] Exercise substitution system (S-tier → S-tier fallbacks)
- [ ] Exercise variety rotation (prevent staleness)

**Week 7-8: Mesocycle Builder**
- [ ] Training split selection (Full Body, Upper/Lower, PPL, Bro Split)
- [ ] Volume prescription (MEV/MAV recommendations by muscle group)
- [ ] Progressive overload scheme:
  - Set progression (start conservative, add sets weekly)
  - Load progression (2.5-5% increases)
  - RIR progression (3 RIR → 1 RIR)
- [ ] Deload protocols (every 4-6 weeks, 50% volume reduction)
- [ ] Generate weekly workout plans

**HealthRAG Advantages Over RP:**
1. ✅ **Equipment-aware** - Program built around YOUR available equipment
2. ✅ **S/S+ Tier Priority** - Best exercises recommended first
3. ✅ **Integrated Nutrition** - No separate app needed
4. ✅ **Free & Local** - No $35/month subscription
5. ✅ **Offline Capable** - MLX runs locally

### 📋 **PHASE 4: Autoregulation & Tracking (Weeks 9-12+)**
- [ ] Workout logging (sets, reps, weight)
- [ ] Feedback collection (pump, soreness, RIR, performance)
- [ ] Auto-adjust volume based on feedback
- [ ] Progressive overload tracking
- [ ] Body weight tracking integration
- [ ] 10,000 steps/day tracking
- [ ] Progress photos
- [ ] Measurement tracking (waist, chest, arms)

### 📋 **PHASE 5: Advanced Features (Future)**
- [ ] Specialization mesocycles (focus on specific muscle groups)
- [ ] Injury accommodation (modify exercises for joint pain)
- [ ] Exercise form videos/cues
- [ ] Rest period timers
- [ ] Superset/giant set programming
- [ ] Cardio integration
- [ ] Sleep tracking integration
- [ ] Recovery metrics

---

## 🎓 KEY LESSONS FOR HEALTHRAG

### 1. **Simplicity > Complexity for Beginners**
**RP Issue:** MEV/MAV/MRV terminology is overwhelming

**HealthRAG Approach:**
- Use simple language: "Starting volume", "Optimal volume", "Max volume"
- Provide tooltips/explanations
- Beginner mode: Hide complexity, just show the workout
- Advanced mode: Show volume concepts for those who want them

### 2. **Exercise Selection is CRITICAL**
**RP Issue:** Poor auto-fill, no equipment guidance, no tier recommendations

**HealthRAG Solution:**
- Jeff Nippard S/S+ tier list integration (95-100% coverage with home + PF!)
- Equipment-first filtering (show only exercises you CAN do)
- Substitution suggestions within same tier
- Default to most accessible equipment (home gym = dumbbells/bodyweight)
- Show alternatives if training elsewhere ("If at PF today: swap X → Y")

### 3. **Integration > Separation**
**RP Issue:** Training app + Diet app = $70/month, two separate experiences

**HealthRAG Advantage:**
- Single unified coach experience
- Nutrition + Training in one dashboard
- Profile drives both systems
- No context switching

### 4. **Local-First > Web-Only**
**RP Issue:** Requires internet, no offline mode

**HealthRAG Advantage:**
- MLX runs locally (no cloud dependency)
- Works in basements, gyms with poor signal
- Data privacy (stays on your machine)
- No subscription fees

### 5. **Proactive > Reactive UX**
**RP Approach:** User navigates to different sections

**HealthRAG Approach:** (Already implemented!)
- Dashboard shows plan automatically
- "Welcome, Jason! Here's your plan:"
- No need to remember what to ask

---

## 🏗️ IMMEDIATE NEXT STEPS (Phase 3)

### **Priority 1: Exercise Database (Week 5)**
Create `src/exercise_database.py`:
```python
# S+ tier exercises from Jeff Nippard
S_PLUS_TIER = {
    'glutes': ['walking_lunge'],
    'quads': ['hack_squat'],
    'triceps': ['overhead_cable_extension'],
    'back': ['chest_supported_row'],
    'biceps': ['face_away_beian_cable_curl'],
    'shoulders': ['cable_lateral_raise']
}

# S tier exercises
S_TIER = {
    'glutes': [
        'machine_hip_abduction',
        'elevated_front_foot_lunge',
        '45_degree_back_extension'
    ],
    'quads': [
        'barbell_back_squat',
        'smith_machine_squat',
        'bulgarian_split_squat',
        'pendulum_squat'
    ],
    # ... etc
}

# Equipment requirements
EXERCISE_EQUIPMENT = {
    'walking_lunge': ['dumbbells', 'bodyweight'],
    'hack_squat': ['hack_squat_machine'],
    'overhead_cable_extension': ['cables'],
    'chest_supported_row': ['chest_supported_row_machine', 'incline_bench', 'dumbbells'],
    # ... etc
}
```

### **Priority 2: Exercise Selection Logic (Week 5)**
Create `src/exercise_selection.py`:
```python
def select_exercises(muscle_group, user_equipment, tier_priority=['S+', 'S', 'A']):
    """
    Select best exercises for muscle group based on available equipment.

    Args:
        muscle_group: Target muscle (e.g., 'quads', 'back')
        user_equipment: List of available equipment
        tier_priority: Order of tiers to check

    Returns:
        List of exercises with tier labels
    """
    available_exercises = []

    # Check S+ tier first
    for exercise in S_PLUS_TIER.get(muscle_group, []):
        if has_equipment(exercise, user_equipment):
            available_exercises.append({
                'name': exercise,
                'tier': 'S+',
                'equipment': EXERCISE_EQUIPMENT[exercise]
            })

    # Then S tier
    for exercise in S_TIER.get(muscle_group, []):
        if has_equipment(exercise, user_equipment):
            available_exercises.append({
                'name': exercise,
                'tier': 'S',
                'equipment': EXERCISE_EQUIPMENT[exercise]
            })

    return available_exercises
```

### **Priority 3: Mesocycle Templates (Week 6)**
Create `src/mesocycle_templates.py`:
```python
MESOCYCLE_TEMPLATES = {
    'upper_lower_4x': {
        'name': 'Upper/Lower 4x per Week',
        'days_per_week': 4,
        'split': {
            'monday': 'upper',
            'tuesday': 'lower',
            'thursday': 'upper',
            'friday': 'lower'
        },
        'muscle_groups': {
            'upper': ['chest', 'back', 'shoulders', 'biceps', 'triceps'],
            'lower': ['quads', 'hamstrings', 'glutes', 'calves']
        }
    },
    'ppl_6x': {
        'name': 'Push/Pull/Legs 6x per Week',
        'days_per_week': 6,
        'split': {
            'monday': 'push',
            'tuesday': 'pull',
            'wednesday': 'legs',
            'thursday': 'push',
            'friday': 'pull',
            'saturday': 'legs'
        },
        'muscle_groups': {
            'push': ['chest', 'shoulders', 'triceps'],
            'pull': ['back', 'biceps'],
            'legs': ['quads', 'hamstrings', 'glutes', 'calves']
        }
    }
}
```

### **Priority 4: Volume Prescription (Week 7)**
Create `src/volume_prescription.py`:
```python
# MEV/MAV/MRV ranges by muscle group (sets per week)
VOLUME_LANDMARKS = {
    'chest': {'MEV': 10, 'MAV': 16, 'MRV': 22},
    'back': {'MEV': 12, 'MAV': 18, 'MRV': 25},
    'quads': {'MEV': 12, 'MAV': 18, 'MRV': 24},
    'glutes': {'MEV': 8, 'MAV': 14, 'MRV': 20},
    'hamstrings': {'MEV': 8, 'MAV': 12, 'MRV': 18},
    'shoulders': {'MEV': 12, 'MAV': 18, 'MRV': 26},
    'biceps': {'MEV': 8, 'MAV': 14, 'MRV': 20},
    'triceps': {'MEV': 8, 'MAV': 12, 'MRV': 18},
    'calves': {'MEV': 8, 'MAV': 12, 'MRV': 16}
}

def calculate_starting_volume(training_level, muscle_group):
    """Start at MEV for beginners, closer to MAV for advanced."""
    mev = VOLUME_LANDMARKS[muscle_group]['MEV']
    mav = VOLUME_LANDMARKS[muscle_group]['MAV']

    if training_level == 'beginner':
        return mev  # Start conservative
    elif training_level == 'intermediate':
        return int((mev + mav) / 2)  # Start in middle
    else:  # advanced
        return mav - 2  # Start near MAV, leave room to grow
```

### **Priority 5: Progressive Overload (Week 8)**
Create `src/progression.py`:
```python
def generate_mesocycle_progression(starting_volume, weeks=6):
    """
    Generate weekly volume progression for mesocycle.

    Weeks 1-5: Increase sets
    Week 6: Deload (50% volume)
    """
    weekly_volumes = []

    for week in range(1, weeks + 1):
        if week == weeks:  # Deload week
            volume = starting_volume * 0.5
            rir = 3  # Easy deload
        else:
            # Add 1-2 sets per week
            volume = starting_volume + ((week - 1) * 2)
            rir = 4 - week  # 3 RIR → 0 RIR

        weekly_volumes.append({
            'week': week,
            'sets': int(volume),
            'rir': max(0, rir)
        })

    return weekly_volumes
```

---

## 🎯 SUCCESS CRITERIA

**HealthRAG will be better than RP Hypertrophy App when:**

1. ✅ **Integrated Nutrition + Training** (RP requires 2 separate apps)
2. ✅ **Equipment-Aware Exercise Selection** (RP has no equipment customization)
3. ✅ **S/S+ Tier Exercise Priority** (RP has poor auto-fill)
4. ✅ **Free & Local** (RP costs $35/month)
5. ✅ **Offline Capable** (RP requires internet)
6. 🔄 **Jeff Nippard Exercise Database** (95-100% tier list coverage)
7. 🔄 **Mesocycle Generation** (comparable to RP's 45+ templates)
8. 📋 **Autoregulation** (future - pump/soreness feedback)

---

## 📚 REFERENCES

**Primary Sources:**
- RP Hypertrophy App Official Site: https://rpstrength.com/pages/hypertrophy-app
- RP Hypertrophy App Help: https://hypertrophy.zendesk.com/hc/en-us

**Independent Reviews:**
- Dr. Muscle RP App Review (2025): https://dr-muscle.com/rp-hypertrophy-app-review/
- Dr. Muscle RP App Critique (13-Point): https://dr-muscle.com/rp-hypertrophy-app-critique/
- Counting Kilos App Showdown: https://countingkilos.com/hypertrophy-app-showdown-rp-vs-adaptive-workout-builder/

**RP Principles:**
- Renaissance Periodization Diet 2.0 Manual (in `data/pdfs/`)
- Jeff Nippard Fundamentals Hypertrophy Program (in `data/pdfs/`)
- Jeff Nippard Exercise Tier List (in `data/pdfs/`)

---

## 💡 CONCLUSION

The RP Hypertrophy App is an excellent evidence-based training tool, but it has significant gaps that **HealthRAG is already positioned to fill**:

✅ **HealthRAG Already Beats RP At:**
1. Integrated nutrition (no separate $35/month app)
2. Equipment-based customization (home gym + Planet Fitness)
3. Proactive coaching UX (dashboard shows plan automatically)
4. Cost (free vs $35/month)
5. Local/offline capability (MLX vs web-only)

🔄 **HealthRAG Needs to Match RP At:**
1. Exercise database & selection (Phase 3, Weeks 5-6)
2. Mesocycle builder (Phase 3, Weeks 7-8)
3. Volume progression system (Phase 3, Week 8)

📋 **HealthRAG Can SURPASS RP Later:**
1. Better exercise selection (S/S+ tier priority vs random auto-fill)
2. Equipment-aware programming (RP doesn't have this)
3. Autoregulation with simpler UI (Phase 4+)

**Bottom Line:** We're building a superior product by integrating the best of RP's science with Jeff Nippard's exercise selection and removing RP's key limitations (equipment awareness, cost, separation of nutrition/training).

---

**Next Step:** Begin Phase 3 implementation (Exercise Database + Mesocycle Builder, Weeks 5-8)
