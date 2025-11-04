# HealthRAG: Diet & Exercise Tracking Platform
## Project Overview & Planning Summary

---

## 🎯 Vision

Transform HealthRAG from a document Q&A system into a **comprehensive nutrition and exercise tracking platform** inspired by MacroFactor, leveraging your personal fitness PDFs and exercise knowledge base.

**Core Philosophy:**
- 🔒 **Privacy-first**: Local-first architecture with optional cloud sync
- 🧠 **AI-Powered**: RAG system for exercise coaching, adaptive algorithms for nutrition
- 📚 **Knowledge-based**: Built on your curated fitness and nutrition documents
- 💰 **Free & Open**: No subscriptions, self-hostable, open source

---

## 📊 Current State

**What Exists:**
- ✅ RAG system with ChromaDB for document Q&A
- ✅ Streamlit web UI
- ✅ Ollama/MLX LLM integration (local inference)
- ✅ PDF processing pipeline
- ✅ Docker deployment setup
- ✅ 1 reference PDF: "The Ultimate Guide to Body Recomposition"
- ✅ 3 workout Excel tracking sheets (RP Fundamentals, Min-Max 4x/5x)

**What's Missing:**
- ❌ Nutrition tracking database
- ❌ Food search/logging system
- ❌ Exercise database and logging
- ❌ Weight tracking
- ❌ Analytics dashboard
- ❌ MacroFactor-style adaptive algorithm

---

## 🎯 Target Features (MacroFactor-Inspired)

### Nutrition Tracking
- [ ] Food database (USDA FoodData Central integration)
- [ ] Barcode scanning (OpenFoodFacts API)
- [ ] Fast food logging (minimal taps)
- [ ] Recipe builder and importer
- [ ] Meal templates and favorites
- [ ] Micronutrient tracking
- [ ] Quick-add macros

### Adaptive Intelligence
- [ ] TDEE calculation and tracking
- [ ] Adaptive calorie/macro recommendations
- [ ] Weight trend analysis (moving averages)
- [ ] Dynamic goal adjustments
- [ ] AI-powered food logging (photo, voice, text)

### Exercise Tracking
- [ ] Exercise library from your PDFs (S Tier Exercises, Jeff Nippard)
- [ ] Equipment-based filtering (Home vs Planet Fitness)
- [ ] Workout program templates (RP, Min-Max, Fundamentals)
- [ ] Workout logging (sets, reps, weight, RPE)
- [ ] Progressive overload tracking
- [ ] AI exercise recommendations
- [ ] RAG-based form coaching

### Analytics
- [ ] Customizable dashboard
- [ ] Weight trends and projections
- [ ] Macro compliance charts
- [ ] Training volume tracking
- [ ] Weekly/monthly summaries
- [ ] Progress photos (optional)

---

## 🏗️ Development Stages

### **MVP (Weeks 1-8): Core Tracking**
**Goal**: Basic nutrition and exercise tracking with local SQLite database

**Features:**
- Manual food entry and search (USDA API)
- Daily macro totals and targets
- Weight logging with trends
- Exercise library (200+ exercises from your PDFs)
- Workout logging (sets, reps, weight)
- Basic analytics dashboard

**Tech Stack:**
- Frontend: Streamlit (extend existing)
- Backend: FastAPI (new)
- Database: SQLite (local)
- Food API: USDA FoodData Central

**Timeline**: 8 weeks
**Deliverable**: Fully functional local tracking app

---

### **STAGE 2 (Weeks 9-14): Enhanced Tracking**
**Goal**: Add barcode scanning, recipes, programs, and advanced analytics

**Features:**
- Barcode scanning (OpenFoodFacts)
- Recipe builder and storage
- Pre-built workout programs (from your PDFs)
- Advanced analytics and charts
- Meal templates and copy functionality
- Micronutrient tracking

**Timeline**: 6 weeks

---

### **STAGE 3 (Weeks 15-20): Adaptive Intelligence**
**Goal**: MacroFactor-style adaptive algorithm and AI features

**Features:**
- TDEE calculation and adaptive recommendations
- AI-powered food logging (photo/voice/text)
- AI exercise program generation
- Exercise substitution suggestions
- RAG-based exercise coaching
- Confidence scoring for recommendations

**Timeline**: 6 weeks

---

### **STAGE 4 (Weeks 21-28): Platform & Deployment**
**Goal**: Mobile-responsive UI, cloud hosting, production features

