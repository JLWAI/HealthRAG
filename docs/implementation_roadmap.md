# HealthRAG Implementation Roadmap

## Overview
Transform HealthRAG from a document Q&A system into a comprehensive nutrition and exercise tracking app with MacroFactor-inspired features.

**Total Timeline**: ~22-28 weeks (5.5-7 months)

---

## MVP (Weeks 1-8): Core Tracking

**Goal**: Basic nutrition and exercise tracking with local SQLite database

### Week 1-2: Project Setup & Architecture

**Tasks:**
- [ ] Review and understand current codebase
- [ ] Set up FastAPI project structure
- [ ] Configure SQLAlchemy with SQLite
- [ ] Create Alembic migrations setup
- [ ] Implement database models (users, foods, food_logs, exercises, workouts)
- [ ] Write initial migration scripts
- [ ] Set up pytest for new features
- [ ] Update documentation

**Deliverables:**
- FastAPI app skeleton (`src/api/`)
- Database models (`src/models/`)
- Initial schema migration
- Updated project structure

**File Structure:**
```
src/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── deps.py          # Dependencies (DB session, etc.)
│   └── routers/
│       ├── __init__.py
│       ├── foods.py
│       ├── nutrition.py
│       ├── exercises.py
│       └── workouts.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── food.py
│   ├── nutrition.py
│   ├── exercise.py
│   └── workout.py
├── schemas/            # Pydantic models
│   ├── __init__.py
│   ├── food.py
│   └── workout.py
├── services/
│   ├── __init__.py
│   ├── usda_service.py
│   └── nutrition_service.py
├── database.py         # DB connection
└── main.py             # Streamlit UI
```

---

### Week 3-4: USDA Integration & Food Database

**Tasks:**
- [ ] Sign up for USDA API key
- [ ] Implement `USDAService` class
- [ ] Create food search endpoint (`GET /api/v1/foods/search`)
- [ ] Create food details endpoint (`GET /api/v1/foods/{id}`)
- [ ] Implement API response caching in SQLite
- [ ] Parse USDA nutrients to our schema
- [ ] Create script to populate top 1000 foods
- [ ] Add error handling and rate limiting
- [ ] Write unit tests for USDA service
- [ ] Test with various food searches

**Deliverables:**
- Working USDA FoodData Central integration
- Food search API endpoint
- Cached food database (1000+ foods)
- Test coverage >80%

**API Endpoints Implemented:**
```
GET  /api/v1/foods/search?q=chicken
GET  /api/v1/foods/{food_id}
POST /api/v1/foods          (custom food creation)
```

---

### Week 5: Nutrition Logging

**Tasks:**
- [ ] Implement food logging endpoints
  - [ ] `POST /api/v1/food-logs` (log food)
  - [ ] `GET /api/v1/food-logs?date=YYYY-MM-DD` (get daily log)
  - [ ] `PUT /api/v1/food-logs/{id}` (update entry)
  - [ ] `DELETE /api/v1/food-logs/{id}` (delete entry)
- [ ] Implement quick-add macros (no food reference)
- [ ] Create daily totals calculation
- [ ] Add meal type filtering (breakfast, lunch, dinner, snack)
- [ ] Implement recent/favorite foods tracking
- [ ] Write API tests

**Deliverables:**
- Complete food logging API
- Daily macro totals calculation
- Recent foods functionality

---

### Week 6: Nutrition UI (Streamlit)

**Tasks:**
- [ ] Create food search UI component
- [ ] Create food logging form
- [ ] Build daily food diary view
- [ ] Display daily macro totals vs. target
- [ ] Add progress bars for macros
- [ ] Implement quick-add macros UI
- [ ] Add meal type selector
- [ ] Create "copy from yesterday" functionality
- [ ] Add delete/edit food log entries
- [ ] Style UI to be clean and usable

**Deliverables:**
- Functional nutrition tracking UI
- Food search and logging workflow
- Daily macro dashboard

**UI Pages:**
```
📊 Dashboard (new default page)
🍽️ Log Food (search, recent foods, quick add)
📖 Food Diary (today's log, edit/delete)
⚖️ Weight Log
🏋️ Workouts
💬 Ask HealthRAG (existing RAG system)
⚙️ Settings
```

---

### Week 7: Weight Tracking & Exercise Library

