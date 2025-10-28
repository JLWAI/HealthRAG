import streamlit as st
import os
from dotenv import load_dotenv
from rag_system import HealthRAG, MLX_AVAILABLE
from profile import UserProfile, EQUIPMENT_PRESETS
from calculations import calculate_nutrition_plan, get_expected_rate_text, get_phase_explanation

load_dotenv()


def render_profile_setup():
    """Render profile creation form"""
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

    with st.sidebar.expander("✏️ Quick Update"):
        new_weight = st.number_input(
            "Update Weight (lbs)",
            min_value=50.0,
            max_value=500.0,
            value=float(info.weight_lbs),
            step=0.5,
            key="update_weight"
        )

        if st.button("Update Weight"):
            profile.update({'personal_info': {'weight_lbs': new_weight}})
            st.success(f"Weight updated to {new_weight} lbs")
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
    if profile.exists():
        render_profile_view()
    else:
        render_profile_setup()

    # Proactive Dashboard (show plan automatically if profile exists)
    if profile.exists():
        render_proactive_dashboard(profile)

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