**Features:**
- Mobile-responsive web app (React or optimized Streamlit)
- User authentication (multi-user support)
- Cloud deployment (Railway/Fly.io/DigitalOcean)
- PWA with offline mode
- Data import/export (MyFitnessPal, Cronometer)
- PDF reports

**Timeline**: 8 weeks

---

## 💻 Technology Stack

### Current (Existing)
```
Frontend:    Streamlit 1.29.0
LLM:         Ollama (llama3.1:70b) / MLX
Vector DB:   ChromaDB 0.4.22
Embeddings:  sentence-transformers (all-MiniLM-L6-v2)
Framework:   LangChain 0.1.0
Docs:        PyPDF 4.0.1
Runtime:     Python 3.11
```

### New Additions (MVP)
```
Backend:     FastAPI 0.110.0
ORM:         SQLAlchemy 2.0
Migrations:  Alembic
Database:    SQLite 3.x (local) → PostgreSQL 14+ (hosted)
Food API:    USDA FoodData Central
Charts:      Plotly / Matplotlib
Testing:     pytest (existing)
```

### Future Additions (Stage 2-4)
```
Barcode:     OpenFoodFacts API
AI:          OpenAI API (optional, for food logging)
Frontend:    React + TypeScript (optional migration)
Hosting:     Railway / Fly.io / DigitalOcean
Auth:        JWT tokens
PWA:         Service workers, offline sync
```

---

## 🗄️ Database Schema

**Core Tables:**
- `users` - User accounts
- `user_profiles` - Goals, targets, preferences
- `foods` - Food database (USDA + user-created)
- `food_logs` - Daily food diary entries
- `recipes` - User recipes
- `weight_logs` - Daily weight tracking
- `exercises` - Exercise library
- `workout_programs` - Pre-built programs
- `workout_sessions` - Workout logs
- `workout_sets` - Individual set performance
- `tdee_calculations` - Adaptive algorithm results
- `weekly_summaries` - Pre-calculated analytics

**See**: `docs/database_schema.md` for full schema

---

## 🔌 API Design

**Nutrition Endpoints:**
```
GET  /api/v1/foods/search?q=chicken
GET  /api/v1/foods/{id}
POST /api/v1/foods              (create custom food)
POST /api/v1/food-logs          (log food)
GET  /api/v1/food-logs?date=YYYY-MM-DD
POST /api/v1/recipes            (create recipe)
GET  /api/v1/weight
POST /api/v1/weight
```

**Exercise Endpoints:**
```
GET  /api/v1/exercises/search?muscle_group=chest&gym=home
GET  /api/v1/exercises/{id}
GET  /api/v1/programs           (list programs)
POST /api/v1/workouts/sessions  (start workout)
POST /api/v1/workouts/sets      (log set)
GET  /api/v1/workouts/sessions  (history)
```

**Analytics Endpoints:**
```
GET  /api/v1/dashboard/summary
GET  /api/v1/analytics/tdee
GET  /api/v1/analytics/weight-trend
GET  /api/v1/analytics/training-volume
```

**AI Endpoints (Stage 3):**
```
POST /api/v1/ai/log-food-image
POST /api/v1/ai/log-food-text
GET  /api/v1/ai/recommend-workout
```

**RAG Endpoint (Existing):**
```
POST /api/v1/rag/query
```

**See**: `docs/api_design.md` for full API specification

---

## 🍔 USDA FoodData Central Integration

**API**: https://fdc.nal.usda.gov/
**Free**: Yes, with API key
**Rate Limit**: 1000 requests/hour
**Database Size**: 400,000+ foods

**Strategy:**
1. **Phase 1 (MVP)**: Direct API calls with caching
2. **Phase 2**: Pre-populate top 1000 foods locally
3. **Phase 3**: Hybrid (popular foods cached, rare foods fetched)

**Barcode Lookup**: OpenFoodFacts API (free, crowdsourced)

**See**: `docs/usda_integration.md` for implementation details

---

## 🏋️ Exercise Data Structure

**Exercise Schema:**
```json
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
  "instructions": "Lie on bench, grip bar...",
  "form_cues": "Retract scapula, arch lower back...",
  "data_source": "s_tier_exercises"
}
```

**Data Sources:**
- S Tier Exercises.rtf → Tier ratings, top exercises per body part
- Jeff Nippard Tier List → Tier ratings, exercise rankings
- Gym equipment info → Equipment availability tagging
- RP/Fundamentals PDFs → Program templates, exercise instructions

