# Personal Health & Fitness RAG Advisor

A completely FREE, local AI-powered health and fitness advisor that uses your own documents. No API keys required!

## 🚀 Quick Start Options

### Option 1: Docker (Recommended - Everything Included)
```bash
# Clone and build
docker-compose up --build

# Access at: http://localhost:8501
# Upload PDFs to: data/pdfs/
```

### Option 2: Local Installation
```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start Ollama and download model
ollama serve
ollama pull llama2

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run src/main.py
```

## 📁 Document Upload Location

**Upload your PDF documents to: `data/pdfs/`**

## ✨ Features

- ✅ **Completely FREE** - No API costs
- ✅ **100% Local** - Your data never leaves your machine
- ✅ **No API Keys** - Uses local Ollama + Sentence Transformers
- ✅ **Docker Support** - One-command setup
- ✅ **PDF Processing** - Automatically processes your health documents

## 💬 Usage Examples

- "What's the best protein intake for muscle building?"
- "How should I structure my workout routine?"
- "What foods help with recovery?"
- "What supplements should I take for endurance?"

## 🏗️ Technical Stack

- **LLM**: Ollama (Llama 2) - Local inference
- **Embeddings**: Sentence Transformers - Local embeddings
- **Vector DB**: ChromaDB - Local storage
- **Interface**: Streamlit - Web UI
- **Documents**: PyPDF - PDF processing

## 📂 Project Structure

```
HealthRAG/
├── src/
│   ├── main.py           # Streamlit web interface
│   └── rag_system.py     # Core RAG functionality
├── data/
│   ├── pdfs/             # Upload your PDFs here
│   └── vectorstore/      # Vector database storage
├── config/
│   └── settings.py       # Configuration settings
├── Dockerfile            # Docker setup
├── docker-compose.yml    # Docker orchestration
└── requirements.txt      # Python dependencies
```

## ⚡ Performance Notes

- First run downloads ~4GB Llama 2 model
- Embedding generation happens once per document
- Responses take 5-15 seconds on typical hardware
- Works offline after initial setup