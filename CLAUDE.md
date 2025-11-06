# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Documentation Structure

This file is part of a hierarchy of agent guidance documents:

1. **Parent Level (applies to ALL JLWAI projects):**
   - [`../AGENTS.md`](../AGENTS.md) - Universal agent contract (branch rules, iteration loop, test-first principles)
   - [`../CLAUDE.md`](../CLAUDE.md) - Parent-level rules (branch enforcement hooks, workflow)

2. **Project Level (HealthRAG-specific):**
   - **`CLAUDE.md`** (this file) - Detailed HealthRAG development guidance
   - [`AGENTS.md`](AGENTS.md) - Repository guidelines (build commands, coding style, testing)

**All agents must read BOTH parent and project-level documentation.**

## Project Context

**HealthRAG** is a FREE, local AI-powered health and fitness advisor using Retrieval-Augmented Generation (RAG). Currently in **Phase 4 development** (Nutrition Tracking & Adaptive TDEE). This is a solo developer project, part-time (10-20 hrs/week).

**Current Status** (as of November 2025):
- Branch: `claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX`
- Development Phase: Phase 4 ✅ COMPLETE
- Codebase: 32 source files, 16,459 LOC
- Phases Complete: Phase 2 ✅ Phase 3 ✅ Phase 4 ✅
- Phase 4 Status: 100% complete - All tracking, adaptive TDEE, and analytics features delivered

## Core Design Philosophy: Daily AI Coach

**CRITICAL**: When in doubt, think of HealthRAG as an **AI nutritional and exercise coach that works with the user daily** to:
1. **Help reach goals** - Provide personalized guidance based on user profile and progress
2. **Track results** - Log weight, workouts, measurements, nutrition data
3. **Analyze results** - Identify trends, detect plateaus, validate progress
4. **Ask for data** - Proactively request information needed for intelligent coaching
5. **Adapt recommendations** - Adjust calories, volume, program based on data

**Daily Coaching Interactions** (Examples):
- "What should I eat today?" → Macro-matched meal suggestions
- "Log workout: Bench 200 lbs × 8 reps" → Track performance, suggest progression
- "My weight went up 3 lbs" → Analyze trend, recommend calorie adjustment
- "I'm not seeing progress" → Analyze strength/body comp, suggest pivot or deload
- "Should I deload this week?" → Check training history, recommend yes/no

**Weekly Check-Ins**:
- Weight trend analysis (7-day averages)
- Strength progression review
- Body composition changes
- Adjustment recommendations (calories, macros, volume)

**Monthly Milestones**:
- Progress reports (muscle gained, fat lost)
- Program adjustments (increase volume if progressing)
- Phase transitions (cut → maintain, recomp → bulk)

**Key Principle**: HealthRAG is NOT a static calculator - it's a conversational coach that learns from user data and provides adaptive, evidence-based guidance over time.

## Architecture Overview

### High-Level System Design

