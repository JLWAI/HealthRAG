# HealthRAG v2.0 - AI Personal Trainer & Nutritionist

A completely **FREE**, **local** AI-powered personal trainer and nutritionist that combines evidence-based knowledge from expert sources (Renaissance Periodization, Jeff Nippard, BFFM) with personalized tracking and adaptive programming to guide you toward your fitness goals.

## 🎯 What is HealthRAG v2.0?

HealthRAG v2.0 is your **complete AI fitness coach** that:
- **Knows YOU**: Personal stats, goals, equipment, training history
- **Generates Programs**: Evidence-based training & nutrition plans
- **Tracks Progress**: Weight, workouts, meals, measurements
- **Adapts Recommendations**: Adjusts based on YOUR actual results
- **Provides Coaching**: Quick answers grounded in expert sources

**Replaces:** Personal trainer ($200-500/month) + Nutrition coaching ($100-300/month) + Tracking apps ($10-30/month)
**Your Cost:** $0 (100% free, local, private)

## 🌟 Why HealthRAG v2.0?

- **💰 Zero Cost**: No API fees, no subscriptions, completely free to run
- **🔒 100% Private**: Your data never leaves your machine
- **🚀 No API Keys**: Uses local Ollama or Apple Silicon MLX
- **📚 Expert Knowledge**: Query Renaissance Periodization, Jeff Nippard, BFFM PDFs
- **🏋️ Personalized**: Programs tailored to your equipment, schedule, experience
- **📊 Adaptive**: Adjusts based on your actual progress, not generic plans
- **⚡ Fast**: Optimized for Apple Silicon with MLX support

## ✨ Complete Feature Set

### 👤 **User Profile System**
- Complete profile with personal stats (weight, height, age, sex, activity level)
- Goal setting (cut/bulk/maintain/recomp) with target rates
- Training experience tracking (beginner/intermediate/advanced)
- Equipment inventory (home gym, commercial, minimal)
- Schedule preferences (days/week, split type)
- Multi-user support with profile switching

### 🏋️ **Program Generation**
- **500+ Exercise Database** from Jeff Nippard's tier list (S/A/B/C/D tiers)
- **Intelligent Exercise Selection** based on equipment and goals
- **Mesocycle Templates**: Upper/Lower, PPL, Full Body splits
- **Volume Prescription**: MEV/MAV/MRV methodology from Renaissance Periodization
- **Progressive Overload**: RIR-based weekly progression
- **Exercise Alternatives**: Equipment-aware substitutions
- **Program Export**: PDF/Excel export for training logs

### 💪 **Workout Tracking**
- Complete workout logging (sets, reps, weight, RIR, RPE)
- AI workout coach with form cues and recommendations
- Autoregulation system based on RP principles
- Workout database (SQLite) for progress tracking
- Performance analytics and strength progression charts

### 🍽️ **Nutrition Tracking**
- **Food Logging** with barcode scanning (privacy-first, camera OFF by default)
- **USDA FDC Integration**: 400K+ foods from USDA database
- **Open Food Facts Integration**: 2.8M+ products with barcode lookup
- **Meal Templates**: One-click logging for frequent meals
- **Macro Tracking**: Real-time progress vs daily targets
- **Camera Barcode Scanning**: Instant product lookup

### ⚖️ **Weight Tracking & Trends**
- **EWMA Trend Weight**: MacroFactor-style exponentially weighted moving average
- **7-Day Moving Average**: Simple smoothing for comparison
- **Rate of Change**: Weekly rate (lbs/week) calculated from trend
- **Goal Tracking**: Visual delta from target weight
- **Interactive Charts**: Plotly visualization with hover details
- **Coaching Insights**: Automatic recommendations based on trends

### 🔬 **Adaptive TDEE & Weekly Check-Ins**
- **Back-Calculated TDEE**: True TDEE from actual weight change + intake (14-day rolling)
- **MacroFactor Algorithm**: `TDEE = Avg_Calories - (Weight_Change × 3500 / Days)`
- **Weekly Check-In**: Compares goal rate vs actual, recommends adjustments
- **Adherence-Neutral Logic**: Assumes perfect tracking, adjusts based on results
- **Smart Thresholds**: ±100-150 cal adjustments based on deviation from goal
- **Phase-Aware**: Different logic for cut/bulk/maintain/recomp

