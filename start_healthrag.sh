#!/bin/bash

# HealthRAG One-Shot Startup Script
# This script will start HealthRAG in Docker with all dependencies

set -e  # Exit on any error

echo "🏃‍♂️ Starting HealthRAG Personal Fitness Advisor..."
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Navigate to HealthRAG directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Check if PDFs exist
PDF_COUNT=$(find data/pdfs -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "⚠️  No PDFs found in data/pdfs/"
    echo "   Upload your health/fitness PDFs to: $SCRIPT_DIR/data/pdfs/"
    echo "   The system will still start, but you'll need PDFs to get answers."
    echo ""
else
    echo "✅ Found $PDF_COUNT PDF(s) in data/pdfs/"
fi

# Stop any existing containers
echo "🧹 Cleaning up any existing containers..."
docker compose down >/dev/null 2>&1 || true

# Build and start the container
echo "🔨 Building and starting HealthRAG container..."
echo "   (First run may take 5-10 minutes to download Llama 2 model)"
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "🎉 HealthRAG is ready!"
    echo "=================================================="
    echo "🌐 Web Interface: http://localhost:8501"
    echo "📁 PDF Upload: $SCRIPT_DIR/data/pdfs/"
    echo ""
    echo "💡 Usage Tips:"
    echo "   • Upload PDFs to data/pdfs/ folder"
    echo "   • Ask questions like:"
    echo "     - 'What's the best protein for muscle building?'"
    echo "     - 'How should I structure my workout routine?'"
    echo "     - 'What foods help with recovery?'"
    echo ""
    echo "🛑 To stop: docker compose down"
    echo "📋 To view logs: docker compose logs -f"
    echo ""
    
    # Optionally open browser (macOS)
    if command -v open >/dev/null 2>&1; then
        read -p "🚀 Open http://localhost:8501 in browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open http://localhost:8501
        fi
    fi
else
    echo "❌ Failed to start containers. Check logs with: docker compose logs"
    exit 1
fi