**Weight Tracking:**
- [ ] Implement weight logging endpoints
  - [ ] `POST /api/v1/weight` (log weight)
  - [ ] `GET /api/v1/weight` (get history)
- [ ] Create weight trends visualization
- [ ] Implement moving average calculation (7-day)
- [ ] Build weight logging UI

**Exercise Library:**
- [ ] Parse S Tier Exercises document → Create exercises JSON
- [ ] Parse Jeff Nippard Tier List → Add tier ratings
- [ ] Parse gym equipment info → Tag exercises
- [ ] Create exercise database seed script
- [ ] Implement exercise search endpoint
- [ ] Add exercise filtering (muscle group, equipment, gym, tier)
- [ ] Write tests for exercise queries

**Deliverables:**
- Weight logging API and UI
- Exercise database populated (200+ exercises)
- Exercise search functionality

---

### Week 8: Workout Logging

**Tasks:**
- [ ] Implement workout session endpoints
  - [ ] `POST /api/v1/workouts/sessions` (start workout)
  - [ ] `POST /api/v1/workouts/sets` (log set)
  - [ ] `PUT /api/v1/workouts/sessions/{id}/complete` (finish workout)
  - [ ] `GET /api/v1/workouts/sessions` (history)
- [ ] Implement exercise performance history
- [ ] Create workout logging UI
  - [ ] Exercise selection (filtered by gym)
  - [ ] Set logging form (weight, reps, RPE)
  - [ ] Timer for rest periods
  - [ ] Session summary
- [ ] Build workout history view
- [ ] Add personal best tracking

**Deliverables:**
- Complete workout logging system
- Exercise performance tracking
- Workout history view

**MVP COMPLETE** ✅
- Nutrition tracking ✅
- Exercise tracking ✅
- Weight tracking ✅
- Basic analytics ✅

---

## STAGE 2 (Weeks 9-14): Enhanced Tracking

**Goal**: Add barcode scanning, recipes, advanced filtering, and analytics

### Week 9-10: Barcode Scanning & Recipe Builder

**Barcode Scanning:**
- [ ] Integrate OpenFoodFacts API
- [ ] Implement barcode lookup endpoint
- [ ] Create barcode service with caching
- [ ] Add barcode to foods table
- [ ] Test with various UPC/EAN codes

**Recipe Builder:**
- [ ] Implement recipe CRUD endpoints
- [ ] Create recipe ingredient management
- [ ] Calculate recipe nutritional totals
- [ ] Build recipe creation UI
- [ ] Add "log recipe" functionality
- [ ] Implement recipe search/favorites

**Deliverables:**
- Barcode lookup working (via API)
- Recipe creation and logging
- Recipe database

---

### Week 11: Workout Programs

**Tasks:**
- [ ] Parse workout program PDFs (RP Fundamentals, Min-Max, etc.)
- [ ] Create program database seed data
- [ ] Implement program endpoints
  - [ ] `GET /api/v1/programs` (list programs)
  - [ ] `GET /api/v1/programs/{id}` (program details)
  - [ ] `POST /api/v1/programs/{id}/activate` (set active)
- [ ] Build program selection UI
- [ ] Create program day viewer
- [ ] Add "start workout from program" flow
- [ ] Implement program progression tracking

**Deliverables:**
- Pre-built workout programs loaded
- Program-based workout tracking
- Progression tracking

**Programs to Include:**
- RP Fundamentals Hypertrophy
- Min-Max Program 4x
- Min-Max Program 5x
- User custom programs

---

### Week 12: Advanced Analytics

**Tasks:**
- [ ] Implement weekly summary calculations
- [ ] Create dashboard endpoints
  - [ ] `GET /api/v1/dashboard/summary`
  - [ ] `GET /api/v1/analytics/weight-trend`
  - [ ] `GET /api/v1/analytics/macros-compliance`
  - [ ] `GET /api/v1/analytics/training-volume`
- [ ] Build dashboard UI with charts
  - [ ] Weight trend chart (last 30 days)
  - [ ] Macro compliance chart
  - [ ] Training volume per muscle group
  - [ ] Weekly summaries
- [ ] Add data export (CSV)

**Deliverables:**
- Comprehensive analytics dashboard
- Charts and visualizations
- Data export functionality

---

### Week 13-14: Meal Planning & Templates

