# HealthRAG

A completely **FREE**, **local** AI-powered health and fitness advisor that uses Retrieval-Augmented Generation (RAG) to provide personalized advice from your own fitness and nutrition documents.

## Why HealthRAG?

- **💰 Zero Cost**: No API fees, completely free to run
- **🔒 100% Private**: Your data never leaves your machine
- **🚀 No API Keys**: Uses local Ollama or Apple Silicon MLX
- **📚 Your Documents**: Query your personal library of fitness PDFs
- **⚡ Fast**: Optimized for Apple Silicon with MLX support

## Quick Start

### Option 1: Homelab Deployment (Recommended)

**Deploy to homelab with shared Ollama service:**

```bash
# One-command deployment
./deploy-to-homelab.sh

# Or manually:
docker-compose up -d

# Access at: http://192.168.0.210:8501 (or your Docker host IP)
```

**Architecture:** Microservices with shared Ollama backend
- HealthRAG container: Lightweight (~2GB RAM), Streamlit UI
- Ollama service: Shared LLM inference on CT 101 (192.168.0.211:11434)
- Backend API: FastAPI + PostgreSQL on jwWinMin (192.168.0.64:8000)

See **[docs/HOMELAB_DEPLOYMENT.md](docs/HOMELAB_DEPLOYMENT.md)** for detailed setup guide.

### Option 2: Local Development (Python venv)

```bash
# One-time setup
chmod +x setup_dependencies.sh && ./setup_dependencies.sh

# Daily usage
source activate_venv.sh
streamlit run src/main.py

# Access at: http://localhost:8501
```

### Option 3: Local Dev with Bundled Ollama

```bash
# Includes Ollama container (no external dependency)
docker-compose -f docker-compose.dev.yml up --build

# Access at: http://localhost:8501
```

### Option 4: Local MLX (macOS Only - Faster)

```bash
./run_local_mlx.sh
# Or: source venv_mlx/bin/activate && streamlit run src/main.py

# Access at: http://localhost:8501
```

## Adding Your Documents

1. Copy your PDF files to `data/pdfs/`
2. Run the processing script:
   ```bash
   python3 process_pdfs.py
   ```
3. Ask questions about your documents!

## Usage Examples

Ask questions like:
- "What's the Renaissance Periodization approach to muscle gain?"
- "How should I structure my workout for hypertrophy?"
- "What's the optimal protein intake for body recomposition?"
- "What does Jeff Nippard recommend for training volume?"

## Technical Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| **LLM** | Ollama / MLX | Llama 3.1 (70B/8B) - Local inference |
| **Embeddings** | Sentence Transformers | all-MiniLM-L6-v2 - Local embeddings |
| **Vector DB** | ChromaDB | Local vector storage |
| **UI** | Streamlit | Web interface |
| **Framework** | LangChain | RAG orchestration |

## Project Structure

```
HealthRAG/
├── src/                       # Streamlit app + core modules (25 files)
├── backend/                   # FastAPI backend (PostgreSQL, JWT auth)
│   ├── api/                   # API routes (auth, nutrition, workouts, weight)
│   ├── models/                # SQLAlchemy models + Pydantic schemas
│   ├── services/              # Business logic (user-scoped, PostgreSQL-backed)
│   └── docker-compose.yml     # Backend deployment (FastAPI + PostgreSQL)
├── frontend/                  # React PWA (Vite + Tailwind)
├── data/                      # Persistent data (vectorstore, PDFs, SQLite)
├── config/settings.py         # Configuration settings
├── Dockerfile                 # Homelab container (no bundled Ollama)
├── docker-compose.yml         # Homelab deployment (shared Ollama)
├── docker-compose.dev.yml     # Dev deployment (bundled Ollama)
├── deploy-to-homelab.sh       # One-command homelab deploy script
├── requirements.txt           # Python dependencies
└── requirements_local.txt     # MLX dependencies (macOS only)
```

## Features

### Dual Backend Support
- **MLX Backend**: Native Apple Silicon acceleration (M1/M2/M3)
- **Ollama Backend**: Docker-based, works on any platform

