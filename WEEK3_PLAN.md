# Week 3 Plan: Profile-Aware RAG System
**Phase 2, Week 3: Making RAG Responses Actionable & Trackable**

---

## 🎯 THE PROBLEM

### Current State (Week 2):
**User asks:** "How much volume should I do?"

**Current RAG response (GENERIC):**
```
According to Renaissance Periodization Volume Landmarks, most individuals need:
- Maintenance Volume (MV): 6-8 sets per muscle per week
- Minimum Effective Volume (MEV): 10-12 sets per muscle per week
- Maximum Adaptive Volume (MAV): 15-20 sets per muscle per week
- Maximum Recoverable Volume (MRV): 22-25 sets per muscle per week

Start with MEV and progress toward MAV over time.

Source: RP Volume Landmarks ebook
```

### ❌ PROBLEMS WITH THIS RESPONSE:

1. **Not personalized** - Doesn't use user's profile (intermediate, 4 days/week)
2. **Not actionable** - Which volume landmark should THEY specifically use?
3. **Not trackable** - No specific set counts to log per workout
4. **Not coaching** - Doesn't say "DO THIS", just "here's what's possible"

### ❌ BIGGER PROBLEM: USER HAS TO ASK!

**Current UX (REACTIVE - WRONG):**
1. User creates profile
2. User has to remember to ask: "What are my macros?"
3. User has to remember to ask: "What's my volume?"
4. Feels like talking to **search engine**, not a **coach**

**Real Coach UX (PROACTIVE - RIGHT):**
1. User creates profile
2. **Coach immediately says:** "Here's YOUR plan: 1,846 cal, 210g protein, here's your training program"
3. User doesn't memorize prompts - **coach tells them upfront**

**Key Insight:** A coach doesn't wait for you to ask "what are my macros?" - they tell you the plan immediately and proactively update you when things change.

### ✅ WHAT WE NEED INSTEAD (PROFILE-AWARE):

**User asks:** "How much volume should I do?"

**Profile-Aware RAG response:**
```
Based on your profile (intermediate, 4 days/week, Upper/Lower split), here's your specific volume prescription:

**YOUR WEEKLY VOLUME TARGETS:**
- Chest: 14-16 sets per week (7-8 sets per Upper day × 2 days)
- Back: 14-16 sets per week (7-8 sets per Upper day × 2 days)
- Shoulders: 12-14 sets per week (6-7 sets per Upper day × 2 days)
- Quads: 14-18 sets per week (7-9 sets per Lower day × 2 days)
- Hamstrings: 12-14 sets per week (6-7 sets per Lower day × 2 days)

**Why These Numbers?**
As an intermediate lifter, you need volume between MEV (10-12 sets) and MAV (15-20 sets).
With 4 training days, this gives you ~7-8 sets per muscle group per session - optimal for
hypertrophy without overtraining.

**What to Track:**
Log total sets per muscle group each week. If you're not progressing after 2-3 weeks,
increase volume by 2 sets per muscle per week.

**Source:** RP Volume Landmarks (Intermediate Volume Recommendations),
RP Hypertrophy Training Guide (Volume per Session)
```

### 🎯 KEY DIFFERENCES:

| Generic (Week 2) | Profile-Aware (Week 3) |
|------------------|------------------------|
| "10-12 sets MEV" | "14-16 sets per week for chest" |
| "Most people need..." | "Based on YOUR profile..." |
| Abstract ranges | Specific numbers to track |
| "Here's info" | "DO THIS, track THIS" |
| Not trackable | Fully trackable |

---

## 📋 WEEK 3 OBJECTIVES

