# HealthRAG Database Schema

## Overview
This document defines the database schema for HealthRAG's nutrition and exercise tracking features.

## Technology Stack
- **Development/Local**: SQLite 3.x
- **Production/Hosted**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0+

---

## Schema Design

### **Users & Profiles**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255), -- NULL for local-only mode
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Personal Info
    date_of_birth DATE,
    gender VARCHAR(20), -- male, female, other, prefer_not_to_say
    height_cm DECIMAL(5,2),

    -- Goals
    goal_type VARCHAR(20), -- cut, maintain, bulk, recomp
    activity_level VARCHAR(20), -- sedentary, lightly_active, moderately_active, very_active, extremely_active

    -- Target Macros (manually set or algorithm-calculated)
    target_calories INTEGER,
    target_protein_g INTEGER,
    target_carbs_g INTEGER,
    target_fat_g INTEGER,

    -- Preferences
    preferred_gym VARCHAR(50), -- home, planet_fitness, other

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);
```

---

### **Nutrition Tracking**

#### **Food Database**

```sql
-- Core food database (from USDA FoodData Central)
CREATE TABLE foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identifiers
    fdc_id INTEGER UNIQUE, -- FoodData Central ID (if from USDA)
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),

    -- Nutritional Info (per 100g or per serving)
    serving_size_g DECIMAL(10,2),
    serving_size_unit VARCHAR(20), -- g, ml, oz, cup, etc.

    -- Macros
    calories DECIMAL(10,2) NOT NULL,
    protein_g DECIMAL(10,2) NOT NULL,
    carbs_g DECIMAL(10,2) NOT NULL,
    fat_g DECIMAL(10,2) NOT NULL,
    fiber_g DECIMAL(10,2),
    sugar_g DECIMAL(10,2),

    -- Micros (optional for MVP)
    sodium_mg DECIMAL(10,2),
    potassium_mg DECIMAL(10,2),
    calcium_mg DECIMAL(10,2),
    iron_mg DECIMAL(10,2),
    vitamin_a_mcg DECIMAL(10,2),
    vitamin_c_mg DECIMAL(10,2),
    vitamin_d_mcg DECIMAL(10,2),

    -- Metadata
    data_source VARCHAR(50), -- usda, user_created, openfoodfacts, manual
    barcode VARCHAR(50), -- UPC/EAN barcode
    is_verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_foods_name ON foods(name);
CREATE INDEX idx_foods_barcode ON foods(barcode);
CREATE INDEX idx_foods_fdc_id ON foods(fdc_id);
```

#### **User Food Diary**

```sql
-- Daily food logs
CREATE TABLE food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_id INTEGER REFERENCES foods(id) ON DELETE SET NULL,

    -- When
    logged_date DATE NOT NULL,
    meal_type VARCHAR(20), -- breakfast, lunch, dinner, snack
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- How Much
    servings DECIMAL(10,2) NOT NULL DEFAULT 1.0,
    serving_size_g DECIMAL(10,2), -- actual serving size used

    -- Nutritional Snapshot (denormalized for history)
    calories DECIMAL(10,2) NOT NULL,
    protein_g DECIMAL(10,2) NOT NULL,
    carbs_g DECIMAL(10,2) NOT NULL,
    fat_g DECIMAL(10,2) NOT NULL,

    -- Metadata
    notes TEXT,
    is_quick_add BOOLEAN DEFAULT FALSE, -- manually entered macros without food reference

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_logs_user_date ON food_logs(user_id, logged_date);
CREATE INDEX idx_food_logs_user_created ON food_logs(user_id, created_at);
```

#### **Recipes**

```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,
    servings INTEGER NOT NULL DEFAULT 1,

    -- Aggregated nutritional info (per serving)
    calories DECIMAL(10,2),
    protein_g DECIMAL(10,2),
    carbs_g DECIMAL(10,2),
    fat_g DECIMAL(10,2),

    source_url TEXT, -- if imported from web
    instructions TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    food_id INTEGER NOT NULL REFERENCES foods(id) ON DELETE CASCADE,

    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20), -- g, oz, cup, etc.

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
```

#### **Favorite/Recent Foods**

```sql
CREATE TABLE user_favorite_foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_id INTEGER NOT NULL REFERENCES foods(id) ON DELETE CASCADE,

    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    use_count INTEGER DEFAULT 1,

    UNIQUE(user_id, food_id)
);

CREATE INDEX idx_favorite_foods_user ON user_favorite_foods(user_id, last_used_at DESC);
```

---

### **Weight & Body Tracking**

```sql
CREATE TABLE weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    logged_date DATE NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,

    -- Optional additional measurements
    body_fat_percentage DECIMAL(4,2),

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, logged_date)
);

CREATE INDEX idx_weight_logs_user_date ON weight_logs(user_id, logged_date);