```
Streamlit UI (main.py - 2,186 LOC)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ RAG System (rag_system.py)                                  │
│ - Dual LLM Backend: Ollama (Docker) | MLX (macOS)          │
│ - ChromaDB VectorStore (28 PDFs: RP, Nippard, BFFM)        │
│ - Evidence-based responses with source citations           │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ User Profile System (profile.py)                            │
│ - JSON storage (data/user_profile.json)                    │
│ - PersonalInfo, Goals, Experience, Equipment, Schedule     │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Calculation Engine (calculations.py - 418 LOC) ✅          │
│ - TDEE (Mifflin-St Jeor), BMR, Activity multipliers        │
│ - Macros (phase-aware: cut/bulk/recomp/maintain)           │
│ - Coaching-style guidance generation                        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Program Generation System ✅ COMPLETE                      │
│ - exercise_database.py (836 LOC) - Jeff Nippard Tier List  │
│ - program_generator.py (411 LOC) - 6-week mesocycles       │
│ - volume_prescription.py (362 LOC) - MEV/MAV/MRV           │
│ - progressive_overload.py (380 LOC) - RIR progression      │
│ - exercise_alternatives.py (483 LOC) - Equipment-aware     │
│ - program_export.py (223 LOC) - Excel/CSV/JSON export      │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Tracking & Analytics Systems ✅ PHASE 4 COMPLETE           │
│                                                              │
│ WORKOUT TRACKING ✅                                         │
│ - workout_logger.py (479 LOC) - SQLite logging             │
│ - workout_database.py (487 LOC) - Database management      │
│ - workout_coach.py (438 LOC) - AI coaching                 │
│ - autoregulation.py (373 LOC) - RP-based adjustments       │
│                                                              │
│ NUTRITION TRACKING ✅                                       │
│ - food_logger.py (644 LOC) - SQLite meal logging           │
│ - meal_templates.py (663 LOC) - One-click meals            │
│ - food_api_fdc.py (343 LOC) - USDA FDC (400K foods)        │
│ - food_api_off.py (377 LOC) - Open Food Facts (2.8M)       │
│ - food_search_integrated.py (258 LOC) - Unified search     │
│ - Camera barcode scanning (privacy-first, opt-in)          │
│                                                              │
│ ADAPTIVE TDEE ✅ COMPLETE                                   │
│ - adaptive_tdee.py (478 LOC) - EWMA + back-calculation     │
│ - tdee_analytics.py (502 LOC) - Historical trends          │
│ - enhanced_tdee_ui.py (426 LOC) - Weekly check-ins         │
│                                                              │
│ BODY MEASUREMENTS ✅ COMPLETE                               │
│ - body_measurements.py (392 LOC) - 13 measurement points   │
│                                                              │
│ PROGRESS PHOTOS ✅ COMPLETE                                 │
│ - progress_photos.py (354 LOC) - Photo storage/retrieval   │
│ - progress_photos_ui.py (287 LOC) - Upload/comparison UI   │
│                                                              │
│ PROGRESS REPORTS ✅ COMPLETE                                │
│ - progress_reports.py (643 LOC) - Monthly analytics        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Data Storage                                                 │
│ - data/user_profile.json - Profile data                    │
│ - data/workouts.db - SQLite workout logs                   │
│ - data/food_log.db - SQLite nutrition logs                 │
│ - data/vectorstore/ - ChromaDB embeddings                  │
│ - data/pdfs/ - 28 expert PDFs                              │
└─────────────────────────────────────────────────────────────┘
```

### Core Components (32 Files, 16,459 LOC)

**1. RAG System** (`src/rag_system.py` - 276 LOC):
- Dual backend support: Ollama (cross-platform) vs MLX (Apple Silicon native)
- ChromaDB vectorstore with `sentence-transformers/all-MiniLM-L6-v2` embeddings
- Retrieves k=5 most relevant document chunks per query
- **Critical Design Principle**: Grounded responses only - uses document context, never hallucinates
- Source attribution for all responses

**2. User Profile System** (`src/profile.py` - 461 LOC):
- JSON storage at `data/user_profile.json`
- Dataclasses: PersonalInfo, Goals, Experience, Equipment, Schedule
- CRUD operations for profile management
- Multi-user support with profile switching
- Equipment presets: minimal, home_gym, planet_fitness, commercial_gym

**3. Calculation Engine** (`src/calculations.py` - 418 LOC) ✅ COMPLETE:
- TDEE calculation (Mifflin-St Jeor formula)
- Activity level multipliers (sedentary 1.2 → extremely_active 1.9)
- Phase-aware adjustments (cut: -500, bulk: +300-500, recomp/maintain: 0)
- Macro calculations (protein 0.8-1.2g/lb, fat 0.3-0.5g/lb, carbs remainder)
- Coaching-style guidance generation (not just numbers)
- 25/25 tests passing with all 5 personas validated

**4. Program Generation System** ✅ PHASE 3 COMPLETE:
- `exercise_database.py` (836 LOC) - Jeff Nippard tier rankings, 200+ exercises
- `exercise_selection.py` (346 LOC) - Equipment filtering, tier prioritization
- `exercise_alternatives.py` (483 LOC) - Location-aware (home/Planet Fitness/commercial)
- `volume_prescription.py` (362 LOC) - MEV/MAV/MRV by muscle group and experience
- `progressive_overload.py` (380 LOC) - RIR-based weekly progression
- `mesocycle_templates.py` (439 LOC) - Upper/Lower, PPL, Full Body splits
- `program_generator.py` (411 LOC) - Complete 6-week mesocycle generation
- `program_export.py` (223 LOC) - Excel/Google Sheets, CSV, JSON export
- `program_manager.py` (254 LOC) - Save, load, versioning

**5. Workout Tracking System** ✅ PHASE 4 PARTIAL:
- `workout_logger.py` (479 LOC) - SQLite logging (sets, reps, weight, RIR, feedback)
- `workout_database.py` (487 LOC) - Database schema and queries
- `workout_models.py` (330 LOC) - Data models (WorkoutSession, ExerciseLog)
- `workout_coach.py` (438 LOC) - AI-powered coaching recommendations
- `autoregulation.py` (373 LOC) - RP-based volume/intensity adjustments
- Database: `data/workouts.db` (SQLite, 28 KB production)

