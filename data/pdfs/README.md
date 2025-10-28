# HealthRAG PDF Document Directory

This directory contains your personal fitness and nutrition documents that are processed by HealthRAG.

## Adding New Documents

1. Copy PDF files to this directory
2. Run the processing script: `python3 process_pdfs.py`
3. The documents will be automatically indexed and available for queries

## Current Documents

Your collection includes:
- Renaissance Periodization (RP) training and diet programs
- Jeff Nippard training programs and guides
- Body recomposition guides
- Paleo diet resources
- Burn the Fat, Feed the Muscle (BFFM) materials
- Nutrition and meal planning guides

## Known Issues

**Corrupted File**: `thePaleoSolution_FoodMatrix.pdf` is corrupted (file contains all zeros, invalid PDF header). This file is automatically skipped during processing. If you have a valid copy of this document, please replace it.

## File Formats Supported

- PDF files (`.pdf`)

Other formats like Excel tracking sheets (`.xlsx`) and ACSM files are stored here but not currently processed by the RAG system.
