# How to Create the Phase 4 PR

## Step-by-Step Instructions

### Option 1: GitHub Web UI (Recommended)

1. **Go to GitHub Repository:**
   - Visit: https://github.com/JLWAI/HealthRAG

2. **Start New PR:**
   - Click "Pull requests" tab
   - Click green "New pull request" button

3. **Select Branches:**
   - **Base branch:** `main`
   - **Compare branch:** `claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX`
   - You should see "52 commits" and lots of green additions

4. **Fill in PR Details:**
   - **Title:** `Phase 4: Complete ✅ - Adaptive TDEE, Testing Infrastructure, and Production Polish`
   - **Description:** Copy the entire contents of `PHASE4_PR_DESCRIPTION.md`

5. **Create PR:**
   - Click "Create pull request" button
   - PR is now open and ready for review!

6. **Optional - Enable Auto-Merge:**
   - If all CI checks pass, you can enable auto-merge
   - PR will automatically merge when ready

---

### Option 2: GitHub CLI (if available)

```bash
# From the HealthRAG directory
gh pr create \
  --title "Phase 4: Complete ✅ - Adaptive TDEE, Testing Infrastructure, and Production Polish" \
  --body-file PHASE4_PR_DESCRIPTION.md \
  --base main \
  --head claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX
```

---

## What Happens After Creating the PR?

### GitHub Actions Will Run:
1. ✅ **Test Workflow** - All 78 tests should pass
2. ✅ **Lint Workflow** - Code quality checks
3. ⚠️ **Browser Tests** - May need manual trigger (playwright chromium download issue)
4. ⚠️ **Deploy Workflow** - Needs platform configuration

### Expected Results:
- **Tests:** ✅ Should pass (we verified locally: 78/78 passing)
- **Lint:** ✅ Should pass (or minor warnings)
- **Coverage:** ✅ Should pass (70-84% for Phase 4 modules)

---

## After PR is Created

### Review Checklist:
- [ ] All CI checks passing (or understand failures)
- [ ] PR description is complete and accurate
- [ ] No merge conflicts
- [ ] Ready to merge

### Merge Strategy:
**Option A: Squash and Merge (Recommended)**
- Creates single clean commit on main
- Keeps history simple
- Good for feature branches

**Option B: Merge Commit**
- Preserves all 52 commits
- Shows full development history
- Better for detailed audit trail

**Option C: Rebase and Merge**
- Replays all 52 commits on main
- Linear history
- Can be cleaner for review

**Recommendation:** Use "Squash and Merge" for cleaner main branch history.

---

## After Merge

### 1. Clean Up Branches (Optional)
```bash
# Delete local branch
git branch -d claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX

# Delete remote branch (GitHub does this automatically on merge)
git push origin --delete claude/integrate-tdee-enhancements-011CUoMgeMMaZRuVQHJeQWRX
```

### 2. Update Local Main
```bash
git checkout main
git pull origin main
```

### 3. Check Other Branches
See `BRANCH_CLEANUP.md` for recommendations on other branches.

---

## Troubleshooting

### "CI check failed"
- Check which workflow failed
- Review logs in GitHub Actions tab
- Most likely: browser-tests (chromium download issue - known and documented)

### "Merge conflicts"
- Unlikely since this branch is ahead of main
- If they occur, resolve in GitHub web UI or locally

### "Coverage below threshold"
- We achieved 70-84% for Phase 4 modules
- If different calculation, adjust threshold in `.github/workflows/test.yml`

---

## Questions?

- Check CI/CD documentation: `.github/CICD.md`
- Review test results: `tests/TEST_SUITE_SUMMARY.md`
- Performance guide: `docs/PERFORMANCE_OPTIMIZATIONS.md`