**Tasks:**
- [ ] Implement meal templates
- [ ] Create "copy meal" functionality
- [ ] Add "copy entire day" feature
- [ ] Build meal planning UI
- [ ] Create favorite meals
- [ ] Implement meal prep mode (log same meal multiple days)
- [ ] Add micronutrient tracking
- [ ] Create micronutrient goals and warnings

**Deliverables:**
- Meal templates and favorites
- Copy meal/day functionality
- Micronutrient tracking

**STAGE 2 COMPLETE** ✅

---

## STAGE 3 (Weeks 15-20): Adaptive Intelligence

**Goal**: MacroFactor-style adaptive algorithm and AI-powered features

### Week 15-16: TDEE Algorithm & Adaptive Recommendations

**Tasks:**
- [ ] Research MacroFactor's adaptive algorithm
- [ ] Implement TDEE calculation logic
  - [ ] Collect 14-day rolling average data
  - [ ] Calculate weight change rate
  - [ ] Estimate TDEE from intake and weight change
  - [ ] Adjust for activity level
- [ ] Create recommendation engine
  - [ ] Determine if on track
  - [ ] Suggest calorie adjustments
  - [ ] Recommend macro splits
- [ ] Implement confidence scoring
- [ ] Build recommendation UI
- [ ] Create algorithm explanation page

**Algorithm Overview:**
```python
# Simplified TDEE calculation
avg_intake = mean(last_14_days_calories)
avg_weight_change = (current_weight - weight_14_days_ago) / 14  # kg/day
expected_rate = (target_deficit_or_surplus) / 7700  # kcal to kg

# If weight change differs from expected, adjust TDEE
tdee_adjustment = (avg_weight_change - expected_rate) * 7700
new_tdee = current_tdee + tdee_adjustment

# Confidence based on data quality
confidence = min(days_logged / 14, weight_logs / 14)
```

**Deliverables:**
- Working TDEE calculation
- Adaptive calorie recommendations
- Confidence scoring
- Explanation UI

---

### Week 17-18: AI-Powered Food Logging

**Option A: OpenAI Vision API** (Easier, costs $)
- [ ] Integrate OpenAI Vision API
- [ ] Implement image-based food detection
- [ ] Implement natural language food entry
- [ ] Create UI for photo upload
- [ ] Add voice input (speech-to-text)
- [ ] Fine-tune prompts for accuracy
- [ ] Add user confirmation flow

**Option B: Local Model** (Harder, free)
- [ ] Research open-source food detection models
- [ ] Implement CLIP or YOLOv8 food detection
- [ ] Create serving size estimation
- [ ] Optimize for local inference
- [ ] Build image upload UI

**Deliverables:**
- AI-powered food logging
- Photo-based logging
- Natural language food entry
- Voice input

**Endpoints:**
```
POST /api/v1/ai/log-food-image
POST /api/v1/ai/log-food-text
```

---

### Week 19-20: AI Exercise Recommendations

**Tasks:**
- [ ] Integrate RAG system with exercise database
- [ ] Implement program generation logic
  - [ ] Based on available equipment
  - [ ] Based on training frequency
  - [ ] Based on experience level
  - [ ] Using S Tier exercises preferentially
- [ ] Create exercise substitution recommendations
- [ ] Build progressive overload suggestions
- [ ] Implement form cue retrieval from PDFs
- [ ] Create AI workout coach UI
- [ ] Add "Ask about exercise" chat interface

**Features:**
- "Generate workout program for me"
- "Suggest alternative for barbell bench press"
- "How do I improve my squat form?" (RAG query)
- "What's the best exercise for rear delts at Planet Fitness?"

**Deliverables:**
- AI-powered program generation
- Exercise substitutions
- RAG-based exercise coaching

**STAGE 3 COMPLETE** ✅

---

## STAGE 4 (Weeks 21-28): Platform & Deployment

**Goal**: Mobile-responsive UI, cloud hosting, and production features

### Week 21-22: React Web App (Optional)

**If staying with Streamlit:**
- [ ] Optimize Streamlit UI for mobile
- [ ] Add responsive CSS
- [ ] Improve navigation
- [ ] Add keyboard shortcuts
- [ ] Polish UI/UX

**If migrating to React:**
- [ ] Set up React + TypeScript + Vite
- [ ] Install Tailwind CSS
- [ ] Build component library
- [ ] Create responsive layouts
- [ ] Implement all views from Streamlit
- [ ] Add state management (Zustand)
- [ ] Connect to FastAPI backend

