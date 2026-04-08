# HealthRAG PDF Document Directory

This directory contains your personal fitness and nutrition documents that are processed by HealthRAG's RAG system.

## Quick Start

```bash
# 1. Copy your PDFs here
cp ~/path/to/your/pdfs/*.pdf data/pdfs/

# 2. Process into vectorstore
python3 process_pdfs.py

# 3. Verify
# The app will now answer questions grounded in your documents
```

## Required PDFs for Full Functionality

### Diet & Nutrition (CRITICAL for cutting/shredding advice)
- `EBOOK_Renaissance_Diet_2.0.pdf` — Primary diet reference, macro calculations
- `November 7th, 2023, The Diet Adjustments Manual v.3.0.9..pdf` — Adaptive TDEE adjustments
- `EBOOK_Simply_RP.pdf` — Simplified RP nutrition guide
- `EBOOK_Time_To_Eat.pdf` — Meal timing strategies
- `BFFM_2012_Version.pdf` — Burn the Fat, Feed the Muscle
- `bffm2003-2.pdf` — BFFM original edition

### Training Science
- `Ebook_Scientific_Principles_of_Hypertrophy_Training.pdf` — RP hypertrophy science
- `Ebook_An_Intro_To_Volume_Landmarks.pdf` — MEV/MAV/MRV (critical for program generation)
- `Ebook_Recovering_From_Training.pdf` — Recovery science

### Programs
- `Fundamentals_Hypertrophy_Program.pdf` — Jeff Nippard program guide
- `THE_MUSCLE_LADDER_-_EBOOK_-_07_-_10.11.24.pdf` — Advanced training
- `RP_6_Month_Hypertrophy_App-Fat_Loss.pdf` — RP cutting program
- `RP_6_Month_Hypertrophy_App-Muscle_Gain.pdf` — RP bulking program

### Body Composition
- `The_Ultimate_Guide_to_Body_Recomposition.pdf` — **Already included**

### Supplementary
- `abfood.pdf`, `food1.pdf`, `food2.pdf` — Nutrition reference
- `bodyfat.pdf` — Body fat estimation
- `shopping-list.pdf`, `Download-Weekly-Shopping-List1.pdf` — Meal prep
- `paleo-quick-start-guide.pdf` — Paleo reference

## Currently Loaded

- `The_Ultimate_Guide_to_Body_Recomposition.pdf` (21 MB)

## Known Issues

**Corrupted File**: `thePaleoSolution_FoodMatrix.pdf` is corrupted. This file is automatically skipped during processing.

## Notes

- PDFs are gitignored (copyrighted material) — you must add them manually
- Processing takes 5-10 minutes depending on PDF count and size
- The vectorstore persists at `data/vectorstore/` — no need to reprocess unless PDFs change
- Run `rm -rf data/vectorstore/ && python3 process_pdfs.py` to rebuild from scratch
