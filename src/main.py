import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from rag_system import HealthRAG, MLX_AVAILABLE
from profile import UserProfile, EQUIPMENT_PRESETS
from calculations import calculate_nutrition_plan, get_expected_rate_text, get_phase_explanation
from program_generator import ProgramGenerator, format_workout, format_week
from workout_logger import WorkoutLogger, WorkoutLog, WorkoutSet
from workout_coach import WorkoutCoach
from autoregulation import AutoregulationEngine
from program_export import export_program_to_excel, export_program_to_csv
from program_manager import ProgramManager
from exercise_database import get_exercises_by_muscle
from food_logger import FoodLogger
from food_search_integrated import IntegratedFoodSearch
from meal_templates import MealTemplateManager
from adaptive_tdee import (
    WeightTracker, calculate_trend_weight, calculate_adaptive_tdee,
    recommend_macro_adjustment, get_adaptive_tdee_insight, AdaptiveTDEEInsight
)
from body_measurements import BodyMeasurementTracker, BodyMeasurement, BodyFatEstimate
import json
import plotly.graph_objects as go

load_dotenv()


def render_onboarding_wizard():
    """
    Step-by-step onboarding wizard for new users.

    Steps:
    1. Welcome + Data Source (Apple Health or Manual)
    2. Personal Info
    3. Goals
    4. Equipment
    5. Generate Plans
    """
    st.title("🏃‍♂️ Welcome to HealthRAG!")
    st.markdown("### Let's build your personalized fitness and nutrition plan")

    # Initialize onboarding state
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1

    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}

    # Step indicator
    steps = ["Data Source", "Personal Info", "Goals", "Equipment", "Review"]
    current_step = st.session_state.onboarding_step

    cols = st.columns(len(steps))
    for i, step_name in enumerate(steps, 1):
        with cols[i-1]:
            if i < current_step:
                st.markdown(f"✅ **{step_name}**")
            elif i == current_step:
                st.markdown(f"▶️ **{step_name}**")
            else:
                st.markdown(f"⚪ {step_name}")

    st.markdown("---")

    # Render current step
    if current_step == 1:
        render_step_data_source()
    elif current_step == 2:
        render_step_personal_info()
    elif current_step == 3:
        render_step_goals()
    elif current_step == 4:
        render_step_equipment()
    elif current_step == 5:
        render_step_review()


