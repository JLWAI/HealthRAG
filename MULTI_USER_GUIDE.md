# Multi-User Guide & Profile Management

## Quick Profile Management

### ✅ What Works Now (No Re-Entry Required!)

**Edit Profile Anytime:**
1. Go to Streamlit app sidebar
2. Expand "✏️ Edit Profile"
3. Change weight, goals, equipment, training schedule
4. Click "💾 Save Changes"
5. Changes persist immediately - no need to re-enter everything!

**Update Training Program:**
1. Make profile changes (see above)
2. Go to "💪 Your Training Program" section
3. Click "🆕 Generate New Program"
4. Old program auto-saved in history
5. New program reflects your updated settings

**Equipment Management:**
Quick presets available:
- **Home Gym - Advanced**: Jason's full setup (Smith, cables, machines)
- **Planet Fitness**: Complete PF equipment list
- **Home Gym + PF**: Combined access (best coverage)
- **Custom**: Pick individual equipment items

---

## Multi-User Scenarios

### Scenario 1: Jason & Wife Using Same Computer

**Current Workaround (Manual Profile Switching):**

#### Option A: Shared Profile with Manual Updates
1. Both use same profile
2. Update weight before each workout
3. Share same training program
4. **Pros:** Simple, no profile switching
5. **Cons:** Programs not personalized per person

#### Option B: Separate Profile Files (Manual Switching)
1. Create Jason's profile → Saves to `data/user_profile.json`
2. Rename to `data/jason_profile.json`
3. Create wife's profile → Saves to `data/user_profile.json`
4. Rename to `data/wife_profile.json`
5. Before using app:
   - Jason: Copy `jason_profile.json` → `user_profile.json`
   - Wife: Copy `wife_profile.json` → `user_profile.json`

**Shell script to switch profiles:**
```bash
# switch_profile.sh
#!/bin/bash

if [ "$1" == "jason" ]; then
    cp data/jason_profile.json data/user_profile.json
    echo "Switched to Jason's profile"
elif [ "$1" == "wife" ]; then
    cp data/wife_profile.json data/user_profile.json
    echo "Switched to Wife's profile"
else
    echo "Usage: ./switch_profile.sh [jason|wife]"
fi
```

Usage:
```bash
chmod +x switch_profile.sh
./switch_profile.sh jason   # Switch to Jason
./switch_profile.sh wife    # Switch to wife
streamlit run src/main.py
```

---

## Future Enhancement: Proper Multi-User Support

### Planned Features (Phase 5):

**Profile Selector at App Start:**
```
┌─────────────────────────────────────┐
│   Welcome to HealthRAG              │
│                                     │
│   Select Your Profile:              │
│   ○ Jason                           │
│   ○ Sarah                           │
│   ○ + Create New Profile            │
│                                     │
│   [Continue] →                      │
└─────────────────────────────────────┘
```

**Implementation:**
- Profiles stored as `data/profiles/jason.json`, `data/profiles/sarah.json`
- Active profile tracked in `data/active_user.txt`
- Training programs per user: `data/programs/jason/`, `data/programs/sarah/`
- Nutrition logs per user: `data/nutrition/jason/`, `data/nutrition/sarah/`
- Weight tracking per user
- Separate progress graphs per user

---

## Current Profile Editing Capabilities

### ✅ Can Edit Without Re-Entering Everything:

**Personal Info:**
- ✅ Weight (update frequently!)
- ✅ Activity level
- ✅ Age (if birthday passed)

**Goals:**
- ✅ Phase (cut → bulk → recomp → maintain)
- ✅ Target weight
- ✅ Timeline

**Training:**
- ✅ Training level (beginner → intermediate → advanced)
- ✅ Days per week
- ✅ Preferred split

**Equipment:**
- ✅ Use presets (Home Gym Advanced, Planet Fitness, etc.)
- ✅ Add individual items (bought new equipment)
- ✅ Remove items (sold equipment)

### ⚠️ Currently Requires Profile Deletion to Change:

- ❌ Name
- ❌ Height
- ❌ Sex

**Workaround:** Edit `data/user_profile.json` directly:
```json
{
  "personal_info": {
    "name": "Jason",           ← Change this
    "height_inches": 69,       ← Or this
    "sex": "male"              ← Or this
  }
}
```

---

## Equipment Update Workflow

### Example: Jason Adds Leg Press to Home Gym

**Current Workflow:**
1. Sidebar → "✏️ Edit Profile"
2. Equipment Access → "Custom Selection"
3. Add "leg_press_machine" to list
4. Click "💾 Save Changes"
5. Go to "💪 Your Training Program" section
6. Click "🆕 Generate New Program"
7. New program includes leg press exercises!
8. Old program saved in history

**Takes:** ~30 seconds

---

## Example: Wife Creates Her Profile

### Step 1: Jason Backs Up His Profile
```bash
cp data/user_profile.json data/jason_profile.json
```