**6. Nutrition Tracking System** ✅ PHASE 4 COMPLETE:
- `food_logger.py` (644 LOC) - SQLite meal logging with transaction safety
- `food_models.py` (430 LOC) - Data models (Food, FoodEntry, DailyNutrition)
- `meal_templates.py` (663 LOC) - One-click multi-food meal system
- `food_api_fdc.py` (343 LOC) - USDA FDC integration (400K foods)
- `food_api_off.py` (377 LOC) - Open Food Facts integration (2.8M products)
- `food_search_integrated.py` (258 LOC) - Unified multi-source search
- Camera barcode scanning with pyzbar (privacy-first: OFF by default)
- Database: `data/food_log.db` (SQLite, 49 KB production)

**7. Adaptive TDEE System** ✅ PHASE 4 COMPLETE:
- `adaptive_tdee.py` (478 LOC) - EWMA trend weight (alpha=0.3), back-calculated TDEE
- `tdee_analytics.py` (502 LOC) - Historical trends, water weight detection, TDEE graphs
- `enhanced_tdee_ui.py` (426 LOC) - Weekly check-ins, macro adjustment recommendations
- MacroFactor-style adherence-neutral logic (±20%/±50% thresholds)
- 14-day rolling window for TDEE calculation
- Phase-aware adjustments (cut/bulk/maintain/recomp)
- Database: `data/weights.db` (SQLite, weight tracking)

**8. Body Measurements System** ✅ PHASE 4 COMPLETE:
- `body_measurements.py` (392 LOC) - 13 measurement points (waist, chest, arms, etc.)
- SQLite storage with date-based tracking
- Trend analysis and visualization
- Integration with progress reports
- Database: `data/measurements.db` (SQLite)

**9. Progress Photos System** ✅ PHASE 4 COMPLETE:
- `progress_photos.py` (354 LOC) - Photo storage and retrieval
- `progress_photos_ui.py` (287 LOC) - Upload interface, gallery, before/after comparison
- Date-based organization with tags (front, side, back)
- Privacy-first: Local storage only
- Database: `data/photos.db` (SQLite), photos stored in `data/progress_photos/`

**10. Progress Reports System** ✅ PHASE 4 COMPLETE:
- `progress_reports.py` (643 LOC) - Monthly automated progress analysis
- Weight trend analysis (7-day, 30-day averages)
- Strength progression tracking (volume load, 1RM estimates)
- Body composition changes (measurements + photos)
- Goal achievement scoring
- Recommendations engine (nutrition, training, recovery adjustments)

**11. Apple Health Integration** (`src/apple_health.py` - 381 LOC):
- Import weight, workouts, nutrition from Apple Health XML exports
- Automatic data sync with HealthRAG databases
- Phase 5 feature completed early

**12. Streamlit UI** (`src/main.py` - 2,186 LOC):
- Chat interface for RAG queries
- Backend/model selection (MLX vs Ollama)
- Profile creation wizard with Apple Health import
- Program generation interface
- Workout logging UI with autoregulation recommendations
- Nutrition tracking UI with barcode scanning
- Weight tracking with EWMA trends
- Adaptive TDEE analytics and weekly check-ins
- Body measurements tracking
- Progress photos (upload, gallery, before/after)
- Monthly progress reports
- 7-tab interface for complete tracking suite
- Session state management

**13. Configuration** (`config/settings.py`):
- Centralized paths, chunking parameters, retrieval settings
- Model endpoints for Ollama and MLX
- Database paths and API configuration

## Development Commands

### Running the Application

**Docker (Cross-Platform)**:
```bash
./start_healthrag.sh              # One-command startup (recommended)
# OR
docker-compose up --build         # Manual Docker
docker-compose down               # Stop containers
docker-compose logs -f            # View logs

# Access: http://localhost:8501
# Ports: 8501 (Streamlit), 11434 (Ollama)
```

**MLX Local (macOS Only - FASTER)**:
```bash
./run_local_mlx.sh                # Setup MLX environment
# OR
source venv_mlx/bin/activate
streamlit run src/main.py

# Access: http://localhost:8501
```

**Simple Local Test**:
```bash
./run_local_simple.sh             # Quick MLX test
```

### Testing

```bash
pytest tests/                      # Run all tests
pytest -v                         # Verbose output
pytest --cov=src tests/           # With coverage
pytest --cov=src --cov-report=html tests/  # HTML coverage report
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m slow                    # Slow tests only
pytest -m "not slow"              # Skip slow tests
```