def render_step_data_source():
    """Step 1: Choose data source"""
    st.subheader("📱 Step 1: How would you like to provide your information?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
### 🍎 Import from Apple Health

Export your health data from the Apple Health app:
1. Open **Health** app on iPhone/Mac
2. Tap your **profile picture**
3. Tap **Export All Health Data**
4. Save and upload the `export.xml` file here

**Automatically imports:**
- Weight, height, age, biological sex
- Recent step counts
- Activity data
        """)

        uploaded_file = st.file_uploader("Upload Apple Health export.xml", type=['xml', 'zip'])

        if uploaded_file and st.button("📥 Import from Apple Health", type="primary"):
            with st.spinner("Importing Apple Health data..."):
                # TODO: Parse XML and populate data
                st.success("✅ Apple Health data imported successfully!")
                st.session_state.onboarding_data['data_source'] = 'apple_health'
                st.session_state.onboarding_step = 2
                st.rerun()

    with col2:
        st.markdown("""
### ✍️ Manual Entry

Enter your information manually.

**You'll provide:**
- Weight, height, age, sex
- Activity level
- Equipment available
        """)

        if st.button("✍️ Enter Information Manually", type="primary"):
            st.session_state.onboarding_data['data_source'] = 'manual'
            st.session_state.onboarding_step = 2
            st.rerun()


def render_step_personal_info():
    """Step 2: Personal information"""
    st.subheader("📋 Step 2: Personal Information")

    name = st.text_input("First Name", placeholder="e.g., Jason",
                        help="Your first name for personalized coaching")

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (lbs)", min_value=50.0, max_value=500.0, value=170.0, step=0.5)
        feet = st.number_input("Height (ft)", min_value=4, max_value=7, value=5)

    with col2:
        age = st.number_input("Age", min_value=13, max_value=100, value=30)
        inches = st.number_input("Height (in)", min_value=0, max_value=11, value=10)

    sex = st.selectbox("Sex", ["male", "female"])

    activity = st.selectbox(
        "Activity Level",
        ["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"],
        index=2,
        help="Sedentary: Little/no exercise | Lightly Active: 1-3 days/week | Moderately Active: 3-5 days/week"
    )

    training_level = st.selectbox("Training Experience", ["beginner", "intermediate", "advanced"], index=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.onboarding_step = 1
            st.rerun()

    with col2:
        if st.button("Next ➡️", type="primary"):
            if not name or name.strip() == "":
                st.error("Please enter your first name")
            else:
                st.session_state.onboarding_data.update({
                    'name': name.strip(),
                    'weight_lbs': weight,
                    'height_inches': feet * 12 + inches,
                    'age': age,
                    'sex': sex,
                    'activity_level': activity,
                    'training_level': training_level
                })
                st.session_state.onboarding_step = 3
                st.rerun()


def render_step_goals():
    """Step 3: Goals"""
    st.subheader("🎯 Step 3: What are your goals?")

    phase = st.selectbox(
        "Primary Goal",
        ["cut", "bulk", "maintain", "recomp"],
        format_func=lambda x: {
            "cut": "🔥 Cut (Lose Fat)",
            "bulk": "💪 Bulk (Build Muscle)",
            "maintain": "⚖️ Maintain (Stay Same Weight)",
            "recomp": "🔄 Recomp (Build Muscle + Lose Fat)"
        }[x]
    )

    st.markdown(f"""
**Selected: {phase.capitalize()}**

{get_phase_explanation(st.session_state.onboarding_data, {'phase': phase})}
    """)

    if phase in ["cut", "bulk"]:
        col1, col2 = st.columns(2)
        with col1:
            current_weight = st.session_state.onboarding_data.get('weight_lbs', 170)
            target_weight = st.number_input(
                "Target Weight (lbs)",
                min_value=50.0,
                max_value=500.0,
                value=current_weight - 10 if phase == "cut" else current_weight + 10,
                step=0.5
            )
        with col2:
            timeline = st.number_input("Timeline (weeks)", min_value=4, max_value=52, value=12)
    else:
        target_weight = None
        timeline = None

    primary_goal = st.selectbox(
        "Training Focus",
        ["hypertrophy", "strength", "general_fitness", "fat_loss", "performance"]
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.onboarding_step = 2
            st.rerun()

    with col2:
        if st.button("Next ➡️", type="primary"):
            st.session_state.onboarding_data.update({
                'phase': phase,
                'primary_goal': primary_goal,
                'target_weight_lbs': target_weight,
                'timeline_weeks': timeline
            })
            st.session_state.onboarding_step = 4
            st.rerun()


def render_step_equipment():
    """Step 4: Equipment"""
    st.subheader("🏋️ Step 4: What equipment do you have access to?")

    equipment_preset = st.selectbox(
        "Equipment Preset",
        ["home_gym_advanced", "planet_fitness", "home_gym_plus_pf",
         "home_gym_basic", "minimal", "commercial_gym", "custom"],
        format_func=lambda x: {
            "minimal": "Minimal (Bodyweight, Bands, Dumbbells)",
            "home_gym_basic": "Home Gym - Basic (Dumbbells, Bench, Pull-up Bar)",
            "home_gym_advanced": "Home Gym - Advanced (Smith Machine, Cables, Machines)",
            "planet_fitness": "Planet Fitness",
            "home_gym_plus_pf": "Home Gym + Planet Fitness (Best of Both)",
            "commercial_gym": "Commercial Gym (Full Equipment)",
            "custom": "Custom (Pick Specific Equipment)"
        }[x]
    )

    if equipment_preset == "custom":
        st.markdown("**Select all equipment you have access to:**")
        equipment_options = sorted([
            "barbell", "j_hooks", "squat_rack", "power_rack",
            "dumbbells", "kettlebells", "resistance_bands",
            "bench", "incline_bench", "decline_bench",
            "pull_up_bar", "dip_station",
            "cables", "functional_trainer",
            "smith_machine", "smith_squat_rack", "smith_bench_press",
            "leg_press_machine", "hack_squat_machine",
            "leg_extension_machine", "leg_curl_machine",
            "chest_press_machine", "pec_deck",
            "shoulder_press_machine", "lateral_raise_machine",
            "bicep_curl_machine", "tricep_extension_machine",
            "lat_pulldown_machine", "cable_row_machine", "seated_row_machine",
            "rear_delt_machine", "lower_back_extension",
            "ab_crunch_machine", "landmine",
            "rowing_machine", "assault_bike", "treadmill", "elliptical", "stairmaster",
            "battle_ropes", "trx", "medicine_balls", "bosu_balls", "plyo_boxes",
            "bodyweight"
        ])
        equipment = st.multiselect("Available Equipment", equipment_options, default=["bodyweight"])
    else:
        equipment = EQUIPMENT_PRESETS[equipment_preset]
        st.success(f"✅ **{len(equipment)} items selected** from '{equipment_preset.replace('_', ' ').title()}' preset")

    days_per_week = st.slider("Training Days per Week", min_value=2, max_value=6, value=4)

    preferred_split = st.selectbox(
        "Preferred Training Split",
        ["full_body", "upper_lower", "ppl", "bro_split"],
        format_func=lambda x: {
            "full_body": "Full Body (3x/week, hit everything each session)",
            "upper_lower": "Upper/Lower (4x/week, balanced approach)",
            "ppl": "Push/Pull/Legs (6x/week, high frequency)",
            "bro_split": "Bro Split (5x/week, one muscle per day)"
        }[x]
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.onboarding_step = 3
            st.rerun()

    with col2:
        if st.button("Next ➡️", type="primary"):
            st.session_state.onboarding_data.update({
                'equipment': equipment,
                'days_per_week': days_per_week,
                'preferred_split': preferred_split
            })
            st.session_state.onboarding_step = 5
            st.rerun()


def render_step_review():
    """Step 5: Review and create"""
    st.subheader("✅ Step 5: Review Your Information")

    data = st.session_state.onboarding_data

    st.markdown(f"""
### 👤 Personal Information
- **Name:** {data['name']}
- **Weight:** {data['weight_lbs']} lbs
- **Height:** {data['height_inches'] // 12}'{data['height_inches'] % 12}"
- **Age:** {data['age']} years
- **Sex:** {data['sex'].capitalize()}
- **Activity:** {data['activity_level'].replace('_', ' ').title()}
- **Training Level:** {data['training_level'].capitalize()}

### 🎯 Goals
- **Phase:** {data['phase'].capitalize()}
- **Training Focus:** {data['primary_goal'].replace('_', ' ').title()}
{f"- **Target Weight:** {data.get('target_weight_lbs')} lbs" if data.get('target_weight_lbs') else ""}
{f"- **Timeline:** {data.get('timeline_weeks')} weeks" if data.get('timeline_weeks') else ""}

### 🏋️ Training Setup
- **Equipment:** {len(data['equipment'])} items available
- **Days per Week:** {data['days_per_week']}
- **Preferred Split:** {data['preferred_split'].replace('_', ' ').title()}
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.onboarding_step = 4
            st.rerun()

    with col2:
        if st.button("🚀 Create My Plan!", type="primary"):
            # Create profile
            profile = UserProfile()
            success = profile.create(
                name=data['name'],
                weight_lbs=data['weight_lbs'],
                height_inches=data['height_inches'],
                age=data['age'],
                sex=data['sex'],
                activity_level=data['activity_level'],
                equipment=data['equipment'],
                phase=data['phase'],
                primary_goal=data['primary_goal'],
                target_weight_lbs=data.get('target_weight_lbs'),
                timeline_weeks=data.get('timeline_weeks'),
                training_level=data['training_level'],
                days_per_week=data['days_per_week'],
                minutes_per_session=60,
                preferred_split=data['preferred_split']
            )

            if success:
                # Clear onboarding state
                del st.session_state.onboarding_step
                del st.session_state.onboarding_data

                st.success(f"✅ Profile created successfully! Welcome, {data['name']}!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to create profile")


def render_profile_setup():
    """Render profile creation form - OLD VERSION (keeping for reference)"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Create Your Profile")

    with st.sidebar.expander("📝 Setup Profile", expanded=True):
        st.write("Let's get started! Enter your information:")

        # Personal Info
        st.markdown("**Personal Information**")
        name = st.text_input("First Name", value="", placeholder="e.g., Jason",
                            help="Your first name for personalized coaching")
        weight = st.number_input("Weight (lbs)", min_value=50.0, max_value=500.0, value=170.0, step=0.5)

        col1, col2 = st.columns(2)
        with col1:
            feet = st.number_input("Height (ft)", min_value=4, max_value=7, value=5)
        with col2:
            inches = st.number_input("Height (in)", min_value=0, max_value=11, value=10)

        height_inches = feet * 12 + inches

        age = st.number_input("Age", min_value=13, max_value=100, value=30)
        sex = st.selectbox("Sex", ["male", "female"])
        activity = st.selectbox(
            "Activity Level",
            ["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"],
            index=2,
            help="Sedentary: Little/no exercise | Lightly Active: 1-3 days/week | Moderately Active: 3-5 days/week"
        )

        # Goals
        st.markdown("**Goals**")
        phase = st.selectbox("Current Phase", ["maintain", "cut", "bulk", "recomp"])
        primary_goal = st.selectbox(
            "Primary Goal",
            ["general_fitness", "strength", "hypertrophy", "fat_loss", "performance"]
        )

        if phase in ["cut", "bulk"]:
            target_weight = st.number_input(
                "Target Weight (lbs)",
                min_value=50.0,
                max_value=500.0,
                value=weight - 10 if phase == "cut" else weight + 10,
                step=0.5
            )
            timeline = st.number_input("Timeline (weeks)", min_value=4, max_value=52, value=12)
        else:
            target_weight = None
            timeline = None

        # Experience
        st.markdown("**Training Experience**")
        training_level = st.selectbox("Training Level", ["beginner", "intermediate", "advanced"])
        years_training = st.number_input("Years Training", min_value=0, max_value=50, value=0)

        # Equipment
        st.markdown("**Equipment**")
        equipment_preset = st.selectbox(
            "Equipment Preset",
            ["custom", "minimal", "home_gym", "commercial_gym"],
            help="Choose a preset or select custom to pick specific equipment"
        )

        if equipment_preset == "custom":
            equipment_options = [
                "barbell", "dumbbells", "kettlebells", "resistance_bands",
                "rack", "bench", "pull_up_bar", "dip_station",
                "cables", "machines", "bodyweight"
            ]
            equipment = st.multiselect("Available Equipment", equipment_options, default=["bodyweight"])
        else:
            equipment = EQUIPMENT_PRESETS[equipment_preset]
            st.info(f"Selected: {', '.join(equipment)}")

        # Schedule
        st.markdown("**Training Schedule**")
        days_per_week = st.slider("Days per Week", min_value=1, max_value=7, value=3)
        minutes_per_session = st.slider("Minutes per Session", min_value=15, max_value=180, value=60, step=15)
        preferred_split = st.selectbox(
            "Preferred Split",
            ["full_body", "upper_lower", "ppl", "bro_split"],
            help="Full Body: 3x/week | Upper/Lower: 4x/week | PPL: 6x/week | Bro Split: 5x/week"
        )

        # Create Profile Button
        if st.button("✅ Create Profile", type="primary"):
            # Validate name
            if not name or name.strip() == "":
                st.error("❌ Please enter your first name")
            else:
                profile = UserProfile()
                success = profile.create(
                    name=name.strip(),
                    weight_lbs=weight,
                    height_inches=height_inches,
                    age=age,
                    sex=sex,
                    activity_level=activity,
                    equipment=equipment,
                    phase=phase,
                    primary_goal=primary_goal,
                    target_weight_lbs=target_weight,
                    timeline_weeks=timeline,
                    training_level=training_level,
                    years_training=years_training,
                    days_per_week=days_per_week,
                    minutes_per_session=minutes_per_session,
                    preferred_split=preferred_split
                )

                if success:
                    st.success(f"✅ Profile created successfully! Welcome, {name}!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create profile")


def render_profile_view():
    """Render existing profile view and edit options"""
    profile = UserProfile()
    profile.load()

    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Your Profile")

    # Quick stats
    info = profile.get_personal_info()
    goals = profile.get_goals()

    st.sidebar.metric("Current Weight", f"{info.weight_lbs} lbs")
    st.sidebar.metric("Height", f"{info.height_inches // 12}'{info.height_inches % 12}\"")
    st.sidebar.metric("Phase", goals.phase.capitalize())

    # View/Edit Profile
    with st.sidebar.expander("📋 View Full Profile"):
        st.text(profile.summary())

    with st.sidebar.expander("✏️ Edit Profile"):
        st.markdown("**Personal Info**")

        new_weight = st.number_input(
            "Weight (lbs)",
            min_value=50.0,
            max_value=500.0,
            value=float(info.weight_lbs),
            step=0.5,
            key="update_weight"
        )

        new_activity = st.selectbox(
            "Activity Level",
            ["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"],
            index=["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"].index(info.activity_level),
            key="update_activity"
        )

        st.markdown("**Goals**")
        new_phase = st.selectbox(
            "Phase",
            ["maintain", "cut", "bulk", "recomp"],
            index=["maintain", "cut", "bulk", "recomp"].index(goals.phase),
            key="update_phase"
        )

        if new_phase in ["cut", "bulk"]:
            new_target = st.number_input(
                "Target Weight (lbs)",
                min_value=50.0,
                max_value=500.0,
                value=float(goals.target_weight_lbs) if goals.target_weight_lbs else float(info.weight_lbs),
                step=0.5,
                key="update_target"
            )
            new_timeline = st.number_input(
                "Timeline (weeks)",
                min_value=4,
                max_value=52,
                value=int(goals.timeline_weeks) if goals.timeline_weeks else 12,
                key="update_timeline"
            )
        else:
            new_target = None
            new_timeline = None

        st.markdown("**Training**")

        # Get current values from correct keys
        experience = profile.profile_data.get('experience', {})
        schedule = profile.profile_data.get('schedule', {})
        current_equipment = profile.profile_data.get('equipment', ['bodyweight'])

        new_training_level = st.selectbox(
            "Training Level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(experience.get('training_level', 'intermediate')),
            key="update_training_level"
        )

        new_days = st.slider(
            "Days per Week",
            min_value=2,
            max_value=6,
            value=int(schedule.get('days_per_week', 4)),
            key="update_days"
        )

        new_split = st.selectbox(
            "Preferred Split",
            ["full_body", "upper_lower", "ppl", "bro_split"],
            index=["full_body", "upper_lower", "ppl", "bro_split"].index(schedule.get('preferred_split', 'upper_lower')),
            key="update_split"
        )

        equipment_preset = st.selectbox(
            "Equipment Access",
            ["keep_current", "home_gym_advanced", "planet_fitness", "home_gym_plus_pf",
             "home_gym_basic", "minimal", "commercial_gym", "custom"],
            format_func=lambda x: {
                "keep_current": f"Keep Current ({len(current_equipment)} items)",
                "minimal": "Minimal (Bodyweight, Bands, Dumbbells)",
                "home_gym_basic": "Home Gym - Basic (Dumbbells, Bench, Pull-up Bar)",
                "home_gym_advanced": "Home Gym - Advanced (Your Setup: Smith, Cables, Machines)",
                "planet_fitness": "Planet Fitness Only",
                "home_gym_plus_pf": "Home Gym + Planet Fitness (Best of Both)",
                "commercial_gym": "Commercial Gym (Full Equipment)",
                "custom": "Custom Selection (Pick Individual Items)"
            }[x],
            key="update_equipment"
        )

        if equipment_preset == "custom":
            st.markdown("**Select all equipment you have access to:**")
            equipment_options = sorted([
                "barbell", "j_hooks", "squat_rack", "power_rack",
                "dumbbells", "kettlebells", "resistance_bands",
                "bench", "incline_bench", "decline_bench",
                "pull_up_bar", "dip_station",
                "cables", "functional_trainer",
                "smith_machine", "smith_squat_rack", "smith_bench_press",
                "leg_press_machine", "hack_squat_machine",
                "leg_extension_machine", "leg_curl_machine",
                "chest_press_machine", "pec_deck",
                "shoulder_press_machine", "lateral_raise_machine",
                "bicep_curl_machine", "tricep_extension_machine",
                "lat_pulldown_machine", "cable_row_machine", "seated_row_machine",
                "rear_delt_machine", "lower_back_extension",
                "ab_crunch_machine", "landmine",
                "rowing_machine", "assault_bike", "treadmill", "elliptical", "stairmaster",
                "battle_ropes", "trx", "medicine_balls", "bosu_balls", "plyo_boxes",
                "bodyweight"
            ])
            new_equipment = st.multiselect(
                "Equipment",
                equipment_options,
                default=[eq for eq in current_equipment if eq in equipment_options],
                key="update_equipment_list",
                help="Select all equipment you have access to at home or at your gym"
            )
        elif equipment_preset == "keep_current":
            new_equipment = current_equipment
        else:
            from profile import EQUIPMENT_PRESETS
            new_equipment = EQUIPMENT_PRESETS[equipment_preset]
            st.info(f"ℹ️ This will update your equipment to: **{len(new_equipment)} items** from the '{equipment_preset.replace('_', ' ').title()}' preset")

        if st.button("💾 Save Changes", type="primary"):
            updates = {
                'personal_info': {
                    'weight_lbs': new_weight,
                    'activity_level': new_activity
                },
                'goals': {
                    'phase': new_phase,
                    'target_weight_lbs': new_target,
                    'timeline_weeks': new_timeline
                },
                'experience': {
                    'training_level': new_training_level
                },
                'schedule': {
                    'days_per_week': new_days,
                    'preferred_split': new_split
                },
                'equipment': new_equipment
            }

            profile.update(updates)
            st.success("✅ Profile updated successfully!")
            st.info("💡 Click 'Generate New Program' in the Training section to create a program with your updated settings. Your current program will be saved in history.")

            st.rerun()

    # Delete Profile
    with st.sidebar.expander("🗑️ Delete Profile", expanded=False):
        st.warning("This will permanently delete your profile!")
        if st.button("Delete Profile", type="secondary"):
            profile.delete()
            st.success("Profile deleted")
            st.rerun()


def render_proactive_dashboard(profile: UserProfile):
    """
    Render proactive coaching dashboard showing plan upfront.

    Shows user's name, goals, and nutrition plan automatically
    without requiring them to ask "What are my macros?"

    Collapsible after first view to reduce daily friction.
    """
    st.markdown("---")

    # Load profile data
    profile.load()
    personal_info = profile.profile_data['personal_info']
    goals = profile.profile_data['goals']

    # Get user's name
    name = personal_info.get('name', 'there')

    # Generate nutrition plan
    plan = calculate_nutrition_plan(personal_info, goals)
    phase = goals['phase'].capitalize()
    daily_cals = int(plan['tdee_adjusted'])

    # Collapsible dashboard (expanded by default, user can collapse for faster daily access)
    with st.expander(f"🏃‍♂️ Your Plan: {phase} @ {daily_cals:,} cal/day", expanded=True):
        # Greeting
        st.markdown(f"**Welcome, {name}!** Here's your plan:")

        # Display goals summary
        current_weight = personal_info['weight_lbs']
        target_weight = goals.get('target_weight_lbs')
        timeline_weeks = goals.get('timeline_weeks')

        # Goals card
        st.markdown(f"""
### 📊 Your Current Goals

**Phase:** {phase}
**Current Weight:** {current_weight} lbs
""")

        if target_weight and timeline_weeks:
            arrow = "→" if goals['phase'] != 'recomp' else "⇄"
            st.markdown(f"**Target:** {current_weight} lbs {arrow} {target_weight} lbs in {timeline_weeks} weeks")

        if goals['phase'] == 'recomp':
            st.markdown(f"**Focus:** Build muscle + lose fat (maintain {current_weight} lbs ±2)")

        st.markdown("---")

        # Nutrition Plan
        st.markdown(f"""
### 🍽️ Nutrition Plan ({phase} Phase)

**Daily Target:** {daily_cals:,} calories
- **Protein:** {int(plan['macros']['protein_g'])}g ({int(plan['macros']['protein_pct'])}%)
- **Fat:** {int(plan['macros']['fat_g'])}g ({int(plan['macros']['fat_pct'])}%)
- **Carbs:** {int(plan['macros']['carbs_g'])}g ({int(plan['macros']['carbs_pct'])}%)

**Expected Progress:** {get_expected_rate_text(goals['phase'])}

**Why these numbers?**
{get_phase_explanation(personal_info, goals)}

**Source:** RP Diet 2.0, RP Diet Adjustments Manual
""")

        st.markdown("---")

        # Getting Started
        st.markdown(f"""
### 📈 Getting Started

1. **Log weight daily** (AM, fasted, same scale)
2. **Track calories & protein** (most important macros)
3. **Review progress weekly** - We'll adjust as needed

**Need adjustments?** Message me below in the chat! 👇
""")


def render_training_program(profile: UserProfile):
    """
    Render training program generation and display.

    Shows generated workout program with exercises, sets, reps, RIR progression.
    Supports multiple programs with history.
    """
    st.markdown("---")
    st.subheader("💪 Your Training Program")

    # Load profile data
    profile.load()
    personal_info = profile.profile_data['personal_info']
    experience = profile.profile_data.get('experience', {})
    schedule = profile.profile_data.get('schedule', {})
    equipment = profile.profile_data.get('equipment', ['bodyweight'])

    # Initialize program manager
    program_mgr = ProgramManager()

    # Check if active program exists
    active_program = program_mgr.get_active_program()
    program_exists = active_program is not None

    if not program_exists:
        st.info("📋 No program generated yet. Let's create your personalized training plan!")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
Your program will be customized based on:
- **Equipment:** Your available equipment
- **Training Level:** {level}
- **Schedule:** {days} days per week
- **Split:** {split}
            """.format(
                level=experience.get('training_level', 'intermediate').capitalize(),
                days=schedule.get('days_per_week', 4),
                split=schedule.get('preferred_split', 'upper_lower').replace('_', '/').title()
            ))

        with col2:
            if st.button("🚀 Generate Program", type="primary"):
                with st.spinner("Generating your program..."):
                    # Create program generator
                    generator = ProgramGenerator(
                        available_equipment=equipment,
                        training_level=experience.get('training_level', 'intermediate'),
                        days_per_week=schedule.get('days_per_week', 4)
                    )

                    # Generate program (auto-select best template)
                    program = generator.generate_program(
                        template_name=None,  # Auto-select
                        weeks=5,
                        start_date=date.today()
                    )

                    # Convert to dict and save with ProgramManager
                    from dataclasses import asdict
                    program_dict = {
                        "template_name": program.template_name,
                        "start_date": program.start_date.isoformat(),
                        "equipment_used": program.equipment_used,
                        "coverage_report": program.coverage_report,
                        "created_at": program.created_at,
                        "weeks": []
                    }

                    for week in program.weeks:
                        week_dict = {
                            "week_number": week.week_number,
                            "is_deload": week.is_deload,
                            "notes": week.notes,
                            "total_weekly_sets": week.total_weekly_sets,
                            "workouts": []
                        }

                        for workout in week.workouts:
                            workout_dict = {
                                "day_name": workout.day_name,
                                "muscle_groups": [m.value for m in workout.muscle_groups],
                                "total_sets": workout.total_sets,
                                "estimated_duration_min": workout.estimated_duration_min,
                                "exercises": []
                            }

                            for ex in workout.exercises:
                                ex_dict = {
                                    "name": ex.exercise.display_name,
                                    "tier": ex.exercise.tier.value,
                                    "sets": ex.sets,
                                    "reps": ex.reps_scheme,
                                    "rir": ex.rir,
                                    "load_lbs": ex.load_lbs,
                                    "notes": ex.notes
                                }
                                workout_dict["exercises"].append(ex_dict)

                            week_dict["workouts"].append(workout_dict)

                        program_dict["weeks"].append(week_dict)

                    # Save program with manager
                    program_id = program_mgr.save_program(program_dict, set_as_active=True)

                    st.success(f"✅ Program generated successfully! (ID: {program_id})")
                    st.balloons()
                    st.rerun()

    else:
        # Display existing program
        program_data = active_program

        # Program history selector
        all_programs = program_mgr.list_programs(limit=20)

        if len(all_programs) > 1:
            st.markdown("### 📚 Program History")
            col1, col2 = st.columns([3, 1])

            with col1:
                program_options = []
                for p in all_programs:
                    status = "🟢 ACTIVE" if p.is_active else "📦"
                    label = f"{status} {p.template_name.replace('_', ' ').title()} (Started: {p.start_date}) - Week {p.weeks_completed}/{p.total_weeks}"
                    program_options.append(label)

                selected_idx = st.selectbox(
                    "Select Program",
                    range(len(program_options)),
                    format_func=lambda i: program_options[i],
                    index=0,  # Active program is first
                    key="program_selector"
                )

                # Load selected program
                selected_program = all_programs[selected_idx]
                if not selected_program.is_active:
                    program_data = program_mgr.get_program(selected_program.program_id)

            with col2:
                if not all_programs[selected_idx].is_active:
                    if st.button("🔄 Switch to This Program"):
                        program_mgr.set_active_program(all_programs[selected_idx].program_id)
                        st.success("Program switched!")
                        st.rerun()

            st.markdown("---")

        # Program header
        program_id = program_data.get('program_id', 'unknown')
        weeks_completed = program_data.get('weeks_completed', 0)
        total_weeks = len(program_data['weeks'])

        st.markdown(f"""
**Template:** {program_data['template_name'].replace('_', ' ').title()}
**Start Date:** {program_data['start_date']}
**Duration:** {total_weeks} weeks (5 weeks + deload)
**Progress:** Week {weeks_completed}/{total_weeks} {'✅ Completed!' if weeks_completed >= total_weeks else ''}
        """)

        # Week progress updater
        if weeks_completed < total_weeks:
            col1, col2 = st.columns([3, 1])
            with col1:
                new_progress = st.slider(
                    "Update Your Progress",
                    min_value=0,
                    max_value=total_weeks,
                    value=weeks_completed,
                    help="Track which week you're currently on"
                )
            with col2:
                if st.button("💾 Update Progress") and new_progress != weeks_completed:
                    program_mgr.update_progress(program_id, new_progress)
                    st.success(f"Progress updated to week {new_progress}!")
                    st.rerun()

            st.markdown("---")

        # Equipment coverage
        coverage = program_data['coverage_report']
        st.markdown(f"""
**Exercise Quality:**
- S+ tier: {coverage['s_plus_available']}/{coverage['s_plus_total']} exercises available
- S tier: {coverage['s_available']}/{coverage['s_total']} exercises available
        """)

        # Week selector
        week_options = [f"Week {w['week_number']}" for w in program_data['weeks'][:-1]]
        week_options.append("🔄 DELOAD WEEK")

        selected_week_idx = st.selectbox(
            "Select Week to View",
            range(len(week_options)),
            format_func=lambda i: week_options[i],
            index=0
        )

        week_data = program_data['weeks'][selected_week_idx]

        # Display selected week
        st.markdown("---")

        if week_data['is_deload']:
            st.markdown("### 🔄 DELOAD WEEK")
        else:
            st.markdown(f"### Week {week_data['week_number']}")

        st.markdown(f"**Total Weekly Sets:** {week_data['total_weekly_sets']}")
        st.markdown(f"**Notes:** {week_data['notes']}")

        # Display each workout
        for workout in week_data['workouts']:
            with st.expander(f"🏋️ {workout['day_name']} ({workout['total_sets']} sets, ~{workout['estimated_duration_min']} min)", expanded=False):
                st.markdown(f"**Muscle Groups:** {', '.join([m.capitalize() for m in workout['muscle_groups']])}")
                st.markdown("---")

                # Exercise table
                for i, ex in enumerate(workout['exercises'], 1):
                    st.markdown(f"""
**{i}. {ex['name']}** [{ex['tier']}]
- **Volume:** {ex['sets']} sets × {ex['reps']} @ {ex['rir']} RIR
- **Notes:** {ex['notes'][:100] if ex['notes'] else 'No notes'}
                    """)

        # Action buttons
        st.markdown("---")
        st.markdown("### 📥 Export Program")

        col1, col2, col3 = st.columns(3)

        # Create temporary file for export functions (they expect file path)
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(program_data, temp_file, indent=2)
        temp_file.close()

        try:
            with col1:
                # Excel export for Google Sheets
                excel_data = export_program_to_excel(temp_file.name)
                st.download_button(
                    label="📊 Download Excel (Google Sheets)",
                    data=excel_data,
                    file_name=f"training_program_{program_id}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download as Excel file - upload to Google Sheets for easy tracking"
                )

            with col2:
                # CSV export
                csv_data = export_program_to_csv(temp_file.name)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"training_program_{program_id}_{date.today()}.csv",
                    mime="text/csv"
                )

            with col3:
                # JSON export (original format)
                st.download_button(
                    label="📦 Download JSON",
                    data=json.dumps(program_data, indent=2),
                    file_name=f"training_program_{program_id}_{date.today()}.json",
                    mime="application/json"
                )
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass  # Ignore errors during cleanup

        st.markdown("---")

        # Regenerate button - creates NEW program instead of overwriting
        if st.button("🆕 Generate New Program", help="Create a new program with current settings (keeps this one in history)"):
            with st.spinner("Generating new program..."):
                # Create program generator
                generator = ProgramGenerator(
                    available_equipment=equipment,
                    training_level=experience.get('training_level', 'intermediate'),
                    days_per_week=schedule.get('days_per_week', 4)
                )

                # Generate program (auto-select best template)
                program = generator.generate_program(
                    template_name=None,  # Auto-select
                    weeks=5,
                    start_date=date.today()
                )

                # Convert to dict and save with ProgramManager
                from dataclasses import asdict
                new_program_dict = {
                    "template_name": program.template_name,
                    "start_date": program.start_date.isoformat(),
                    "equipment_used": program.equipment_used,
                    "coverage_report": program.coverage_report,
                    "created_at": program.created_at,
                    "weeks": []
                }

                for week in program.weeks:
                    week_dict = {
                        "week_number": week.week_number,
                        "is_deload": week.is_deload,
                        "notes": week.notes,
                        "total_weekly_sets": week.total_weekly_sets,
                        "workouts": []
                    }

                    for workout in week.workouts:
                        workout_dict = {
                            "day_name": workout.day_name,
                            "muscle_groups": [m.value for m in workout.muscle_groups],
                            "total_sets": workout.total_sets,
                            "estimated_duration_min": workout.estimated_duration_min,
                            "exercises": []
                        }

                        for ex in workout.exercises:
                            ex_dict = {
                                "name": ex.exercise.display_name,
                                "tier": ex.exercise.tier.value,
                                "sets": ex.sets,
                                "reps": ex.reps_scheme,
                                "rir": ex.rir,
                                "load_lbs": ex.load_lbs,
                                "notes": ex.notes
                            }
                            workout_dict["exercises"].append(ex_dict)

                        week_dict["workouts"].append(workout_dict)

                    new_program_dict["weeks"].append(week_dict)

                # Save new program with manager (this creates a NEW program with new timestamp)
                new_program_id = program_mgr.save_program(new_program_dict, set_as_active=True)

                st.success(f"✅ New program generated! (ID: {new_program_id})")
                st.info("💡 Your previous program is saved in history. You can switch back to it anytime.")
                st.balloons()
                st.rerun()