### 🍎 **Apple Health Integration** (macOS)
- Import weight data from Apple Health
- Import workout data
- Import nutrition data
- Automatic sync with HealthRAG databases

### 💬 **RAG-Based Coaching**
- Evidence-based answers from expert PDFs
- Profile-aware responses (considers YOUR stats and goals)
- Source attribution for all recommendations
- No hallucination - grounded in documents

## 🚀 Quick Start

### Option 1: Local Development (Recommended)

**One-time setup:**
```bash
# Run the automated setup script (installs all dependencies)
chmod +x setup_dependencies.sh
./setup_dependencies.sh
```

**Daily usage:**
```bash
# Activate virtual environment (includes ZBar library path for barcode scanning)
source activate_venv.sh

# Start the application
streamlit run src/main.py

# Access at: http://localhost:8501
```

**To deactivate:**
```bash
deactivate
```

### Option 2: Docker (Cross-Platform)

```bash
# Start everything with one command
docker compose up --build

# Access at: http://localhost:8501
```

### Option 3: Local MLX (macOS Only - Faster)

```bash
# Run the setup script
./run_local_mlx.sh

# Or manually:
source venv_mlx/bin/activate
streamlit run src/main.py

# Access at: http://localhost:8501
```

## 📖 Getting Started Guide

### 1. Add Your Documents (Optional)

Copy fitness/nutrition PDFs to `data/pdfs/` and process them:
```bash
python3 process_pdfs.py
```

**Recommended PDFs:**
- Renaissance Periodization (RP) programs
- Jeff Nippard training guides
- Body For Life Movement (BFFM)
- Any fitness/nutrition resources

### 2. Create Your Profile

1. Open http://localhost:8501
2. Navigate to sidebar: **"👤 User Profile"**
3. Fill in:
   - Personal stats (weight, height, age, sex, activity level)
   - Goals (target weight, phase: cut/bulk/maintain, timeline)
   - Training experience (beginner/intermediate/advanced)
   - Equipment available (select from presets or custom)
   - Schedule (days/week, preferred split)
4. Click **"Save Profile"**

### 3. Get Your Baseline Metrics

HealthRAG automatically calculates:
- ✅ **TDEE** (Total Daily Energy Expenditure) - Mifflin-St Jeor formula
- ✅ **BMR** (Basal Metabolic Rate)
- ✅ **Target Calories** based on your phase
- ✅ **Macro Targets** (protein/carbs/fat split)

### 4. Generate Your Training Program

1. Navigate to: **"🏋️ Program Generator"**
2. Select:
   - Training split (Upper/Lower, PPL, Full Body)
   - Program duration (4-8 weeks)
   - Volume level (MEV/MAV based on experience)
3. Click **"Generate Program"**
4. Review exercises, sets, reps, RIR progression
5. Export to PDF/Excel for gym use

### 5. Start Tracking

**Daily Workflow:**
- 📊 **Log Weight**: "⚖️ Weight Tracking" → Enter daily weight
- 💪 **Log Workout**: "💪 Workout Tracker" → Log sets/reps/weight/RIR
- 🍽️ **Log Meals**: "🍽️ Nutrition Tracking" → Search foods or scan barcodes
- 📈 **Review Progress**: Check trends, charts, and coaching insights

**Weekly Check-In:**
- 🔬 Navigate to: "🔬 Adaptive TDEE & Check-In"
- Review weekly rate of change vs goal
- Apply recommended macro adjustments (±100-150 cal)
- Update program based on strength progression

### 6. Ask Your Coach

Navigate to **"💬 Chat with RAG"** and ask:
- "What's the Renaissance Periodization approach to muscle gain?"
- "How should I structure my workout for hypertrophy?"
- "What's my optimal protein intake?" (profile-aware!)
- "Should I deload this week?" (based on your logs)

