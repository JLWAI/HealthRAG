# Branch Cleanup Recommendations

## Current Branch Status

### ✅ Active Branch (Keep Until PR Merged)
**`claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX`**
- **Status:** Ready for PR to main
- **Commits Ahead:** 52 commits
- **Contains:** All Phase 4 work + 7 new commits (testing, CI/CD, performance, docs)
- **Action:** Create PR, then delete after merge

---

### 🗑️ Branches to Delete (After PR Merged)

#### 1. `feat/phase4-tracking-ui`
**Why Delete:**
- All commits from this branch are in `claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX`
- Superseded by the claude branch which has additional improvements

**Verification:**
```bash
# Check if all commits are in current branch
git log --oneline feat/phase4-tracking-ui | head -10
# All these commits appear in claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX
```

**How to Delete (after PR merge):**
```bash
# Delete local branch
git branch -d feat/phase4-tracking-ui

# Delete remote branch
git push origin --delete feat/phase4-tracking-ui
```

---

#### 2. `claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX`
**Why Consider Deleting:**
- Contains 2 commits: planning documentation and TDEE enhancement suite
- The TDEE work has been superseded by more complete implementation in current branch

**Verification Needed:**
```bash
# Check what's unique on this branch
git log claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX --not main
```

**Commits on this branch:**
- `111334d` - Add comprehensive TDEE enhancement suite - MacroFactor-inspired features
- `0f10dba` - Add comprehensive planning documentation for diet/nutrition and exercise features

**Decision:**
- If these planning docs are valuable and not in current branch, cherry-pick them first
- Otherwise, safe to delete after PR merge

**How to Delete (after verification):**
```bash
# Delete local branch
git branch -d claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX

# Delete remote branch
git push origin --delete claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX
```

---

### 📦 Already Merged Branches (Check if Can Delete)

These remote branches may already be merged to main:

```bash
# Check status
git branch -r --merged origin/main
```

Likely candidates for deletion:
- `remotes/origin/feat/phase2-user-profile-system`
- `remotes/origin/feat/phase3-program-generation`
- `remotes/origin/feat/project-cleanup-and-documentation`
- `remotes/origin/feat/week3-proactive-dashboard`

**How to verify and delete:**
```bash
# For each merged branch, delete from remote
git push origin --delete feat/phase2-user-profile-system
git push origin --delete feat/phase3-program-generation
git push origin --delete feat/project-cleanup-and-documentation
git push origin --delete feat/week3-proactive-dashboard
```

---

## Step-by-Step Cleanup Process

### After Phase 4 PR is Merged

**1. Update local main:**
```bash
git checkout main
git pull origin main
```

**2. Delete local branches:**
```bash
# Delete the claude branch (now merged)
git branch -d claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX

# Delete superseded feat branch
git branch -d feat/phase4-tracking-ui

# Delete review branch (after verifying)
git branch -d claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX
```

**3. Delete remote branches:**
```bash
# GitHub usually auto-deletes PR branch on merge, but if not:
git push origin --delete claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX

# Delete other obsolete branches
git push origin --delete feat/phase4-tracking-ui
git push origin --delete claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX
```

**4. Clean up old merged branches:**
```bash
# Delete old feature branches (verify they're merged first!)
git push origin --delete feat/phase2-user-profile-system
git push origin --delete feat/phase3-program-generation
git push origin --delete feat/project-cleanup-and-documentation
git push origin --delete feat/week3-proactive-dashboard
```

**5. Prune deleted remote branches locally:**
```bash
git fetch --prune
```

---

## Final Branch State (After Cleanup)

### Branches to Keep:
- **`main`** - Production branch
- Any active development branches (none currently)

### Branches Deleted:
- ✅ `claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX` (merged to main)
- ✅ `feat/phase4-tracking-ui` (superseded)
- ✅ `claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX` (superseded)
- ✅ Old merged feature branches

---

## Verification Commands

**Before deleting any branch, verify it's safe:**

```bash
# Check if branch is merged to main
git branch --merged main | grep <branch-name>

# Check what commits are unique to the branch
git log <branch-name> --not main --oneline

# Check if commits are in another branch
git log <other-branch> --oneline | grep <commit-hash>
```

**Safe delete commands:**
```bash
# This will only delete if branch is merged
git branch -d <branch-name>

# Force delete (use cautiously)
git branch -D <branch-name>
```

---

## Summary

**Immediate Action (After PR Merge):**
1. Delete `claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX` (merged)
2. Delete `feat/phase4-tracking-ui` (superseded)

**Optional Cleanup:**
1. Delete `claude/review-diet-nutrition-011CUoMgeMMaZRuVQHJeQWRX` (verify first)
2. Delete old merged feature branches

**Result:**
- Clean repository with only `main` branch
- Ready for Phase 5 development
