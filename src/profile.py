"""
User Profile Management for HealthRAG

Handles user profile data including personal stats, goals, equipment,
and training schedule. Provides CRUD operations for profile management.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class PersonalInfo:
    """User's personal statistics"""
    name: str  # User's first name for personalization
    weight_lbs: float
    height_inches: int
    age: int
    sex: str  # 'male' or 'female'
    activity_level: str  # 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active'


@dataclass
class Goals:
    """User's fitness goals"""
    target_weight_lbs: Optional[float] = None
    phase: str = 'maintain'  # 'cut', 'bulk', 'maintain', 'recomp'
    timeline_weeks: Optional[int] = None
    target_rate_per_week: Optional[float] = None  # lbs per week
    primary_goal: str = 'general_fitness'  # 'strength', 'hypertrophy', 'fat_loss', 'performance', 'general_fitness'


@dataclass
class Experience:
    """User's training experience"""
    training_level: str = 'beginner'  # 'beginner', 'intermediate', 'advanced'
    years_training: int = 0
    injury_history: List[str] = None

    def __post_init__(self):
        if self.injury_history is None:
            self.injury_history = []


@dataclass
class Schedule:
    """User's training schedule"""
    days_per_week: int = 3
    minutes_per_session: int = 60
    preferred_split: str = 'full_body'  # 'full_body', 'upper_lower', 'ppl', 'bro_split'
    preferred_time: str = 'flexible'  # 'morning', 'afternoon', 'evening', 'flexible'


class UserProfile:
    """
    User profile management system.

    Handles loading, saving, and managing user profile data including
    personal stats, goals, equipment, and training schedule.
    """

    def __init__(self, profile_path: str = "data/user_profile.json"):
        """
        Initialize profile manager.

        Args:
            profile_path: Path to profile JSON file
        """
        self.profile_path = profile_path
        self.profile_data = None
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.profile_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def exists(self) -> bool:
        """Check if profile exists"""
        return os.path.exists(self.profile_path)

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load profile from file.

        Returns:
            Profile data dict or None if doesn't exist
        """
        if not self.exists():
            return None

        try:
            with open(self.profile_path, 'r') as f:
                self.profile_data = json.load(f)
            return self.profile_data
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def save(self, profile_data: Dict[str, Any]) -> bool:
        """
        Save profile to file.

        Args:
            profile_data: Profile data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamps
            if 'created_at' not in profile_data:
                profile_data['created_at'] = datetime.now().isoformat()
            profile_data['updated_at'] = datetime.now().isoformat()

            # Save to file
            with open(self.profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)

            self.profile_data = profile_data
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def create(self,
               name: str,
               weight_lbs: float,
               height_inches: int,
               age: int,
               sex: str,
               activity_level: str = 'moderately_active',
               equipment: List[str] = None,
               **kwargs) -> bool:
        """
        Create new user profile.

        Args:
            name: User's first name for personalization
            weight_lbs: Current weight in pounds
            height_inches: Height in inches
            age: Age in years
            sex: 'male' or 'female'
            activity_level: Activity level for TDEE calculation
            equipment: List of available equipment
            **kwargs: Additional optional fields (goals, schedule, etc.)

        Returns:
            True if successful, False otherwise
        """
        if self.exists():
            print("Profile already exists. Use update() to modify.")
            return False

        # Build profile structure
        profile_data = {
            'personal_info': {
                'name': name,
                'weight_lbs': weight_lbs,
                'height_inches': height_inches,
                'age': age,
                'sex': sex,
                'activity_level': activity_level
            },
            'goals': {
                'target_weight_lbs': kwargs.get('target_weight_lbs'),
                'phase': kwargs.get('phase', 'maintain'),
                'timeline_weeks': kwargs.get('timeline_weeks'),
                'target_rate_per_week': kwargs.get('target_rate_per_week'),
                'primary_goal': kwargs.get('primary_goal', 'general_fitness')
            },
            'experience': {
                'training_level': kwargs.get('training_level', 'beginner'),
                'years_training': kwargs.get('years_training', 0),
                'injury_history': kwargs.get('injury_history', [])
            },
            'equipment': equipment or ['bodyweight'],
            'schedule': {
                'days_per_week': kwargs.get('days_per_week', 3),
                'minutes_per_session': kwargs.get('minutes_per_session', 60),
                'preferred_split': kwargs.get('preferred_split', 'full_body'),
                'preferred_time': kwargs.get('preferred_time', 'flexible')
            }
        }

        return self.save(profile_data)

    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Update existing profile.

        Args:
            updates: Dictionary with fields to update (can be nested)

        Returns:
            True if successful, False otherwise
        """
        if not self.exists():
            print("Profile doesn't exist. Use create() first.")
            return False

        # Load current profile
        current = self.load()
        if not current:
            return False

        # Deep merge updates
        def deep_merge(base: dict, updates: dict) -> dict:
            """Recursively merge updates into base dict"""
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        updated_profile = deep_merge(current, updates)
        return self.save(updated_profile)

    def delete(self) -> bool:
        """
        Delete profile file.

        Returns:
            True if successful, False otherwise
        """
        if not self.exists():
            return True

        try:
            os.remove(self.profile_path)
            self.profile_data = None
            return True
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get value from profile using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'personal_info.weight_lbs')
            default: Default value if key not found

        Returns:
            Value at key path or default
        """
        if not self.profile_data:
            self.load()

        if not self.profile_data:
            return default

        keys = key_path.split('.')
        value = self.profile_data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_personal_info(self) -> Optional[PersonalInfo]:
        """Get personal info as dataclass"""
        info = self.get('personal_info')
        if info:
            return PersonalInfo(**info)
        return None

    def get_goals(self) -> Optional[Goals]:
        """Get goals as dataclass"""
        goals = self.get('goals')
        if goals:
            return Goals(**goals)
        return None

    def get_experience(self) -> Optional[Experience]:
        """Get experience as dataclass"""
        exp = self.get('experience')
        if exp:
            return Experience(**exp)
        return None

    def get_schedule(self) -> Optional[Schedule]:
        """Get schedule as dataclass"""
        sched = self.get('schedule')
        if sched:
            return Schedule(**sched)
        return None

    def summary(self) -> str:
        """
        Generate profile summary string.

        Returns:
            Formatted profile summary
        """
        if not self.profile_data:
            self.load()

        if not self.profile_data:
            return "No profile exists."

        info = self.get_personal_info()
        goals = self.get_goals()
        exp = self.get_experience()
        sched = self.get_schedule()

        summary_lines = [
            "=== USER PROFILE ===",
            "",
            "Personal Info:",
            f"  Weight: {info.weight_lbs} lbs",
            f"  Height: {info.height_inches} inches ({info.height_inches // 12}'{info.height_inches % 12}\")",
            f"  Age: {info.age} years",
            f"  Sex: {info.sex.capitalize()}",
            f"  Activity Level: {info.activity_level.replace('_', ' ').title()}",
            "",
            "Goals:",
            f"  Phase: {goals.phase.capitalize()}",
            f"  Primary Goal: {goals.primary_goal.replace('_', ' ').title()}",
        ]

        if goals.target_weight_lbs:
            summary_lines.append(f"  Target Weight: {goals.target_weight_lbs} lbs")
        if goals.timeline_weeks:
            summary_lines.append(f"  Timeline: {goals.timeline_weeks} weeks")

        summary_lines.extend([
            "",
            "Experience:",
            f"  Level: {exp.training_level.capitalize()}",
            f"  Years Training: {exp.years_training}",
            "",
            "Schedule:",
            f"  Days/Week: {sched.days_per_week}",
            f"  Minutes/Session: {sched.minutes_per_session}",
            f"  Split: {sched.preferred_split.replace('_', ' ').title()}",
            "",
            "Equipment:",
            "  " + ", ".join(self.get('equipment', [])),
            "",
            f"Last Updated: {self.get('updated_at', 'Never')}"
        ])

        return "\n".join(summary_lines)