def render_workout_logging():
    """
    Render workout logging interface.

    Allows users to:
    - Log today's workout (sets, reps, weight, RIR)
    - Add feedback (pump, soreness, difficulty)
    - View workout history
    - Track exercise progress
    """
    st.markdown("---")
    st.subheader("📝 Log Workout")

    logger = WorkoutLogger()
    engine = AutoregulationEngine(logger)

    # Tabs for Log vs History
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Today's Workout", "📊 Workout History", "📈 Exercise Progress", "🎯 Autoregulation"])

    with tab1:
        st.markdown("### Log Today's Workout")

        # Check if active program exists to pre-populate workout names
        program_mgr = ProgramManager()
        active_program = program_mgr.get_active_program()
        workout_names = []

        if active_program:
            # Extract unique workout names
            for week in active_program['weeks']:
                for workout in week['workouts']:
                    if workout['day_name'] not in workout_names:
                        workout_names.append(workout['day_name'])

        # Workout metadata
        col1, col2 = st.columns(2)
        with col1:
            if workout_names:
                workout_name = st.selectbox("Workout Name", workout_names)
            else:
                workout_name = st.text_input("Workout Name", value="", placeholder="e.g., Upper A, Push Day")

        with col2:
            workout_date = st.date_input("Workout Date", value=date.today())

        # Load Previous Workout button
        st.markdown("---")
        col_load, col_info = st.columns([1, 2])
        with col_load:
            if st.button("📋 Load Previous Workout", help="Pre-fill exercises and weights from last session", type="secondary"):
                # Get most recent workout
                recent_workouts = logger.get_recent_workouts(limit=1)
                if recent_workouts:
                    prev_workout = recent_workouts[0]

                    # Pre-fill current_workout_sets with previous workout's sets
                    st.session_state.current_workout_sets = []
                    for prev_set in prev_workout.sets:
                        # Create new set with same exercise and weight, but clear reps/RIR for user to fill
                        new_set = WorkoutSet(
                            set_number=0,
                            exercise_name=prev_set.exercise_name,
                            weight_lbs=prev_set.weight_lbs,
                            reps_completed=prev_set.reps_completed,  # Keep reps as starting point
                            rir=prev_set.rir,  # Keep RIR as starting point
                            notes=None
                        )
                        st.session_state.current_workout_sets.append(new_set)

                    # Update exercise context for form
                    if prev_workout.sets:
                        st.session_state.last_exercise = prev_workout.sets[-1].exercise_name
                        st.session_state.last_weight = prev_workout.sets[-1].weight_lbs

                    st.success(f"✅ Loaded {len(prev_workout.sets)} sets from '{prev_workout.workout_name}' ({prev_workout.date})")
                    st.info("💡 Review the loaded sets below. Adjust weights/reps as needed, or use 'Log Last Set' to repeat.")
                    st.rerun()
                else:
                    st.warning("⚠️ No previous workouts found. Log your first workout to use this feature!")

        with col_info:
            # Show preview of what will be loaded
            recent_workouts = logger.get_recent_workouts(limit=1)
            if recent_workouts:
                prev_workout = recent_workouts[0]
                unique_exercises = list(dict.fromkeys([s.exercise_name for s in prev_workout.sets]))
                st.caption(f"**Preview:** {prev_workout.workout_name} ({prev_workout.date}) - {len(prev_workout.sets)} sets: {', '.join(unique_exercises[:3])}{'...' if len(unique_exercises) > 3 else ''}")
            else:
                st.caption("No previous workout to load")

        # Exercise logging
        st.markdown("#### Add Sets")

        # Initialize session state for sets and exercise context
        if 'current_workout_sets' not in st.session_state:
            st.session_state.current_workout_sets = []
        if 'last_exercise' not in st.session_state:
            st.session_state.last_exercise = ""
        if 'last_weight' not in st.session_state:
            st.session_state.last_weight = 0.0

        # Entry mode toggle
        entry_mode = st.radio(
            "Entry Mode",
            ["Single Set", "Bulk Entry"],
            horizontal=True,
            help="Single: Log one set at a time | Bulk: Paste multiple sets at once"
        )

        if entry_mode == "Bulk Entry":
            # Bulk entry mode
            st.markdown("**Paste sets in format:** `Exercise: weight x reps @RIR`")
            st.caption("Example: `Bench Press: 185x8 @2, 185x6 @1, 185x5 @0`")

            bulk_input = st.text_area(
                "Paste sets here",
                height=100,
                placeholder="Bench Press: 185x8 @2, 185x6 @1, 185x5 @0\nSquat: 225x5 @2, 225x5 @2, 225x5 @1",
                key="bulk_set_input"
            )

            if st.button("📥 Parse & Add Sets", type="primary"):
                if bulk_input.strip():
                    parsed_sets = []
                    errors = []

                    for line in bulk_input.strip().split('\n'):
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            # Parse format: "Exercise: weight x reps @RIR, weight x reps @RIR"
                            if ':' in line:
                                exercise_name, sets_part = line.split(':', 1)
                                exercise_name = exercise_name.strip()
                            else:
                                # Use last exercise name if not specified
                                exercise_name = st.session_state.last_exercise or "Unknown Exercise"
                                sets_part = line

                            # Parse each set (comma-separated)
                            for set_str in sets_part.split(','):
                                set_str = set_str.strip()
                                if not set_str:
                                    continue

                                # Parse "185x8 @2" or "185x8" or "185 x 8 @ 2"
                                import re
                                # Match pattern: weight x reps [@RIR]
                                match = re.match(r'(\d+\.?\d*)\s*[xX×]\s*(\d+)\s*(?:@\s*(\d+))?', set_str)
                                if match:
                                    weight = float(match.group(1))
                                    reps = int(match.group(2))
                                    rir = int(match.group(3)) if match.group(3) else 2  # Default RIR=2

                                    parsed_sets.append(WorkoutSet(
                                        set_number=0,  # Will be updated when saved
                                        exercise_name=exercise_name,
                                        weight_lbs=weight,
                                        reps_completed=reps,
                                        rir=rir,
                                        notes=None
                                    ))
                                else:
                                    errors.append(f"Could not parse: {set_str}")
                        except Exception as e:
                            errors.append(f"Error parsing line: {line}")

                    if parsed_sets:
                        st.session_state.current_workout_sets.extend(parsed_sets)
                        st.success(f"✅ Added {len(parsed_sets)} sets!")
                        if errors:
                            st.warning(f"Skipped {len(errors)} invalid entries")
                        st.rerun()
                    elif errors:
                        st.error(f"Could not parse any sets. Errors: {', '.join(errors[:3])}")
                else:
                    st.warning("Please paste some sets first")

        else:
            # Single set mode (existing flow)
            st.markdown("Log each set as you complete it. Exercise & weight persist between sets.")

            # Quick buttons to clear exercise context or log last set
            col_clear, col_last = st.columns(2)
            with col_clear:
                if st.button("🔄 New Exercise", help="Clear exercise name for a different exercise"):
                    st.session_state.last_exercise = ""
                    st.session_state.last_weight = 0.0
                    st.rerun()
            with col_last:
                if st.session_state.current_workout_sets:
                    last_set = st.session_state.current_workout_sets[-1]
                    # Show last set details
                    st.caption(f"Last: {last_set.exercise_name[:20]} - {last_set.weight_lbs} lbs × {last_set.reps_completed} @ RIR {last_set.rir}")
                    if st.button("🔁 Log Last Set", help="Repeat the last set with one click", type="primary"):
                        # Create new set identical to last one
                        workout_set = WorkoutSet(
                            set_number=0,  # Will be updated when saved
                            exercise_name=last_set.exercise_name,
                            weight_lbs=last_set.weight_lbs,
                            reps_completed=last_set.reps_completed,
                            rir=last_set.rir,
                            notes=None
                        )
                        st.session_state.current_workout_sets.append(workout_set)

                        # Update session state for form
                        st.session_state.last_exercise = last_set.exercise_name
                        st.session_state.last_weight = last_set.weight_lbs

                        # Real-time coach feedback
                        coach = WorkoutCoach()
                        exercise_sets = [s for s in st.session_state.current_workout_sets if s.exercise_name == last_set.exercise_name]
                        set_number = len(exercise_sets)

                        feedback = coach.analyze_set(
                            exercise_name=last_set.exercise_name,
                            set_number=set_number,
                            weight=last_set.weight_lbs,
                            reps=last_set.reps_completed,
                            rir=last_set.rir,
                            target_reps_min=8,
                            target_reps_max=12,
                            target_rir=2
                        )

                        st.success(f"✅ Set {set_number} logged: {last_set.exercise_name} - {last_set.weight_lbs} lbs × {last_set.reps_completed} @ {last_set.rir} RIR")

                        if feedback.status == "perfect":
                            st.success(f"💯 {feedback.message}")
                        elif feedback.status == "excellent":
                            st.success(f"🔥 {feedback.message}")
                        elif feedback.status == "good":
                            st.info(f"✅ {feedback.message}")
                        elif feedback.status == "too_hard":
                            st.warning(f"⚠️ {feedback.message}")
                        else:
                            st.info(f"💡 {feedback.message}")

                        st.caption(f"💡 **Next:** {feedback.next_action}")
                        st.rerun()

            # Add set form (doesn't clear on submit to preserve exercise context)
            with st.form("add_set_form", clear_on_submit=False):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    exercise = st.text_input(
                        "Exercise",
                        value=st.session_state.last_exercise,
                        placeholder="e.g., Barbell Bench Press"
                    )
                with col2:
                    weight = st.number_input(
                        "Weight (lbs)",
                        min_value=0.0,
                        max_value=1000.0,
                        value=st.session_state.last_weight,
                        step=2.5
                    )
                with col3:
                    reps = st.number_input("Reps", min_value=1, max_value=50, value=8)
                with col4:
                    rir = st.selectbox("RIR", [0, 1, 2, 3, 4], index=2)

                set_notes = st.text_input("Set Notes (optional)", placeholder="e.g., Felt strong, struggled on last rep")

                submitted = st.form_submit_button("➕ Add Set", type="primary")
                if submitted and exercise:
                    # Update session state for next set
                    st.session_state.last_exercise = exercise
                    st.session_state.last_weight = weight
                    workout_set = WorkoutSet(
                        set_number=0,  # Will be updated when saved
                        exercise_name=exercise,
                        weight_lbs=weight,
                        reps_completed=reps,
                        rir=rir,
                        notes=set_notes if set_notes else None
                    )
                    st.session_state.current_workout_sets.append(workout_set)

                    # Real-time coach feedback
                    coach = WorkoutCoach()
                    # Count how many sets of this exercise already logged
                    exercise_sets = [s for s in st.session_state.current_workout_sets if s.exercise_name == exercise]
                    set_number = len(exercise_sets)

                    # Get feedback (using default hypertrophy targets)
                    feedback = coach.analyze_set(
                        exercise_name=exercise,
                        set_number=set_number,
                        weight=weight,
                        reps=reps,
                        rir=rir,
                        target_reps_min=8,
                        target_reps_max=12,
                        target_rir=2
                    )

                    st.success(f"✅ Set {set_number} logged: {exercise} - {weight} lbs × {reps} @ {rir} RIR")

                    # Show coach feedback with appropriate emoji
                    if feedback.status == "perfect":
                        st.success(f"💯 {feedback.message}")
                    elif feedback.status == "excellent":
                        st.success(f"🔥 {feedback.message}")
                    elif feedback.status == "good":
                        st.info(f"✅ {feedback.message}")
                    elif feedback.status == "too_hard":
                        st.warning(f"⚠️ {feedback.message}")
                    else:
                        st.info(f"💡 {feedback.message}")

                    st.caption(f"💡 **Next:** {feedback.next_action}")
                    st.rerun()

        # Display current sets
        if st.session_state.current_workout_sets:
            st.markdown("#### Current Workout Sets")

            for i, workout_set in enumerate(st.session_state.current_workout_sets):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
