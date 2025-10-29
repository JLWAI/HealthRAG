import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date
from rag_system import HealthRAG, MLX_AVAILABLE
from profile import UserProfile, EQUIPMENT_PRESETS
from calculations import calculate_nutrition_plan, get_expected_rate_text, get_phase_explanation
from program_generator import ProgramGenerator, format_workout, format_week
from workout_logger import WorkoutLogger, WorkoutLog, WorkoutSet
from autoregulation import AutoregulationEngine
import json

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
        ["minimal", "home_gym", "commercial_gym", "custom"],
        format_func=lambda x: {
            "minimal": "Minimal (Bodyweight, Resistance Bands)",
            "home_gym": "Home Gym (Dumbbells, Bench, Pull-up Bar)",
            "commercial_gym": "Commercial Gym (Full Equipment)",
            "custom": "Custom (Pick Specific Equipment)"
        }[x]
    )

    if equipment_preset == "custom":
        equipment_options = [
            "barbell", "dumbbells", "kettlebells", "resistance_bands",
            "rack", "bench", "incline_bench", "pull_up_bar", "dip_station",
            "cables", "machines", "smith_machine", "leg_press_machine",
            "chest_press_machine", "lat_pulldown_machine", "bodyweight"
        ]
        equipment = st.multiselect("Available Equipment", equipment_options, default=["bodyweight"])
    else:
        equipment = EQUIPMENT_PRESETS[equipment_preset]
        st.info(f"**Selected:** {', '.join(equipment)}")

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
            "Equipment",
            ["keep_current", "minimal", "home_gym", "commercial_gym", "custom"],
            format_func=lambda x: {
                "keep_current": f"Keep Current ({len(current_equipment)} items)",
                "minimal": "Minimal (Bodyweight, Bands)",
                "home_gym": "Home Gym (Dumbbells, Bench, Pull-up Bar)",
                "commercial_gym": "Commercial Gym (Full Equipment)",
                "custom": "Custom Selection"
            }[x],
            key="update_equipment"
        )

        if equipment_preset == "custom":
            equipment_options = [
                "barbell", "dumbbells", "kettlebells", "resistance_bands",
                "rack", "bench", "incline_bench", "pull_up_bar", "dip_station",
                "cables", "machines", "smith_machine", "leg_press_machine",
                "chest_press_machine", "lat_pulldown_machine", "bodyweight"
            ]
            new_equipment = st.multiselect(
                "Select Equipment",
                equipment_options,
                default=[eq for eq in current_equipment if eq in equipment_options],
                key="update_equipment_list"
            )
        elif equipment_preset == "keep_current":
            new_equipment = current_equipment
        else:
            from profile import EQUIPMENT_PRESETS
            new_equipment = EQUIPMENT_PRESETS[equipment_preset]

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

            # Delete current program so it regenerates with new settings
            if os.path.exists("data/current_program.json"):
                os.remove("data/current_program.json")
                st.info("💡 Your training program will regenerate with your new settings")

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
    """
    st.markdown("---")
    st.subheader("🏃‍♂️ Your Personalized Plan")

    # Load profile data
    profile.load()
    personal_info = profile.profile_data['personal_info']
    goals = profile.profile_data['goals']

    # Get user's name
    name = personal_info.get('name', 'there')

    # Greeting
    st.markdown(f"**Welcome, {name}!** Here's your plan:")

    # Generate nutrition plan
    plan = calculate_nutrition_plan(personal_info, goals)

    # Display goals summary
    phase = goals['phase'].capitalize()
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

**Daily Target:** {int(plan['tdee_adjusted']):,} calories
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

    st.markdown("---")


def render_training_program(profile: UserProfile):
    """
    Render training program generation and display.

    Shows generated workout program with exercises, sets, reps, RIR progression.
    """
    st.markdown("---")
    st.subheader("💪 Your Training Program")

    # Load profile data
    profile.load()
    personal_info = profile.profile_data['personal_info']
    experience = profile.profile_data.get('experience', {})
    schedule = profile.profile_data.get('schedule', {})
    equipment = profile.profile_data.get('equipment', ['bodyweight'])

    # Check if program already exists
    program_file = "data/current_program.json"
    program_exists = os.path.exists(program_file)

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

                    # Save program
                    generator.save_program(program, program_file)

                    st.success("✅ Program generated successfully!")
                    st.rerun()

    else:
        # Display existing program
        import json
        with open(program_file, 'r') as f:
            program_data = json.load(f)

        # Program header
        st.markdown(f"""
**Template:** {program_data['template_name'].replace('_', ' ').title()}
**Start Date:** {program_data['start_date']}
**Duration:** {len(program_data['weeks'])} weeks (5 weeks + deload)
        """)

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
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Program"):
                os.remove(program_file)
                st.rerun()

        with col2:
            if st.button("📥 Download Program"):
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(program_data, indent=2),
                    file_name=f"training_program_{date.today()}.json",
                    mime="application/json"
                )


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

        # Check if program exists to pre-populate workout names
        program_file = "data/current_program.json"
        workout_names = []

        if os.path.exists(program_file):
            with open(program_file, 'r') as f:
                program_data = json.load(f)
                # Extract unique workout names
                for week in program_data['weeks']:
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

        # Exercise logging
        st.markdown("#### Add Sets")
        st.markdown("Log each set as you complete it")

        # Initialize session state for sets
        if 'current_workout_sets' not in st.session_state:
            st.session_state.current_workout_sets = []

        # Add set form
        with st.form("add_set_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                exercise = st.text_input("Exercise", placeholder="e.g., Barbell Bench Press")
            with col2:
                weight = st.number_input("Weight (lbs)", min_value=0.0, max_value=1000.0, value=0.0, step=2.5)
            with col3:
                reps = st.number_input("Reps", min_value=1, max_value=50, value=8)
            with col4:
                rir = st.selectbox("RIR", [0, 1, 2, 3, 4], index=2)

            set_notes = st.text_input("Set Notes (optional)", placeholder="e.g., Felt strong, struggled on last rep")

            submitted = st.form_submit_button("➕ Add Set")
            if submitted and exercise:
                workout_set = WorkoutSet(
                    exercise_name=exercise,
                    weight_lbs=weight,
                    reps=reps,
                    rir=rir,
                    notes=set_notes if set_notes else None
                )
                st.session_state.current_workout_sets.append(workout_set)
                st.success(f"✅ Added: {exercise} - {weight} lbs × {reps} @ {rir} RIR")
                st.rerun()

        # Display current sets
        if st.session_state.current_workout_sets:
            st.markdown("#### Current Workout Sets")

            for i, workout_set in enumerate(st.session_state.current_workout_sets):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
**Set {i+1}: {workout_set.exercise_name}**
- {workout_set.weight_lbs} lbs × {workout_set.reps} reps @ {workout_set.rir} RIR
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
                        st.success(f"🎉 Workout saved successfully! (ID: {workout_id})")
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

    # Proactive Dashboard (show plan automatically if profile exists)
    if profile.exists():
        render_proactive_dashboard(profile)
        render_training_program(profile)
        render_workout_logging()

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