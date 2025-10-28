FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/pdfs data/vectorstore

# Expose ports
EXPOSE 8501 11434

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama server in background\n\
ollama serve &\n\
\n\
# Wait for Ollama to be ready\n\
sleep 5\n\
\n\
# Pull both models for testing\n\
ollama pull llama3.1:70b\n\
ollama pull llama3.1:8b\n\
\n\
# Start Streamlit app\n\
streamlit run src/main.py --server.port 8501 --server.address 0.0.0.0' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]