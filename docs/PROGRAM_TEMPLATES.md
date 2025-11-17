# Program Templates & Reference Files

This document catalogs the Excel tracking sheets and reference files available for use in Phase 3 (Program Generation).

## 📊 Available Templates

### 1. Fundamentals Hypertrophy Program
**File:** `data/pdfs/Fundamentals_Hypertrophy_Program_Excel_Tracking_Sheet.xlsx`
**Size:** 256 KB
**Source:** Jeff Nippard

**Description:**
- Beginner to intermediate hypertrophy program
- Full tracking sheet with exercise progression
- Designed for muscle building fundamentals

**Use Cases:**
- Template for beginner/intermediate users
- Example of progression scheme
- Exercise selection reference
- Volume tracking format

**Phase 3 Integration:**
- Parse Excel structure for program template
- Extract exercise list and order
- Use sets/reps schemes as baseline
- Implement similar progression model

---

### 2. Min-Max Program (4x per week)
**File:** `data/pdfs/Min-Max_Program_4x.xlsx`
**Size:** 113 KB
**Source:** Jeff Nippard

**Description:**
- 4-day per week training split
- Optimized for minimal time, maximal results
- Upper/Lower or similar split structure

**Use Cases:**
- Template for 4-day schedule users
- Time-efficient programming model
- Exercise selection for limited time
- Volume optimization reference

**Phase 3 Integration:**
- Reference for 4-day program generation
- Exercise efficiency prioritization
- Time-per-session calculations
- Split structure template

---

### 3. Min-Max Program (5x per week)
**File:** `data/pdfs/Min-Max_Program_5x.xlsx`
**Size:** 134 KB
**Source:** Jeff Nippard

**Description:**
- 5-day per week training split
- Higher frequency variant
- More volume distribution across week

**Use Cases:**
- Template for 5-day schedule users
- Higher frequency programming
- Volume distribution strategies
- Advanced user reference

**Phase 3 Integration:**
- Reference for 5-day program generation
- Frequency optimization
- Recovery considerations
- Split structure variations

---

### 4. Jeff Nippard's Exercise Tier List
**File:** `data/pdfs/Jeff Nippard's Tier List.rtf`
**Size:** 12 KB
**Source:** Jeff Nippard

**Description:**
- Tier rankings of exercises by muscle group
- S-Tier, A-Tier, B-Tier, C-Tier classifications
- Evidence-based exercise effectiveness ratings
- Top picks for each body part

**Use Cases:**
- **PRIMARY:** Exercise selection for program generation
- Prioritize S/A-tier exercises
- Substitute similar tier exercises
- Equipment-based alternatives

**Phase 3 Integration:**
- **CRITICAL:** Core reference for exercise selection
- Build exercise database from tier list
- Filter by equipment availability
- Prioritize higher-tier exercises
- Provide alternatives within same tier

**Format Notes:**
- Currently RTF format (Rich Text Format)
- Needs conversion to PDF or direct parsing
- Contains structured tier lists by muscle group

---

## 🔧 Technical Integration Plan (Phase 3)

### Excel File Parsing Strategy

**Libraries:**
```python
import openpyxl  # For .xlsx files
import pandas as pd  # For data manipulation
```

**Extraction Goals:**
1. **Program Structure:**
   - Days per week
   - Split type (Upper/Lower, PPL, etc.)
   - Session duration

2. **Exercise Data:**
   - Exercise names
   - Muscle groups targeted
   - Sets and rep ranges
   - Order/sequence

3. **Progression Schemes:**
   - Week-to-week changes
   - Progressive overload strategy
   - Deload timing

4. **Volume Metrics:**
   - Sets per muscle group
   - Total weekly volume
   - Frequency per muscle

### Tier List Integration

**Processing Steps:**
1. Convert RTF to structured format (JSON/CSV)
2. Parse by muscle group
3. Extract exercise names and tier rankings
4. Build exercise selection database

**Data Structure:**
```json
{
  "chest": {
    "S_tier": ["Barbell Bench Press", "Incline Dumbbell Press"],
    "A_tier": ["Dips", "Cable Flyes"],
    "B_tier": ["Push-ups", "Pec Deck"],
    "C_tier": ["..."]
  },
  "back": {
    "S_tier": ["Pull-ups", "Barbell Rows"],
    "A_tier": ["..."],
  }
}
```

**Exercise Selection Logic:**
```python
def select_exercises(muscle_group, available_equipment, tier_priority=['S', 'A']):
    """
    Select best exercises based on:
    1. Tier ranking
    2. Equipment availability
    3. User experience level
    """
    # Filter by equipment
    # Prioritize higher tiers
    # Return top exercises
```

---

## 📋 Template Usage Guidelines

### When Generating Programs (Phase 3)

**User Profile Matching:**
- **4 days/week available** → Use Min-Max 4x template
- **5 days/week available** → Use Min-Max 5x template
- **Beginner level** → Use Fundamentals template
- **Intermediate+ level** → Adapt Min-Max templates

**Exercise Selection Priority:**
1. Check equipment availability (from user profile)
2. Reference Tier List for muscle group
3. Select S/A-tier exercises user can perform
4. Substitute B-tier if equipment limited
5. Avoid C-tier unless no alternatives

**Volume Calculation:**
- Parse existing templates for baseline volumes
- Query RAG for Nippard volume landmarks
- Adjust for user experience level
- Factor in recovery capacity

---

## 🎯 Phase 3 Milestones

### Week 5-6: Excel Parser
- [ ] Build Excel parsing module
- [ ] Extract exercise lists from all 3 templates
- [ ] Identify program structures (splits, frequencies)
- [ ] Document progression schemes

### Week 7: Tier List Integration
- [ ] Convert RTF tier list to structured format
- [ ] Build exercise selection database
- [ ] Implement tier-based exercise filtering
- [ ] Test exercise selection logic

### Week 8: Template-Based Generation
- [ ] Match user profile to appropriate template
- [ ] Substitute exercises based on equipment
- [ ] Adjust volume for experience level
- [ ] Generate 4-week program from template

### Week 9: Program Export
- [ ] Format program as Excel tracking sheet
- [ ] Include progression formulas
- [ ] Add volume calculations
- [ ] Export PDF summary

---

## 🔍 Current Status

**Files Cataloged:** 4 total
- ✅ 3 Excel program templates
- ✅ 1 RTF tier list

**Processing Status:**
- ⏸️ **On Hold for Phase 3**
- Files preserved in original format
- Structure/content not yet parsed
- Ready for Phase 3 integration

**Next Action:**
- Continue with Phase 2 (Profile & Calculations)
- Revisit these files in Week 5 of development

---

## 📝 Notes for Future Development

### Additional Templates Needed
- [ ] Cutting-specific programs (lower volume)
- [ ] Bulking-specific programs (higher volume)
- [ ] Body part specialization templates
- [ ] Home gym / minimal equipment variants

### Enhancement Ideas
- Import user's own Excel tracking sheets
- Auto-detect program type from Excel structure
- Extract rest times and tempo prescriptions
- Parse training notes and modifications

### Data Extraction Challenges
- Excel files may have complex formatting
- Need to identify which sheets contain program data
- Formulas may reference other cells
- Notes/instructions may be in merged cells

---

**Last Updated:** 2025-10-27
**Status:** Documented for Phase 3 Use
**Owner:** HealthRAG Development