**Deliverables:**
- Mobile-responsive web app
- Polished UI/UX

---

### Week 23: Authentication & Multi-User (for Hosted)

**Tasks:**
- [ ] Implement JWT authentication
- [ ] Create user registration endpoint
- [ ] Create login/logout endpoints
- [ ] Add password hashing (bcrypt)
- [ ] Implement refresh tokens
- [ ] Add authentication middleware
- [ ] Update all endpoints to use user context
- [ ] Create user settings page
- [ ] Add password reset flow

**Deliverables:**
- Secure authentication system
- Multi-user support
- User settings

---

### Week 24: Cloud Deployment Setup

**Tasks:**
- [ ] Choose hosting provider (Railway, Fly.io, DigitalOcean)
- [ ] Set up PostgreSQL database
- [ ] Update SQLAlchemy for PostgreSQL
- [ ] Create production environment config
- [ ] Set up environment variables
- [ ] Configure CI/CD (GitHub Actions)
- [ ] Set up SSL/HTTPS
- [ ] Configure domain name
- [ ] Create backup strategy

**Deliverables:**
- Production environment
- Database migration from SQLite to PostgreSQL
- CI/CD pipeline

---

### Week 25: Testing & Bug Fixes

**Tasks:**
- [ ] Write comprehensive integration tests
- [ ] Test all user flows end-to-end
- [ ] Load testing (simulate multiple users)
- [ ] Fix critical bugs
- [ ] Optimize slow queries
- [ ] Add database indexes where needed
- [ ] Security audit
- [ ] Dependency updates

**Deliverables:**
- Test coverage >90%
- Performance optimizations
- Bug-free experience

---

### Week 26: Progressive Web App (PWA) Features

**Tasks:**
- [ ] Add service worker for offline mode
- [ ] Implement local data sync
- [ ] Add install prompt
- [ ] Create app icons and manifest
- [ ] Implement push notifications (optional)
- [ ] Add background sync for food logs
- [ ] Test offline functionality

**Deliverables:**
- Installable PWA
- Offline mode
- Local data persistence

---

### Week 27: Data Import/Export & Migrations

**Tasks:**
- [ ] Implement MyFitnessPal import
- [ ] Implement Cronometer import
- [ ] Create data export (CSV, JSON)
- [ ] Build PDF report generation
- [ ] Create data migration tools
- [ ] Add data backup/restore
- [ ] Implement account deletion

**Deliverables:**
- Import from other apps
- Comprehensive export options
- PDF reports

---

### Week 28: Documentation & Launch

**Tasks:**
- [ ] Write user guide
- [ ] Create video tutorials
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Write deployment guide
- [ ] Create contributing guidelines
- [ ] Set up issue templates
- [ ] Prepare launch announcement
- [ ] Beta testing with friends/family

**Deliverables:**
- Complete documentation
- Launch-ready app
- Beta feedback incorporated

**STAGE 4 COMPLETE** ✅

---

## Deployment Options Comparison

### Option 1: Local Only (Current)

**Pros:**
- Free forever
- Maximum privacy
- Fast (no network)
- Complete control

**Cons:**
- Single device only
- No mobile access
- Manual backups
- Harder to share

**Best for:** Personal use, maximum privacy

**Cost:** $0/month

---

### Option 2: Self-Hosted (VPS)

**Pros:**
- Access anywhere
- Your data, your server
- One-time setup
- Mobile friendly

**Cons:**
- Requires server management
- Ongoing cost
- Security responsibility

**Best for:** Tech-savvy users, multiple devices

**Recommended Providers:**
- **DigitalOcean Droplet**: $12/month (2GB RAM)
- **Hetzner Cloud**: €5/month (2GB RAM)
- **Linode**: $12/month (2GB RAM)

**Setup:**
```bash
# Docker Compose on VPS
version: '3.8'
services:
  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  web:
    build: ./web
    ports:
      - "80:80"
      - "443:443"
```

**Cost:** $5-12/month

---

### Option 3: Managed Platform (PaaS)

**Pros:**
- Easy deployment
- Auto-scaling
- Built-in backups
- SSL included

**Cons:**
- Higher cost
- Less control
- Vendor lock-in

**Best for:** Ease of use, no server management

**Recommended Platforms:**
- **Railway**: ~$5-20/month
- **Render**: ~$7-21/month
- **Fly.io**: ~$0-20/month (generous free tier)

