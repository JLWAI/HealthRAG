# HealthRAG API Design

## Overview
FastAPI-based REST API for nutrition and exercise tracking with MacroFactor-inspired features.

## Base URL
- **Local**: `http://localhost:8000/api/v1`
- **Hosted**: `https://healthrag.example.com/api/v1`

---

## Authentication (Stage 2+)

```http
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

**MVP**: Single local user, no auth required
**Stage 2**: JWT tokens for hosted version

---

## **Nutrition Endpoints**

### **Foods Database**

#### Search Foods
```http
GET /foods/search?q=chicken%20breast&limit=20&offset=0
```

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional, default=20): Results per page
- `offset` (optional, default=0): Pagination offset
- `source` (optional): Filter by source (usda, openfoodfacts, user_created)

**Response:**
```json
{
  "total": 156,
  "limit": 20,
  "offset": 0,
  "results": [
    {
      "id": 1234,
      "name": "Chicken Breast, Raw",
      "brand": null,
      "calories": 165,
      "protein_g": 31,
      "carbs_g": 0,
      "fat_g": 3.6,
      "serving_size_g": 100,
      "serving_size_unit": "g",
      "data_source": "usda",
      "fdc_id": 171477,
      "is_verified": true
    }
  ]
}
```

#### Get Food by ID
```http
GET /foods/{food_id}
```

**Response:**
```json
{
  "id": 1234,
  "name": "Chicken Breast, Raw",
  "brand": null,
  "fdc_id": 171477,
  "calories": 165,
  "protein_g": 31,
  "carbs_g": 0,
  "fat_g": 3.6,
  "fiber_g": 0,
  "sugar_g": 0,
  "sodium_mg": 74,
  "potassium_mg": 256,
  "serving_size_g": 100,
  "serving_size_unit": "g",
  "data_source": "usda",
  "is_verified": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Search by Barcode
```http
GET /foods/barcode/{barcode}
```

**Example:**
```http
GET /foods/barcode/038000845406
```

**Response:** Same as Get Food by ID

#### Create Custom Food
```http
POST /foods
```

**Request Body:**
```json
{
  "name": "My Protein Shake",
  "calories": 320,
  "protein_g": 50,
  "carbs_g": 10,
  "fat_g": 8,
  "serving_size_g": 250,
  "serving_size_unit": "ml",
  "notes": "Post-workout shake"
}
```

**Response:** Created food object with ID

#### Recent/Favorite Foods
```http
GET /foods/recent?limit=20
GET /foods/favorites?limit=50
```

---

### **Food Logging**

#### Log Food Entry
```http
POST /food-logs
```

**Request Body:**
```json
{
  "food_id": 1234,
  "logged_date": "2025-01-15",
  "meal_type": "lunch",
  "servings": 1.5,
  "notes": "Post-workout meal"
}
```

**Response:**
```json
{
  "id": 5678,
  "food_id": 1234,
  "food_name": "Chicken Breast, Raw",
  "logged_date": "2025-01-15",
  "meal_type": "lunch",
  "servings": 1.5,
  "calories": 247.5,
  "protein_g": 46.5,
  "carbs_g": 0,
  "fat_g": 5.4,
  "created_at": "2025-01-15T13:45:00Z"
}
```

#### Quick Add Macros (no food reference)
```http
POST /food-logs/quick-add
```

**Request Body:**
```json
{
  "logged_date": "2025-01-15",
  "meal_type": "snack",
  "calories": 200,
  "protein_g": 10,
  "carbs_g": 20,
  "fat_g": 8,
  "notes": "Trail mix"
}
```

#### Get Daily Food Log
```http
GET /food-logs?date=2025-01-15
```

**Response:**
```json
{
  "date": "2025-01-15",
  "totals": {
    "calories": 2150,
    "protein_g": 180,
    "carbs_g": 210,
    "fat_g": 65
  },
  "target": {
    "calories": 2200,
    "protein_g": 175,
    "carbs_g": 220,
    "fat_g": 70
  },
  "meals": {
    "breakfast": [
      {
        "id": 5670,
        "food_name": "Oatmeal with Protein",
        "servings": 1.0,
        "calories": 350,
        "protein_g": 30,
        "carbs_g": 45,
        "fat_g": 8
      }
    ],
    "lunch": [/* ... */],
    "dinner": [/* ... */],
    "snack": [/* ... */]
  }
}
```

#### Update Food Log Entry
```http
PUT /food-logs/{log_id}
PATCH /food-logs/{log_id}
```

#### Delete Food Log Entry
```http
DELETE /food-logs/{log_id}
```

#### Copy Meal
```http
POST /food-logs/copy-meal
```

**Request Body:**
```json
{
  "from_date": "2025-01-14",
  "from_meal_type": "breakfast",
  "to_date": "2025-01-15",
  "to_meal_type": "breakfast"
}
```

---

### **Recipes**

```http
GET /recipes                    # List user's recipes
GET /recipes/{recipe_id}        # Get recipe details
POST /recipes                   # Create recipe
PUT /recipes/{recipe_id}        # Update recipe
DELETE /recipes/{recipe_id}     # Delete recipe
POST /recipes/import            # Import from URL
POST /recipes/{recipe_id}/log   # Log entire recipe to food diary
```

---

### **Weight Tracking**

#### Log Weight
```http
POST /weight
```

**Request Body:**
```json
{
  "logged_date": "2025-01-15",
  "weight_kg": 82.5,
  "notes": "Morning weight, after bathroom"
}
```

#### Get Weight History
```http
GET /weight?start_date=2025-01-01&end_date=2025-01-15&include_trend=true
```

**Response:**
```json
{
  "entries": [
    {
      "logged_date": "2025-01-15",
      "weight_kg": 82.5,
      "trend_weight_kg": 82.8
    },
    {
      "logged_date": "2025-01-14",
      "weight_kg": 83.1,
      "trend_weight_kg": 82.9
    }
  ],
  "statistics": {
    "start_weight": 84.2,
    "current_weight": 82.5,
    "total_change": -1.7,
    "average_weekly_change": -0.42
  }
}
```

---

## **Exercise Endpoints**

### **Exercise Library**

#### Search Exercises
```http
GET /exercises/search?q=press&muscle_group=chest&gym=planet_fitness&tier=S
```

**Query Parameters:**
- `q` (optional): Search query
- `muscle_group` (optional): Filter by muscle group
- `equipment` (optional): Filter by equipment type
- `gym` (optional): Filter by gym location (home, planet_fitness)
- `tier` (optional): Filter by tier rating (S, A, B, C)
- `difficulty` (optional): beginner, intermediate, advanced

**Response:**
```json
{
  "total": 8,
  "results": [
    {
      "id": 42,
      "name": "Barbell Bench Press",
      "primary_muscle_group": "chest",
      "secondary_muscle_groups": ["triceps", "shoulders"],
      "equipment_required": ["barbell", "bench"],
      "available_at_home": false,
      "available_at_planet_fitness": false,
      "tier_rating": "S",
      "is_compound": true,
      "difficulty_level": "beginner",
      "instructions": "Lie on bench, grip bar slightly wider than shoulders..."
    }
  ]
}
```

#### Get Exercise by ID
```http
GET /exercises/{exercise_id}
```

**Response includes:**
- Full exercise details
- Personal best records
- Recent performance history (last 10 times performed)
- Form cues and tips

#### Get Exercise Substitutions
```http
GET /exercises/{exercise_id}/substitutions?gym=home
```

**Purpose:** Suggest alternative exercises when equipment unavailable

---

### **Workout Programs**

#### List Programs
```http
GET /programs?type=system         # Pre-built programs (RP, Min-Max, Fundamentals)
GET /programs?type=user           # User's custom programs
GET /programs/active              # User's currently active program
```

#### Get Program Details
```http
GET /programs/{program_id}
```

**Response:**
```json
{
  "id": 15,
  "name": "Renaissance Periodization Fundamentals",
  "description": "5-day hypertrophy program",
  "duration_weeks": 24,
  "frequency_per_week": 5,
  "is_system_program": true,
  "days": [
    {
      "day_number": 1,
      "day_name": "Back & Biceps",
      "exercises": [
        {
          "exercise_id": 10,
          "exercise_name": "Barbell Row",
          "sets": 4,
          "reps_min": 8,
          "reps_max": 12,
          "rpe_target": 8.0,
          "rest_seconds": 120,
          "notes": "Control the eccentric"
        }
      ]
    }
  ]
}
```

#### Create Custom Program
```http
POST /programs
```

#### Activate Program
```http
POST /programs/{program_id}/activate
```

---

### **Workout Logging**

#### Start Workout Session
```http
POST /workouts/sessions
```

**Request Body:**
```json
{
  "session_date": "2025-01-15",
  "program_id": 15,
  "program_day_id": 1,
  "started_at": "2025-01-15T18:30:00Z"
}
```

**Response:**
```json
{
  "id": 789,
  "session_date": "2025-01-15",
  "program_day_name": "Back & Biceps",
  "started_at": "2025-01-15T18:30:00Z",
  "exercises": [
    {
      "exercise_id": 10,
      "exercise_name": "Barbell Row",
      "planned_sets": 4,
      "planned_reps": "8-12",
      "last_performance": {
        "date": "2025-01-08",
        "best_set": "80kg × 10 reps @ RPE 8"
      }
    }
  ]
}
```

#### Log Set
```http
POST /workouts/sets
```

**Request Body:**
```json
{
  "session_id": 789,
  "exercise_id": 10,
  "set_number": 1,
  "weight_kg": 80,
  "reps": 10,
  "rpe": 8.0,
  "is_warmup": false
}
```

#### Complete Workout Session
```http
PUT /workouts/sessions/{session_id}/complete
```

**Request Body:**
```json
{
  "ended_at": "2025-01-15T19:45:00Z",
  "overall_rating": 4,
  "notes": "Felt strong today"
}
```

#### Get Workout History
```http
GET /workouts/sessions?start_date=2025-01-01&end_date=2025-01-15
```

#### Get Exercise Performance History
```http
GET /workouts/exercises/{exercise_id}/history?limit=20
```

**Response:**
```json
{
  "exercise_name": "Barbell Row",
  "personal_bests": {
    "max_weight": {
      "weight_kg": 100,
      "reps": 5,
      "date": "2024-12-20"
    },
    "max_volume_set": {
      "weight_kg": 80,
      "reps": 15,
      "volume_kg": 1200,
      "date": "2025-01-10"
    }
  },
  "recent_sessions": [
    {
      "date": "2025-01-15",
      "sets": [
        {"set_number": 1, "weight_kg": 80, "reps": 10, "rpe": 8.0},
        {"set_number": 2, "weight_kg": 80, "reps": 9, "rpe": 8.5},
        {"set_number": 3, "weight_kg": 80, "reps": 8, "rpe": 9.0}
      ],
      "total_volume_kg": 2160
    }
  ]
}
```

---

## **Analytics & Adaptive Features**

### Dashboard
```http
GET /dashboard/summary?period=week
```

**Response:**
```json
{
  "period": "2025-01-08 to 2025-01-15",
  "nutrition": {
    "avg_daily_calories": 2180,
    "avg_daily_protein_g": 178,
    "target_compliance_rate": 0.86,
    "days_logged": 7
  },
  "weight": {
    "start_weight_kg": 83.2,
    "end_weight_kg": 82.5,
    "change_kg": -0.7,
    "trend_weight_kg": 82.8
  },
  "training": {
    "workouts_completed": 5,
    "total_volume_kg": 28500,
    "avg_session_duration_minutes": 68
  }
}
```

### TDEE Calculation & Recommendations
```http
GET /analytics/tdee
POST /analytics/tdee/calculate
```

**Response:**
```json
{
  "calculation_date": "2025-01-15",
  "estimated_tdee": 2650,
  "confidence_score": 0.85,
  "data_period_days": 14,
  "weight_change_kg": -0.8,
  "avg_daily_calories": 2200,
  "recommendations": {
    "action": "continue",
    "recommended_calories": 2200,
    "recommended_protein_g": 180,
    "recommended_carbs_g": 220,
    "recommended_fat_g": 65,
    "reasoning": "Weight loss is on track. Current intake is appropriate."
  }
}
```

### Progress Charts
```http
GET /analytics/weight-trend?start_date=2025-01-01&end_date=2025-01-15
GET /analytics/macros-compliance?period=month
GET /analytics/training-volume?start_date=2025-01-01&muscle_group=chest
```

---

## **User Profile**

### Get/Update Profile
```http
GET /profile
PUT /profile
```

**Request Body:**
```json
{
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "height_cm": 180,
  "goal_type": "recomp",
  "activity_level": "moderately_active",
  "target_calories": 2200,
  "target_protein_g": 180,
  "target_carbs_g": 220,
  "target_fat_g": 65,
  "preferred_gym": "planet_fitness"
}
```

### Get/Update Settings
```http
GET /settings
PUT /settings
```

---

## **AI-Powered Features (Stage 3)**

### AI Food Logging
```http
POST /ai/log-food-image
```

**Request:** Multipart form with image file

**Response:**
```json
{
  "detected_foods": [
    {
      "name": "Grilled Chicken Breast",
      "confidence": 0.92,
      "estimated_serving_g": 150,
      "calories": 248,
      "protein_g": 46,
      "carbs_g": 0,
      "fat_g": 5.4
    },
    {
      "name": "Brown Rice",
      "confidence": 0.88,
      "estimated_serving_g": 200,
      "calories": 220,
      "protein_g": 5,
      "carbs_g": 45,
      "fat_g": 2
    }
  ]
}
```

### AI Natural Language Food Entry
```http
POST /ai/log-food-text
```

**Request Body:**
```json
{
  "description": "two scrambled eggs with cheese and toast",
  "meal_type": "breakfast",
  "logged_date": "2025-01-15"
}
```

### AI Workout Recommendations
```http
GET /ai/recommend-workout?goal=hypertrophy&available_days=4&gym=home
```

---

## **RAG System Integration** (Existing)

### Exercise Knowledge Query
```http
POST /rag/query
```

**Request Body:**
```json
{
  "question": "What does Jeff Nippard recommend for optimal back thickness training?",
  "context_type": "exercise"
}
```

**Response:**
```json
{
  "answer": "According to Jeff Nippard's research, back thickness is best developed through...",
  "source_documents": [
    {
      "source": "Jeff_Nippard_Back_Training.pdf",
      "page": 12,
      "excerpt": "..."
    }
  ],
  "response_time": 3.2
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "calories",
      "issue": "Must be a positive number"
    }
  }
}
```

### HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Auth required (Stage 2+)
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Business logic error
- `429 Too Many Requests` - Rate limit exceeded (hosted)
- `500 Internal Server Error` - Server error

---

## Rate Limiting (Hosted Only)

```
Tier: Free (Local)
- No rate limits

Tier: Self-hosted
- 1000 requests/hour per IP
- 100 AI queries/day

Tier: Premium (Future)
- Unlimited requests
- Unlimited AI queries
```

---

## Versioning

API versioned via URL: `/api/v1/`, `/api/v2/`

Breaking changes will increment major version.

---

## Next Steps

1. Implement FastAPI app structure
2. Create Pydantic models for request/response validation
3. Implement CRUD operations for each endpoint
4. Add USDA FoodData Central integration
5. Build Streamlit UI consuming these endpoints
