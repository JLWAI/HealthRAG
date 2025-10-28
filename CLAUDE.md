# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**HealthRAG** is a FREE, local AI-powered health and fitness advisor using Retrieval-Augmented Generation (RAG). Currently in **Phase 2 development** (User Profile & State Management, Week 2). This is a solo developer project, part-time (10-20 hrs/week), with a 3-6 month timeline to complete Phase 2.

**Current Status**:
- Branch: `feat/phase2-user-profile-system`
- Active Milestone: Week 2 - Calculation Engine (TDEE, macros)
- Next Milestone: Week 4 - "Tell me my daily macros based on my stats" working end-to-end

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
Streamlit UI (main.py)
    ↓
RAG System (rag_system.py) ←→ User Profile System (profile.py)
    ↓                              ↓
Dual LLM Backend              JSON Storage
├─ Ollama (Docker)            (user_profile.json)
└─ MLX (macOS)
    ↓
ChromaDB VectorStore
(28 PDFs from RP, Nippard, BFFM)
```

### Core Components

**1. RAG System** (`src/rag_system.py`):
- Dual backend support: Ollama (cross-platform) vs MLX (Apple Silicon native)
- ChromaDB vectorstore with `sentence-transformers/all-MiniLM-L6-v2` embeddings
- Retrieves k=5 most relevant document chunks per query
- **Critical Design Principle**: Grounded responses only - uses document context, never hallucinates
- Source attribution for all responses

**2. User Profile System** (`src/profile.py`):
- JSON storage at `data/user_profile.json`
- Dataclasses: PersonalInfo, Goals, Experience, Schedule
- CRUD operations for profile management
- Designed for Phase 2 Week 2-4: TDEE calculations, macro recommendations

**3. Streamlit UI** (`src/main.py`):
- Chat interface for RAG queries
- Backend/model selection (MLX vs Ollama)
- Profile creation wizard and management (sidebar)
- Session state management

**4. Configuration** (`config/settings.py`):
- Centralized paths, chunking parameters, retrieval settings
- Model endpoints for Ollama and MLX

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
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest tests/test_profile.py      # Profile system tests (30+ tests)
```

**Test Files**:
- `tests/test_profile.py` - Profile CRUD, dataclass validation
- `tests/test_rag_system.py` - Backend switching, document loading
- `tests/test_model_comparison.py` - (newly added)

**pytest.ini Configuration**:
- Markers: `slow`, `integration`, `unit`
- Use markers to separate fast/slow tests

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

### Current Development Phase

**Phase 2: User Profile & State Management (Weeks 1-4)**

Week 1 - **COMPLETED**:
- Profile system, JSON storage, Streamlit UI, CRUD operations, tests

Week 2 - **IN PROGRESS** (Current Focus):
- [ ] Calculation Engine (`src/calculations.py`)
- [ ] TDEE calculation (Mifflin-St Jeor formula)
- [ ] Activity level multipliers
- [ ] Macro calculations (cut/bulk/maintain)
- [ ] Query RAG for formulas from RP/BFFM PDFs
- [ ] Verify calculations against PDF recommendations

Week 3 - **PLANNED**:
- Progress Tracking Database (`src/tracker.py`)
- SQLite database (`data/progress.db`)
- Tables: daily_weights, measurements, workout_logs, nutrition_logs

Week 4 - **MILESTONE**:
- Integration & First Milestone
- Profile-aware RAG queries
- Dashboard view with key stats
- **Target**: "Tell me my daily macros based on my stats" working end-to-end

### Future Phases

**Phase 3** (Weeks 5-9): Program Generation
- Training program generator using Jeff Nippard Tier List
- Nutrition planning
- Excel template parsing (will require `openpyxl`)
- Program export (PDF/Excel)

**Phase 4** (Weeks 10-14): Adaptive Coaching
- Progress analysis, adjustment engine, proactive check-ins

**Phase 5** (Weeks 15+): Polish & Advanced Features
- Voice input, photo tracking, mobile app (React Native)

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
4. **Incremental milestones** - Each week delivers testable value aligned with scenarios

**Current Week 2 Scenario**:
- **Scenario 2**: Calculate TDEE & Macros (Phase 2 - CURRENT FOCUS)
- **Personas to test**: All 5 (Ben, Ian, Claire, Ryan, Megan)
- **Acceptance criteria**: TDEE within 5%, macros in recommended ranges, RAG citations required
- **Expected outputs**: See `SCENARIOS.md` Scenario 2 for detailed expected responses

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

## Code Organization & Design Patterns

### File Structure
```
src/
├── main.py           # Streamlit UI, session state
├── rag_system.py     # Core RAG engine, dual backends
├── profile.py        # User profile management
└── calculations.py   # (Week 2) TDEE, macros - TO BE IMPLEMENTED

config/
└── settings.py       # Centralized configuration

data/
├── pdfs/             # 28 PDFs (ignored in git except specific files)
├── vectorstore/      # ChromaDB (ignored in git)
└── user_profile.json # JSON profile storage

tests/
├── fixtures/
│   ├── __init__.py          # Test fixture exports
│   └── personas.py          # 5 user personas + edge cases for testing
├── test_profile.py          # Profile CRUD tests (30+ cases)
├── test_rag_system.py       # Backend switching, document loading
└── test_model_comparison.py # (newly added)
```

### Design Patterns
- **Separation of Concerns**: UI (main.py), Business Logic (rag_system.py, profile.py), Config (settings.py)
- **Dataclasses**: Type-safe data structures (PersonalInfo, Goals, Experience, Schedule)
- **Backend Abstraction**: MLXModel and OllamaLLM both implement `_call()` interface
- **Dependency Injection**: Paths and backends configurable at initialization

## Testing Strategy

- **Unit Tests**: Profile CRUD, dataclass validation, calculations (Week 2)
- **Integration Tests**: Backend switching, document loading, end-to-end RAG queries
- **Fixtures**: Temporary paths, sample data (`tests/conftest.py`)
- **Markers**: Use `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit` to separate test categories
- **Coverage**: Run `pytest --cov=src tests/` to ensure new features are tested

## Configuration & Environment

### Environment Variables
- `.env` file (read-only, manually updated by developer per global CLAUDE.md)
- Ignored in `.gitignore`
- No API keys needed (100% local)

### Git Workflow
- **MANDATORY**: Always create feature branches (see parent CLAUDE.md for branch enforcement rules)
- **Current Branch**: `feat/phase2-user-profile-system`
- **Main Branch**: `main` (protected)

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
6. **Excel Parsing**: Phase 3 will require `openpyxl` (not yet in requirements.txt)
7. **RTF Conversion**: Jeff Nippard Tier List needs conversion to JSON/CSV for Phase 3

## Quick Reference: Week 2 Focus

**Current Task**: Implement Calculation Engine (`src/calculations.py`)

**Requirements**:
1. TDEE calculation using Mifflin-St Jeor formula
2. Activity level multipliers (sedentary, lightly active, moderately active, very active, extremely active)
3. Macro calculations for cut/bulk/maintain/recomp goals
4. Query RAG system to retrieve formulas from RP Diet 2.0 and BFFM PDFs
5. Verify calculations against PDF recommendations
6. Write pytest tests for all calculation functions
7. Integrate with profile system (read PersonalInfo, Goals)

**Success Criteria**:
- Unit tests pass for all calculation functions
- Manual testing with real profile data
- RAG queries return relevant formulas with source attribution
- Calculated values match PDF recommendations (within 5% tolerance)