### Primary Goals:
1. **Make RAG queries profile-aware** (personalized, actionable, trackable)
2. **Add proactive coaching dashboard** (show plan upfront, don't make user ask)

### Success Criteria - Profile-Aware RAG:
1. ✅ User asks volume question → Gets specific set counts per muscle group
2. ✅ User asks exercise question → Gets exercises filtered by THEIR equipment
3. ✅ User asks training question → Gets recommendations for THEIR experience level
4. ✅ All responses include "Based on your profile..." context
5. ✅ All responses provide trackable metrics (sets, reps, weight progressions)

### Success Criteria - Proactive Coaching:
1. ✅ After profile creation → Immediately show nutrition plan (no need to ask)
2. ✅ Dashboard shows: Today's targets, current phase, progress this week
3. ✅ User doesn't memorize prompts - coach tells them upfront
4. ✅ Chat is for clarification/adjustments, not for getting basic plan info

---

## 🎯 NEW: PROACTIVE COACHING DASHBOARD

### The Vision: Coach That Tells, Not Waits

**After user creates profile, show immediately:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏃‍♂️ YOUR PERSONALIZED PLAN

Welcome! Based on your profile, here's your plan:

📊 NUTRITION PLAN (Cutting Phase)
   • Daily Target: 1,846 calories
   • Protein: 210g | Fat: 74g | Carbs: 84g
   • Expected: ~1.0 lb/week loss

   Why these numbers?
   As a 210 lb male cutting, you need high protein (1.0g/lb) to preserve
   muscle during your deficit. We'll adjust based on weekly weigh-ins.

   Source: RP Diet 2.0 (Chapter 3)

💪 TRAINING PROGRAM (Coming in Phase 3)
   • Program recommendation will appear here after Week 5
   • For now: Focus on progressive overload, track your lifts

📈 GETTING STARTED
   1. Log your weight daily (weigh in AM, fasted)
   2. Track your calories and protein
   3. We'll review progress weekly and adjust as needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 CHAT WITH YOUR COACH
Have questions about your plan? Need adjustments? I'm here to help!

[Type your message...]
```

### Dashboard Components (Week 3 Implementation):

**Component 1: Nutrition Summary (Auto-Generated)**
- Uses `calculate_nutrition_plan()` from Week 2
- Displays immediately after profile creation
- Updates when user updates weight or phase

**Component 2: Progress Indicators (Phase 4 - Future)**
- Weight trend (7-day moving average)
- Workouts completed this week
- On track / Need adjustment indicators

**Component 3: Next Steps (Auto-Generated)**
- Based on current phase
- Cut: "Focus on preserving strength, track weight daily"
- Bulk: "Progressive overload is key, increase weight each week"
- Recomp: "Track body comp via photos and measurements"

### Implementation in src/main.py:

```python
def render_proactive_dashboard(profile: UserProfile):
    """Render proactive coaching dashboard (Week 3)"""
    st.markdown("---")
    st.subheader("🏃‍♂️ Your Personalized Plan")

    # Load profile data
    profile.load()
    personal_info = profile.profile_data['personal_info']
    goals = profile.profile_data['goals']

    # Generate nutrition plan (Week 2 function)
    plan = calculate_nutrition_plan(personal_info, goals)

    # Display nutrition summary
    st.markdown(f"""
### 📊 Nutrition Plan ({goals['phase'].capitalize()} Phase)

**Daily Target:** {int(plan['tdee_adjusted']):,} calories
- **Protein:** {int(plan['macros']['protein_g'])}g
- **Fat:** {int(plan['macros']['fat_g'])}g
- **Carbs:** {int(plan['macros']['carbs_g'])}g

**Expected Progress:** {get_expected_rate_text(goals['phase'])}

**Why these numbers?**
{get_phase_explanation(personal_info, goals, plan)}

**Source:** RP Diet 2.0, RP Diet Adjustments Manual
""")

    # Display getting started steps
    st.markdown(f"""
### 📈 Getting Started

1. **Log weight daily** (AM, fasted, same scale)
2. **Track calories & protein** (most important macros)
3. **Review progress weekly** - We'll adjust as needed

**Need adjustments?** Message me below and I'll help! 👇
""")

    st.markdown("---")


# In main():
if profile.exists():
    # Show proactive dashboard FIRST
    render_proactive_dashboard(profile)

    # THEN show chat interface below
    st.subheader("💬 Chat with Your Coach")
    # ... existing chat code
```

---

## 🔧 IMPLEMENTATION PLAN

### Step 1: Profile Context Builder (`src/profile_context.py`)

**Create a function that builds RAG context from user profile:**

```python
def build_profile_context(profile: UserProfile) -> str:
    """
    Build profile context string for RAG query injection.

    Returns a compact summary of user profile to inject into RAG prompts.
    """
    personal_info = profile.get_personal_info()
    goals = profile.get_goals()
    experience = profile.get_experience()
    schedule = profile.get_schedule()
    equipment = profile.get_equipment()

    context = f"""
USER PROFILE CONTEXT:
- Experience: {experience.training_level} ({experience.years_training} years training)
- Schedule: {schedule.days_per_week} days/week, {schedule.minutes_per_session} min/session
- Split: {schedule.preferred_split}
- Equipment: {', '.join(equipment[:5])}{'...' if len(equipment) > 5 else ''}
- Current Phase: {goals.phase} ({personal_info.weight_lbs} lbs → {goals.target_weight_lbs or personal_info.weight_lbs} lbs)
- Goal: {goals.primary_goal}

INSTRUCTIONS FOR RAG RESPONSE:
- Provide SPECIFIC recommendations for THIS user (not generic advice)
- Use their experience level to determine volume/intensity
- Only recommend exercises they can do with THEIR equipment
- Provide TRACKABLE metrics (sets, reps, weight progressions)
- Structure response as coaching advice ("Based on your profile, DO THIS")
"""

    return context.strip()
```

**Example Output:**
```
USER PROFILE CONTEXT:
- Experience: intermediate (5 years training)
- Schedule: 4 days/week, 65 min/session
- Split: upper_lower
- Equipment: barbell, dumbbells, bench, rack, cables...
- Current Phase: bulk (185 lbs → 200 lbs)
- Goal: hypertrophy

INSTRUCTIONS FOR RAG RESPONSE:
- Provide SPECIFIC recommendations for THIS user (not generic advice)
- Use their experience level to determine volume/intensity
- Only recommend exercises they can do with THEIR equipment
- Provide TRACKABLE metrics (sets, reps, weight progressions)
- Structure response as coaching advice ("Based on your profile, DO THIS")
```

---

### Step 2: Update RAG Query Function (`src/rag_system.py`)

**Modify `query()` method to inject profile context:**

```python
class HealthRAG:
    def query(self, user_query: str, profile_context: str = None) -> Tuple[str, float]:
        """
        Query the RAG system with optional profile context.

        Args:
            user_query: User's question
            profile_context: Optional profile context string (from build_profile_context)

        Returns:
            (response, response_time)
        """
        start_time = time.time()

        # Retrieve relevant documents from ChromaDB
        docs = self.vectorstore.similarity_search(user_query, k=5)

        # Build context from retrieved documents
        doc_context = "\n\n".join([doc.page_content for doc in docs])

        # Build full prompt with profile context if provided
        if profile_context:
            prompt = f"""You are a personal fitness and nutrition coach providing advice to your client.

{profile_context}

RELEVANT KNOWLEDGE BASE:
{doc_context}

USER QUESTION:
{user_query}

YOUR COACHING RESPONSE:
Provide a personalized, actionable response based on the user's profile above. Include:
1. Specific recommendations (numbers, exercises, protocols)
2. Trackable metrics (sets, reps, progressions)
3. Reasoning based on their experience level and schedule
4. Citations from the knowledge base

Respond as their coach, not as a generic information source.
"""
        else:
            # Fallback to generic prompt (if no profile)
            prompt = f"""Based on the following context, answer the user's question:

{doc_context}

Question: {user_query}

Answer:"""

        # Generate response
        response = self.llm.invoke(prompt)

        response_time = time.time() - start_time
        return (response, response_time)
```

---

### Step 3: Update Main UI (`src/main.py`)

**Detect training/volume queries and inject profile context:**

```python
# In chat handler (src/main.py)

# Nutrition keywords (Week 2 - already implemented)
nutrition_keywords = [
    'macro', 'macros', 'calories', 'calorie', 'tdee',
    'protein', 'fat', 'carbs', 'nutrition'
]

# NEW: Training keywords (Week 3)
training_keywords = [
    'volume', 'sets', 'reps', 'how much',
    'exercise', 'workout', 'program', 'training',
    'routine', 'split', 'frequency'
]

is_nutrition_query = any(keyword in prompt.lower() for keyword in nutrition_keywords)
is_training_query = any(keyword in prompt.lower() for keyword in training_keywords)

if is_nutrition_query and profile.exists():
    # Week 2: Local calculation
    ...

elif is_training_query and profile.exists():
    # Week 3: Profile-aware RAG query
    with st.spinner(f"Analyzing your profile and training knowledge..."):
        profile.load()

        # Build profile context
        profile_context = build_profile_context(profile)

        # Query RAG with profile context
        response, response_time = st.session_state.rag_system.query(
            prompt,
            profile_context=profile_context
        )

        st.markdown(response)
        st.caption(f"⏱️ Response time: {response_time:.1f}s | 📊 Profile-Aware Coaching")

else:
    # Generic RAG query (no profile context)
    response, response_time = st.session_state.rag_system.query(prompt)
    ...
```

---

### Step 4: Test Profile-Aware Queries

**Create test cases for profile-aware responses:**

```python
# tests/test_profile_aware_rag.py

def test_volume_query_intermediate_4_days():
    """Test volume query with intermediate, 4 days/week profile"""
    profile = UserProfile()
    profile.load()  # Intermediate Ian profile

    query = "How much volume should I do per week?"
    profile_context = build_profile_context(profile)

    response, _ = rag_system.query(query, profile_context=profile_context)

    # Should mention specific numbers
    assert "14" in response or "16" in response  # Sets per muscle
    assert "intermediate" in response.lower()
    assert "4 days" in response.lower() or "four days" in response.lower()
    assert "Based on your profile" in response or "As an intermediate" in response


def test_exercise_query_home_gym():
    """Test exercise query filters by user's equipment"""
    profile = UserProfile()
    profile.load()  # Beginner Ben (home gym: dumbbells, bench, pull-up bar)

    query = "What are the best chest exercises I can do?"
    profile_context = build_profile_context(profile)

    response, _ = rag_system.query(query, profile_context=profile_context)

    # Should recommend exercises user CAN do
    assert "dumbbell" in response.lower()
    assert "push-up" in response.lower() or "push up" in response.lower()

    # Should NOT recommend exercises user CANNOT do
    assert "barbell bench" not in response.lower()  # No barbell
    assert "cable" not in response.lower()  # No cables


def test_generic_query_no_profile():
    """Test that generic queries still work without profile"""
    query = "What is progressive overload?"

    response, _ = rag_system.query(query, profile_context=None)

    # Should still provide answer
    assert "progressive" in response.lower()
    assert "overload" in response.lower()
```

---

## 📊 EXPECTED IMPROVEMENTS

### Before Week 3 (Generic RAG):
```
User: "How much volume should I do?"
Response: "Most people need 10-20 sets per muscle group per week."
Trackability: ❌ No specific numbers
Actionable: ❌ "Most people" not "YOU"
```

### After Week 3 (Profile-Aware RAG):
```
User: "How much volume should I do?"
Response: "Based on your profile (intermediate, 4 days/week Upper/Lower):
- Chest: 14-16 sets/week (7-8 sets each Upper day)
- Back: 14-16 sets/week (7-8 sets each Upper day)
- Quads: 16-18 sets/week (8-9 sets each Lower day)

Track total sets per muscle weekly. Increase by 2 sets if no progress after 2 weeks."

Trackability: ✅ Specific set counts per muscle
Actionable: ✅ "DO THIS, track THAT"
```

---

## 🎯 SUCCESS METRICS

### Week 3 Goals:

1. **Profile Context Injection** ✅
   - `build_profile_context()` function created
   - Profile context includes: experience, schedule, equipment, goals
   - Context instructs RAG to provide specific recommendations

2. **Profile-Aware Volume Recommendations** ✅
   - User asks "How much volume?" → Gets specific set counts per muscle
   - Recommendations based on experience level (beginner: 10-12, intermediate: 14-16, advanced: 18-22)
   - Recommendations based on schedule (4 days/week → 7-8 sets per session)

3. **Equipment-Filtered Exercise Recommendations** ✅
   - User asks "Best chest exercises?" → Gets exercises they CAN do
   - Filters out exercises requiring equipment they don't have
   - Prioritizes S/A-tier exercises from available equipment

4. **Trackable Metrics in All Responses** ✅
   - Every response includes specific numbers (sets, reps, weight)
   - Progression protocols included ("increase by 2 sets after 2 weeks")
   - Clear logging instructions ("track total sets per muscle weekly")

5. **Coaching Tone** ✅
   - Responses start with "Based on your profile..."
   - Use "you" not "most people"
   - Provide specific actions ("DO THIS") not just information

---

## 📝 TESTING SCENARIOS

### Scenario 1: Volume Question (Intermediate, 4 Days/Week)
**User:** "How much volume should I do per week?"

**Expected Response:**
- Mentions "intermediate" experience level
- Provides 14-16 sets per muscle group
- Breaks down by session (7-8 sets per muscle per workout)
- Includes progression protocol
- Cites RP Volume Landmarks

### Scenario 2: Exercise Selection (Home Gym)
**User:** "What are the best chest exercises?"

**Expected Response:**
- Filters to home gym equipment (dumbbells, bench, pull-up bar)
- Recommends: Dumbbell bench press, dumbbell flyes, push-ups
- Does NOT recommend: Barbell bench, cable flyes, dip station exercises
- Explains why (equipment constraints)
- Cites Jeff Nippard Tier List

### Scenario 3: Training Split Question (4 Days/Week)
**User:** "What split should I use?"

**Expected Response:**
- Recommends Upper/Lower (optimal for 4 days/week)
- Explains why (frequency, volume distribution)
- Provides sample structure (Mon: Upper, Tue: Lower, Thu: Upper, Sat: Lower)
- Cites RP training principles

### Scenario 4: Progression Protocol (Beginner)
**User:** "How do I progress on my lifts?"

**Expected Response:**
- Beginner-specific progression (linear progression)
- Specific protocol: Add 5 lbs per session (upper), 10 lbs (lower)
- When to deload (3 failed sessions in a row)
- Cites RP progression guidelines

---

## 🚀 IMPLEMENTATION ORDER (REVISED)

**Priority 1: Proactive Dashboard (Days 1-2) - MOST IMPORTANT**

User insight: "I'm not trying to memorize prompts like 'what are my macros?' since I'm acting as if this is my coach with a plan."

### Day 1: Proactive Dashboard MVP
- [ ] Create helper functions in `src/calculations.py`:
  - [ ] `get_expected_rate_text(phase)` - Returns "~1.0 lb/week loss" text
  - [ ] `get_phase_explanation(personal_info, goals, plan)` - Why these numbers?
- [ ] Create `render_proactive_dashboard()` in `src/main.py`
- [ ] Show nutrition plan automatically after profile load
- [ ] Remove need to ask "What are my macros?"

### Day 2: Dashboard Polish & Testing
- [ ] Add "Getting Started" steps (log weight, track calories)
- [ ] Add phase-specific coaching tips (cut vs bulk vs recomp)
- [ ] Test with all 5 personas
- [ ] Verify user sees plan immediately without asking

**Priority 2: Profile-Aware RAG (Days 3-5)**

### Day 3: Profile Context Builder
- [ ] Create `src/profile_context.py`
- [ ] Implement `build_profile_context(profile)`
- [ ] Test context generation with all 5 personas

### Day 4: RAG System Updates
- [ ] Update `src/rag_system.py` `query()` method
- [ ] Add profile_context parameter
- [ ] Update prompt template with profile injection
- [ ] Test with/without profile context

### Day 5: Training Query Detection
- [ ] Update `src/main.py` with training query detection
- [ ] Add profile context building for training queries
- [ ] Test: "How much volume?" → Gets personalized answer

**Priority 3: Testing & Documentation (Days 6-7)**

### Day 6: Testing
- [ ] Create `tests/test_profile_aware_rag.py`
- [ ] Test volume query → Specific set counts
- [ ] Test exercise query → Equipment-filtered results
- [ ] Test generic query → Still works without profile

### Day 7: Documentation & Week 3 Summary
- [ ] Document proactive dashboard approach
- [ ] Document profile-aware RAG improvements
- [ ] Create WEEK3_SUMMARY.md
- [ ] Update SCENARIOS.md with Week 3 progress

---

## 📈 EXPECTED OUTCOMES

### User Experience Improvements:
- **Before:** "Here's what's generally recommended..."
- **After:** "Based on your profile, DO THIS: 14-16 sets per muscle weekly, track these numbers..."

### Trackability:
- **Before:** Abstract ranges (10-20 sets)
- **After:** Specific targets (14-16 sets chest, 16-18 sets quads)

### Actionability:
- **Before:** "Most people need..."
- **After:** "YOU should do..."

### Coaching Quality:
- **Before:** Information retrieval
- **After:** Personalized coaching

---

## 🎓 KEY INSIGHT

**The user is absolutely right:** Generic answers are NOT helpful nor trackable.

A coach doesn't say "Most people need 10-20 sets."
A coach says "YOU need 14 sets for chest this week. Track it. If you're not progressing in 2 weeks, we'll increase to 16 sets."

**That's what Week 3 delivers.**

---

## ✅ READY TO START

**First Task:** Create `src/profile_context.py` with `build_profile_context()` function.

**End Goal:** Every RAG query becomes a coaching conversation, not a generic info dump.

Let's make HealthRAG actually coach! 💪