**Test Files** (9 test files):
- `tests/test_profile.py` - Profile CRUD, dataclass validation (30+ tests)
- `tests/test_calculations.py` - TDEE/macro validation with 5 personas (25 tests)
- `tests/test_rag_system.py` - Backend switching, document loading
- `tests/test_model_comparison.py` - LLM comparison
- `tests/test_workout_database.py` - Workout DB operations
- `tests/test_workout_models.py` - Workout data models
- `tests/test_workout_coach.py` - AI coaching logic
- `tests/test_meal_prep_workflow.py` - Meal template workflow
- `tests/fixtures/personas.py` - 5 user personas + 4 edge cases for testing

**pytest.ini Configuration**:
- Markers: `slow`, `integration`, `unit`
- Use markers to separate fast/slow tests
- Coverage reports available in `htmlcov/` directory

### Processing New PDFs

```bash
python3 process_pdfs.py           # Adds PDFs to vectorstore
rm -rf data/vectorstore/          # Rebuild vectorstore from scratch
```

### Data Management

```bash
ls data/pdfs                      # List PDFs (28 files)
cat data/user_profile.json        # View user profile
```

## Knowledge Base & Data Sources

### Document Collection (28 PDFs in `/data/pdfs/`)

**Renaissance Periodization (RP)**:
- Diet 2.0, Scientific Principles of Hypertrophy, Simply RP, Time To Eat, Volume Landmarks

**Jeff Nippard**:
- Exercise Tier List (S/A/B/C rankings) - **CRITICAL for Phase 3 program generation**
- Fundamentals Hypertrophy Program

**Body For Life Movement (BFFM)**:
- 2003 & 2012 versions

**Program Templates** (Excel tracking sheets):
- Min-Max 4x/week, Min-Max 5x/week
- **Required for Phase 3**: Will need `openpyxl` to parse these templates

**Key Reference Files**:
- `Jeff Nippard's Tier List.rtf` - Exercise selection database (must be converted for Phase 3)
- See `PROGRAM_TEMPLATES.md` for detailed catalog

### VectorStore
- **Location**: `data/vectorstore/`
- **Technology**: ChromaDB (local, persistent)
- **Lifecycle**: Created once via `process_pdfs.py`, reused across sessions

## Development Workflow & Principles

### Evidence-Based Coaching Principle
**ALL recommendations must be grounded in PDF sources AND contextualized to the user's profile/progress**. The RAG system is designed to:
1. **Grounded responses only** - Use document context (no hallucination), cite RP/Nippard/BFFM sources
2. **Profile-aware** - Consider user's experience level, equipment, schedule, goals when providing advice
3. **Progress-aware** - Reference user's historical data (weight trends, strength gains, body comp changes)
4. **Conversational coaching** - Not just facts, but actionable guidance ("Here's what to do next...")
5. **Adaptive** - Adjust recommendations based on what's working/not working for the user

**Examples of Coaching vs. Static Responses**:

❌ **Static Calculator**: "Your TDEE is 2,600 calories"
✅ **AI Coach**: "Based on your profile (210 lbs, sedentary), your maintenance is ~2,600 cal. For your cutting goal, I recommend starting at 2,100 cal (-500 deficit, 1 lb/week loss). We'll adjust based on your weekly weigh-ins."

❌ **Static Response**: "Renaissance Periodization recommends 12-18 sets per muscle group per week"
✅ **AI Coach**: "As an intermediate lifter training 4 days/week, you should start with 14-16 sets per muscle group. If you're not progressing after 3-4 weeks, we'll increase to 18 sets. RP Volume Landmarks supports this progression approach."

When implementing features that query the RAG system (e.g., TDEE formulas, macro calculations), always verify responses against the actual PDF content AND frame them as personalized coaching guidance.

### Development Phase Status

**Phase 2: User Profile & State Management** ✅ COMPLETE
- ✅ Profile system with JSON storage and CRUD operations
- ✅ Calculation engine (TDEE, BMR, macros) with 25/25 tests passing
- ✅ Profile-aware RAG queries
- ✅ Dashboard view with key stats
- ✅ All 5 personas validated (Beginner Ben, Intermediate Ian, Cutting Claire, Recomp Ryan, Minimal Megan)