# Activity level multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,  # Little or no exercise
    'lightly_active': 1.375,  # Exercise 1-3 days/week
    'moderately_active': 1.55,  # Exercise 3-5 days/week
    'very_active': 1.725,  # Exercise 6-7 days/week
    'extremely_active': 1.9  # Hard exercise 2x/day, physical job
}

# Common equipment lists
EQUIPMENT_PRESETS = {
    'minimal': ['bodyweight', 'resistance_bands', 'dumbbells'],
    'home_gym': ['barbell', 'dumbbells', 'rack', 'bench', 'pull_up_bar'],
    'commercial_gym': ['barbell', 'dumbbells', 'rack', 'bench', 'cables',
                       'machines', 'pull_up_bar', 'dip_station']
}


if __name__ == "__main__":
    # Example usage and testing
    print("Profile Manager Test\n")

    # Create test profile
    profile = UserProfile("data/test_profile.json")

    # Delete if exists (for clean test)
    if profile.exists():
        profile.delete()

    # Create new profile
    print("Creating profile...")
    success = profile.create(
        weight_lbs=185,
        height_inches=72,
        age=35,
        sex='male',
        activity_level='moderately_active',
        equipment=EQUIPMENT_PRESETS['commercial_gym'],
        phase='cut',
        target_weight_lbs=175,
        timeline_weeks=16,
        training_level='intermediate',
        years_training=5,
        days_per_week=4
    )

    if success:
        print("✅ Profile created successfully\n")
        print(profile.summary())

        # Test update
        print("\n\nUpdating weight...")
        profile.update({'personal_info': {'weight_lbs': 183}})
        print(f"New weight: {profile.get('personal_info.weight_lbs')} lbs")

        # Clean up
        profile.delete()
        print("\n✅ Test profile deleted")
    else:
        print("❌ Failed to create profile")