## 📊 Technical Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| **LLM** | Ollama / MLX | Llama 3.1 (70B/8B) - Local inference |
| **Embeddings** | Sentence Transformers | all-MiniLM-L6-v2 - Local embeddings |
| **Vector DB** | ChromaDB | Local vector storage |
| **Tracking DB** | SQLite | Workouts, nutrition, weight data |
| **UI** | Streamlit | Web interface with tabs |
| **Charts** | Plotly | Interactive progress charts |
| **Framework** | LangChain | RAG orchestration |
| **Barcode** | pyzbar + ZBar | Camera barcode scanning |
| **Food Data** | USDA FDC + Open Food Facts | 3M+ food products |

## 📂 Project Structure

```
HealthRAG/
├── src/
│   ├── main.py                      # Streamlit UI (all tabs)
│   ├── rag_system.py                # Core RAG engine
│   ├── profile.py                   # User profile management
│   ├── calculations.py              # TDEE/macro calculators
│   │
│   ├── exercise_database.py         # 500+ exercises (Nippard tiers)
│   ├── exercise_selection.py        # Equipment-aware selection
│   ├── exercise_alternatives.py     # Substitutions
│   ├── mesocycle_templates.py       # Training splits
│   ├── volume_prescription.py       # MEV/MAV/MRV
│   ├── progressive_overload.py      # RIR progression
│   ├── program_generator.py         # Complete program builder
│   ├── program_manager.py           # Program versioning
│   ├── program_export.py            # PDF/Excel export
│   │
│   ├── workout_logger.py            # Workout logging
│   ├── workout_database.py          # Workout DB
│   ├── workout_coach.py             # AI coaching
│   ├── workout_models.py            # Data models
│   ├── autoregulation.py            # RPE/RIR system
│   │
│   ├── food_logger.py               # Food logging
│   ├── food_api_fdc.py              # USDA FDC integration
│   ├── food_api_off.py              # Open Food Facts integration
│   ├── food_search_integrated.py    # Unified search
│   ├── food_models.py               # Data models
│   ├── meal_templates.py            # One-click meals
│   │
│   ├── adaptive_tdee.py             # MacroFactor-style TDEE
│   └── apple_health.py              # Apple Health import
│
├── data/
│   ├── pdfs/                        # Your PDF documents
│   ├── vectorstore/                 # ChromaDB embeddings
│   ├── user_profile.json            # Profile storage
│   ├── workouts.db                  # Workout logs (SQLite)
│   ├── food_log.db                  # Nutrition logs (SQLite)
│   └── weights.db                   # Weight tracking (SQLite)
│
├── tests/
│   ├── test_profile.py              # Profile tests
│   ├── test_calculations.py         # TDEE/macro tests
│   ├── test_workout_*.py            # Workout tests
│   ├── test_adaptive_tdee.py        # Adaptive TDEE tests
│   ├── fixtures/personas.py         # Test personas
│   └── browser/                     # Playwright browser tests
│
├── docs/
│   ├── VISION.md                    # v2.0 product vision
│   ├── PHASE4_PLAN.md               # Implementation roadmap
│   ├── KNOWLEDGE_BASE.md            # Claude agent knowledge
│   ├── TESTING.md                   # Testing strategy
│   └── WORKOUT_TRACKING_GUIDE.md    # User guides
│
├── .github/workflows/               # CI/CD automation
├── setup_dependencies.sh            # Automated setup
├── activate_venv.sh                 # Venv activation
└── process_pdfs.py                  # PDF processing
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test suite
pytest tests/test_calculations.py -v

# Run browser tests (requires Playwright)
pytest tests/browser/ -v
```

## 📚 Documentation

- **[VISION.md](VISION.md)** - v2.0 product vision and roadmap
- **[PHASE4_PLAN.md](PHASE4_PLAN.md)** - Phase 4 implementation plan
- **[WORKOUT_TRACKING_GUIDE.md](WORKOUT_TRACKING_GUIDE.md)** - How to log workouts
- **[MULTI_USER_GUIDE.md](MULTI_USER_GUIDE.md)** - Multi-profile management
- **[docs/KNOWLEDGE_BASE.md](docs/KNOWLEDGE_BASE.md)** - Claude agent knowledge base
- **[docs/TESTING.md](docs/TESTING.md)** - Testing strategy and local-first workflow

