"""
Tests for User Profile Management System
"""

import pytest
import os
import json
import tempfile
from src.profile import UserProfile, PersonalInfo, Goals, Experience, Schedule, EQUIPMENT_PRESETS


@pytest.fixture
def temp_profile_path(tmp_path):
    """Create temporary profile path"""
    return str(tmp_path / "test_profile.json")


@pytest.fixture
def profile(temp_profile_path):
    """Create UserProfile instance with temp path"""
    return UserProfile(temp_profile_path)


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing"""
    return {
        'name': 'Test User',
        'weight_lbs': 185.0,
        'height_inches': 72,
        'age': 35,
        'sex': 'male',
        'activity_level': 'moderately_active',
        'equipment': ['barbell', 'dumbbells', 'rack'],
        'phase': 'cut',
        'target_weight_lbs': 175.0,
        'training_level': 'intermediate',
        'days_per_week': 4
    }


class TestProfileCreation:
    """Test profile creation"""

    def test_create_new_profile(self, profile, sample_profile_data):
        """Test creating a new profile"""
        success = profile.create(**sample_profile_data)
        assert success is True
        assert profile.exists() is True

    def test_create_duplicate_profile_fails(self, profile, sample_profile_data):
        """Test that creating duplicate profile fails"""
        profile.create(**sample_profile_data)
        success = profile.create(**sample_profile_data)
        assert success is False

    def test_created_profile_has_timestamps(self, profile, sample_profile_data):
        """Test that created profile includes timestamps"""
        profile.create(**sample_profile_data)
        data = profile.load()
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_minimal_profile_creation(self, profile):
        """Test creating profile with minimal required fields"""
        success = profile.create(
            name='Minimal User',
            weight_lbs=170.0,
            height_inches=68,
            age=25,
            sex='female'
        )
        assert success is True
        assert profile.get('personal_info.weight_lbs') == 170.0


class TestProfileLoading:
    """Test profile loading"""

    def test_load_existing_profile(self, profile, sample_profile_data):
        """Test loading an existing profile"""
        profile.create(**sample_profile_data)
        loaded = profile.load()
        assert loaded is not None
        assert loaded['personal_info']['weight_lbs'] == 185.0

    def test_load_nonexistent_profile(self, profile):
        """Test loading profile that doesn't exist"""
        loaded = profile.load()
        assert loaded is None

    def test_exists_check(self, profile, sample_profile_data):
        """Test profile existence check"""
        assert profile.exists() is False
        profile.create(**sample_profile_data)
        assert profile.exists() is True


class TestProfileUpdates:
    """Test profile updates"""

    def test_update_weight(self, profile, sample_profile_data):
        """Test updating weight"""
        profile.create(**sample_profile_data)
        success = profile.update({'personal_info': {'weight_lbs': 183.0}})
        assert success is True
        assert profile.get('personal_info.weight_lbs') == 183.0

    def test_update_multiple_fields(self, profile, sample_profile_data):
        """Test updating multiple fields"""
        profile.create(**sample_profile_data)
        updates = {
            'personal_info': {'weight_lbs': 180.0},
            'goals': {'phase': 'bulk'}
        }
        success = profile.update(updates)
        assert success is True
        assert profile.get('personal_info.weight_lbs') == 180.0
        assert profile.get('goals.phase') == 'bulk'

    def test_update_nonexistent_profile_fails(self, profile):
        """Test that updating nonexistent profile fails"""
        success = profile.update({'personal_info': {'weight_lbs': 180.0}})
        assert success is False

    def test_update_preserves_other_fields(self, profile, sample_profile_data):
        """Test that updates don't overwrite other fields"""
        profile.create(**sample_profile_data)
        original_age = profile.get('personal_info.age')
        profile.update({'personal_info': {'weight_lbs': 180.0}})
        assert profile.get('personal_info.age') == original_age