**Phase 3: Program Generation** ✅ COMPLETE
- ✅ Exercise database (836 LOC) with Jeff Nippard tier rankings
- ✅ Equipment-aware exercise selection and alternatives
- ✅ Volume prescription (MEV/MAV/MRV by muscle group and experience level)
- ✅ Progressive overload system (RIR-based weekly progression)
- ✅ Mesocycle templates (Upper/Lower, PPL, Full Body splits)
- ✅ Complete 6-week program generation
- ✅ Program export (Excel/Google Sheets, CSV, JSON)
- ✅ Program management (save, load, versioning)

**Phase 4: Nutrition Tracking & Adaptive TDEE** ✅ 100% COMPLETE

**ALL FEATURES DELIVERED:**
- ✅ Workout logging system (SQLite: sets, reps, weight, RIR, feedback)
- ✅ Food logging system (SQLite: meals, macros, daily totals)
- ✅ Meal templates (one-click multi-food meals)
- ✅ USDA FDC integration (400K foods)
- ✅ Open Food Facts integration (2.8M products)
- ✅ Unified food search across multiple sources
- ✅ Camera barcode scanning (privacy-first, opt-in)
- ✅ Autoregulation engine (RP-based workout adjustments)
- ✅ AI workout coach (personalized recommendations)
- ✅ Apple Health integration (weight, workouts, nutrition import)
- ✅ **Adaptive TDEE algorithm** - EWMA trend weight (alpha=0.3), back-calculation TDEE
- ✅ **TDEE Analytics** - Historical trends, water weight detection, visualization
- ✅ **Weekly coaching check-ins** - Automated progress analysis with recommendations
- ✅ **Weekly macro adjustments** - Adherence-neutral calorie recommendations (±20%/±50% thresholds)
- ✅ **Body measurements tracking** - 13 measurement points (waist, chest, arms, legs, etc.)
- ✅ **Progress photos** - Upload, gallery, before/after comparison
- ✅ **Monthly progress reports** - Comprehensive analytics (weight, strength, body comp, goals)

**Phase 4 Summary:**
- 8 new files added (adaptive_tdee.py, tdee_analytics.py, enhanced_tdee_ui.py, body_measurements.py, progress_photos.py, progress_photos_ui.py, progress_reports.py, + 1 test file)
- 3,082 new lines of code
- All MacroFactor-inspired features delivered
- Complete 7-tab tracking interface
- Production-ready with comprehensive testing

See `PHASE4_SUMMARY.md` for detailed completion report.

**Phase 5: Polish & Advanced Features** 🔮 FUTURE
- Mobile app (React Native)
- Voice input for workout logging
- Enhanced data visualizations
- Exercise video library
- Meal planning and grocery lists

See `VISION.md` for detailed Phase 2-5 roadmap with diagrams.

### Scenario-Driven Development

HealthRAG development is guided by **5 realistic user personas** and **12 core scenarios** that map to each development phase. This approach ensures features are valuable, testable, and aligned with real user needs.

**Key Resources**:
- **`SCENARIOS.md`**: Comprehensive scenarios document with:
  - 5 user personas (Beginner Ben, Intermediate Ian, Cutting Claire, Recomp Ryan, Minimal Megan)
  - 12 core scenarios mapped to Phases 2-5
  - 8 edge cases (unrealistic goals, conflicting inputs, dietary restrictions, injuries, etc.)
  - Acceptance criteria matrix (must-have/should-have/nice-to-have per phase)
  - Testing strategies with expected outputs

- **`tests/fixtures/personas.py`**: Test data for all personas
  - Pre-defined profile data for consistent testing
  - Expected calculation ranges (TDEE, macros, BMR)
  - Edge case personas for validation testing
  - Import via: `from tests.fixtures import BEGINNER_BEN, INTERMEDIATE_IAN, etc.`

**Development Approach**:
1. **Each feature maps to a scenario** - Before implementing, check SCENARIOS.md for user story and acceptance criteria
2. **Test with all personas** - Validate new features against all 5 personas to ensure broad compatibility
3. **Edge cases are documented** - Handle edge cases per SCENARIOS.md (unrealistic goals, conflicting inputs, etc.)
4. **Incremental milestones** - Each phase delivers testable value aligned with scenarios

**Current Phase 4 Focus**:
- **Primary Goal**: Implement Adaptive TDEE algorithm (MacroFactor-style)
- **Key Features**: EWMA trend weight, back-calculation TDEE, weekly macro adjustments
- **Personas to test**: All 5 (Ben cutting, Ian bulking, Claire cutting, Ryan recomp, Megan maintenance)
- **Success criteria**: TDEE adjusts based on actual weight trend + intake, within ±50 cal of MacroFactor
- **Expected outputs**: See `PHASE4_PLAN.md` for detailed algorithm specifications

## Technology Stack