### Smart Document Processing
- Automatic PDF chunking (1000 chars, 200 overlap)
- Persistent vector store
- Error handling for corrupted files

### Grounded Responses
- Only answers from your documents
- Source attribution
- No hallucination - explicit when info not available

### 📷 Camera Barcode Scanning (Privacy-First)
- **Privacy-focused**: Camera OFF by default, user must explicitly enable
- **Automatic detection**: Uses pyzbar to decode UPC/EAN barcodes
- **Instant lookup**: Queries Open Food Facts database (2.8M+ products)
- **Full nutrition info**: Calories, protein, carbs, fat, serving sizes
- **Quick logging**: Add scanned products directly to food log
- **Manual fallback**: Original manual entry always available
- **Success rate**: 70-80% in good conditions (lighting, centering)

**How to use:**
1. Navigate to: "🍽️ Nutrition Tracking" → "🔍 Search & Add" tab
2. Click "📷 Enable Camera" button
3. Position barcode to webcam (centered, good lighting)
4. Take photo - automatic detection + product lookup
5. Select servings/meal type and add to log
6. Click "🚫 Disable Camera" when done

### ⚖️ Weight Tracking & Adaptive TDEE

Track your weight with **MacroFactor-style trend analysis** for data-driven coaching:

**Features:**
- **EWMA Trend Weight**: Exponentially Weighted Moving Average (alpha=0.3) smooths daily fluctuations
- **7-Day Moving Average**: Simple moving average for comparison
- **Rate of Change**: Weekly rate (lbs/week) calculated from trend data
- **Goal Tracking**: Visual delta from target weight
- **Interactive Charts**: Plotly visualization with hover details
- **Coaching Insights**: Automatic recommendations based on rate of change

**How to use:**
1. Navigate to: "⚖️ Weight Tracking & Trends"
2. **Log Weight** tab: Enter daily weight (replaces existing entry for same date)
3. **Weight Trends** tab: View charts, trends, and insights
4. Log consistently (7+ days for weekly trends, 14+ days for rate of change)

**What the trends mean:**
- **Daily Weight** (blue dots): Your actual scale readings
- **Trend Weight** (blue line): EWMA-smoothed weight (less reactive to daily fluctuations)
- **7-Day Average** (green dashed): Simple moving average
- **Goal Line** (red dotted): Your target weight from profile

**Coaching insights:**
- ✅ Stable: ±0.25 lbs/week (maintenance)
- 📉 Cutting: -0.5 to -2.0 lbs/week (sustainable fat loss)
- ⚠️ Too fast: > 2.0 lbs/week (consider slowing down)
- 📈 Bulking: +0.5 to +2.0 lbs/week (muscle gain)

**Database:** Weight data stored in `data/weights.db` (SQLite)

---

### 🔬 Adaptive TDEE & Weekly Check-Ins

**MacroFactor-style back-calculated TDEE** using your actual data for data-driven adjustments:

**Features:**
- **Back-Calculated TDEE**: Calculates your true TDEE from actual weight change + calorie intake (14-day rolling window)
- **Formula**: `TDEE = Avg_Calories - (Weight_Change_lbs × 3500 / Days)`
- **Weekly Check-In**: Compares goal rate vs actual rate, recommends macro adjustments
- **Adherence-Neutral Logic**: Assumes perfect tracking, adjusts based on results not compliance
- **Smart Thresholds**:
  - Within ±20% of goal: No change (natural variation)
  - Within ±50% of goal: ±100 cal adjustment (minor tweak)
  - Beyond ±50% of goal: ±150 cal adjustment (significant correction)
- **Phase-Aware**: Different logic for cut/bulk/maintain/recomp phases

**How to use:**
1. Navigate to: "🔬 Adaptive TDEE & Check-In"
2. Log 14+ days of weight and food intake
3. View adaptive TDEE comparison vs formula estimate
4. Review weekly check-in recommendations
5. Apply macro adjustments with one click

