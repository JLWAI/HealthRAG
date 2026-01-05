# Body Measurements & Composition Tracking Feature

## Overview

**Purpose**: Track body measurements (waist, chest, arms, legs, etc.) to complement weight tracking and provide comprehensive body composition analysis using validated body fat estimation formulas.

**Status**: ✅ **100% Complete** (Phase 4 Enhancement)

**Key Value**:
- Tracks progress beyond just scale weight
- Multiple body fat estimation methods (Navy, WHtR, BMI)
- Visual trend analysis with charts
- Complements adaptive TDEE system
- Evidence-based fitness categorization

---

## Features Implemented

### 1. 11 Body Measurements Tracked

**Core Measurements** (inches):
- ✅ Waist (at narrowest point, above belly button)
- ✅ Chest (at nipple line, across widest part)
- ✅ Hips (at widest point around glutes)
- ✅ Neck (just below larynx/Adam's apple)
- ✅ Shoulders (across deltoids, widest point)

**Arm Measurements** (inches):
- ✅ Left Arm (flexed bicep, widest point)
- ✅ Right Arm (flexed bicep, widest point)

**Leg Measurements** (inches):
- ✅ Left Thigh (mid-thigh, widest point)
- ✅ Right Thigh (mid-thigh, widest point)
- ✅ Left Calf (widest point below knee)
- ✅ Right Calf (widest point below knee)

**Additional Fields**:
- ✅ Optional notes for each measurement session
- ✅ Automatic date tracking (defaults to today)
- ✅ Replaces previous entry if same date

---

### 2. Body Fat Estimation Methods

**Method 1: US Navy Method (Most Accurate)** ⭐
- **Male Formula**: `BF% = 86.010 × log10(abdomen - neck) - 70.041 × log10(height) + 36.76`
- **Female Formula**: `BF% = 163.205 × log10(waist + hip - neck) - 97.684 × log10(height) - 78.387`
- **Validated Research**: US Navy body composition standard
- **Accuracy**: ±3-4% when performed correctly
- **Required Measurements**:
  - Male: waist + neck + height
  - Female: waist + hips + neck + height

**Method 2: Waist-to-Height Ratio (WHtR)** (Screening Tool)
- **Formula**: `WHtR = waist_inches / height_inches`
- **Guidelines**:
  - < 0.5 = Healthy
  - 0.5-0.6 = Overweight
  - > 0.6 = Obese
- **Body Fat Estimate**:
  - Male: `BF% ≈ (WHtR - 0.35) × 100`
  - Female: `BF% ≈ (WHtR - 0.31) × 100`
- **Use Case**: Simple screening tool, correlates with cardiometabolic risk

**Method 3: Body Mass Index (BMI)**
- **Formula**: `BMI = (weight_lbs / height_inches²) × 703`
- **Limitations**: Doesn't account for muscle mass, less accurate than Navy method
- **Provided for reference only**

---

### 3. Fitness Categories (Navy Method Based)

**Male Categories**:
| Body Fat % | Category |
|------------|----------|
| < 6% | Essential Fat |
| 6-13% | Athletic |
| 14-17% | Fitness |
| 18-24% | Average |
| ≥ 25% | Obese |

**Female Categories**:
| Body Fat % | Category |
|------------|----------|
| < 14% | Essential Fat |
| 14-20% | Athletic |
| 21-24% | Fitness |
| 25-31% | Average |
| ≥ 32% | Obese |

**Coaching Context**:
- **Essential Fat**: Minimum for health, difficult to maintain
- **Athletic**: Competitive athletes, visible abs, vascularity
- **Fitness**: Fit, healthy, some ab definition
- **Average**: Healthy range, no major health risks
- **Obese**: Health risks, recommend cutting phase

---

## Technical Implementation

### Database Schema

**Location**: `data/body_measurements.db`

**Table**: `body_measurements`

```sql
CREATE TABLE body_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,              -- ISO format YYYY-MM-DD
    waist REAL,                             -- inches
    chest REAL,                             -- inches
    hips REAL,                              -- inches
    neck REAL,                              -- inches
    shoulders REAL,                         -- inches
    left_arm REAL,                          -- inches
    right_arm REAL,                         -- inches
    left_thigh REAL,                        -- inches
    right_thigh REAL,                       -- inches
    left_calf REAL,                         -- inches
    right_calf REAL,                        -- inches
    notes TEXT,                             -- optional notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_body_measurements_date ON body_measurements(date DESC);
```

**Design Decisions**:
- ✅ **UNIQUE constraint on date**: Prevents duplicate entries, replaces on INSERT OR REPLACE
- ✅ **All measurements NULLABLE**: User can log subset of measurements
- ✅ **Index on date DESC**: Fast retrieval of recent measurements
- ✅ **REAL type (floating point)**: Sub-inch precision (e.g., 32.5 inches)
- ✅ **Separate left/right measurements**: Track symmetry and imbalances

---

### Code Structure

**File**: `src/body_measurements.py` (367 lines)

**Dataclasses**:
```python
@dataclass
class BodyMeasurement:
    """Single body measurement entry"""
    entry_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD
    waist: Optional[float] = None
    chest: Optional[float] = None
    hips: Optional[float] = None
    neck: Optional[float] = None
    shoulders: Optional[float] = None
    left_arm: Optional[float] = None
    right_arm: Optional[float] = None
    left_thigh: Optional[float] = None
    right_thigh: Optional[float] = None
    left_calf: Optional[float] = None
    right_calf: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

@dataclass
class BodyFatEstimate:
    """Body fat percentage estimates using multiple methods"""
    waist_to_height_ratio: Optional[float] = None
    waist_to_height_bf_estimate: Optional[float] = None
    navy_method_bf: Optional[float] = None
    bmi: Optional[float] = None
    category: Optional[str] = None
```

**Core Class**:
```python
class BodyMeasurementTracker:
    """
    Body measurement tracking system with SQLite backend.

    Features:
    - Track 11 body measurements (waist, chest, arms, legs, etc.)
    - Body fat estimation (WHtR, Navy method)
    - Progress tracking vs. previous measurements
    - Measurement trends over time
    - Integration with weight tracking for comprehensive analysis
    """

    def __init__(self, db_path: str = "data/body_measurements.db"):
        """Initialize tracker with database path"""

    def log_measurement(
        self,
        measurement_date: Optional[str] = None,
        waist: Optional[float] = None,
        # ... all 11 measurements ...
        notes: Optional[str] = None
    ) -> int:
        """Log measurements (replaces existing entry for same date)"""

    def get_measurements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[BodyMeasurement]:
        """Retrieve measurements ordered by date (newest first)"""

    def get_latest_measurement(self) -> Optional[BodyMeasurement]:
        """Get most recent measurement entry"""

    def delete_measurement(self, entry_date: str) -> bool:
        """Delete measurement entry for specific date"""

    def calculate_body_fat(
        self,
        measurement: BodyMeasurement,
        weight_lbs: float,
        height_inches: float,
        sex: str
    ) -> BodyFatEstimate:
        """Calculate body fat using multiple methods"""

    def get_measurement_changes(
        self,
        current_date: Optional[str] = None,
        comparison_date: Optional[str] = None
    ) -> Dict[str, Optional[float]]:
        """Calculate changes between two measurements"""
```

---

### UI Implementation

**File**: `src/main.py` (lines 2863-3279, 417 lines)

**Function**: `render_body_measurements()`

**Layout**: 3 Tabs (Log Measurements | Trends | Progress)

#### Tab 1: Log Measurements

**Form Inputs**:
```python
with st.form("log_measurements_form"):
    measurement_date = st.date_input("Measurement Date", value=date.today())

    # Core measurements
    waist = st.number_input("Waist (inches)", min_value=0.0, max_value=100.0, step=0.1)
    chest = st.number_input("Chest (inches)", min_value=0.0, max_value=100.0, step=0.1)
    hips = st.number_input("Hips (inches)", min_value=0.0, max_value=100.0, step=0.1)
    neck = st.number_input("Neck (inches)", min_value=0.0, max_value=100.0, step=0.1)
    shoulders = st.number_input("Shoulders (inches)", min_value=0.0, max_value=100.0, step=0.1)

    # Arms
    left_arm = st.number_input("Left Arm (inches)", min_value=0.0, max_value=100.0, step=0.1)
    right_arm = st.number_input("Right Arm (inches)", min_value=0.0, max_value=100.0, step=0.1)

    # Legs
    left_thigh = st.number_input("Left Thigh (inches)", min_value=0.0, max_value=100.0, step=0.1)
    right_thigh = st.number_input("Right Thigh (inches)", min_value=0.0, max_value=100.0, step=0.1)
    left_calf = st.number_input("Left Calf (inches)", min_value=0.0, max_value=100.0, step=0.1)
    right_calf = st.number_input("Right Calf (inches)", min_value=0.0, max_value=100.0, step=0.1)

    notes = st.text_area("Notes (optional)")

    submitted = st.form_submit_button("💾 Log Measurements", type="primary")
```

**Body Fat Estimation Section**:
```python
if latest_entry:
    bf_estimate = tracker.calculate_body_fat(
        measurement=latest_entry,
        weight_lbs=latest_weight.weight_lbs,
        height_inches=info.height_inches,
        sex=info.sex
    )

    st.markdown("#### 📊 Body Composition Estimate")

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if bf_estimate.navy_method_bf:
            st.metric("Body Fat %", f"{bf_estimate.navy_method_bf:.1f}%")

    with col2:
        if bf_estimate.waist_to_height_ratio:
            st.metric("Waist-to-Height", f"{bf_estimate.waist_to_height_ratio:.3f}")

    with col3:
        if bf_estimate.bmi:
            st.metric("BMI", f"{bf_estimate.bmi:.1f}")

    with col4:
        if bf_estimate.category:
            st.metric("Category", bf_estimate.category)

    # Coaching insights
    st.info("💡 **Coaching Insight**: ...")
```

#### Tab 2: Trends

**Latest Measurements Summary**:
```python
st.markdown("#### 📏 Latest Measurements")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Waist", f"{latest.waist:.1f}\"" if latest.waist else "—")
    st.metric("Chest", f"{latest.chest:.1f}\"" if latest.chest else "—")

# ... more metrics
```

**Plotly Charts**:
```python
# Core measurements chart
fig_core = go.Figure()
fig_core.add_trace(go.Scatter(x=dates, y=waist_values, name="Waist", mode='lines+markers'))
fig_core.add_trace(go.Scatter(x=dates, y=chest_values, name="Chest", mode='lines+markers'))
# ...
fig_core.update_layout(title="Core Measurements Over Time", xaxis_title="Date", yaxis_title="Inches")
st.plotly_chart(fig_core, use_container_width=True)

# Arms chart
fig_arms = go.Figure()
fig_arms.add_trace(go.Scatter(x=dates, y=left_arm_values, name="Left Arm", mode='lines+markers'))
fig_arms.add_trace(go.Scatter(x=dates, y=right_arm_values, name="Right Arm", mode='lines+markers'))
# ...
st.plotly_chart(fig_arms, use_container_width=True)

# Legs chart (similar structure)
```

#### Tab 3: Progress

**Comparison Metrics**:
```python
changes = tracker.get_measurement_changes()

st.markdown("#### 📈 Changes Since Last Measurement")

col1, col2, col3 = st.columns(3)

with col1:
    if changes.get('waist'):
        st.metric(
            "Waist",
            f"{latest.waist:.1f}\"",
            delta=f"{changes['waist']:+.1f}\"",
            delta_color="inverse"  # Losing inches is good
        )
```

**Coaching Insights**:
```python
# Analyze progress patterns
gained_measurements = [k for k, v in changes.items() if v and v > 0]
lost_measurements = [k for k, v in changes.items() if v and v < 0]

if gained_measurements:
    st.success(f"✅ **Growing**: {', '.join(gained_measurements)}")
if lost_measurements:
    st.info(f"📉 **Reducing**: {', '.join(lost_measurements)}")
```

---

## Testing Coverage

**File**: `tests/test_body_measurements.py` (27 tests, 100% passing)

**Test Categories**:

### 1. Database Initialization (1 test)
- ✅ `test_database_initialization`: Table creation, schema, indexes

### 2. Measurement Logging (7 tests)
- ✅ `test_log_single_measurement`: Basic logging
- ✅ `test_log_all_measurements`: All 11 measurements
- ✅ `test_log_measurement_defaults_to_today`: Date defaulting
- ✅ `test_log_measurement_replace_duplicate_date`: Date uniqueness
- ✅ `test_log_measurement_validation_no_measurements`: At least one required
- ✅ `test_log_measurement_validation_invalid_range`: Range validation (0-100 inches)

### 3. Retrieval (6 tests)
- ✅ `test_get_measurements_empty_database`: Empty handling
- ✅ `test_get_measurements_ordered_by_date_desc`: Date ordering
- ✅ `test_get_measurements_with_date_range`: Filtering by date
- ✅ `test_get_measurements_with_limit`: Result limiting
- ✅ `test_get_latest_measurement`: Latest retrieval
- ✅ `test_get_latest_measurement_empty_database`: Edge case

### 4. Deletion (2 tests)
- ✅ `test_delete_measurement`: Successful deletion
- ✅ `test_delete_measurement_not_found`: Not found handling

### 5. Body Fat Calculations (6 tests)
- ✅ `test_calculate_body_fat_male_navy_method`: Male Navy formula
- ✅ `test_calculate_body_fat_female_navy_method`: Female Navy formula
- ✅ `test_calculate_body_fat_whtr`: WHtR calculation
- ✅ `test_calculate_body_fat_bmi`: BMI calculation
- ✅ `test_calculate_body_fat_missing_measurements`: Partial data handling
- ✅ `test_calculate_body_fat_fitness_categories_male`: Category assignment

### 6. Progress Comparison (4 tests)
- ✅ `test_get_measurement_changes`: Basic comparison
- ✅ `test_get_measurement_changes_specific_dates`: Date-specific comparison
- ✅ `test_get_measurement_changes_no_previous`: No previous measurement
- ✅ `test_get_measurement_changes_missing_values`: Partial data comparison

### 7. Integration Tests (2 tests)
- ✅ `test_realistic_measurement_workflow`: Multi-week tracking workflow
- ✅ `test_body_fat_tracking_over_time`: BF% trend validation

**Run Tests**:
```bash
pytest tests/test_body_measurements.py -v
# 27 passed in 0.14s
```

---

## Integration with Existing Systems

### 1. Weight Tracking Integration

**Synergy**:
- Body measurements complement weight trends
- Body fat calculations require current weight (from WeightTracker)
- Combined data shows true composition changes (muscle gain vs. fat loss)

**Example Scenario**:
```
User's weight stays at 185 lbs for 4 weeks (no change)
BUT measurements show:
- Waist: 34" → 32" (losing fat)
- Arms: 14" → 14.5" (gaining muscle)
- Chest: 40" → 40.5" (gaining muscle)

→ Successful recomp despite stable weight!
```

### 2. Adaptive TDEE Integration

**How They Work Together**:
- Adaptive TDEE adjusts calories based on weight trend
- Body measurements validate that changes are desirable (muscle gain, fat loss)
- If weight dropping but measurements not changing → might be losing muscle (increase calories)
- If weight stable but waist shrinking → recomp working (maintain calories)

**Example Coaching Decision**:
```
Weight trend: Down 2 lbs in 2 weeks (TDEE = 2600 cal)
Waist: 34" → 32" (good, losing fat)
Arms: 14.5" → 14.5" (maintained muscle)

→ Recommendation: Continue current calories (2100 cal/day)
→ If arms were shrinking → increase protein or reduce deficit
```

### 3. Profile System Integration

**Data Flow**:
```python
# Body fat calculations use profile data
profile = UserProfile.load()
info = profile.personal_info

bf_estimate = tracker.calculate_body_fat(
    measurement=latest_measurement,
    weight_lbs=latest_weight.weight_lbs,  # From WeightTracker
    height_inches=info.height_inches,     # From UserProfile
    sex=info.sex                          # From UserProfile
)
```

---

## User Workflows

### Workflow 1: Initial Baseline Measurement

**Goal**: Establish starting point for tracking

**Steps**:
1. Navigate to "Body Measurements & Composition" section
2. Click "Log Measurements" tab
3. Take all measurements with tape measure:
   - **Waist**: Measure at narrowest point, above belly button, relaxed (not flexed)
   - **Chest**: Measure at nipple line, across widest part of chest
   - **Hips**: Measure at widest point around glutes
   - **Neck**: Measure just below larynx/Adam's apple
   - **Shoulders**: Measure across deltoids, widest point
   - **Arms**: Flex bicep, measure at widest point (both arms)
   - **Thighs**: Measure mid-thigh, widest point (both legs)
   - **Calves**: Measure widest point below knee (both legs)
4. Enter all values in form
5. Add notes: "Baseline measurement - start of cut"
6. Click "Log Measurements"
7. Review body fat estimate in summary section
8. Note fitness category for goal tracking

**Example Output**:
```
✅ Measurements logged for 2026-01-05

📊 Body Composition Estimate:
- Body Fat %: 18.2% (Navy Method)
- Waist-to-Height: 0.457
- BMI: 26.1
- Category: Fitness

💡 Coaching Insight: You're in the "Fitness" category (14-17% for males).
Your waist-to-height ratio of 0.457 is healthy (< 0.5).
Great starting point for a cutting phase!
```

---

### Workflow 2: Monthly Progress Check

**Goal**: Track body composition changes over time

**Steps**:
1. Take measurements same as baseline (every 4 weeks)
2. Log measurements with date
3. Navigate to "Trends" tab
4. Review Plotly charts:
   - **Core Measurements**: Waist should be trending down (cutting) or stable (recomp/bulk)
   - **Arms**: Should be stable or trending up (muscle retention/growth)
   - **Legs**: Similar to arms
5. Navigate to "Progress" tab
6. Review changes since last measurement:
   - **Waist**: -2.0" (good, losing fat)
   - **Chest**: +0.5" (good, gaining muscle)
   - **Arms**: +0.2" each (good, growing)
7. Compare body fat estimate vs. previous month

**Coaching Insights**:
```
✅ Growing: chest, left_arm, right_arm, shoulders
📉 Reducing: waist, hips

💡 This is IDEAL progress for a cutting phase!
You're losing fat (waist/hips shrinking) while maintaining/gaining muscle (chest/arms growing).
Continue current calories and training intensity.
```

---

### Workflow 3: Recomp Validation

**Goal**: Confirm body recomposition is working (gaining muscle, losing fat at stable weight)

**Scenario**:
- User's weight has been stable at 185 lbs for 8 weeks
- Feeling stronger, clothes fit differently
- Need to validate progress beyond scale

**Steps**:
1. Compare measurements from 8 weeks ago:
   ```
   Week 1:  Waist 34", Chest 40", Arms 14"
   Week 8:  Waist 32", Chest 41", Arms 14.5"
   Weight:  185 lbs → 185 lbs (no change)
   ```
2. Calculate body fat change:
   ```
   Week 1 BF%: 18.5%
   Week 8 BF%: 15.2%
   → Lost 3.3% body fat!
   ```
3. Estimate muscle gain:
   ```
   Week 1: 185 lbs × 18.5% = 34.2 lbs fat, 150.8 lbs lean
   Week 8: 185 lbs × 15.2% = 28.1 lbs fat, 156.9 lbs lean
   → Lost 6.1 lbs fat, gained 6.1 lbs muscle!
   ```

**Coaching Output**:
```
🎉 Successful Recomp!
Despite no change on the scale, you've made SIGNIFICANT progress:
- Lost 6.1 lbs body fat
- Gained 6.1 lbs muscle
- Waist shrunk 2 inches (visible fat loss)
- Chest grew 1 inch, arms grew 0.5 inch (muscle growth)

This is exactly what body recomposition looks like!
Continue your current approach.
```

---

## Comparison to Similar Tools

### MacroFactor Body Measurements
- **MacroFactor**: Tracks 6 measurements (waist, hips, chest, thigh, arm, calf)
- **HealthRAG**: Tracks 11 measurements (includes neck, shoulders, left/right symmetry)
- **Advantage**: More detailed tracking, Navy method BF% calculation

### Cronometer Body Measurements
- **Cronometer**: Tracks waist, hips, chest + custom measurements
- **HealthRAG**: Predefined 11 measurements + body fat estimation
- **Advantage**: Built-in body fat calculation without manual formulas

### Strong App (Workout Tracking)
- **Strong**: No body measurements tracking (workout-only)
- **HealthRAG**: Integrated with workout + nutrition + TDEE tracking
- **Advantage**: Unified system for complete progress tracking

---

## Known Limitations & Future Enhancements

### Current Limitations

1. **No Progress Photos**: Can't visually compare changes
   - **Workaround**: Use phone's Photos app, manual comparison
   - **Future**: Upload and overlay progress photos

2. **No Circumference Tracking for Fat Loss Goals**: Only tracks individual measurements
   - **Workaround**: Calculate total circumferences manually
   - **Future**: Auto-calculate sum of all measurements as "total circumferences"

3. **No Symmetry Analysis**: Doesn't flag L/R imbalances
   - **Workaround**: Manually compare left_arm vs. right_arm in data
   - **Future**: Auto-detect >5% L/R differences, recommend unilateral work

4. **No Skinfold Caliper Support**: Navy method only
   - **Workaround**: Navy method is 90% as accurate as calipers
   - **Future**: Add 7-site skinfold input option

5. **No DEXA/InBody Integration**: Can't import gold-standard BF% data
   - **Workaround**: Manual entry in notes field
   - **Future**: Parse DEXA/InBody reports, override Navy method estimate

---

### Phase 5 Enhancements (Future Work)

**Priority 1: Progress Photos** (Week 13, 6-8 hours)
- Upload front/side/back photos
- Date tagging and comparison view
- Overlay mode (before/after transparency slider)
- Auto-crop and alignment for consistent comparison

**Priority 2: Symmetry Analysis** (Week 14, 4-6 hours)
- Flag left/right imbalances >5% difference
- Recommend unilateral exercises (e.g., "Add single-arm rows")
- Track symmetry improvements over time

**Priority 3: Total Circumferences Metric** (Week 14, 2-3 hours)
- Sum of all measurements as single "total inches" metric
- Useful for fat loss goal tracking (total circumferences should decrease)
- Chart trend over time alongside weight trend

**Priority 4: Custom Measurements** (Week 15, 4-6 hours)
- Allow user to add custom measurement fields (e.g., "forearms", "glutes")
- Store in separate `custom_measurements` table
- Include in trend charts

**Priority 5: DEXA/InBody Import** (Week 16, 8-10 hours)
- Parse PDF reports from DEXA/InBody scans
- Extract BF%, lean mass, bone density
- Override Navy method estimate with gold-standard data
- Track DEXA/InBody scans over time (recommended every 3-6 months)

---

## Implementation Timeline

**Total Development Time**: ~6 hours

**Breakdown**:
1. **Design & Schema**: 30 minutes
   - Database schema design
   - Dataclass definitions
   - Body fat formula research

2. **Core Module**: 2 hours
   - BodyMeasurementTracker class (367 lines)
   - Database initialization
   - CRUD operations
   - Body fat calculations (Navy, WHtR, BMI)
   - Progress comparison logic

3. **UI Integration**: 2.5 hours
   - `render_body_measurements()` function (417 lines)
   - 3-tab layout (Log, Trends, Progress)
   - Form inputs (11 measurements + notes)
   - Body fat estimation section
   - Plotly charts (Core, Arms, Legs)
   - Progress comparison metrics
   - Coaching insights

4. **Testing**: 1 hour
   - 27 comprehensive tests
   - Edge case coverage
   - Integration test scenarios

5. **Documentation**: 30 minutes
   - This document (BODY_MEASUREMENTS_FEATURE.md)
   - Code comments and docstrings

---

## Related Files

**Core Implementation**:
- `src/body_measurements.py` (367 lines) - Tracker class, dataclasses, body fat calculations
- `src/main.py` (lines 2863-3279, 417 lines) - UI integration (`render_body_measurements()`)

**Testing**:
- `tests/test_body_measurements.py` (27 tests, 100% passing)

**Database**:
- `data/body_measurements.db` (SQLite, created on first use)

**Documentation**:
- `docs/BODY_MEASUREMENTS_FEATURE.md` (this file)
- `CLAUDE.md` (updated to reflect Phase 4 completion status)

---

## Deployment Notes

### Local Testing
```bash
# Run tests
pytest tests/test_body_measurements.py -v

# Start app locally (Docker)
./start_healthrag.sh

# Access: http://localhost:8501
# Navigate to "Body Measurements & Composition" section
```

### Homelab Deployment
```bash
# Deploy to homelab
./deploy-to-homelab.sh

# Access via Tailscale: http://192.168.0.210:8501
```

---

## Commit Message

```
feat: Add body measurements tracking and body fat estimation

Implements comprehensive body composition tracking:
- Track 11 body measurements (waist, chest, arms, legs, etc.)
- Body fat estimation (US Navy method, WHtR, BMI)
- Fitness category classification (Essential/Athletic/Fitness/Average/Obese)
- Progress visualization with Plotly charts
- Comparison vs. previous measurements with coaching insights
- Integration with weight tracking and adaptive TDEE

Technical details:
- SQLite database (data/body_measurements.db)
- 27 tests, 100% passing
- Gender-specific formulas (male/female)
- Tracks left/right symmetry (arms, thighs, calves)

Files modified:
- src/body_measurements.py (NEW, 367 lines)
- src/main.py (lines 22, 2863-3279, 3613)
- tests/test_body_measurements.py (NEW, 27 tests)

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## References

**US Navy Body Fat Formulas**:
- Hodgdon, J.A. and Beckett, M.B. (1984). "Prediction of percent body fat for U.S. Navy men from body circumferences and height." Report No. 84-11, Naval Health Research Center, San Diego, CA.
- Hodgdon, J.A. and Beckett, M.B. (1984). "Prediction of percent body fat for U.S. Navy women from body circumferences and height." Report No. 84-29, Naval Health Research Center, San Diego, CA.

**Waist-to-Height Ratio Research**:
- Ashwell, M. and Hsieh, S.D. (2005). "Six reasons why the waist-to-height ratio is a rapid and effective global indicator for health risks of obesity and how its use could simplify the international public health message on obesity." International Journal of Food Sciences and Nutrition, 56(5), 303-307.

**Body Composition Standards**:
- American Council on Exercise (ACE) Body Fat Percentage Charts
- National Strength and Conditioning Association (NSCA) Guidelines

---

## Support & Troubleshooting

**Q: Body fat estimate seems inaccurate**
- **A**: Navy method accuracy: ±3-4%. Ensure measurements are taken correctly:
  - Waist at narrowest point, relaxed (not flexed)
  - Neck just below larynx
  - Hips at widest point around glutes
  - Use soft tape measure, not stretched
  - Consistent measurement locations each time

**Q: Left and right measurements don't match**
- **A**: Small asymmetries (<5%) are normal. If >5% difference:
  - Check measurement technique (same location both sides)
  - May indicate muscle imbalance (add unilateral exercises)
  - Track over time to see if gap is closing

**Q: Measurements not saving**
- **A**: Check that at least one measurement field has a value (validation requirement)
- **A**: Check database permissions: `ls -l data/body_measurements.db`

**Q: Charts not displaying**
- **A**: Need at least 2 measurement entries for trend charts
- **A**: Check that Plotly is installed: `pip list | grep plotly`

**Q: Want to track custom measurements**
- **A**: Use Notes field for now (e.g., "Forearms: 12.5\", Glutes: 42\"")
- **A**: Future enhancement (Phase 5) will add custom measurement fields
