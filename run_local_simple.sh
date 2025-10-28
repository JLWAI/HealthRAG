#!/bin/bash

# Simple MLX local test script

echo "🚀 Running HealthRAG with MLX locally (simplified)..."
echo "=================================================="

# Skip complex dependencies, use existing Docker vectorstore
echo "📂 Using existing PDFs and vectorstore from Docker..."

# Quick install of just MLX
echo "📥 Installing MLX-LM..."
pip3 install mlx-lm

echo ""
echo "🎯 Starting local HealthRAG with MLX support..."
echo "   This will use your existing processed PDFs"
echo ""

# Run with streamlit
streamlit run src/main.py