**What the metrics mean:**
- **Formula TDEE**: Mifflin-St Jeor estimate from your stats (static)
- **Adaptive TDEE**: Back-calculated from your actual data (dynamic)
- **TDEE Delta**: Difference between adaptive and formula (± cal/day)
- **Avg Intake**: Your average daily calories (last 14 days)
- **Weight Change**: Trend weight change using EWMA smoothing

**Coaching insights:**
- ✅ On track: Actual rate within ±20% of goal (keep current macros)
- ⚠️ Losing too fast: Actual rate > goal (increase calories +100-150)
- 📉 Losing too slow: Actual rate < goal (decrease calories -100-150)
- 📈 Gaining too fast/slow: Same logic for bulking phases
- 🔄 Maintenance: Absolute threshold (±0.25 lbs/week = stable)

**Example:**
```
Week 1-2 data:
- Weight: 210 → 208 lbs (trend: -2 lbs)
- Avg intake: 2100 cal/day
- Adaptive TDEE: 2100 - (-2 × 3500 / 14) = 2600 cal/day

Goal: -1.0 lb/week
Actual: -1.0 lb/week
✅ On track! Keep current macros.
```

**Database:** Combined data from `data/weights.db` + `data/food_log.db`

---

## Configuration

Edit `config/settings.py` to customize:

```python
DATA_PATH = "data/pdfs"              # PDF directory
VECTORSTORE_PATH = "data/vectorstore" # Vector DB location
CHUNK_SIZE = 1000                     # Text chunk size
CHUNK_OVERLAP = 200                   # Chunk overlap
RETRIEVAL_K = 5                       # Number of docs to retrieve
```

## Backend Switching

Switch between backends in the Streamlit UI:
1. MLX (Apple Silicon) - Faster, macOS only
2. Ollama (Docker) - Cross-platform

Or configure in code:
```python
from src.rag_system import HealthRAG

# Use MLX
rag = HealthRAG(backend="mlx")

# Use Ollama
rag = HealthRAG(backend="ollama")

# Switch backends
rag.switch_backend("mlx")
```

## Performance

- **First Run**: Downloads ~4-8GB model (one time)
- **Embedding**: Once per document (cached)
- **Query Response**: 5-15 seconds typical
- **Works Offline**: After initial setup

## Requirements

### Docker Option
- Docker Desktop
- 16GB RAM recommended
- 10GB disk space for models

### MLX Option
- macOS with Apple Silicon (M1/M2/M3)
- Python 3.10+
- 16GB RAM recommended
- 10GB disk space for models

## Troubleshooting

### Corrupted PDF
One known issue: `thePaleoSolution_FoodMatrix.pdf` is corrupted. The system automatically skips it. Replace with a valid copy if available.

### MLX Not Available
If MLX isn't available, the system falls back to Ollama automatically.

### Ollama Connection Error
Make sure Docker is running or Ollama is started:
```bash
ollama serve
```

### Port Already in Use
Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Change 8502 to any available port
```

## Development

### Adding Tests
```bash
# Create tests in tests/ directory
pytest tests/
```

### Processing New PDFs
```bash
python3 process_pdfs.py
```

### Rebuilding Vector Store
```bash
rm -rf data/vectorstore/
python3 process_pdfs.py
```

## Privacy & Security

- **All processing is local** - No cloud APIs
- **Your documents stay private** - Never uploaded anywhere
- **No telemetry** - No tracking or analytics
- **Open source** - Audit the code yourself

## Known Limitations

- PDF-only support (no Word docs, images, etc.)
- English language optimized (other languages may vary)
- Requires significant RAM for large document collections
- Response quality depends on your document quality

## Contributing

This is a personal project, but suggestions welcome! Open an issue or submit a PR.

## License

[Your License Here]

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain)
- [Ollama](https://ollama.ai/)
- [MLX](https://github.com/ml-explore/mlx)
- [ChromaDB](https://www.trychroma.com/)
- [Streamlit](https://streamlit.io/)

---

**Note**: This is a personal health advisor tool. Always consult qualified healthcare professionals for medical advice.
