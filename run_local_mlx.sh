#!/bin/bash

# HealthRAG MLX Local Setup Script
# Run this to test MLX performance on your Mac

echo "🚀 Setting up HealthRAG with MLX support locally..."
echo "=================================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ MLX is only supported on macOS. Use Docker version instead."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv_mlx" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv_mlx
fi

# Activate virtual environment
source venv_mlx/bin/activate

# Install requirements
echo "📥 Installing requirements with MLX support..."
pip install -r requirements_local.txt

# Copy PDFs from Docker volume if they exist
if [ -d "data/pdfs" ] && [ "$(ls -A data/pdfs)" ]; then
    echo "✅ PDFs found in data/pdfs/"
else
    echo "⚠️  No PDFs found. Please add your health/fitness PDFs to data/pdfs/"
fi

echo ""
echo "🎉 Local MLX setup complete!"
echo "=================================================="
echo "🚀 To start HealthRAG with MLX:"
echo "   source venv_mlx/bin/activate"
echo "   streamlit run src/main.py"
echo ""
echo "💡 This will run natively on your Mac with MLX acceleration"
echo "   Much faster than the Docker version!"
echo ""