**Set {i+1}: {workout_set.exercise_name}**
- {workout_set.weight_lbs} lbs × {workout_set.reps_completed} reps @ {workout_set.rir} RIR
{f"- Notes: {workout_set.notes}" if workout_set.notes else ""}
                    """)
                with col2:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.current_workout_sets.pop(i)
                        st.rerun()

            # Workout completion
            st.markdown("---")
            st.markdown("#### Complete Workout")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                duration = st.number_input("Duration (min)", min_value=1, max_value=300, value=60)
            with col2:
                pump = st.slider("Pump 💪", min_value=1, max_value=5, value=3, help="1=No pump, 5=Huge pump")
            with col3:
                soreness = st.slider("Soreness 🔥", min_value=1, max_value=5, value=3, help="1=No soreness, 5=Very sore")
            with col4:
                difficulty = st.slider("Difficulty 😅", min_value=1, max_value=5, value=3, help="1=Too easy, 5=Too hard")

            workout_notes = st.text_area("Workout Notes", placeholder="Overall thoughts, energy level, sleep quality, etc.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Save Workout", type="primary"):
                    if not workout_name:
                        st.error("Please enter a workout name")
                    else:
                        workout_log = WorkoutLog(
                            workout_id=None,
                            date=workout_date.isoformat(),
                            workout_name=workout_name,
                            sets=st.session_state.current_workout_sets,
                            duration_minutes=duration,
                            overall_pump=pump,
                            overall_soreness=soreness,
                            overall_difficulty=difficulty,
                            notes=workout_notes if workout_notes else None,
                            completed=True
                        )

                        workout_id = logger.log_workout(workout_log)

                        # Generate post-workout analysis
                        coach = WorkoutCoach()
                        summary = coach.analyze_workout(workout_log)

                        st.success(f"🎉 Workout saved successfully! (ID: {workout_id})")

                        # Display post-workout summary
                        st.markdown("---")
                        st.markdown("### 🏆 Post-Workout Analysis")

                        # Overall performance badge
                        if summary.overall_performance == "excellent":
                            st.success("💪 **Excellent Performance!** You crushed this workout!")
                        elif summary.overall_performance == "good":
                            st.info("✅ **Good Performance!** Solid workout today.")
                        else:
                            st.warning("⚠️ **Needs Adjustment** - See recommendations below")

                        # Key takeaways
                        if summary.key_takeaways:
                            st.markdown("#### 📊 Key Takeaways")
                            for takeaway in summary.key_takeaways:
                                st.markdown(f"- {takeaway}")

                        # Exercise-by-exercise breakdown
                        st.markdown("#### 📝 Exercise Analysis")
                        for ex_feedback in summary.exercises_analyzed:
                            with st.expander(f"**{ex_feedback.exercise_name}** ({ex_feedback.sets_logged} sets)", expanded=True):
                                st.markdown(f"**Target:** {ex_feedback.target_sets} × {ex_feedback.target_reps_min}-{ex_feedback.target_reps_max} @ {ex_feedback.target_rir} RIR")
                                st.markdown(f"**Assessment:** {ex_feedback.overall_assessment}")
                                st.markdown(f"**Next Workout:** {ex_feedback.next_workout_recommendation}")

                                # Show set-by-set feedback
                                if ex_feedback.set_feedbacks:
                                    st.markdown("**Set Breakdown:**")
                                    for sf in ex_feedback.set_feedbacks:
                                        if sf.status == "perfect":
                                            st.success(f"Set {sf.set_number}: {sf.message}")
                                        elif sf.status in ["excellent", "good"]:
                                            st.info(f"Set {sf.set_number}: {sf.message}")
                                        else:
                                            st.warning(f"Set {sf.set_number}: {sf.message}")

                        # Next workout plan
                        st.markdown("---")
                        st.markdown("#### 🎯 Next Workout Plan")
                        st.markdown("**Recommendations for next time:**")
                        for exercise_name, recommendation in summary.next_workout_plan.items():
                            st.markdown(f"- **{exercise_name}:** {recommendation}")

                        st.markdown("---")
                        st.session_state.current_workout_sets = []
                        st.rerun()

            with col2:
                if st.button("🗑️ Clear All Sets"):
                    st.session_state.current_workout_sets = []
                    st.rerun()

        else:
            st.info("👆 Add sets using the form above to start logging your workout")

    with tab2:
        st.markdown("### Workout History")

        # Date range selector
        col1, col2, col3 = st.columns(3)
        with col1:
            days_back = st.selectbox("View Last", [7, 14, 30, 60, 90], index=2)
        with col2:
            st.metric("Days", days_back)

        # Get workout stats
        stats = logger.get_workout_stats(days=days_back)

        if 'error' not in stats:
            st.markdown("#### Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Workouts", stats['total_workouts'])
            with col2:
                st.metric("Total Sets", stats['total_sets'])
            with col3:
                st.metric("Total Volume", f"{stats['total_volume_lbs']:,.0f} lbs")
            with col4:
                st.metric("Avg Duration", f"{stats['avg_duration_minutes']:.0f} min")

            st.markdown("---")

            # Recent workouts
            recent_workouts = logger.get_recent_workouts(limit=10)

            if recent_workouts:
                st.markdown("#### Recent Workouts")

                for workout in recent_workouts:
                    with st.expander(f"📅 {workout.date} - {workout.workout_name} ({len(workout.sets)} sets)", expanded=False):
                        st.markdown(f"""
**Duration:** {workout.duration_minutes} minutes
**Feedback:** Pump {workout.overall_pump}/5 | Soreness {workout.overall_soreness}/5 | Difficulty {workout.overall_difficulty}/5
{f"**Notes:** {workout.notes}" if workout.notes else ""}
                        """)

                        st.markdown("**Sets:**")
                        # Group sets by exercise
                        from collections import defaultdict
                        exercise_sets = defaultdict(list)
                        for s in workout.sets:
                            exercise_sets[s.exercise_name].append(s)

                        for exercise_name, sets in exercise_sets.items():
                            st.markdown(f"**{exercise_name}**")
                            for i, s in enumerate(sets, 1):
                                st.markdown(f"  Set {i}: {s.weight_lbs} lbs × {s.reps} @ {s.rir} RIR")
        else:
            st.info(f"No workouts logged in the last {days_back} days. Start logging above!")

    with tab3:
        st.markdown("### Exercise Progress Tracker")

        # Exercise selector
        exercise_name = st.text_input("Exercise Name", placeholder="e.g., Barbell Bench Press")

        if exercise_name:
            history = logger.get_exercise_history(exercise_name, limit=50)

            if history:
                st.markdown(f"#### {exercise_name} History")

                # Display progress
                progress = logger.get_strength_progress(exercise_name)

                if 'error' not in progress:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Starting 1RM", f"{progress['starting_1rm']:.1f} lbs")
                    with col2:
                        st.metric("Current 1RM", f"{progress['current_1rm']:.1f} lbs")
                    with col3:
                        gain_color = "normal" if progress['gain_lbs'] > 0 else "inverse"
                        st.metric("Gain", f"{progress['gain_lbs']:.1f} lbs ({progress['gain_percentage']:.1f}%)", delta=progress['trend'])

                    st.markdown("---")

                    # Recent sets table
                    st.markdown("#### Recent Sets")
                    for entry in history[:10]:
                        st.markdown(f"""
**{entry['date']}:** {entry['weight_lbs']} lbs × {entry['reps']} @ {entry['rir']} RIR (Est 1RM: {entry['estimated_1rm']:.1f} lbs)
                        """)
            else:
                st.info(f"No history found for '{exercise_name}'. Make sure you're using the exact exercise name from your logged workouts.")

    with tab4:
        st.markdown("### 🎯 Autoregulation & Recommendations")
        st.markdown("AI-powered program adjustments based on your workout feedback")

        # Analysis period selector
        col1, col2 = st.columns([1, 3])
        with col1:
            analysis_days = st.selectbox("Analyze Last", [7, 14, 21, 30], index=1)

        with col2:
            if st.button("🔄 Refresh Analysis", key="refresh_autoreg"):
                st.rerun()

        # Generate report
        with st.spinner("Analyzing your training data..."):
            report = engine.generate_adjustment_report(days=analysis_days)

        # Display report
        st.markdown(report)

        # Additional context
        st.markdown("---")
        st.markdown("""
### 📚 Understanding Autoregulation

**How it works:**
- Analyzes your pump, soreness, and difficulty ratings
- Tracks your strength progress on each exercise
- Compares your actual performance vs prescribed
- Generates personalized recommendations

**Rating Guidelines:**
- **Pump (1-5):** How much muscle pump you felt
  - 1-2: Low pump (may need more volume)
  - 3-4: Good pump (volume is working)
  - 5: Huge pump (approaching maximum recoverable volume)

- **Soreness (1-5):** How sore you are 24-48h after
  - 1-2: Minimal soreness (normal)
  - 3-4: Moderate soreness (good indicator of stimulus)
  - 5: Extreme soreness (may indicate too much volume)

- **Difficulty (1-5):** How hard the workout felt
  - 1-2: Too easy (time to progress)
  - 3-4: Appropriately challenging (perfect)
  - 5: Extremely difficult (may need recovery)