-- Body measurements (waist, arms, etc.)
CREATE TABLE body_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    logged_date DATE NOT NULL,

    -- Measurements in cm
    neck_cm DECIMAL(5,2),
    chest_cm DECIMAL(5,2),
    waist_cm DECIMAL(5,2),
    hips_cm DECIMAL(5,2),
    bicep_left_cm DECIMAL(5,2),
    bicep_right_cm DECIMAL(5,2),
    thigh_left_cm DECIMAL(5,2),
    thigh_right_cm DECIMAL(5,2),
    calf_left_cm DECIMAL(5,2),
    calf_right_cm DECIMAL(5,2),

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_body_measurements_user_date ON body_measurements(user_id, logged_date);
```

---

### **Exercise Tracking**

#### **Exercise Library**

```sql
-- Exercise definitions
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Categories
    primary_muscle_group VARCHAR(50), -- chest, back, legs, shoulders, arms, core
    secondary_muscle_groups TEXT, -- JSON array: ["triceps", "shoulders"]

    -- Equipment
    equipment_required TEXT, -- JSON array: ["barbell", "bench"]
    available_at_home BOOLEAN DEFAULT FALSE,
    available_at_planet_fitness BOOLEAN DEFAULT FALSE,

    -- Exercise tier/rating
    tier_rating VARCHAR(10), -- S, A, B, C (from S Tier Exercises / Jeff Nippard)

    -- Instructions (from RAG/PDFs)
    instructions TEXT,
    form_cues TEXT, -- key form points
    video_url TEXT,

    -- Metadata
    is_compound BOOLEAN DEFAULT TRUE,
    difficulty_level VARCHAR(20), -- beginner, intermediate, advanced

    data_source VARCHAR(50), -- s_tier_exercises, jeff_nippard, user_created, rp_training

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exercises_muscle_group ON exercises(primary_muscle_group);
CREATE INDEX idx_exercises_tier ON exercises(tier_rating);
CREATE INDEX idx_exercises_name ON exercises(name);
```

#### **Workout Programs**

```sql
-- Workout program templates
CREATE TABLE workout_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- NULL for system programs

    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_weeks INTEGER,

    program_type VARCHAR(50), -- hypertrophy, strength, min_max_4x, fundamentals
    frequency_per_week INTEGER, -- 3, 4, 5, 6

    is_system_program BOOLEAN DEFAULT FALSE, -- from your PDFs (RP, Fundamentals, etc.)
    is_active BOOLEAN DEFAULT FALSE, -- user's currently active program

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workout_program_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL REFERENCES workout_programs(id) ON DELETE CASCADE,

    day_number INTEGER NOT NULL, -- 1, 2, 3, 4 (for 4x/week program)
    day_name VARCHAR(100), -- "Upper A", "Lower A", "Push", "Pull", etc.

    description TEXT,

    UNIQUE(program_id, day_number)
);