**Core Dependencies**:
- `langchain==0.1.0` + `langchain-community==0.0.10` (document processing, chains)
- `chromadb==0.4.22` (vector database)
- `sentence-transformers==2.7.0` (embeddings)
- `streamlit==1.29.0` (UI)
- `ollama==0.1.7` (Ollama client)
- `mlx-lm==0.14.0` (MLX backend, macOS only - in `requirements_local.txt`)
- `pytest==7.4.3` + `pytest-cov` (testing)

**LLM Models**:
- Ollama: `llama3.1:70b` (default), `llama3.1:8b` (fallback)
- MLX: `Meta-Llama-3.1-70B-Instruct-4bit` (macOS native acceleration)

**Infrastructure**:
- Python 3.10+ (virtual environment: `venv_mlx`)
- Docker (multi-stage build: Python 3.11-slim + Ollama)
- Platform Support: Docker (all), MLX (macOS only)

**Additional Dependencies** (Phase 4):
- `Pillow==10.2.0` - Image processing for barcode scanning
- `pyzbar==0.1.9` - Barcode decoding (requires ZBar library: `brew install zbar`)
- `openpyxl==3.1.2` - Excel export for training programs
- `pandas==2.2.0` - Data processing and analysis
- `numpy==1.26.3` - Numerical computations

## Code Organization & Design Patterns

### File Structure (32 source files, 16,459 LOC)

```
src/
├── main.py                      # Streamlit UI (2,186 LOC) - Main application
├── rag_system.py                # Core RAG engine (276 LOC)
├── profile.py                   # User profile management (461 LOC)
│
├── calculations.py              # TDEE, macros, BMR (418 LOC) ✅
│
├── exercise_database.py         # Jeff Nippard Tier List (836 LOC) ✅
├── exercise_selection.py        # Equipment filtering (346 LOC) ✅
├── exercise_alternatives.py     # Location-aware (483 LOC) ✅
├── volume_prescription.py       # MEV/MAV/MRV (362 LOC) ✅
├── progressive_overload.py      # RIR progression (380 LOC) ✅
├── mesocycle_templates.py       # Training splits (439 LOC) ✅
├── program_generator.py         # 6-week programs (411 LOC) ✅
├── program_export.py            # Excel/CSV export (223 LOC) ✅
├── program_manager.py           # Save/load (254 LOC) ✅
│
├── workout_logger.py            # Workout logging (479 LOC) ✅
├── workout_database.py          # Workout DB (487 LOC) ✅
├── workout_models.py            # Data models (330 LOC) ✅
├── workout_coach.py             # AI coaching (438 LOC) ✅
├── autoregulation.py            # RP adjustments (373 LOC) ✅
│
├── food_logger.py               # Food logging (644 LOC) ✅
├── food_models.py               # Data models (430 LOC) ✅
├── meal_templates.py            # One-click meals (663 LOC) ✅
├── food_api_fdc.py              # USDA FDC (343 LOC) ✅
├── food_api_off.py              # Open Food Facts (377 LOC) ✅
├── food_search_integrated.py    # Unified search (258 LOC) ✅
│
├── adaptive_tdee.py             # Adaptive TDEE (478 LOC) ✅
├── tdee_analytics.py            # TDEE analytics (502 LOC) ✅
├── enhanced_tdee_ui.py          # Weekly check-ins (426 LOC) ✅
├── body_measurements.py         # Body measurements (392 LOC) ✅
├── progress_photos.py           # Photo storage (354 LOC) ✅
├── progress_photos_ui.py        # Photo UI (287 LOC) ✅
├── progress_reports.py          # Monthly reports (643 LOC) ✅
│
└── apple_health.py              # Apple Health import (381 LOC) ✅

config/
└── settings.py                  # Centralized configuration

data/
├── pdfs/                        # 28 expert PDFs
├── vectorstore/                 # ChromaDB embeddings (ignored in git)
├── user_profile.json            # Profile storage (1.2 KB)
├── workouts.db                  # SQLite workout logs (28 KB)
├── food_log.db                  # SQLite nutrition logs (49 KB)
└── .env                         # API keys (USDA FDC, etc.)

tests/
├── fixtures/
│   ├── __init__.py              # Test fixture exports
│   └── personas.py              # 5 personas + 4 edge cases (316 LOC)
├── test_profile.py              # Profile CRUD (30+ tests)
├── test_calculations.py         # TDEE/macros (25 tests) ✅
├── test_rag_system.py           # Backend switching
├── test_model_comparison.py     # LLM comparison
├── test_workout_database.py     # Workout DB tests
├── test_workout_models.py       # Workout models
├── test_workout_coach.py        # Coaching logic
└── test_meal_prep_workflow.py  # Meal templates
```