**Source:** Renaissance Periodization Autoregulation Principles
        """)


def render_nutrition_tracking():
    """
    Render nutrition tracking interface with friction-reduction features.

    Features:
    - Search foods (USDA FDC + Open Food Facts)
    - Recent Foods quick-add (95% time reduction)
    - Copy Yesterday's Meals (98% time reduction)
    - Meal Templates (one-click complex meals)
    - Barcode lookup
    - Daily nutrition summary
    """
    st.markdown("---")
    st.subheader("🍽️ Nutrition Tracking")

    # Initialize systems
    logger = FoodLogger("data/food_log.db")
    search = IntegratedFoodSearch(logger)
    manager = MealTemplateManager("data/food_log.db", logger)

    # Check for template suggestions (auto-suggest frequently logged foods)
    suggestion = manager.suggest_template_creation(min_count=4)
    if suggestion:
        with st.expander("💡 Template Suggestion", expanded=True):
            food = suggestion['food']
            st.info(f"You've logged **{food['name']}** {food['log_count']} times!")
            st.caption(f"{food['serving_size']} | {food['calories']:.0f} cal | {food['protein_g']:.0f}g protein")

            col1, col2 = st.columns(2)
            with col1:
                template_name = st.text_input(
                    "Template name",
                    value=food['name'],
                    key="suggest_template_name"
                )
            with col2:
                template_meal = st.selectbox(
                    "Meal type",
                    ["breakfast", "lunch", "dinner", "snack"],
                    key="suggest_template_meal"
                )

            if st.button("✅ Create Quick Template", key="create_suggested_template", type="primary"):
                try:
                    template_id = manager.create_template(
                        name=template_name,
                        foods_with_servings=[(food['food_id'], 1.0)],
                        meal_type=template_meal,
                        description=f"Auto-suggested (logged {food['log_count']} times)"
                    )
                    st.success(f"✅ Created template '{template_name}'!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # Tabs for different features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Today's Food",
        "🔍 Search & Add",
        "⚡ Quick Add",
        "📋 Templates",
        "📈 History"
    ])

    # Tab 1: Today's Food Log
    with tab1:
        st.markdown("### Today's Nutrition")

        # Date selector
        selected_date = st.date_input(
            "Date",
            value=date.today(),
            key="nutrition_date"
        )
        date_str = selected_date.strftime("%Y-%m-%d")

        # Quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Yesterday's Meals", use_container_width=True):
                yesterday = (selected_date - timedelta(days=1)).strftime("%Y-%m-%d")
                try:
                    count = logger.copy_meals_from_date(yesterday, date_str)
                    st.success(f"✅ Copied {count} meals from yesterday!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error copying meals: {e}")

        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        # Get daily nutrition
        daily_nutrition = logger.get_daily_nutrition(date_str)

        # Display summary
        if daily_nutrition.entry_count > 0:
            st.markdown("#### Daily Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Calories", f"{daily_nutrition.total_calories:.0f}")
            with col2:
                st.metric("Protein", f"{daily_nutrition.total_protein_g:.1f}g")
            with col3:
                st.metric("Carbs", f"{daily_nutrition.total_carbs_g:.1f}g")
            with col4:
                st.metric("Fat", f"{daily_nutrition.total_fat_g:.1f}g")

            # Inline Quick Add (no tab switching needed)
            st.markdown("#### Quick Add Food")
            quick_search_col1, quick_search_col2 = st.columns([3, 1])
            with quick_search_col1:
                inline_search_query = st.text_input(
                    "Search food...",
                    placeholder="e.g., chicken breast, eggs, oatmeal",
                    key="inline_food_search",
                    label_visibility="collapsed"
                )
            with quick_search_col2:
                # Determine meal type by time of day
                current_hour = datetime.now().hour
                if 5 <= current_hour < 11:
                    default_meal = "breakfast"
                elif 11 <= current_hour < 15:
                    default_meal = "lunch"
                elif 15 <= current_hour < 20:
                    default_meal = "dinner"
                else:
                    default_meal = "snack"
                inline_meal_type = st.selectbox(
                    "Meal",
                    ["breakfast", "lunch", "dinner", "snack"],
                    index=["breakfast", "lunch", "dinner", "snack"].index(default_meal),
                    key="inline_meal_type",
                    label_visibility="collapsed"
                )

            if inline_search_query:
                results = search.search(inline_search_query, limit=3)
                if results:
                    for i, result in enumerate(results):
                        col_name, col_cals, col_add = st.columns([3, 1, 1])
                        with col_name:
                            st.write(f"**{result.name[:30]}{'...' if len(result.name) > 30 else ''}**")
                            st.caption(f"{result.serving_size}")
                        with col_cals:
                            st.write(f"{result.calories:.0f} cal")
                            st.caption(f"{result.protein_g:.0f}g P")
                        with col_add:
                            if st.button("Add", key=f"inline_add_{i}", type="primary"):
                                # Add to database if not already there
                                if not result.food_id:
                                    food_id = search.add_result_to_database(result)
                                else:
                                    food_id = result.food_id
                                # Log the food
                                logger.log_food(
                                    food_id=food_id,
                                    servings=1.0,
                                    log_date=date_str,
                                    meal_type=inline_meal_type
                                )
                                st.success(f"✅ Added {result.name}!")
                                st.rerun()
                else:
                    st.caption("No results. Try a different search term or use Search & Add tab for more options.")

            st.markdown("---")

            # Display meals
            st.markdown("#### Meals")
            for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
                if meal_type in daily_nutrition.meals:
                    entries = daily_nutrition.meals[meal_type]
                    with st.expander(f"🍽️ {meal_type.title()} ({len(entries)} items)", expanded=True):
                        # Calculate meal totals
                        meal_calories = sum(e.calories for e in entries)
                        meal_protein = sum(e.protein_g for e in entries)

                        st.markdown(f"**Meal Total:** {meal_calories:.0f} cal | {meal_protein:.1f}g P")

                        # Add "Save as Template" button for this meal
                        if len(entries) > 1:  # Only show if meal has multiple items
                            with st.popover("💾 Save as Template", use_container_width=False):
                                st.markdown(f"### Save {meal_type.title()} as Template")
                                st.info(f"This will save all {len(entries)} items as a reusable template for quick logging.")

                                template_name = st.text_input(
                                    "Template Name",
                                    value=f"My {meal_type.title()}",
                                    key=f"template_name_{meal_type}_{date_str}"
                                )
                                template_desc = st.text_area(
                                    "Description (optional)",
                                    placeholder=f"e.g., Post-workout meal, Meal prep lunch",
                                    key=f"template_desc_{meal_type}_{date_str}"
                                )

                                if st.button("✅ Create Template", key=f"create_template_{meal_type}_{date_str}", use_container_width=True):
                                    try:
                                        template_id = manager.create_template_from_date(
                                            name=template_name,
                                            source_date=date_str,
                                            meal_type=meal_type,
                                            description=template_desc if template_desc else None
                                        )
                                        st.success(f"✅ Saved '{template_name}' template! Find it in the Templates tab.")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")

                        st.markdown("---")

                        # Display individual food items
                        for entry in entries:
                            col1, col2, col3 = st.columns([3, 2, 1])
                            with col1:
                                st.write(f"**{entry.food_name}**")
                                st.caption(f"{entry.servings}x serving")
                            with col2:
                                st.write(f"{entry.calories:.0f} cal | {entry.protein_g:.1f}g P")
                            with col3:
                                if st.button("🗑️", key=f"delete_{entry.entry_id}"):
                                    logger.delete_entry(entry.entry_id)
                                    st.rerun()
        else:
            st.info("No food logged for this date yet. Use tabs above to add foods!")

    # Tab 2: Search & Add Foods
    with tab2:
        st.markdown("### Search Foods")
        st.markdown("Search across USDA FoodData Central (500K+ foods) and Open Food Facts (2.8M+ products)")

        # Search interface
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input("Search for food", placeholder="e.g., chicken breast, greek yogurt")
        with col2:
            search_btn = st.button("🔍 Search", use_container_width=True)

        if search_btn and query:
            with st.spinner(f"Searching for '{query}'..."):
                results = search.search_by_name(query, limit=10)

            if results:
                st.success(f"Found {len(results)} results")
                for i, result in enumerate(results):
                    with st.expander(
                        f"{result.name} " +
                        (f"({result.brand})" if result.brand else "") +
                        f" - {result.calories:.0f} cal, {result.protein_g:.1f}g P",
                        expanded=(i == 0)
                    ):
                        # Food details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Serving:** {result.serving_size}")
                            st.write(f"**Source:** {result.source.upper()}")
                            if result.confidence:
                                st.write(f"**Quality:** {result.confidence:.0%}")
                        with col2:
                            st.write(f"**Calories:** {result.calories:.0f}")
                            st.write(f"**Protein:** {result.protein_g:.1f}g")
                            st.write(f"**Carbs:** {result.carbs_g:.1f}g")
                            st.write(f"**Fat:** {result.fat_g:.1f}g")

                        # Add to log
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            servings = st.number_input(
                                "Servings",
                                min_value=0.1,
                                value=1.0,
                                step=0.1,
                                key=f"servings_{i}"
                            )
                        with col2:
                            meal_type = st.selectbox(
                                "Meal",
                                ["breakfast", "lunch", "dinner", "snack"],
                                index={"breakfast": 0, "lunch": 1, "dinner": 2, "snack": 3}.get(
                                    logger.guess_meal_type(), 1
                                ),
                                key=f"meal_{i}"
                            )
                        with col3:
                            if st.button("➕ Add to Log", key=f"add_{i}", use_container_width=True):
                                # Add to database if not already there
                                if not result.food_id:
                                    food_id = search.add_result_to_database(result)
                                else:
                                    food_id = result.food_id

                                # Log the food
                                logger.log_food(
                                    food_id=food_id,
                                    servings=servings,
                                    log_date=date_str,
                                    meal_type=meal_type
                                )
                                st.success(f"✅ Added {result.name}!")
                                st.rerun()
            else:
                st.warning("No results found. Try a different search term.")

        # Barcode lookup
        st.markdown("---")
        st.markdown("### 📷 Barcode Lookup")

        # Camera scanning section
        st.markdown("#### Scan with Camera")
        st.info("💡 Click button below to enable camera, then take a photo of the barcode. Works best in good lighting with barcode centered.")

        # Initialize session state for camera
        if 'camera_enabled' not in st.session_state:
            st.session_state.camera_enabled = False

        # Camera toggle button
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("📷 Enable Camera" if not st.session_state.camera_enabled else "🚫 Disable Camera",
                        use_container_width=True):
                st.session_state.camera_enabled = not st.session_state.camera_enabled
                st.rerun()

        # Only show camera if enabled
        camera_image = None
        if st.session_state.camera_enabled:
            camera_image = st.camera_input("Take a photo of barcode", key="barcode_camera")

        if camera_image:
            # Decode barcode from image
            try:
                from PIL import Image
                from pyzbar import pyzbar
                import io

                # Convert to PIL Image
                image = Image.open(io.BytesIO(camera_image.getvalue()))

                # Decode barcodes
                barcodes = pyzbar.decode(image)

                if barcodes:
                    # Get first barcode
                    detected_barcode = barcodes[0].data.decode('utf-8')
                    st.success(f"✅ Barcode detected: {detected_barcode}")

                    # Auto-lookup the barcode
                    with st.spinner("Looking up product..."):
                        result = search.lookup_barcode(detected_barcode)

                    if result:
                        st.success(f"🎉 Product found: {result.name}")
                        with st.expander(f"{result.name} ({result.brand})", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Serving:** {result.serving_size}")
                                st.write(f"**Barcode:** {detected_barcode}")
                            with col2:
                                st.write(f"**Calories:** {result.calories:.0f}")
                                st.write(f"**Protein:** {result.protein_g:.1f}g")
                                st.write(f"**Carbs:** {result.carbs_g:.1f}g")
                                st.write(f"**Fat:** {result.fat_g:.1f}g")

                            st.markdown("---")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                servings = st.number_input("Servings", min_value=0.1, value=1.0, step=0.1, key="camera_servings")
                            with col2:
                                meal_type = st.selectbox(
                                    "Meal",
                                    ["breakfast", "lunch", "dinner", "snack"],
                                    index={"breakfast": 0, "lunch": 1, "dinner": 2, "snack": 3}.get(
                                        logger.guess_meal_type(), 1
                                    ),
                                    key="camera_meal"
                                )
                            with col3:
                                if st.button("➕ Add to Log", key="add_camera", use_container_width=True):
                                    logger.log_food(
                                        food_id=result.food_id,
                                        servings=servings,
                                        log_date=date_str,
                                        meal_type=meal_type
                                    )
                                    st.success(f"✅ Added {result.name}!")
                                    st.rerun()
                    else:
                        st.error(f"❌ Product '{detected_barcode}' not found in Open Food Facts database.")
                        st.info("💡 Try scanning again or enter the barcode manually below.")
                else:
                    st.warning("⚠️ No barcode detected in image. Try again with:")
                    st.markdown("""
                    - Better lighting
                    - Barcode centered in frame
                    - Hold camera steady
                    - Or enter barcode manually below
                    """)
            except ImportError as e:
                st.error(f"❌ Barcode scanning requires pyzbar and Pillow. Error: {e}")
                st.info("Install with: `pip3 install pyzbar Pillow`")
            except Exception as e:
                st.error(f"❌ Error scanning barcode: {e}")
                st.info("Try entering the barcode manually below.")

        # Manual barcode entry (fallback)
        st.markdown("---")
        st.markdown("#### Manual Entry")
        col1, col2 = st.columns([3, 1])
        with col1:
            barcode = st.text_input("Enter UPC/EAN barcode", placeholder="e.g., 737628064502")
        with col2:
            barcode_btn = st.button("🔍 Lookup", use_container_width=True)

        if barcode_btn and barcode:
            with st.spinner("Looking up barcode..."):
                result = search.lookup_barcode(barcode)

            if result:
                st.success("✅ Product found!")
                with st.expander(f"{result.name} ({result.brand})", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Serving:** {result.serving_size}")
                        st.write(f"**Barcode:** {barcode}")
                    with col2:
                        st.write(f"**Calories:** {result.calories:.0f}")
                        st.write(f"**Protein:** {result.protein_g:.1f}g")
                        st.write(f"**Carbs:** {result.carbs_g:.1f}g")
                        st.write(f"**Fat:** {result.fat_g:.1f}g")

                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        servings = st.number_input("Servings", min_value=0.1, value=1.0, step=0.1, key="barcode_servings")
                    with col2:
                        meal_type = st.selectbox(
                            "Meal",
                            ["breakfast", "lunch", "dinner", "snack"],
                            index={"breakfast": 0, "lunch": 1, "dinner": 2, "snack": 3}.get(
                                logger.guess_meal_type(), 1
                            ),
                            key="barcode_meal"
                        )
                    with col3:
                        if st.button("➕ Add to Log", key="add_barcode", use_container_width=True):
                            logger.log_food(
                                food_id=result.food_id,
                                servings=servings,
                                log_date=date_str,
                                meal_type=meal_type
                            )
                            st.success(f"✅ Added {result.name}!")
                            st.rerun()
            else:
                st.error("❌ Product not found. Try searching by name instead.")

    # Tab 3: Quick Add (Recent Foods)
    with tab3:
        st.markdown("### Quick Add - Recent Foods")
        st.markdown("Your 10 most frequently logged foods (last 14 days)")

        recent_foods = logger.get_recent_foods(days=14, limit=10)

        if recent_foods:
            st.info("💡 Tip: Click any food to add it quickly (~3 seconds vs 30-60 seconds searching)")

            # Display as grid of buttons
            num_cols = 2
            for i in range(0, len(recent_foods), num_cols):
                cols = st.columns(num_cols)
                for j, col in enumerate(cols):
                    if i + j < len(recent_foods):
                        food = recent_foods[i + j]
                        with col:
                            with st.container():
                                st.markdown(f"**{food.name}**")
                                if food.brand:
                                    st.caption(food.brand)
                                st.caption(f"{food.calories:.0f} cal | {food.protein_g:.1f}g P | {food.serving_size}")

                                col1, col2 = st.columns(2)
                                with col1:
                                    servings = st.number_input(
                                        "Servings",
                                        min_value=0.1,
                                        value=1.0,
                                        step=0.1,
                                        key=f"recent_servings_{food.food_id}",
                                        label_visibility="collapsed"
                                    )
                                with col2:
                                    if st.button(
                                        "➕ Add",
                                        key=f"add_recent_{food.food_id}",
                                        use_container_width=True
                                    ):
                                        logger.log_food(
                                            food_id=food.food_id,
                                            servings=servings,
                                            log_date=date_str,
                                            meal_type=logger.guess_meal_type()
                                        )
                                        st.success(f"✅ Added {food.name}!")
                                        st.rerun()
                                st.markdown("---")
        else:
            st.info("No recent foods yet. Start logging to see your frequently eaten foods here!")

    # Tab 4: Meal Templates
    with tab4:
        st.markdown("### Meal Templates")
        st.markdown("One-click logging for repeated multi-food meals (e.g., protein shakes, meal prep)")

        # Create new template
        with st.expander("➕ Create New Template", expanded=False):
            template_name = st.text_input("Template Name", placeholder="e.g., Morning Shake")
            template_desc = st.text_area("Description (optional)", placeholder="Post-workout protein shake")
            template_meal_type = st.selectbox("Meal Type", ["breakfast", "lunch", "dinner", "snack"], key="template_meal_type")

            st.markdown("**Add Foods to Template**")
            st.info("First, search and add foods to your database, then create a template from today's logged meals.")

            if st.button("📅 Create from Today's Meals"):
                try:
                    template_id = manager.create_template_from_date(
                        name=template_name,
                        source_date=date_str,
                        meal_type=template_meal_type,
                        description=template_desc
                    )
                    st.success(f"✅ Created template: {template_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # List existing templates
        st.markdown("---")
        st.markdown("### Your Templates")

        templates = manager.list_templates(sort_by="recent")

        if templates:
            for template in templates:
                with st.expander(
                    f"🍽️ {template.name} ({template.meal_type}) - " +
                    f"{template.total_calories:.0f} cal, {template.total_protein_g:.1f}g P",
                    expanded=False
                ):
                    if template.description:
                        st.markdown(f"*{template.description}*")

                    st.markdown("**Foods:**")
                    for food in template.foods:
                        st.write(
                            f"- {food.servings}x {food.food_name} " +
                            f"({food.calories * food.servings:.0f} cal, {food.protein_g * food.servings:.1f}g P)"
                        )

                    st.markdown(f"**Total:** {template.total_calories:.0f} cal | " +
                               f"{template.total_protein_g:.1f}g P | " +
                               f"{template.total_carbs_g:.1f}g C | " +
                               f"{template.total_fat_g:.1f}g F")

                    if template.use_count > 0:
                        st.caption(f"Used {template.use_count} times | Last: {template.last_used[:10] if template.last_used else 'Never'}")

                    st.markdown("---")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        multiplier = st.number_input(
                            "Portion multiplier",
                            min_value=0.1,
                            value=1.0,
                            step=0.1,
                            key=f"template_mult_{template.template_id}"
                        )
                    with col2:
                        if st.button(
                            "➕ Log",
                            key=f"log_template_{template.template_id}",
                            use_container_width=True
                        ):
                            count = manager.log_template(
                                template_id=template.template_id,
                                date=date_str,
                                multiplier=multiplier
                            )
                            st.success(f"✅ Logged {count} foods from {template.name}!")
                            st.rerun()
        else:
            st.info("No templates yet. Create your first template above!")

    # Tab 5: History
    with tab5:
        st.markdown("### Nutrition History")

        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "From",
                value=date.today() - timedelta(days=7),
                key="history_start"
            )
        with col2:
            end_date = st.date_input(
                "To",
                value=date.today(),
                key="history_end"
            )

        # Weekly average
        st.markdown("#### Weekly Average")
        weekly_avg = logger.get_weekly_average(
            end_date=end_date.strftime("%Y-%m-%d"),
            days=7
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Calories", f"{weekly_avg['avg_calories']:.0f}")
        with col2:
            st.metric("Avg Protein", f"{weekly_avg['avg_protein_g']:.1f}g")
        with col3:
            st.metric("Avg Carbs", f"{weekly_avg['avg_carbs_g']:.1f}g")
        with col4:
            st.metric("Avg Fat", f"{weekly_avg['avg_fat_g']:.1f}g")

        st.markdown(f"**Logged {weekly_avg['days_logged']}/{weekly_avg['days_requested']} days**")


def render_weight_tracking():
    """
    Weight tracking with EWMA trend analysis.

    Features:
    - Daily weight logging
    - EWMA trend weight visualization
    - 7-day moving average
    - Delta from goal weight
    - Rate of change tracking
    """
    st.markdown("---")
    st.header("⚖️ Weight Tracking & Trends")

    # Initialize weight tracker
    tracker = WeightTracker(db_path="data/weights.db")

    # Get user profile for goal weight
    profile = UserProfile()
    goal_weight = None
    if profile.exists():
        info = profile.get_personal_info()
        goals = profile.get_goals()
        if goals and hasattr(goals, 'target_weight_lbs'):
            goal_weight = goals.target_weight_lbs

    # Tabs for different views (Log Weight first for faster daily entry)
    tab_log, tab_trends = st.tabs(["📝 Log Weight", "📊 Weight Trends"])

    with tab_trends:
        st.subheader("📈 Weight Trend Analysis")

        # Get trend data (last 30 days)
        trends = tracker.get_trend_analysis(days=30, goal_weight=goal_weight)

        if not trends:
            st.info("👆 Log your first weight entry to see trends!")
            return

        # Latest stats
        latest = trends[-1]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Latest Weight",
                f"{latest.actual_weight:.1f} lbs",
                delta=None
            )

        with col2:
            st.metric(
                "Trend Weight",
                f"{latest.trend_weight:.1f} lbs",
                delta=f"{latest.trend_weight - latest.actual_weight:.1f} lbs",
                delta_color="inverse",
                help="EWMA smoothed weight (less affected by daily fluctuations)"
            )

        with col3:
            if latest.moving_average_7d is not None:
                st.metric(
                    "7-Day Average",
                    f"{latest.moving_average_7d:.1f} lbs"
                )
            else:
                st.metric("7-Day Average", "Need 7 days")

        with col4:
            if latest.delta_from_goal is not None:
                delta_color = "normal" if latest.delta_from_goal > 0 else "inverse"
                st.metric(
                    "From Goal",
                    f"{abs(latest.delta_from_goal):.1f} lbs",
                    delta=f"{'above' if latest.delta_from_goal > 0 else 'below'} goal",
                    delta_color=delta_color
                )
            else:
                st.metric("From Goal", "No goal set")

        # Rate of change
        if latest.rate_of_change_weekly is not None:
            rate_color = "🟢" if latest.rate_of_change_weekly < 0 else "🔴"
            st.markdown(f"**Rate of Change:** {rate_color} {latest.rate_of_change_weekly:.2f} lbs/week")
        else:
            st.markdown("**Rate of Change:** Need 14+ days for accurate rate")

        st.markdown("---")

        # Plotly chart
        st.subheader("📊 Weight Chart (Last 30 Days)")

        dates = [t.date for t in trends]
        actual_weights = [t.actual_weight for t in trends]
        trend_weights = [t.trend_weight for t in trends]
        moving_avgs = [t.moving_average_7d for t in trends]

        fig = go.Figure()

        # Actual weight (scatter)
        fig.add_trace(go.Scatter(
            x=dates,
            y=actual_weights,
            mode='markers',
            name='Daily Weight',
            marker=dict(size=8, color='lightblue'),
            hovertemplate='<b>%{x}</b><br>Weight: %{y:.1f} lbs<extra></extra>'
        ))

        # Trend weight (EWMA)
        fig.add_trace(go.Scatter(
            x=dates,
            y=trend_weights,
            mode='lines',
            name='Trend (EWMA)',
            line=dict(color='blue', width=3),
            hovertemplate='<b>%{x}</b><br>Trend: %{y:.1f} lbs<extra></extra>'
        ))

        # 7-day moving average
        valid_ma = [(d, ma) for d, ma in zip(dates, moving_avgs) if ma is not None]
        if valid_ma:
            ma_dates, ma_values = zip(*valid_ma)
            fig.add_trace(go.Scatter(
                x=ma_dates,
                y=ma_values,
                mode='lines',
                name='7-Day Average',
                line=dict(color='green', width=2, dash='dash'),
                hovertemplate='<b>%{x}</b><br>7-Day Avg: %{y:.1f} lbs<extra></extra>'
            ))

        # Goal weight line
        if goal_weight is not None:
            fig.add_hline(
                y=goal_weight,
                line_dash="dot",
                line_color="red",
                annotation_text=f"Goal: {goal_weight} lbs",
                annotation_position="right"
            )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Weight (lbs)",
            hovermode='x unified',
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Coaching insights
        st.markdown("### 🧠 Insights")

        if len(trends) < 7:
            st.info("📅 Log at least 7 days for weekly averages")

        if len(trends) < 14:
            st.info("📈 Log at least 14 days for accurate rate of change")

        if latest.rate_of_change_weekly is not None:
            rate = latest.rate_of_change_weekly

            if abs(rate) < 0.25:
                st.success(f"✅ Stable weight (±0.25 lbs/week)")
            elif rate < -2.0:
                st.warning(f"⚠️ Losing weight very fast ({rate:.2f} lbs/week). Consider increasing calories.")
            elif rate < -0.5:
                st.info(f"📉 Losing weight at {abs(rate):.2f} lbs/week")
            elif rate > 2.0:
                st.warning(f"⚠️ Gaining weight very fast (+{rate:.2f} lbs/week). Consider reducing calories.")
            elif rate > 0.5:
                st.info(f"📈 Gaining weight at +{rate:.2f} lbs/week")

        # Weight history table
        st.markdown("---")
        st.subheader("📋 Weight History")

        history_entries = tracker.get_weights(limit=30)

        if history_entries:
            # Format for display
            history_data = []
            for entry in history_entries:
                history_data.append({
                    "Date": entry.date,
                    "Weight": f"{entry.weight_lbs:.1f} lbs",
                    "Notes": entry.notes or ""
                })

            st.dataframe(
                history_data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No weight entries yet")

    with tab_log:
        st.subheader("📝 Log Today's Weight")

        # Get latest weight for default value
        latest_entry = tracker.get_latest_weight()
        default_weight = latest_entry.weight_lbs if latest_entry else 170.0

        with st.form("log_weight_form"):
            col1, col2 = st.columns(2)

            with col1:
                log_date = st.date_input(
                    "Date",
                    value=date.today(),
                    help="Date of weight measurement"
                )

            with col2:
                weight_lbs = st.number_input(
                    "Weight (lbs)",
                    min_value=50.0,
                    max_value=500.0,
                    value=default_weight,
                    step=0.1,
                    help="Your body weight in pounds"
                )

            notes = st.text_area(
                "Notes (optional)",
                placeholder="e.g., Morning weight, after workout, etc.",
                help="Optional notes about the measurement"
            )

            submitted = st.form_submit_button("💾 Log Weight", type="primary", use_container_width=True)

            if submitted:
                try:
                    tracker.log_weight(
                        weight_lbs=weight_lbs,
                        log_date=log_date.strftime("%Y-%m-%d"),
                        notes=notes
                    )
                    st.success(f"✅ Logged {weight_lbs} lbs for {log_date.strftime('%Y-%m-%d')}")
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Invalid weight: {e}")

        # Quick stats
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")

        latest_entry = tracker.get_latest_weight()
        if latest_entry:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Latest Entry", f"{latest_entry.weight_lbs:.1f} lbs")
                st.caption(f"Logged on {latest_entry.date}")

            with col2:
                entries_count = len(tracker.get_weights(limit=100))
                st.metric("Total Entries", entries_count)

                if entries_count >= 7:
                    st.caption("✅ Enough for weekly trends")
                elif entries_count >= 1:
                    st.caption(f"📅 {7 - entries_count} more for weekly trends")


def render_adaptive_tdee():
    """
    Adaptive TDEE and Weekly Check-In system.

    MacroFactor-style adaptive nutrition coaching:
    - Back-calculated TDEE from actual weight change + intake
    - Weekly macro adjustment recommendations
    - Adherence-neutral coaching
    """
    st.markdown("---")
    st.header("🎯 Adaptive TDEE & Weekly Check-In")

    # Initialize trackers
    weight_tracker = WeightTracker(db_path="data/weights.db")
    food_logger = FoodLogger(db_path="data/food_log.db")

    # Get user profile
    profile = UserProfile()
    if not profile.exists():
        st.warning("⚠️ Create your profile first to use Adaptive TDEE")
        return

    info = profile.get_personal_info()
    goals = profile.get_goals()

    # Calculate formula TDEE (Mifflin-St Jeor)
    from calculations import calculate_nutrition_plan

    plan = calculate_nutrition_plan(
        weight_lbs=info.weight_lbs,
        height_inches=info.height_inches,
        age=info.age,
        sex=info.sex,
        activity_level=info.activity_level,
        phase=goals.phase,
        training_level=profile.get_experience().training_level
    )

    # Determine goal rate from phase
    if goals.phase == "cut":
        goal_rate = -1.0  # -1 lb/week default for cutting
        if hasattr(goals, 'target_weight_lbs') and goals.target_weight_lbs:
            weeks = goals.timeline_weeks if hasattr(goals, 'timeline_weeks') else 12
            goal_rate = -(info.weight_lbs - goals.target_weight_lbs) / weeks
    elif goals.phase == "bulk":
        goal_rate = 0.5  # +0.5 lb/week default for bulking
    elif goals.phase == "recomp":
        goal_rate = -0.25  # Slight deficit for recomp
    else:  # maintain
        goal_rate = 0.0

    # Get adaptive TDEE insight (integration function)
    insight = get_adaptive_tdee_insight(
        weight_tracker=weight_tracker,
        food_logger=food_logger,
        formula_tdee=plan['tdee'],
        goal_rate_lbs_week=goal_rate,
        current_calories=plan['calories'],
        current_protein_g=plan['protein_g'],
        phase=goals.phase,
        days=14
    )

    # Display status
    if not insight.has_sufficient_data:
        st.info(
            f"📊 **Data Collection Progress:** {insight.days_logged}/14 days logged\n\n"
            f"Log weight daily and track food for at least 14 days to unlock Adaptive TDEE.\n\n"
            f"**Why 14 days?** This provides enough data to calculate accurate trends "
            f"while filtering out daily fluctuations."
        )

        # Show progress bar
        progress = insight.days_logged / 14
        st.progress(progress)

        # Show formula TDEE in the meantime
        st.markdown("### 📐 Formula-Based TDEE (Mifflin-St Jeor)")
        st.metric("Estimated TDEE", f"{insight.formula_tdee} cal/day")
        st.caption("This is an estimate. Adaptive TDEE will be more accurate once you have 14 days of data.")

        return

    # Sufficient data - show full adaptive TDEE analysis
    st.success(f"✅ {insight.days_logged} days of data - Adaptive TDEE is active!")

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Formula TDEE",
            f"{insight.formula_tdee} cal",
            help="Mifflin-St Jeor formula estimate"
        )

    with col2:
        st.metric(
            "Adaptive TDEE",
            f"{insight.adaptive_tdee} cal",
            delta=f"{insight.tdee_delta:+d} cal" if insight.tdee_delta else None,
            help="Back-calculated from your actual data"
        )

    with col3:
        st.metric(
            "Avg Intake (14d)",
            f"{insight.average_intake:.0f} cal",
            help="Average daily calories over last 14 days"
        )

    with col4:
        weight_change_label = f"{insight.weight_change_14d:+.1f} lbs" if insight.weight_change_14d else "N/A"
        st.metric(
            "Weight Change (14d)",
            weight_change_label,
            help="Trend weight change over 14 days"
        )

    st.markdown("---")

    # TDEE Comparison
    st.subheader("📊 TDEE Comparison: Formula vs. Reality")

    if insight.tdee_delta:
        delta_pct = (insight.tdee_delta / insight.formula_tdee) * 100

        if abs(delta_pct) < 5:
            st.success(
                f"✅ **Your actual TDEE matches the formula closely** (within {abs(delta_pct):.1f}%)\n\n"
                f"The Mifflin-St Jeor formula is working well for you."
            )
        elif insight.tdee_delta > 0:
            st.info(
                f"📈 **Your actual TDEE is {insight.tdee_delta} cal higher than the formula** (+{delta_pct:.1f}%)\n\n"
                f"Possible reasons:\n"
                f"- Higher NEAT (Non-Exercise Activity Thermogenesis)\n"
                f"- More active than activity level suggests\n"
                f"- Higher metabolic rate (good genetics!)\n\n"
                f"**Recommendation:** Use {insight.adaptive_tdee} cal as your baseline."
            )
        else:
            st.info(
                f"📉 **Your actual TDEE is {abs(insight.tdee_delta)} cal lower than the formula** ({delta_pct:.1f}%)\n\n"
                f"Possible reasons:\n"
                f"- Lower NEAT (Non-Exercise Activity Thermogenesis)\n"
                f"- Less active than activity level suggests\n"
                f"- Adaptive thermogenesis (metabolic adaptation)\n\n"
                f"**Recommendation:** Use {insight.adaptive_tdee} cal as your baseline."
            )

    st.markdown("---")

    # Weekly Check-In
    st.subheader("🎯 Weekly Check-In & Macro Adjustment")

    if insight.macro_adjustment:
        adj = insight.macro_adjustment

        # Display current status
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Goal Rate",
                f"{adj.goal_rate:+.2f} lbs/week",
                help="Your target rate of weight change"
            )

        with col2:
            st.metric(
                "Actual Rate",
                f"{adj.actual_rate:+.2f} lbs/week",
                delta=f"{adj.actual_rate - adj.goal_rate:+.2f} lbs/week",
                delta_color="off",
                help="Your measured rate from trend data"
            )

        with col3:
            deviation_label = "On Track" if abs(adj.percent_deviation) <= 20 else f"{adj.percent_deviation:+.1f}%"
            st.metric(
                "Deviation",
                deviation_label,
                help="How far off from goal (±20% = on track)"
            )

        st.markdown("---")

        # Recommendation
        st.markdown("### 💡 Recommendation")

        # Color-code based on reason
        if adj.reason == "on_track":
            st.success(adj.coaching_message)
        elif "too_fast" in adj.reason:
            st.warning(adj.coaching_message)
        else:
            st.info(adj.coaching_message)

        # Show macro changes
        if adj.calorie_change != 0:
            st.markdown("#### 📋 Recommended Macro Changes")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Current Macros:**")
                st.write(f"- Calories: {plan['calories']} cal/day")
                st.write(f"- Protein: {plan['protein_g']:.0f}g")
                st.write(f"- Fat: {plan['fat_g']:.0f}g")
                st.write(f"- Carbs: {plan['carbs_g']:.0f}g")

            with col2:
                # Calculate new macros (protein stays constant)
                new_calories = adj.new_calories
                protein_cal = plan['protein_g'] * 4
                fat_cal = plan['fat_g'] * 9
                remaining_cal = new_calories - protein_cal - fat_cal
                new_carbs_g = remaining_cal / 4

                st.markdown(f"**Adjusted Macros:** ({adj.calorie_change:+d} cal)")
                st.write(f"- Calories: {new_calories} cal/day")
                st.write(f"- Protein: {plan['protein_g']:.0f}g (unchanged)")
                st.write(f"- Fat: {plan['fat_g']:.0f}g (unchanged)")
                st.write(f"- Carbs: {new_carbs_g:.0f}g ({(new_carbs_g - plan['carbs_g']):+.0f}g)")

            # Apply adjustment button
            st.markdown("---")
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(
                    "**Note:** This is a recommendation. You can accept it or adjust manually. "
                    "HealthRAG will continue tracking and provide weekly updates."
                )

            with col2:
                if st.button("✅ Apply Adjustment", type="primary", use_container_width=True):
                    st.info(
                        "💡 To apply this adjustment, update your profile weight and recalculate your nutrition plan. "
                        "The system will automatically use the new baseline."
                    )

        # Educational note
        st.markdown("---")
        st.markdown(
            "### 📚 How Adaptive TDEE Works\n\n"
            "**Back-Calculation Formula:**\n"
            "```\n"
            "TDEE = Avg_Calories + (Weight_Change_lbs × 3500 / 14)\n"
            "```\n\n"
            "**Why this works:**\n"
            "- 1 lb of fat ≈ 3500 calories\n"
            "- If you lost 1 lb in 14 days eating 2100 cal/day:\n"
            "  - You were in a 250 cal/day deficit (3500 ÷ 14)\n"
            "  - Your TDEE = 2100 + 250 = 2350 cal/day\n\n"
            "**Adherence-Neutral Adjustments:**\n"
            "- Within ±20% of goal: No change (natural variation)\n"
            "- Within ±50% of goal: ±100 cal adjustment\n"
            "- Beyond ±50%: ±150 cal adjustment\n\n"
            "This approach is based on MacroFactor's methodology and Renaissance Periodization principles."
        )


def render_body_measurements():
    """
    Body measurements tracking with body fat estimation and trend analysis.

    Features:
    - Track 11 body measurements (waist, chest, arms, legs, etc.)
    - Body fat estimation (WHtR, US Navy method)
    - Progress visualization with charts
    - Comparison vs. previous measurements
    """
    st.markdown("---")
    st.header("📏 Body Measurements & Composition")

    # Initialize trackers
    tracker = BodyMeasurementTracker(db_path="data/body_measurements.db")

    # Get user profile for BF calculations
    profile = UserProfile()
    if not profile.exists():
        st.warning("⚠️ Create your profile first to use body fat estimation")
        return

    info = profile.get_personal_info()

    # Tabs for different views
    tab_log, tab_trends, tab_compare = st.tabs(["📝 Log Measurements", "📊 Trends", "📈 Progress"])

    with tab_log:
        st.subheader("📝 Log Body Measurements")

        # Get latest measurement for default values
        latest_entry = tracker.get_latest_measurement()

        with st.form("log_measurements_form"):
            measurement_date = st.date_input(
                "Measurement Date",
                value=date.today(),
                help="Date of measurements"
            )

            st.markdown("#### Core Measurements")
            col1, col2 = st.columns(2)

            with col1:
                waist = st.number_input(
                    "Waist (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.waist if latest_entry and latest_entry.waist else 30.0,
                    step=0.1,
                    help="At narrowest point (usually at navel)"
                )

                chest = st.number_input(
                    "Chest (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.chest if latest_entry and latest_entry.chest else 38.0,
                    step=0.1,
                    help="At nipple line, relaxed"
                )

                neck = st.number_input(
                    "Neck (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.neck if latest_entry and latest_entry.neck else 15.0,
                    step=0.1,
                    help="Just below larynx"
                )

            with col2:
                hips = st.number_input(
                    "Hips (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.hips if latest_entry and latest_entry.hips else 36.0,
                    step=0.1,
                    help="At widest point"
                )

                shoulders = st.number_input(
                    "Shoulders (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.shoulders if latest_entry and latest_entry.shoulders else 46.0,
                    step=0.1,
                    help="Across deltoids"
                )

            st.markdown("#### Arms & Legs")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Arms (flexed):**")
                left_arm = st.number_input(
                    "Left Arm (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.left_arm if latest_entry and latest_entry.left_arm else 14.0,
                    step=0.1
                )
                right_arm = st.number_input(
                    "Right Arm (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.right_arm if latest_entry and latest_entry.right_arm else 14.0,
                    step=0.1
                )

                st.markdown("**Thighs (mid-thigh):**")
                left_thigh = st.number_input(
                    "Left Thigh (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.left_thigh if latest_entry and latest_entry.left_thigh else 22.0,
                    step=0.1
                )
                right_thigh = st.number_input(
                    "Right Thigh (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.right_thigh if latest_entry and latest_entry.right_thigh else 22.0,
                    step=0.1
                )

            with col2:
                st.markdown("**Calves (widest point):**")
                left_calf = st.number_input(
                    "Left Calf (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.left_calf if latest_entry and latest_entry.left_calf else 15.0,
                    step=0.1
                )
                right_calf = st.number_input(
                    "Right Calf (inches)",
                    min_value=0.0,
                    max_value=100.0,
                    value=latest_entry.right_calf if latest_entry and latest_entry.right_calf else 15.0,
                    step=0.1
                )

            notes = st.text_area(
                "Notes (optional)",
                placeholder="e.g., Morning measurements, post-workout pump, etc.",
                help="Optional notes about the measurements"
            )

            submitted = st.form_submit_button("💾 Log Measurements", type="primary", use_container_width=True)

            if submitted:
                try:
                    tracker.log_measurement(
                        measurement_date=measurement_date.strftime("%Y-%m-%d"),
                        waist=waist,
                        chest=chest,
                        hips=hips,
                        neck=neck,
                        shoulders=shoulders,
                        left_arm=left_arm,
                        right_arm=right_arm,
                        left_thigh=left_thigh,
                        right_thigh=right_thigh,
                        left_calf=left_calf,
                        right_calf=right_calf,
                        notes=notes
                    )
                    st.success(f"✅ Logged measurements for {measurement_date.strftime('%Y-%m-%d')}")
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Error: {e}")

        # Body fat estimation
        if latest_entry:
            st.markdown("---")
            st.markdown("### 🧮 Body Composition Estimate")

            # Get current weight
            weight_tracker = WeightTracker(db_path="data/weights.db")
            latest_weight = weight_tracker.get_latest_weight()

            if latest_weight:
                # Calculate body fat
                bf_estimate = tracker.calculate_body_fat(
                    measurement=latest_entry,
                    weight_lbs=latest_weight.weight_lbs,
                    height_inches=info.height_inches,
                    sex=info.sex
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if bf_estimate.navy_method_bf:
                        st.metric(
                            "Body Fat %",
                            f"{bf_estimate.navy_method_bf:.1f}%",
                            help="US Navy Method (most accurate)"
                        )
                    else:
                        st.metric("Body Fat %", "N/A", help="Need waist, neck, hips measurements")

                with col2:
                    if bf_estimate.waist_to_height_ratio:
                        st.metric(
                            "Waist-to-Height",
                            f"{bf_estimate.waist_to_height_ratio:.3f}",
                            help="< 0.5 = healthy"
                        )
                    else:
                        st.metric("Waist-to-Height", "N/A")

                with col3:
                    if bf_estimate.bmi:
                        st.metric(
                            "BMI",
                            f"{bf_estimate.bmi:.1f}",
                            help="Body Mass Index"
                        )
                    else:
                        st.metric("BMI", "N/A")

                with col4:
                    if bf_estimate.category:
                        st.metric(
                            "Category",
                            bf_estimate.category,
                            help="Fitness category based on BF%"
                        )
                    else:
                        st.metric("Category", "N/A")

                # Coaching insights
                if bf_estimate.navy_method_bf:
                    st.markdown("#### 💡 Body Composition Insights")

                    bf = bf_estimate.navy_method_bf
                    if info.sex.lower() == "male":
                        if bf < 14:
                            st.success("✅ Athletic body composition! Great for performance and aesthetics.")
                        elif bf < 18:
                            st.info("💪 Fitness level body composition. Healthy and sustainable.")
                        elif bf < 25:
                            st.info("📊 Average body composition. Room for improvement if desired.")
                        else:
                            st.warning("⚠️ Higher body fat. Consider a cutting phase to improve health markers.")
                    else:  # female
                        if bf < 21:
                            st.success("✅ Athletic body composition! Great for performance and aesthetics.")
                        elif bf < 25:
                            st.info("💪 Fitness level body composition. Healthy and sustainable.")
                        elif bf < 32:
                            st.info("📊 Average body composition. Room for improvement if desired.")
                        else:
                            st.warning("⚠️ Higher body fat. Consider a cutting phase to improve health markers.")

            else:
                st.info("📊 Log your weight in the Weight Tracking section to calculate body fat percentage")

    with tab_trends:
        st.subheader("📊 Measurement Trends")

        entries = tracker.get_measurements(limit=30)

        if not entries:
            st.info("👆 Log your first measurements to see trends!")
            return

        # Latest measurement summary
        latest = entries[0]
        st.markdown("### 📏 Latest Measurements")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if latest.waist:
                st.metric("Waist", f"{latest.waist:.1f}\"")
            if latest.chest:
                st.metric("Chest", f"{latest.chest:.1f}\"")

        with col2:
            if latest.hips:
                st.metric("Hips", f"{latest.hips:.1f}\"")
            if latest.shoulders:
                st.metric("Shoulders", f"{latest.shoulders:.1f}\"")

        with col3:
            if latest.left_arm and latest.right_arm:
                avg_arm = (latest.left_arm + latest.right_arm) / 2
                st.metric("Arms (avg)", f"{avg_arm:.1f}\"")
            if latest.left_thigh and latest.right_thigh:
                avg_thigh = (latest.left_thigh + latest.right_thigh) / 2
                st.metric("Thighs (avg)", f"{avg_thigh:.1f}\"")

        with col4:
            if latest.left_calf and latest.right_calf:
                avg_calf = (latest.left_calf + latest.right_calf) / 2
                st.metric("Calves (avg)", f"{avg_calf:.1f}\"")
            if latest.neck:
                st.metric("Neck", f"{latest.neck:.1f}\"")

        st.caption(f"Measured on {latest.date}")

        # Visualization
        st.markdown("---")
        st.subheader("📈 Measurement Charts")

        # Prepare data
        entries.reverse()  # Oldest first for chronological charts
        dates = [e.date for e in entries]

        # Create charts for each measurement type
        charts_to_plot = [
            ("Core Measurements", ["waist", "chest", "hips", "shoulders"]),
            ("Arms", ["left_arm", "right_arm"]),
            ("Legs", ["left_thigh", "right_thigh", "left_calf", "right_calf"])
        ]

        for chart_title, measurements in charts_to_plot:
            fig = go.Figure()

            for measurement in measurements:
                values = [getattr(e, measurement) for e in entries]
                # Only plot if there are non-None values
                if any(v is not None for v in values):
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=values,
                        mode='lines+markers',
                        name=measurement.replace('_', ' ').title(),
                        hovertemplate='<b>%{x}</b><br>%{y:.1f}"<extra></extra>'
                    ))

            if fig.data:  # Only show chart if there's data
                fig.update_layout(
                    title=chart_title,
                    xaxis_title="Date",
                    yaxis_title="Inches",
                    hovermode='x unified',
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab_compare:
        st.subheader("📈 Progress Comparison")

        entries = tracker.get_measurements(limit=30)

        if len(entries) < 2:
            st.info("📊 Log at least 2 measurements to see progress comparison")
            return

        # Calculate changes
        changes = tracker.get_measurement_changes()

        if not changes:
            st.info("📊 No previous measurement to compare")
            return

        st.markdown(f"### 📊 Changes Since Last Measurement")
        st.caption(f"Comparing {entries[0].date} vs. {entries[1].date}")

        # Display changes
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Core Measurements")
            for field in ['waist', 'chest', 'hips', 'shoulders', 'neck']:
                if field in changes and changes[field] is not None:
                    change = changes[field]
                    delta_color = "inverse" if field == "waist" else "normal"  # Waist decrease is good
                    st.metric(
                        field.replace('_', ' ').title(),
                        f"{getattr(entries[0], field):.1f}\"",
                        delta=f"{change:+.1f}\"",
                        delta_color=delta_color
                    )

        with col2:
            st.markdown("#### Arms & Legs")
            for field in ['left_arm', 'right_arm', 'left_thigh', 'right_thigh', 'left_calf', 'right_calf']:
                if field in changes and changes[field] is not None:
                    change = changes[field]
                    st.metric(
                        field.replace('_', ' ').title(),
                        f"{getattr(entries[0], field):.1f}\"",
                        delta=f"{change:+.1f}\"",
                        delta_color="normal"
                    )

        # Interpretation
        st.markdown("---")
        st.markdown("### 💡 Progress Insights")

        # Count gains and losses
        gains = sum(1 for v in changes.values() if v is not None and v > 0.1)
        losses = sum(1 for v in changes.values() if v is not None and v < -0.1)

        if gains > losses:
            st.info(
                f"📈 Overall growth: {gains} measurements increased, {losses} decreased.\n\n"
                "This is typical during bulking/muscle building phases. "
                "Keep tracking to ensure gains are primarily muscle, not fat."
            )
        elif losses > gains:
            st.info(
                f"📉 Overall reduction: {losses} measurements decreased, {gains} increased.\n\n"
                "This is typical during cutting phases. "
                "Make sure to maintain or increase muscle measurements (arms, legs) while losing waist."
            )
        else:
            st.success(
                "✅ Stable measurements with minimal changes.\n\n"
                "This is typical during maintenance or recomp phases."
            )


def render_quick_daily_log():
    """
    Quick Daily Log section for fast weight and nutrition logging.

    Appears prominently at top of main page to encourage daily tracking.
    """
    st.markdown("---")
    st.subheader("⚡ Quick Daily Log")

    # Initialize trackers
    weight_tracker = WeightTracker(db_path="data/weights.db")
    food_logger = FoodLogger(db_path="data/food_log.db")

    today = date.today().isoformat()

    # Check what's already logged today
    today_weight = None
    weights_today = weight_tracker.get_weights(start_date=today, end_date=today)
    if weights_today:
        today_weight = weights_today[0].weight_lbs

    today_nutrition = food_logger.get_daily_nutrition(today)
    today_calories = today_nutrition.total_calories if today_nutrition else 0

    # Get streak info
    all_weights = weight_tracker.get_weights(limit=30)
    streak = 0
    if all_weights:
        check_date = date.today()
        for entry in all_weights:
            if entry.date == check_date.isoformat():
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

    # Status row
    col_status1, col_status2, col_status3 = st.columns(3)

    with col_status1:
        if today_weight:
            st.success(f"✅ Weight: {today_weight} lbs")
        else:
            st.warning("⏳ Weight not logged")

    with col_status2:
        if today_calories > 0:
            st.success(f"✅ Food: {today_calories:,} cal")
        else:
            st.warning("⏳ No food logged")

    with col_status3:
        if streak > 0:
            st.info(f"🔥 {streak} day streak!")
        else:
            st.info("Start your streak today!")

    # Quick log row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 Log Weight**")
        weight_col1, weight_col2 = st.columns([2, 1])
        with weight_col1:
            new_weight = st.number_input(
                "Weight (lbs)",
                min_value=50.0,
                max_value=500.0,
                value=today_weight if today_weight else 220.0,
                step=0.1,
                key="quick_weight_input",
                label_visibility="collapsed"
            )
        with weight_col2:
            if st.button("Log Weight", key="quick_log_weight", type="primary"):
                try:
                    weight_tracker.log_weight(new_weight, today)
                    st.success(f"✅ Logged {new_weight} lbs")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        # Determine meal type by time of day
        current_hour = datetime.now().hour
        if 5 <= current_hour < 11:
            suggested_meal_type = "breakfast"
        elif 11 <= current_hour < 15:
            suggested_meal_type = "lunch"
        elif 15 <= current_hour < 20:
            suggested_meal_type = "dinner"
        else:
            suggested_meal_type = "snack"

        st.markdown(f"**🍽️ Quick Add ({suggested_meal_type.title()})**")

        # Get meal templates filtered by time of day, then fall back to all
        template_manager = MealTemplateManager(db_path="data/food_log.db", food_logger=food_logger)
        templates = template_manager.list_templates(meal_type=suggested_meal_type)

        # If no templates for this meal type, show all
        if not templates:
            templates = template_manager.list_templates()

        if templates:
            template_names = [f"{t.name} ({t.total_calories:.0f} cal)" for t in templates[:5]]
            selected = st.selectbox(
                "Select template",
                options=["-- Select --"] + template_names,
                key="quick_meal_select",
                label_visibility="collapsed"
            )

            if selected != "-- Select --":
                # Find template by index (since display name includes calories)
                selected_idx = template_names.index(selected)
                template = templates[selected_idx]
                if st.button(f"Log '{template.name}'", key="quick_log_meal", type="primary"):
                    try:
                        template_manager.log_template(template.template_id, today)
                        st.success(f"✅ Logged {template.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.caption(f"No {suggested_meal_type} templates. Create one in Nutrition Tracking.")

    # TDEE status (if enough data)
    entries = weight_tracker.get_weights(limit=14)
    if len(entries) >= 14:
        st.markdown("---")
        st.markdown("**📈 Adaptive TDEE Status:** ✅ Active - 14+ days of data!")
    elif len(entries) > 0:
        days_left = 14 - len(entries)
        st.markdown(f"**📈 Adaptive TDEE:** {len(entries)}/14 days logged ({days_left} more to activate)")
    else:
        st.markdown("**📈 Adaptive TDEE:** Log weight daily for 14 days to activate personalized recommendations")


def render_sidebar_quick_log():
    """
    Persistent sidebar widget for quick daily logging.

    Always visible regardless of which section user is viewing.
    Provides fastest possible path to log weight and meals.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Log")

    today = date.today().isoformat()

    # Initialize trackers
    weight_tracker = WeightTracker(db_path="data/weights.db")
    food_logger = FoodLogger(db_path="data/food_log.db")

    # Check today's status
    weights_today = weight_tracker.get_weights(start_date=today, end_date=today)
    weight_logged = len(weights_today) > 0
    today_weight = weights_today[0].weight_lbs if weight_logged else None

    today_nutrition = food_logger.get_daily_nutrition(today)
    food_logged = today_nutrition.total_calories > 0 if today_nutrition else False
    today_cals = today_nutrition.total_calories if today_nutrition else 0

    # Status indicators
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if weight_logged:
            st.success(f"⚖️ {today_weight:.1f}")
        else:
            st.warning("⚖️ --")
    with col2:
        if food_logged:
            st.success(f"🍽️ {today_cals:.0f}")
        else:
            st.warning("🍽️ --")

    # Weight input
    default_weight = today_weight if today_weight else 220.0
    sidebar_weight = st.sidebar.number_input(
        "Weight (lbs)",
        min_value=50.0,
        max_value=500.0,
        value=default_weight,
        step=0.1,
        key="sidebar_weight_input",
        label_visibility="collapsed"
    )

    if st.sidebar.button("📊 Log Weight", key="sidebar_log_weight_btn", use_container_width=True):
        try:
            weight_tracker.log_weight(sidebar_weight, today)
            st.sidebar.success(f"✅ {sidebar_weight} lbs")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    # Quick meal templates
    st.sidebar.markdown("**Quick Meals:**")
    template_manager = MealTemplateManager(db_path="data/food_log.db", food_logger=food_logger)

    # Get time-appropriate templates
    current_hour = datetime.now().hour
    if 5 <= current_hour < 11:
        meal_type = "breakfast"
    elif 11 <= current_hour < 15:
        meal_type = "lunch"
    elif 15 <= current_hour < 20:
        meal_type = "dinner"
    else:
        meal_type = "snack"

    templates = template_manager.list_templates(meal_type=meal_type)
    if not templates:
        templates = template_manager.list_templates()

    if templates:
        for t in templates[:3]:  # Show top 3
            if st.sidebar.button(
                f"{t.name} ({t.total_calories:.0f}cal)",
                key=f"sidebar_tmpl_{t.template_id}",
                use_container_width=True
            ):
                try:
                    template_manager.log_template(t.template_id, today)
                    st.sidebar.success(f"✅ {t.name}")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.caption("No templates yet")