**Filtering:**
- By muscle group (chest, back, legs, shoulders, arms, core)
- By equipment (barbell, dumbbell, cable, bodyweight, machine)
- By gym location (home, planet_fitness)
- By tier rating (S, A, B, C)
- By difficulty (beginner, intermediate, advanced)

---

## 🚀 Deployment Options

### Option 1: Local Only (Current)
**Pros**: Free, maximum privacy, fast
**Cons**: Single device, no mobile
**Cost**: $0/month
**Best for**: Personal use, maximum privacy

### Option 2: Self-Hosted VPS
**Pros**: Access anywhere, your data/server
**Cons**: Requires server management
**Cost**: $5-12/month (Hetzner, DigitalOcean, Linode)
**Best for**: Tech-savvy users, multiple devices

### Option 3: Managed Platform (PaaS)
**Pros**: Easy deployment, auto-scaling
**Cons**: Higher cost, vendor lock-in
**Cost**: $5-20/month (Railway, Render, Fly.io)
**Best for**: Ease of use, no server management

### Option 4: Hybrid (Local + Cloud Sync)
**Pros**: Best of both worlds
**Cons**: Complex setup, sync conflicts
**Cost**: $5-10/month (minimal server)
**Best for**: Primary local use, mobile backup access

**Recommended**: Start with **Option 1 (Local)** for MVP, add **Option 4 (Hybrid)** in Stage 3-4

---

## 📁 New Project Structure

```
HealthRAG/
├── src/
│   ├── api/                     # NEW: FastAPI backend
│   │   ├── main.py
│   │   ├── deps.py
│   │   └── routers/
│   │       ├── foods.py
│   │       ├── nutrition.py
│   │       ├── exercises.py
│   │       ├── workouts.py
│   │       └── analytics.py
│   ├── models/                  # NEW: SQLAlchemy models
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── nutrition.py
│   │   ├── exercise.py
│   │   └── workout.py
│   ├── schemas/                 # NEW: Pydantic schemas
│   │   ├── food.py
│   │   ├── workout.py
│   │   └── user.py
│   ├── services/                # NEW: Business logic
│   │   ├── usda_service.py
│   │   ├── nutrition_service.py
│   │   ├── workout_service.py
│   │   └── barcode_service.py
│   ├── main.py                  # EXISTING: Streamlit UI
│   ├── rag_system.py            # EXISTING: RAG implementation
│   └── database.py              # NEW: DB connection
├── alembic/                     # NEW: Database migrations
│   └── versions/
├── data/
│   ├── pdfs/                    # EXISTING: Fitness PDFs
│   ├── vectorstore/             # EXISTING: ChromaDB
│   └── health.db                # NEW: SQLite database
├── docs/                        # NEW: Documentation
│   ├── PROJECT_OVERVIEW.md      # This file
│   ├── database_schema.md
│   ├── api_design.md
│   ├── usda_integration.md
│   └── implementation_roadmap.md
├── tests/                       # EXISTING: Tests
│   ├── test_rag_system.py       # EXISTING
│   ├── test_api/                # NEW
│   └── test_services/           # NEW
├── scripts/                     # NEW: Utility scripts
│   ├── populate_exercises.py
│   └── populate_popular_foods.py
├── config/
│   └── settings.py              # EXISTING: Config
├── requirements.txt             # EXISTING: Dependencies
└── alembic.ini                  # NEW: Alembic config
```

---

## ✅ MVP Success Criteria

### Functional Requirements
- ✅ User can search for foods (USDA database)
- ✅ User can log food and see daily macro totals
- ✅ User can set macro targets (calories, protein, carbs, fat)
- ✅ User can log weight and see trend chart
- ✅ User can search exercises filtered by equipment/gym
- ✅ User can log workout sets (exercise, weight, reps)
- ✅ User can view workout history and personal bests
- ✅ Dashboard shows weekly summary

### Technical Requirements
- ✅ Works 100% offline after initial setup
- ✅ Response time <1 second for all operations
- ✅ Database can handle 1+ year of daily tracking
- ✅ Test coverage >80%
- ✅ Zero data loss (proper database transactions)

### User Experience
- ✅ Food logging takes <30 seconds
- ✅ Workout logging is quick and intuitive
- ✅ UI is clean and uncluttered
- ✅ Navigation is obvious
- ✅ Help text explains features