## 🔧 Configuration

Edit `config/settings.py` to customize:

```python
DATA_PATH = "data/pdfs"              # PDF directory
VECTORSTORE_PATH = "data/vectorstore" # Vector DB location
CHUNK_SIZE = 1000                     # Text chunk size
CHUNK_OVERLAP = 200                   # Chunk overlap
RETRIEVAL_K = 5                       # Number of docs to retrieve
```

## 🐛 Troubleshooting

### Barcode Scanning Not Working
- **macOS**: Install ZBar: `brew install zbar`
- **Linux**: Install ZBar: `sudo apt-get install libzbar0`
- **Windows**: Download ZBar from http://zbar.sourceforge.net/
- Camera must be enabled in browser/OS permissions

### Ollama Connection Error
```bash
# Start Ollama service
ollama serve

# Pull model
ollama pull llama3.1:8b
```

### MLX Not Available
MLX only works on macOS with Apple Silicon. System falls back to Ollama automatically.

### Port Already in Use
Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Change 8502 to any available port
```

### Missing Dependencies
```bash
# Reinstall all dependencies
chmod +x setup_dependencies.sh
./setup_dependencies.sh
```

## 🔐 Privacy & Security

- **All processing is local** - No cloud APIs (except optional food databases)
- **Your documents stay private** - Never uploaded anywhere
- **No telemetry** - No tracking or analytics
- **Open source** - Audit the code yourself
- **Camera privacy** - OFF by default, user must explicitly enable

## 💡 Usage Examples

### Profile-Aware Coaching
```
You: "How much protein do I need?"
HealthRAG: "Based on your profile (210 lbs, cutting phase),
Renaissance Periodization recommends 1.0-1.2g/lb = 210-252g protein.
Your current target is 220g (from your macros). This is optimal for
preserving muscle during fat loss."
```

### Program Generation
```
You: Generate upper/lower split, 4 days/week, intermediate volume
HealthRAG: [Generates complete 6-week program]
- Day 1: Upper A (8 exercises, 16-18 sets)
- Day 2: Lower A (7 exercises, 14-16 sets)
- Day 3: Rest
- Day 4: Upper B (8 exercises, 16-18 sets)
- Day 5: Lower B (7 exercises, 14-16 sets)
- Progression: RIR 3 → 2 → 1 → deload
```

### Adaptive TDEE
```
Week 1-2 Data:
- Weight: 210 → 208 lbs (trend: -2 lbs, -1 lb/week)
- Avg intake: 2100 cal/day
- Adaptive TDEE: 2600 cal/day (formula TDEE: 2550, delta: +50)

Goal: -1.0 lb/week
Actual: -1.0 lb/week
✅ On track! Keep current macros (2100 cal).
```

## 🌍 Contributing

This is a personal project, but suggestions welcome! Open an issue or submit a PR.

## 📄 License

MIT License - Feel free to use, modify, and distribute this project. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - RAG framework
- [Ollama](https://ollama.ai/) - Local LLM inference
- [MLX](https://github.com/ml-explore/mlx) - Apple Silicon acceleration
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Streamlit](https://streamlit.io/) - Web UI
- [Plotly](https://plotly.com/) - Interactive charts
- [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar) - Barcode scanning

**Expert Sources:**
- Renaissance Periodization (RP) - Dr. Mike Israetel
- Jeff Nippard - Science-based training
- Body For Life Movement (BFFM) - Tom Venuto

---

## ⚠️ Disclaimer

This is a personal health advisor tool built for educational and informational purposes. **Always consult qualified healthcare professionals** for medical advice, especially before starting any new diet or exercise program.

---

**HealthRAG v2.0** - Your AI Personal Trainer & Nutritionist, 100% Free, 100% Private, 100% Local 🏋️🍽️📊