**Key Databases:**
- `workouts.db` - Workout sessions, exercise logs, sets/reps/weight/RIR
- `food_log.db` - Daily meals, food entries, macro totals, templates
- `weights.db` - Daily weight tracking with EWMA trends
- `measurements.db` - Body measurements (13 points)
- `photos.db` - Progress photo metadata
- `vectorstore/` - ChromaDB persistent embeddings (28 PDFs)

### Design Patterns

- **Separation of Concerns**: UI (main.py), Business Logic (rag_system.py, profile.py), Config (settings.py)
- **Dataclasses**: Type-safe data structures (PersonalInfo, Goals, Experience, Schedule, WorkoutSession, Food)
- **Backend Abstraction**: MLXModel and OllamaLLM both implement `_call()` interface
- **Dependency Injection**: Paths and backends configurable at initialization
- **Database Layer**: SQLite with dedicated database classes (workout_database.py, food_logger.py)
- **Transaction Safety**: BEGIN TRANSACTION/COMMIT pattern for data integrity (see food_logger.py)
- **Equipment Presets**: Centralized equipment definitions for reusability
- **Coaching Mindset**: All calculation functions return coaching guidance, not just numbers

### Key Architecture Patterns

**1. Multi-Tier Data Flow**:
```
User Input (Streamlit)
    → Profile/Calculation Layer (profile.py, calculations.py)
    → RAG Validation Layer (rag_system.py queries PDFs)
    → Database Persistence (SQLite: workouts.db, food_log.db)
    → UI Feedback (coaching guidance, charts, recommendations)
```

**2. Dual Food Search Strategy** (src/food_search_integrated.py):
- Priority 1: Local USDA FDC database (400K foods, fast)
- Priority 2: Open Food Facts API (2.8M products, slower)
- Fallback: Manual food entry
- Camera barcode → OFF API lookup → Display nutrition → Log to DB

**3. Program Generation Pipeline** (Phase 3):
```
User Profile (equipment, schedule, experience)
    → Template Selection (mesocycle_templates.py: Upper/Lower, PPL, Full Body)
    → Volume Prescription (volume_prescription.py: MEV/MAV/MRV)
    → Exercise Selection (exercise_database.py: S/A/B tier filtering)
    → Equipment Alternatives (exercise_alternatives.py: location-aware)
    → Progressive Overload (progressive_overload.py: RIR progression)
    → Export (program_export.py: Excel/Google Sheets)
```

**4. Workout Coaching Workflow** (Phase 4):
```
User Logs Workout (sets, reps, weight, RIR)
    → workout_logger.py stores to workouts.db
    → workout_coach.py analyzes performance
    → autoregulation.py applies RP principles
    → Recommendations displayed in UI:
        - "Great session! Add 5 lbs next time"
        - "RIR too low (0-1), reduce weight or take deload"
        - "Volume accumulating, consider deload in 1-2 weeks"
```

**5. Nutrition Tracking Workflow** (Phase 4):
```
User Searches Food
    → food_search_integrated.py queries USDA FDC + OFF
    → User selects food + serving size
    → food_logger.py logs to food_log.db
    → Daily macro totals calculated
    → UI displays progress: "1,847 / 2,100 cal (88%)"
```

**6. Profile-Aware RAG Queries**:
```
User asks: "How much protein do I need?"
    → RAG retrieves general recommendations from RP/Nippard PDFs
    → Calculations layer applies user's weight, goals, phase
    → Response: "For cutting at 210 lbs, RP recommends 1.0-1.2g/lb = 210-252g protein"
```

## Testing Strategy

- **Unit Tests**: Profile CRUD, calculations (TDEE/macros), workout/food models
- **Integration Tests**: Backend switching, document loading, end-to-end RAG queries, database operations
- **Fixtures**: `tests/fixtures/personas.py` - 5 user personas + 4 edge cases for consistent testing
- **Markers**: Use `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit` to separate test categories
- **Coverage**: Run `pytest --cov=src --cov-report=html tests/` for HTML coverage reports
- **Test Data**: All 5 personas (Beginner Ben, Intermediate Ian, Cutting Claire, Recomp Ryan, Minimal Megan) validated
- **Current Test Count**: 80+ tests across 9 test files

## Configuration & Environment

### Environment Variables
- `data/.env` file (read-only, manually updated by developer per global CLAUDE.md)
- Ignored in `.gitignore`
- **API Keys**: USDA FDC API key (for food database, free tier)
- **Optional**: Open Food Facts uses public API (no key needed)

