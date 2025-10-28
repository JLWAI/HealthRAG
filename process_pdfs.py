#!/usr/bin/env python3
"""
Script to process new PDFs and add them to the HealthRAG vector database.
Run this whenever you add new PDFs to the data/pdfs directory.
"""

import os
import glob
from src.rag_system import HealthRAG

def process_new_pdfs():
    """Process all PDFs in the data/pdfs directory"""
    print("🔄 Processing PDFs for HealthRAG...")
    
    # Get all PDF files
    pdf_directory = "data/pdfs"
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in data/pdfs directory")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {os.path.basename(pdf)}")
    
    # Initialize RAG system
    print("\n🚀 Initializing RAG system...")
    rag = HealthRAG(backend="mlx")
    
    # Add documents to vectorstore
    print("\n📝 Processing and adding documents...")
    rag.add_documents(pdf_files)
    
    print("\n✅ PDF processing complete!")
    print("Your HealthRAG system now has access to all your fitness and nutrition documents.")
    print("\n💡 You can now ask questions about:")
    print("  - Diet and nutrition strategies")
    print("  - Training programs and hypertrophy")
    print("  - Body recomposition")
    print("  - Renaissance Periodization methods")
    print("  - Paleo diet approaches")
    print("  - And much more based on your document collection!")

if __name__ == "__main__":
    process_new_pdfs()