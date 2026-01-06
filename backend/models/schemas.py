"""
Pydantic Schemas for Request/Response Validation.

Defines data validation models for all API endpoints.
Separates from SQLAlchemy models for clean API contracts.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# User Profile Schemas
# ============================================

class UserProfileBase(BaseModel):
    """Base schema for user profile (shared fields)"""
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    sex: Optional[str] = Field(None, pattern="^(male|female)$")
    height_inches: Optional[float] = Field(None, gt=0, le=108)  # 0-9 feet
    current_weight_lbs: Optional[float] = Field(None, gt=0, le=1000)

    goal_type: Optional[str] = Field(None, pattern="^(cut|bulk|recomp|maintain)$")
    target_weight_lbs: Optional[float] = Field(None, gt=0, le=1000)
    weekly_goal_lbs: Optional[float] = Field(None, ge=-5, le=5)  # ±5 lbs/week max

    training_experience: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    equipment_access: Optional[str] = Field(None, pattern="^(minimal|home_gym|planet_fitness|commercial_gym)$")


class UserProfileCreate(UserProfileBase):
    """Schema for creating a new user profile"""
    email: EmailStr


class UserProfileUpdate(UserProfileBase):
    """Schema for updating user profile (all fields optional)"""
    pass


class UserProfileResponse(UserProfileBase):
    """Schema for user profile API response"""
    id: str
    email: str
    created_at: datetime
    updated_at: datetime

    # Calculated metrics
    tdee: Optional[float] = None
    bmr: Optional[float] = None
    target_calories: Optional[int] = None
    target_protein_g: Optional[int] = None
    target_carbs_g: Optional[int] = None
    target_fat_g: Optional[int] = None

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


# ============================================
# Workout Schemas
# ============================================

class WorkoutSetBase(BaseModel):
    """Base schema for workout set"""
    set_number: int = Field(ge=1)
    exercise_name: str = Field(min_length=1, max_length=100)
    weight_lbs: float = Field(ge=0, le=2000)  # 0-2000 lbs
    reps_completed: int = Field(ge=0, le=100)
    rir: Optional[int] = Field(None, ge=0, le=10)  # Rate of Intensity Reserved
    notes: Optional[str] = None


class WorkoutSetCreate(WorkoutSetBase):
    """Schema for creating a workout set"""
    pass


class WorkoutSetResponse(WorkoutSetBase):
    """Schema for workout set API response"""
    id: int
    session_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class WorkoutSessionBase(BaseModel):
    """Base schema for workout session"""
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    workout_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class WorkoutSessionCreate(WorkoutSessionBase):
    """Schema for creating a workout session"""
    sets: List[WorkoutSetCreate] = []


class WorkoutSessionResponse(WorkoutSessionBase):
    """Schema for workout session API response"""
    id: int
    user_id: str
    created_at: datetime
    sets: List[WorkoutSetResponse] = []

    class Config:
        from_attributes = True


# ============================================
# Weight Entry Schemas
# ============================================

class WeightEntryBase(BaseModel):
    """Base schema for weight entry"""
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    weight_lbs: float = Field(gt=0, le=1000)
    notes: Optional[str] = None


class WeightEntryCreate(WeightEntryBase):
    """Schema for creating a weight entry"""
    pass


class WeightEntryResponse(WeightEntryBase):
    """Schema for weight entry API response"""
    id: int
    user_id: str
    trend_weight_lbs: Optional[float] = None  # EWMA calculated
    created_at: datetime

    class Config:
        from_attributes = True


class WeightTrendResponse(BaseModel):
    """Schema for weight trend analysis"""
    entries: List[WeightEntryResponse]
    ewma_alpha: float = 0.3
    latest_trend: Optional[float] = None
    weekly_change_lbs: Optional[float] = None
    monthly_change_lbs: Optional[float] = None


# ============================================
# Food/Nutrition Schemas
# ============================================

class FoodEntryBase(BaseModel):
    """Base schema for food entry"""
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    meal_type: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")
    food_name: str = Field(min_length=1, max_length=200)
    serving_size: Optional[str] = Field(None, max_length=100)
    serving_quantity: float = Field(gt=0, default=1.0)

    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)

    fiber_g: Optional[float] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)

    barcode: Optional[str] = None
    source: Optional[str] = Field(None, pattern="^(usda_fdc|open_food_facts|manual)$")
    notes: Optional[str] = None


class FoodEntryCreate(FoodEntryBase):
    """Schema for creating a food entry"""
    pass


class FoodEntryResponse(FoodEntryBase):
    """Schema for food entry API response"""
    id: int
    user_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class DailyNutritionSummary(BaseModel):
    """Schema for daily nutrition totals"""
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: Optional[float] = None
    entry_count: int
    entries: List[FoodEntryResponse] = []


class FoodSearchResult(BaseModel):
    """Schema for food search API response"""
    food_name: str
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    source: str  # "usda_fdc" or "open_food_facts"
    external_id: Optional[str] = None  # For caching


# ============================================
# Body Measurements Schemas (Tier 1)
# ============================================

class BodyMeasurementBase(BaseModel):
    """Base schema for body measurements"""
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    waist: Optional[float] = Field(None, gt=0, le=100)
    chest: Optional[float] = Field(None, gt=0, le=100)
    hips: Optional[float] = Field(None, gt=0, le=100)
    neck: Optional[float] = Field(None, gt=0, le=100)
    shoulders: Optional[float] = Field(None, gt=0, le=100)
    left_arm: Optional[float] = Field(None, gt=0, le=100)
    right_arm: Optional[float] = Field(None, gt=0, le=100)
    left_thigh: Optional[float] = Field(None, gt=0, le=100)
    right_thigh: Optional[float] = Field(None, gt=0, le=100)
    left_calf: Optional[float] = Field(None, gt=0, le=100)
    right_calf: Optional[float] = Field(None, gt=0, le=100)
    notes: Optional[str] = None


class BodyMeasurementCreate(BodyMeasurementBase):
    """Schema for creating body measurements"""
    pass


class BodyMeasurementResponse(BodyMeasurementBase):
    """Schema for body measurements API response"""
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Sync Protocol Schemas
# ============================================

class SyncPullRequest(BaseModel):
    """Schema for pulling changes from server"""
    last_sync_timestamp: Optional[datetime] = None
    table_names: List[str] = ["workouts", "food", "weight", "profile"]  # Tables to sync


class SyncPushRequest(BaseModel):
    """Schema for pushing local changes to server"""
    changes: dict  # JSON payload with changes per table
    device_id: str


class SyncResponse(BaseModel):
    """Schema for sync operation response"""
    timestamp: datetime
    changes: dict  # Changes pulled from server
    conflicts: List[dict] = []  # Conflicts detected (Last Write Wins)
    synced_count: int


# ============================================
# Auth Schemas
# ============================================

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Schema for decoded JWT token data"""
    user_id: str
    email: str


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """Schema for signup request"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = None


# ============================================
# Generic API Response
# ============================================

class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None
    status_code: int