### Step 2: Delete Current Profile in App
1. Sidebar → "🗑️ Delete Profile"
2. Confirm deletion

### Step 3: Wife Completes Onboarding
1. App shows onboarding wizard
2. Step 1: Import from Apple Health or manual entry
   - Name: Sarah
   - Weight: 135 lbs
   - Height: 5'6"
   - Age: 48
   - Sex: Female
3. Step 2: Personal info entered
4. Step 3: Goals
   - Phase: Recomp (build muscle + lose fat)
   - Focus: Hypertrophy
5. Step 4: Equipment
   - Select: "Home Gym + Planet Fitness"
   - Days: 4x/week
   - Split: Upper/Lower
6. Step 5: Review & Create
7. ✅ Profile created → `data/user_profile.json`

### Step 4: Backup Wife's Profile
```bash
cp data/user_profile.json data/sarah_profile.json
```

### Step 5: Restore Jason's Profile
```bash
cp data/jason_profile.json data/user_profile.json
```

### Step 6: Switching Profiles
Use the `switch_profile.sh` script above, or manually:
```bash
# Jason's turn
cp data/jason_profile.json data/user_profile.json

# Sarah's turn
cp data/sarah_profile.json data/user_profile.json
```

---

## Program Regeneration - No Re-Entry!

### Scenario: Jason Loses 10 lbs, Wants Updated Program

**OLD Way (annoying):**
1. Delete profile
2. Re-enter all personal info
3. Re-enter all goals
4. Re-select all equipment
5. Generate program

**NEW Way (30 seconds):**
1. Sidebar → "✏️ Edit Profile"
2. Update weight: 221 lbs → 211 lbs
3. Click "💾 Save Changes"
4. Scroll to "💪 Your Training Program"
5. Click "🆕 Generate New Program"
6. Done! Old program in history.

---

## Equipment Scenarios

### Adding Planet Fitness Membership

**Current equipment:** Home Gym Advanced (22 items)

**Steps:**
1. Sidebar → "✏️ Edit Profile"
2. Equipment Access → "Home Gym + PF (Best of Both)"
3. Click "💾 Save Changes"
4. Message shows: "43 items selected"
5. Training Program → "🆕 Generate New Program"
6. New program includes PF-exclusive exercises:
   - Leg Press
   - Hack Squats
   - Pec Deck
   - More machine variations

**Takes:** 30 seconds

### Canceling Planet Fitness, Home Only

**Steps:**
1. Equipment Access → "Home Gym - Advanced"
2. Save Changes
3. Generate New Program
4. Program now uses only home equipment

---

## Profile Persistence - What's Saved

**Automatically Persists:**
- ✅ All personal info
- ✅ All goals
- ✅ All equipment
- ✅ All training preferences
- ✅ Updated timestamp

**Survives:**
- ✅ App restart
- ✅ Computer restart
- ✅ Streamlit refresh

**Stored in:**
- `data/user_profile.json` - Current active profile
- `data/programs/` - All training program history
- `data/active_program.json` - Currently active program

---

## Common Questions

### Q: Do I need to re-enter everything to change my weight?
**A:** No! Edit Profile → Update weight → Save. Done in 10 seconds.

### Q: Will updating my equipment delete my programs?
**A:** No! Your current program stays in history. Generate a new one to use updated equipment.

### Q: Can my wife and I both use this?
**A:** Yes, but requires manual profile switching (see guide above). Proper multi-user coming in Phase 5.

### Q: What if I buy new equipment (e.g., add a leg press)?
**A:** Edit Profile → Equipment → Custom → Add "leg_press_machine" → Save → Generate New Program

### Q: Do I lose my progress when I update my profile?
**A:** No! All programs are saved in history. Weight logs, workout logs, and nutrition logs persist separately.

### Q: Can I switch between home gym and Planet Fitness easily?
**A:** Yes! Edit Profile → Equipment Access → Select preset → Save (30 seconds)

---

## Phase 5 Multi-User Roadmap

**Planned Features:**
1. Profile selector on app start
2. Per-user data directories
3. Quick profile switching (no file copying)
4. Per-user program history
5. Per-user nutrition tracking
6. Per-user weight graphs
7. Family progress dashboard (optional)

**Timeline:** After Phase 4 nutrition tracking complete (Week 15+)

---

## Summary

### ✅ Current Capabilities:
- Edit profile without re-entering everything
- Update weight, goals, equipment, schedule easily
- Equipment presets (Home Gym Advanced, Planet Fitness, Combined)
- Program regeneration in 30 seconds
- All changes persist automatically
- Program history preserved

### ⏳ Coming Soon (Phase 5):
- Proper multi-user profile management
- Profile selector at app start
- No manual file switching needed
- Per-user dashboards

### 🛠️ Current Workaround for Multiple Users:
- Manual profile file switching
- Shell script provided above
- Simple but effective until Phase 5