class TestProfileGetters:
    """Test profile getter methods"""

    def test_get_with_dot_notation(self, profile, sample_profile_data):
        """Test getting values with dot notation"""
        profile.create(**sample_profile_data)
        weight = profile.get('personal_info.weight_lbs')
        assert weight == 185.0

    def test_get_nonexistent_key_returns_default(self, profile, sample_profile_data):
        """Test that getting nonexistent key returns default"""
        profile.create(**sample_profile_data)
        value = profile.get('nonexistent.key', 'default')
        assert value == 'default'

    def test_get_personal_info_dataclass(self, profile, sample_profile_data):
        """Test getting personal info as dataclass"""
        profile.create(**sample_profile_data)
        info = profile.get_personal_info()
        assert isinstance(info, PersonalInfo)
        assert info.name == 'Test User'
        assert info.weight_lbs == 185.0
        assert info.height_inches == 72

    def test_get_goals_dataclass(self, profile, sample_profile_data):
        """Test getting goals as dataclass"""
        profile.create(**sample_profile_data)
        goals = profile.get_goals()
        assert isinstance(goals, Goals)
        assert goals.phase == 'cut'
        assert goals.target_weight_lbs == 175.0

    def test_get_experience_dataclass(self, profile, sample_profile_data):
        """Test getting experience as dataclass"""
        profile.create(**sample_profile_data)
        exp = profile.get_experience()
        assert isinstance(exp, Experience)
        assert exp.training_level == 'intermediate'

    def test_get_schedule_dataclass(self, profile, sample_profile_data):
        """Test getting schedule as dataclass"""
        profile.create(**sample_profile_data)
        sched = profile.get_schedule()
        assert isinstance(sched, Schedule)
        assert sched.days_per_week == 4


class TestProfileDeletion:
    """Test profile deletion"""

    def test_delete_existing_profile(self, profile, sample_profile_data):
        """Test deleting existing profile"""
        profile.create(**sample_profile_data)
        assert profile.exists() is True
        success = profile.delete()
        assert success is True
        assert profile.exists() is False

    def test_delete_nonexistent_profile(self, profile):
        """Test deleting nonexistent profile"""
        success = profile.delete()
        assert success is True  # Should succeed (idempotent)


class TestProfileSummary:
    """Test profile summary generation"""

    def test_summary_with_profile(self, profile, sample_profile_data):
        """Test generating summary with profile"""
        profile.create(**sample_profile_data)
        summary = profile.summary()
        assert '185' in summary and 'lbs' in summary
        assert '72 inches' in summary
        assert 'Cut' in summary
        assert 'Intermediate' in summary

    def test_summary_without_profile(self, profile):
        """Test summary when no profile exists"""
        summary = profile.summary()
        assert 'No profile exists' in summary


class TestEquipmentPresets:
    """Test equipment preset constants"""

    def test_equipment_presets_exist(self):
        """Test that equipment presets are defined"""
        expected_presets = {
            'minimal',
            'home_gym_basic',
            'home_gym_advanced',
            'planet_fitness',
            'home_gym_plus_pf',
            'commercial_gym'
        }
        assert expected_presets.issubset(set(EQUIPMENT_PRESETS.keys()))

    def test_commercial_gym_has_expected_equipment(self):
        """Test commercial gym preset has expected equipment"""
        gym = EQUIPMENT_PRESETS['commercial_gym']
        assert 'barbell' in gym
        assert 'dumbbells' in gym
        assert 'cables' in gym


class TestDataClasses:
    """Test dataclass constructors"""

    def test_personal_info_creation(self):
        """Test PersonalInfo dataclass"""
        info = PersonalInfo(
            name='Sample User',
            weight_lbs=185.0,
            height_inches=72,
            age=35,
            sex='male',
            activity_level='moderately_active'
        )
        assert info.weight_lbs == 185.0
        assert info.sex == 'male'

    def test_goals_with_defaults(self):
        """Test Goals dataclass with default values"""
        goals = Goals()
        assert goals.phase == 'maintain'
        assert goals.primary_goal == 'general_fitness'

    def test_experience_with_defaults(self):
        """Test Experience dataclass with defaults"""
        exp = Experience()
        assert exp.training_level == 'beginner'
        assert exp.years_training == 0
        assert exp.injury_history == []

    def test_schedule_with_defaults(self):
        """Test Schedule dataclass with defaults"""
        sched = Schedule()
        assert sched.days_per_week == 3
        assert sched.minutes_per_session == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