CREATE TABLE workout_program_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_day_id INTEGER NOT NULL REFERENCES workout_program_days(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,

    exercise_order INTEGER NOT NULL, -- order in workout

    -- Volume prescription
    sets INTEGER NOT NULL,
    reps_min INTEGER, -- 8 (for 8-12 reps)
    reps_max INTEGER, -- 12
    rpe_target DECIMAL(3,1), -- Rate of Perceived Exertion (6.0-10.0)
    rir_target INTEGER, -- Reps in Reserve (0-4)

    rest_seconds INTEGER, -- rest between sets

    notes TEXT, -- "Focus on stretch", "Explosive concentric", etc.

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Workout Logs**

```sql
-- Individual workout sessions
CREATE TABLE workout_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    program_id INTEGER REFERENCES workout_programs(id) ON DELETE SET NULL,
    program_day_id INTEGER REFERENCES workout_program_days(id) ON DELETE SET NULL,

    session_date DATE NOT NULL,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,

    notes TEXT,
    overall_rating INTEGER, -- 1-5 subjective rating

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_sessions_user_date ON workout_sessions(user_id, session_date);

-- Individual exercise sets logged
CREATE TABLE workout_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,

    set_number INTEGER NOT NULL, -- 1, 2, 3, 4

    -- Performance
    weight_kg DECIMAL(6,2),
    reps INTEGER NOT NULL,
    rpe DECIMAL(3,1), -- Rate of Perceived Exertion
    rir INTEGER, -- Reps in Reserve

    -- Metadata
    is_warmup BOOLEAN DEFAULT FALSE,
    is_drop_set BOOLEAN DEFAULT FALSE,
    is_failure BOOLEAN DEFAULT FALSE,

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_sets_session ON workout_sets(session_id);
CREATE INDEX idx_workout_sets_exercise ON workout_sets(exercise_id, created_at);
```

---

### **Adaptive Algorithm & Analytics**

```sql
-- TDEE (Total Daily Energy Expenditure) tracking
CREATE TABLE tdee_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    calculation_date DATE NOT NULL,

    -- Inputs
    avg_daily_calories DECIMAL(10,2), -- average calories consumed (7-14 day average)
    avg_weight_kg DECIMAL(5,2), -- average weight (7-14 day moving average)
    weight_change_kg DECIMAL(5,2), -- weight change over period

    -- Calculated TDEE
    estimated_tdee DECIMAL(10,2), -- calculated maintenance calories
    confidence_score DECIMAL(3,2), -- 0.0-1.0 (based on data quality)

    -- Recommendations
    recommended_calories INTEGER,
    recommended_protein_g INTEGER,
    recommended_carbs_g INTEGER,
    recommended_fat_g INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, calculation_date)
);

CREATE INDEX idx_tdee_user_date ON tdee_calculations(user_id, calculation_date);

-- Weekly summaries for dashboard
CREATE TABLE weekly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,

    -- Nutrition
    avg_daily_calories DECIMAL(10,2),
    avg_daily_protein_g DECIMAL(10,2),
    avg_daily_carbs_g DECIMAL(10,2),
    avg_daily_fat_g DECIMAL(10,2),
    days_logged INTEGER, -- how many days had food logs

    -- Weight
    start_weight_kg DECIMAL(5,2),
    end_weight_kg DECIMAL(5,2),
    avg_weight_kg DECIMAL(5,2),
    weight_change_kg DECIMAL(5,2),

    -- Training
    workouts_completed INTEGER,
    total_volume_kg DECIMAL(10,2), -- total tonnage (sets × reps × weight)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, week_start_date)
);

CREATE INDEX idx_weekly_summaries_user_week ON weekly_summaries(user_id, week_start_date);
```

---

### **System Tables**

```sql
-- API cache for USDA FoodData Central
CREATE TABLE food_api_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    cache_key VARCHAR(255) UNIQUE NOT NULL, -- fdc_id or search query hash
    cache_type VARCHAR(50), -- food_detail, search_result, barcode_lookup

    response_data TEXT, -- JSON response

    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_api_cache_key ON food_api_cache(cache_key);
CREATE INDEX idx_food_api_cache_expires ON food_api_cache(expires_at);

-- User preferences/settings
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Units
    weight_unit VARCHAR(10) DEFAULT 'kg', -- kg or lbs
    height_unit VARCHAR(10) DEFAULT 'cm', -- cm or inches

    -- Display preferences
    theme VARCHAR(20) DEFAULT 'light', -- light, dark
    default_meal_order TEXT, -- JSON: ["breakfast", "lunch", "dinner", "snack"]

    -- Notifications (for future)
    notify_weight_log BOOLEAN DEFAULT TRUE,
    notify_workout_log BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);
```

---

## Indexes Summary

All foreign keys have indexes. Additional indexes:
- User/date combinations for time-series queries
- Name/search fields for autocomplete
- Frequently filtered fields (muscle group, tier rating, etc.)

---

## Data Sizes Estimation

**Per User (1 year of tracking):**
- Food logs: ~365 days × 15 entries/day × 200 bytes = **1.1 MB**
- Workout logs: ~150 sessions × 100 sets × 100 bytes = **1.5 MB**
- Weight logs: 365 entries × 100 bytes = **37 KB**
- **Total per user/year**: ~3 MB

**Shared Data:**
- Foods database: ~50,000 foods × 500 bytes = **25 MB**
- Exercises library: ~500 exercises × 1 KB = **500 KB**
- **Total shared**: ~26 MB

**SQLite performance**: Excellent up to 100GB, no issues for personal use

---

## Migration Strategy

### Phase 1: SQLite (MVP)
- Single file database: `data/health.db`
- No server required
- Perfect for local-first development

### Phase 2: PostgreSQL (Hosted)
- Use SQLAlchemy for abstraction
- Migrations via Alembic
- Keep SQLite for local development

### Schema Migration Plan:
```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Support both databases
DATABASE_URL=sqlite:///./data/health.db  # Local
DATABASE_URL=postgresql://user:pass@host/db  # Hosted
```

---

## Next Steps

1. Implement SQLAlchemy ORM models
2. Create Alembic migration scripts
3. Build FastAPI endpoints for CRUD operations
4. Integrate USDA FoodData Central API with caching
5. Populate exercises table from S Tier Exercises and PDFs

---

## Questions to Resolve

1. **S Tier Exercises structure**: What muscles/exercises are included?
2. **Gym equipment**: Specific equipment list for Home and Planet Fitness?
3. **Workout programs**: Which programs from PDFs should be pre-loaded?
4. **Food database**: Start with USDA API + user-created foods, or import existing database?
