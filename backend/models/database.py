"""
SQLAlchemy Database Configuration and Models.

Defines database connection, session management, and base models
for all HealthRAG entities (workouts, food, weight, profile).
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# Dependency for getting database session
def get_db():
    """
    Database session dependency for FastAPI endpoints.

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# User Profile Model
# ============================================

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True)  # Supabase user UUID
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personal Information
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)  # "male", "female"
    height_inches = Column(Float, nullable=True)
    current_weight_lbs = Column(Float, nullable=True)

    # Goals
    goal_type = Column(String, nullable=True)  # "cut", "bulk", "recomp", "maintain"
    target_weight_lbs = Column(Float, nullable=True)
    weekly_goal_lbs = Column(Float, nullable=True)  # e.g., -1.0 for cutting

    # Experience & Equipment
    training_experience = Column(String, nullable=True)  # "beginner", "intermediate", "advanced"
    equipment_access = Column(String, nullable=True)  # "minimal", "home_gym", "commercial_gym"

    # Calculated Metrics
    tdee = Column(Float, nullable=True)  # Total Daily Energy Expenditure
    bmr = Column(Float, nullable=True)  # Basal Metabolic Rate
    target_calories = Column(Integer, nullable=True)
    target_protein_g = Column(Integer, nullable=True)
    target_carbs_g = Column(Integer, nullable=True)
    target_fat_g = Column(Integer, nullable=True)

    # Relationships
    workouts = relationship("WorkoutSession", back_populates="user")
    weight_entries = relationship("WeightEntry", back_populates="user")
    food_entries = relationship("FoodEntry", back_populates="user")


# ============================================
# Workout Models
# ============================================

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    date = Column(String, nullable=False)  # ISO format YYYY-MM-DD
    workout_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserProfile", back_populates="workouts")
    sets = relationship("WorkoutSet", back_populates="session", cascade="all, delete-orphan")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    exercise_name = Column(String, nullable=False)
    weight_lbs = Column(Float, nullable=False)
    reps_completed = Column(Integer, nullable=False)
    rir = Column(Integer, nullable=True)  # Rate of Intensity Reserved (0-10)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("WorkoutSession", back_populates="sets")


# ============================================
# Weight Tracking Model
# ============================================

class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    date = Column(String, unique=True, nullable=False)  # ISO format YYYY-MM-DD
    weight_lbs = Column(Float, nullable=False)
    trend_weight_lbs = Column(Float, nullable=True)  # EWMA calculated
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserProfile", back_populates="weight_entries")


# ============================================
# Food/Nutrition Models
# ============================================

class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    date = Column(String, nullable=False)  # ISO format YYYY-MM-DD
    meal_type = Column(String, nullable=True)  # "breakfast", "lunch", "dinner", "snack"
    food_name = Column(String, nullable=False)
    serving_size = Column(String, nullable=True)
    serving_quantity = Column(Float, default=1.0)

    # Macronutrients (per serving)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)

    # Optional micronutrients
    fiber_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)

    # Metadata
    barcode = Column(String, nullable=True)
    source = Column(String, nullable=True)  # "usda_fdc", "open_food_facts", "manual"
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserProfile", back_populates="food_entries")


# ============================================
# Body Measurements Model (Optional - Tier 1)
# ============================================

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    date = Column(String, unique=True, nullable=False)  # ISO format YYYY-MM-DD

    # 11 measurements (inches)
    waist = Column(Float, nullable=True)
    chest = Column(Float, nullable=True)
    hips = Column(Float, nullable=True)
    neck = Column(Float, nullable=True)
    shoulders = Column(Float, nullable=True)
    left_arm = Column(Float, nullable=True)
    right_arm = Column(Float, nullable=True)
    left_thigh = Column(Float, nullable=True)
    right_thigh = Column(Float, nullable=True)
    left_calf = Column(Float, nullable=True)
    right_calf = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("✅ Database tables created successfully!")