**Cost:** $0-20/month

---

### Option 4: Hybrid (Local + Cloud Sync)

**Pros:**
- Primary data local
- Cloud backup
- Works offline
- Access from mobile

**Cons:**
- Complex setup
- Sync conflicts possible

**Best for:** Best of both worlds

**Architecture:**
```
Local SQLite (primary) ← sync → PostgreSQL (cloud backup)
                                      ↓
                                Mobile/Web App
```

**Cost:** $5-10/month (minimal server for sync)

---

## Tech Stack Final Recommendation

### MVP (Weeks 1-8)
```
Frontend:  Streamlit (extend existing)
Backend:   FastAPI (new)
Database:  SQLite (local)
Vector DB: ChromaDB (existing)
LLM:       Ollama (existing)
Food API:  USDA FoodData Central
```

### Stage 2-3 (Weeks 9-20)
```
Same as MVP, plus:
Barcode:   OpenFoodFacts API
AI:        OpenAI API (optional, for food logging)
Analytics: Matplotlib/Plotly charts
```

### Stage 4 (Weeks 21-28)
```
Frontend:  React + TypeScript (optional migration)
Backend:   FastAPI (same)
Database:  PostgreSQL (hosted)
Hosting:   Railway or Fly.io
Auth:      JWT tokens
PWA:       Service workers
```

---

## Milestones Summary

| Week | Milestone | Features |
|------|-----------|----------|
| **2** | Database Schema Complete | Models, migrations, tests |
| **4** | Food Search Working | USDA integration, 1000+ foods cached |
| **6** | Nutrition Tracking MVP | Log food, view diary, macro totals |
| **8** | **MVP COMPLETE** ✅ | Nutrition + exercise + weight tracking |
| **14** | **STAGE 2 COMPLETE** ✅ | Barcode, recipes, programs, analytics |
| **20** | **STAGE 3 COMPLETE** ✅ | Adaptive algorithm, AI features |
| **28** | **STAGE 4 COMPLETE** ✅ | Hosted, mobile-responsive, production-ready |

---

## Success Criteria

### MVP Success
- [ ] Can log food and see daily macros
- [ ] Can log workouts and track progress
- [ ] Can log weight and see trends
- [ ] Works 100% offline (local)
- [ ] Response time <1 second for all operations

### Stage 2 Success
- [ ] Barcode scanning works for common products
- [ ] Can create and log recipes
- [ ] Can follow pre-built workout programs
- [ ] Analytics show meaningful insights

### Stage 3 Success
- [ ] TDEE algorithm provides accurate recommendations
- [ ] AI food logging works 80%+ accuracy
- [ ] Exercise recommendations are personalized and helpful

### Stage 4 Success
- [ ] App is accessible from phone/tablet
- [ ] Hosted version has 99.9% uptime
- [ ] Multiple users can use the system
- [ ] Data is backed up automatically

---

## Risk Mitigation

### Technical Risks

**Risk:** USDA API rate limits
**Mitigation:** Aggressive caching, pre-populate popular foods

**Risk:** AI food logging inaccuracy
**Mitigation:** Always show confidence score, allow manual editing

**Risk:** Database performance with large history
**Mitigation:** Proper indexing, archiving old data

### Scope Risks

**Risk:** Feature creep delaying MVP
**Mitigation:** Strict MVP scope, defer nice-to-haves to Stage 2+

**Risk:** Overengineering too early
**Mitigation:** Start simple (SQLite, Streamlit), upgrade later

---

## Next Steps (This Week)

1. ✅ Review and approve this roadmap
2. ⏭️ Answer exercise data questions (S Tier Exercises content)
3. ⏭️ Sign up for USDA API key
4. ⏭️ Start Week 1 implementation (database setup)
5. ⏭️ Set up git branch for development

---

## Questions Before Starting

1. **Exercise Data**: Can you share the content of "S Tier Exercises.rtf" and gym equipment info?
2. **Deployment Preference**: Which deployment option appeals to you most? (Local, Self-hosted, PaaS, Hybrid)
3. **React Migration**: Do you want to stick with Streamlit or eventually migrate to React?
4. **AI Features**: Willing to pay for OpenAI API (~$10-20/month) or prefer local models only?
5. **Timeline**: Is 8 weeks to MVP reasonable, or do you need faster/slower pace?

---

Ready to start implementation? Let me know if you want to adjust anything in this roadmap!