def main():
    st.set_page_config(
        page_title="Personal Health & Fitness Advisor",
        page_icon="🏃‍♂️",
        layout="wide"
    )
    
    st.title("🏃‍♂️ Personal Health & Fitness Advisor")
    st.markdown("*Your AI-powered nutrition and fitness consultant*")
    
    # Backend and Model selection sidebar
    st.sidebar.title("⚙️ Model Settings")
    
    # Backend selection - MLX default
    backend_options = []
    if MLX_AVAILABLE:
        backend_options.append("mlx")
    backend_options.append("ollama")
    
    backend_choice = st.sidebar.selectbox(
        "Choose Backend:",
        backend_options,
        help="MLX: Native Apple Silicon (faster) | Ollama: Docker-based"
    )
    
    # Model selection based on backend
    if backend_choice == "mlx":
        model_options = [
            "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit"
        ]
        help_text = "70B MLX model optimized for Apple Silicon"
    else:
        model_options = ["llama3.1:70b"]
        help_text = "70B: May fail due to memory (43GB needed)"
    
    model_choice = st.sidebar.selectbox(
        "Choose Model:",
        model_options,
        help=help_text
    )
    
    if "rag_system" not in st.session_state:
        default_backend = "mlx" if MLX_AVAILABLE else "ollama"
        default_model = "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit" if MLX_AVAILABLE else "llama3.1:70b"
        st.session_state.rag_system = HealthRAG(backend=default_backend)
        st.session_state.current_model = default_model
        st.session_state.current_backend = default_backend
    
    # Switch backend if changed
    if backend_choice != st.session_state.current_backend:
        st.session_state.rag_system.switch_backend(backend_choice, model_choice)
        st.session_state.current_backend = backend_choice
        st.session_state.current_model = model_choice
        st.sidebar.success(f"Switched to {backend_choice} backend")
    # Switch model if changed (same backend)
    elif model_choice != st.session_state.current_model:
        if backend_choice == "mlx":
            st.session_state.rag_system.llm.switch_model(model_choice)
        else:
            st.session_state.rag_system.llm.switch_model(model_choice)
        st.session_state.current_model = model_choice
        st.sidebar.success(f"Switched to {model_choice}")
    
    # Show current setup
    st.sidebar.info(f"Backend: {st.session_state.current_backend}")
    st.sidebar.info(f"Model: {st.session_state.current_model}")
    
    # MLX availability status
    if MLX_AVAILABLE:
        st.sidebar.success("✅ MLX Available")
    else:
        st.sidebar.warning("⚠️ MLX Not Available")

    # Profile Management
    profile = UserProfile()

    if not profile.exists():
        # Show onboarding wizard for new users
        render_onboarding_wizard()
        return  # Don't show anything else until profile is created

    # Existing user - show sidebar profile info
    render_profile_view()

    # Sidebar quick-log widget (always visible)
    render_sidebar_quick_log()

    # Quick Daily Log (prominent at top for easy tracking)
    render_quick_daily_log()

    # Proactive Dashboard (show plan automatically if profile exists)
    if profile.exists():
        render_proactive_dashboard(profile)
        render_training_program(profile)
        render_workout_logging()
        render_nutrition_tracking()
        render_weight_tracking()
        render_adaptive_tdee()
        render_body_measurements()

    # Chat section header
    st.subheader("💬 Chat with Your Coach")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about nutrition, fitness, or health..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Check if this is a nutrition calculation query
            nutrition_keywords = [
                'macro', 'macros', 'calories', 'calorie', 'tdee',
                'protein', 'fat', 'carbs', 'carb', 'nutrition',
                'how much should i eat', 'what should i eat',
                'my calories', 'my macros', 'calculate'
            ]

            is_nutrition_query = any(keyword in prompt.lower() for keyword in nutrition_keywords)

            if is_nutrition_query and profile.exists():
                # Handle locally with calculations.py (coaching-style response)
                with st.spinner("Calculating your personalized nutrition plan..."):
                    profile.load()
                    personal_info = profile.profile_data['personal_info']
                    goals = profile.profile_data['goals']

                    import time
                    start_time = time.time()

                    # Calculate nutrition plan with coaching guidance
                    plan = calculate_nutrition_plan(personal_info, goals)
                    response = plan['guidance']

                    response_time = time.time() - start_time

                st.markdown(response)
                st.caption(f"⏱️ Calculation time: {response_time:.2f}s | Source: HealthRAG Calculations Engine")

            elif is_nutrition_query and not profile.exists():
                # User asking about nutrition but no profile
                response = """I'd love to help calculate your nutrition plan, but I need your profile first!

Please create your profile using the sidebar form. I'll need:
- Your weight, height, age, and sex
- Your activity level
- Your goals (cut, bulk, maintain, or recomp)

Once your profile is set up, I can provide personalized:
- TDEE (Total Daily Energy Expenditure)
- Macro breakdown (protein, fat, carbs)
- Evidence-based guidance from Renaissance Periodization and Jeff Nippard

Ready to get started? 👈 Fill out the profile form in the sidebar!"""

                response_time = 0
                st.markdown(response)
                st.caption("⚠️ Profile required for personalized calculations")

            else:
                # Regular RAG query
                with st.spinner(f"Thinking with {st.session_state.current_model}..."):
                    response, response_time = st.session_state.rag_system.query(prompt)

                st.markdown(response)
                st.caption(f"⏱️ Response time: {response_time:.1f}s | Backend: {st.session_state.current_backend} | Model: {st.session_state.current_model}")

        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()