---

## 🎓 Learning Resources

**FastAPI:**
- Official tutorial: https://fastapi.tiangolo.com/tutorial/
- SQLAlchemy + FastAPI: https://fastapi.tiangolo.com/tutorial/sql-databases/

**SQLAlchemy:**
- Official docs: https://docs.sqlalchemy.org/
- Alembic migrations: https://alembic.sqlalchemy.org/

**USDA API:**
- API guide: https://fdc.nal.usda.gov/api-guide.html
- Nutrient database: https://fdc.nal.usda.gov/

**MacroFactor Research:**
- Algorithm explanation: https://help.macrofactorapp.com/
- Reddit discussions: r/MacroFactor

---

## ⚠️ Open Questions & Decisions Needed

### Critical (Before Starting MVP)

1. **Exercise Data Content**
   - Can you share or describe the content of "S Tier Exercises.rtf"?
   - What exercises are listed per body part?
   - What's the format?

2. **Gym Equipment Lists**
   - What equipment is available at your home gym?
   - What equipment is available at Planet Fitness?
   - Are there equipment restrictions? (e.g., no barbells at PF)

3. **USDA API Key**
   - Need to sign up at: https://fdc.nal.usda.gov/api-key-signup.html
   - Takes 1-2 business days

### Important (Before Stage 2)

4. **Deployment Preference**
   - Local only? Self-hosted? Managed platform? Hybrid?
   - See deployment options comparison above

5. **UI Framework**
   - Stick with Streamlit for entire project?
   - Or migrate to React later for better mobile UX?

6. **AI Features Priority**
   - Willing to pay for OpenAI API (~$10-20/month)?
   - Or prefer local models only (free but less accurate)?

### Nice to Have (Before Stage 3)

7. **Workout Programs to Include**
   - Which programs from your PDFs should be pre-loaded?
   - RP Fundamentals? Min-Max? Others?

8. **Timeline Flexibility**
   - Is 8 weeks to MVP reasonable?
   - Need faster/slower pace?

---

## 🚦 Next Steps

### Immediate (This Week)
1. ✅ Review this planning documentation
2. ⏭️ Answer the open questions above (especially exercise data)
3. ⏭️ Sign up for USDA API key
4. ⏭️ Decide on deployment strategy
5. ⏭️ Approve MVP scope and timeline

### Week 1 (If Approved)
1. Set up FastAPI project structure
2. Create SQLAlchemy models
3. Set up Alembic migrations
4. Create initial database schema
5. Write basic CRUD tests

### Week 2
1. Integrate USDA FoodData Central API
2. Implement food search endpoint
3. Create food database caching
4. Populate top 1000 foods
5. Test food search functionality

---

## 📈 Timeline Summary

| Stage | Duration | End Date (approx) | Deliverable |
|-------|----------|-------------------|-------------|
| **MVP** | 8 weeks | ~8 weeks from start | Core tracking (local) |
| **Stage 2** | 6 weeks | ~14 weeks | Enhanced features |
| **Stage 3** | 6 weeks | ~20 weeks | AI & adaptive |
| **Stage 4** | 8 weeks | ~28 weeks | Hosted & mobile |
| **Total** | 22-28 weeks | ~5-7 months | Production-ready platform |

**Note**: Timeline is flexible based on your availability and priorities.

---

## 📚 Documentation Files Created

1. **`PROJECT_OVERVIEW.md`** (this file) - High-level summary
2. **`database_schema.md`** - Complete database design
3. **`api_design.md`** - REST API specification
4. **`usda_integration.md`** - Food API integration details
5. **`implementation_roadmap.md`** - Detailed week-by-week plan

---

## 💬 Questions?

**Ready to start?** Let me know:
1. Your answers to the open questions
2. Any adjustments to the plan
3. When you want to begin implementation

**Need clarification?** Ask about:
- Any technical decisions
- Timeline adjustments
- Feature priorities
- Deployment options

---

## 🎉 Let's Build This!

Your HealthRAG project has a solid foundation. By adding nutrition and exercise tracking with MacroFactor-inspired features, you'll have a powerful, privacy-first health platform that leverages your curated fitness knowledge base.

**The best part?** Everything is open source, self-hostable, and works 100% offline. No subscriptions, no vendor lock-in, complete control over your health data.

**Let's make it happen!** 💪