### Git Workflow
- **MANDATORY**: Always create feature branches (see parent CLAUDE.md for branch enforcement rules)
- **Current Branch**: `feat/phase4-tracking-ui`
- **Main Branch**: `main` (protected)
- **Recent Branches**: `feat/phase3-program-generation` (merged), `feat/phase2-user-profile-system` (merged)

### Deployment Frequency Constraint ⚠️ CRITICAL

**Render.com deploys cost time and money. Target: ≤10 deploys per day, with one consolidated GitHub push per deploy cycle.**

**REQUIRED WORKFLOW:**
1. **Test locally FIRST** - Run `./test-checklist.sh` before ANY push to GitHub
2. **Batch commits** - Group related changes into ONE commit when possible
3. **Combine updates before pushing** - Accumulate fixes locally and push/merge once per deploy so Render builds only once
4. **Only push to main when confident** - Feature branches don't trigger deploys
5. **One deploy per feature** - Avoid iterative "fix, push, fix, push" cycles on main

**Cost Impact:**
- Before local-first testing: 150-300 deploys/month ($$$$)
- After local-first testing: 8-12 deploys/month ($) - 96% reduction!

**See `docs/TESTING.md` for detailed local-first workflow.**

### File Ignores
Key items in `.gitignore`:
- `data/vectorstore/`, `data/pdfs/*.pdf` (except specific reference files)
- `venv/`, `venv_mlx/`
- `*.log` (streamlit.log, pdf_processing.log)
- `.DS_Store` (macOS)
- Corrupted file: `thePaleoSolution_FoodMatrix.pdf`

## Solo Developer Context (from global CLAUDE.md)

- **Resources**: Solo developer (Jason), part-time (10-20 hrs/week)
- **Budget**: $0-100/month for tools (bootstrap/self-funded)
- **Timeline**: 6-12 months to MVP, conservative estimates
- **Success Metric**: Break-even is victory, 100 customers is massive success
- **Philosophy**: Incremental value, simple first, test as you go

When proposing features:
1. Ask "How complex should this be?" before implementing
2. Default to simplest version unless told otherwise
3. Estimate in hours of coding time, not dollars
4. Assume part-time development (weeks/months, not days)

## Key Documentation

- **README.md**: Comprehensive setup instructions, project overview
- **VISION.md**: Detailed Phase 2-5 roadmap with Mermaid diagrams
- **SCENARIOS.md**: User personas, use cases, testing strategies for Phases 2-5
- **PROGRAM_TEMPLATES.md**: Catalogs Excel/RTF files for Phase 3 program generation
- **CLAUDE.md** (this file): Development guidance for AI agents

## Common Pitfalls & Gotchas

1. **Corrupted PDF**: `thePaleoSolution_FoodMatrix.pdf` is corrupted - skip it in processing
2. **Backend Switching**: MLX only works on macOS with Apple Silicon - use Ollama for cross-platform
3. **ChromaDB Persistence**: Vectorstore survives restarts - no need to re-embed unless PDFs change
4. **Profile Before Query**: UI requires profile creation before allowing RAG queries
5. **Evidence-Based Only**: Never implement features that hallucinate - always cite PDF sources
6. **Excel Export**: Uses `openpyxl` (already in requirements.txt) for program export
7. **Barcode Scanning**: Requires `pyzbar` + ZBar library (macOS: `brew install zbar`)
8. **Database Transactions**: Always use BEGIN/COMMIT for food_logger.py modifications (see src/food_logger.py:644)
9. **Equipment Constants**: Use `USERS_HOME_GYM` not `JASONS_HOME_GYM` (recent refactoring in exercise_alternatives.py)

## Next Steps: Phase 5 Planning

**Phase 4 is now complete!** All tracking, adaptive TDEE, and analytics features have been delivered.

**Potential Phase 5 Focus Areas:**
1. **Mobile App** - React Native app for iOS/Android
2. **Voice Input** - Voice logging for workouts and meals
3. **Exercise Video Library** - Form demonstrations with AI coaching
4. **Meal Planning** - Weekly meal plans and grocery lists
5. **Enhanced Visualizations** - Interactive charts and progress dashboards
6. **Community Features** - Share programs, tips, progress (optional)
7. **Wearable Integration** - Deeper Apple Health, Fitbit, Whoop integration

**Current Priority**: Consolidate Phase 4 work, gather user feedback, and plan Phase 5 roadmap.

See `VISION.md` for detailed Phase 5 possibilities.
