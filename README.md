# HealthRAG

A completely **FREE**, **local** AI-powered health and fitness advisor that uses Retrieval-Augmented Generation (RAG) to provide personalized advice from your own fitness and nutrition documents.

## Why HealthRAG?

- **💰 Zero Cost**: No API fees, completely free to run
- **🔒 100% Private**: Your data never leaves your machine
- **🚀 No API Keys**: Uses local Ollama or Apple Silicon MLX
- **📚 Your Documents**: Query your personal library of fitness PDFs
- **⚡ Fast**: Optimized for Apple Silicon with MLX support

## Quick Start

### Option 1: Docker (Cross-Platform, Recommended)

```bash
# Start everything with one command
./start_healthrag.sh

# Or manually:
docker-compose up --build

# Access at: http://localhost:8501
```

### Option 2: Local MLX (macOS Only - Faster)

```bash
# Run the setup script
./run_local_mlx.sh

# Or manually:
source venv_mlx/bin/activate
streamlit run src/main.py

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
├── src/
│   ├── main.py              # Streamlit web interface
│   └── rag_system.py        # Core RAG implementation
├── data/
│   ├── pdfs/                # Your PDF documents
│   └── vectorstore/         # ChromaDB vector database
├── config/
│   └── settings.py          # Configuration settings
├── Dockerfile               # Docker container setup
├── docker-compose.yml       # Docker orchestration
├── start_healthrag.sh       # Docker startup script
├── run_local_mlx.sh         # MLX local setup
├── process_pdfs.py          # PDF processing script
├── requirements.txt         # Ollama dependencies
└── requirements_local.txt   # MLX dependencies
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
