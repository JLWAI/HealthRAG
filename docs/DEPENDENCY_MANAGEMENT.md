# 📦 Dependency Management Guide

## Overview

HealthRAG uses an automated dependency management system to keep packages up-to-date and secure while minimizing manual work.

**Goals:**
- 🔒 Keep dependencies secure (patch CVEs quickly)
- 🆕 Stay current with latest features and bug fixes
- ⚡ Minimize time spent on routine updates (target: <1 hour/week)
- 🧪 Prevent breaking changes through automated testing
- 📝 Maintain clear documentation of changes

---

## 🤖 Automated Systems

### 1. Weekly Dependency Check (GitHub Actions)

**File:** `.github/workflows/weekly-dependency-check.yml`

**Schedule:** Every Monday at 2 AM UTC

**What It Does:**
1. Scans all Python dependencies for updates
2. Runs security audit with `pip-audit`
3. Checks for CVEs and vulnerabilities
4. **Automatically creates GitHub issue** with findings
5. Prioritizes by severity (security issues = HIGH priority)

**View Results:**
- GitHub Actions: https://github.com/[username]/HealthRAG/actions
- Issues: Labeled with `dependencies`, `maintenance`
- Artifacts: Security reports stored for 30 days

**Manual Trigger:**
```bash
# Via GitHub UI: Actions → Weekly Dependency Check → Run workflow
# Or via CLI:
gh workflow run weekly-dependency-check.yml
```

---

### 2. Dependabot (GitHub Native)

**File:** `.github/dependabot.yml`

**Schedule:** Weekly (Monday 3 AM UTC, after dependency check)

**What It Does:**
1. Automatically creates PRs for dependency updates
2. Groups updates by severity/type:
   - **Security patches**: Auto-created immediately
   - **Minor/patch**: Grouped weekly
   - **Major versions**: Separate PRs (manual review required)
3. Runs CI/CD tests on each PR
4. Can be configured for auto-merge (security patches only)

**Configuration:**
- Open PRs limit: 10 max
- Target branch: `main`
- Assignee: @jasonewillis
- Labels: `dependencies`, `automated`

**Ignore Major Updates:**
- `langchain` (breaking changes common)
- `streamlit` (UI compatibility)
- `mlx` (Apple Silicon specific)

---

## 📋 Weekly Workflow

### For Developers (You)

**Time Investment:** ~1-2 hours/week (routine) or 3-4 hours (if major updates)

#### Monday Morning Routine:

1. **Check GitHub Issues**
   ```bash
   gh issue list --label "dependencies"
   ```
   - Look for auto-created issue: `[DEPS] Weekly Dependency Update - Week XX`
   - Review security vulnerabilities (HIGH priority)
   - Review outdated packages (MEDIUM priority)

2. **Review Dependabot PRs**
   ```bash
   gh pr list --label "dependencies"
   ```
   - Security patches: Review and merge quickly
   - Minor/patch: Test locally if concerned
   - Major updates: Read changelog before merging

3. **Create Update Branch**
   ```bash
   git checkout main
   git pull
   git checkout -b deps/weekly-update-$(date +%Y-%m-%d)
   ```

4. **Run Security Audit Locally**
   ```bash
   pip install pip-audit
   pip-audit --desc
   ```
   - Fix HIGH/CRITICAL vulnerabilities immediately
   - Document MEDIUM/LOW for batch updates

5. **Update Dependencies**
   ```bash
   # Check what's outdated
   pip list --outdated

   # Update specific packages
   pip install --upgrade <package-name>

   # Or update all (CAUTION)
   pip list --outdated --format=json | jq -r '.[] | .name' | xargs pip install --upgrade

   # Test immediately after
   python3 -c "import <package>; print(<package>.__version__)"
   ```

6. **Run Test Suite**
   ```bash
   # Quick smoke tests
   python3 src/rag_system.py
   python3 tests/test_meal_prep_workflow.py

   # Full test suite
   pytest tests/ -v

   # Streamlit UI test
   streamlit run src/main.py --server.port 8503
   # Manually test: profile, nutrition, workouts, camera scanning
   ```

7. **Update Requirements Files**
   ```bash
   # Generate new requirements
   pip freeze > requirements-new.txt

   # Compare changes
   diff requirements.txt requirements-new.txt

   # Update if tests pass
   mv requirements-new.txt requirements.txt

   # Update MLX-specific (if changed)
   pip freeze | grep -E "(mlx|numpy)" > requirements-mlx.txt

   # Update Ollama-specific (if changed)
   pip freeze | grep -E "(langchain|chromadb)" > requirements-ollama.txt
   ```

8. **Commit and Create PR**
   ```bash
   git add requirements*.txt
   git commit -m "chore(deps): weekly dependency update - $(date +%Y-%m-%d)

   - Updated X packages (see issue #XXX)
   - Fixed Y security vulnerabilities
   - All tests passing
   - No breaking changes"

   git push -u origin deps/weekly-update-$(date +%Y-%m-%d)

   gh pr create \
     --title "Weekly Dependency Update - $(date +%Y-%m-%d)" \
     --body "Closes #XXX (auto-generated issue)" \
     --label "dependencies,maintenance"
   ```

9. **Merge and Close Issue**
   ```bash
   # After PR approval (or self-merge for solo dev)
   gh pr merge --squash --delete-branch

   # Close the weekly issue with summary
   gh issue close <issue-number> --comment "✅ Completed. See PR #XXX. Summary:
   - Updated X packages
   - Fixed Y vulnerabilities
   - Tests passing
   - Time spent: ~X hours"
   ```

---

## 🚨 Emergency Security Updates

If a HIGH/CRITICAL CVE is discovered mid-week:

### Immediate Response (< 1 hour)

1. **Verify Impact**
   ```bash
   pip show <vulnerable-package>
   pip-audit --desc | grep <vulnerable-package>
   ```

2. **Create Hotfix Branch**
   ```bash
   git checkout main
   git pull
   git checkout -b hotfix/security-<package>-$(date +%Y-%m-%d)
   ```

3. **Update Package**
   ```bash
   pip install --upgrade <package>==<safe-version>
   ```

4. **Quick Test**
   ```bash
   # Test only affected functionality
   python3 -c "import <package>; print('OK')"
   # Run critical path tests only
   ```

5. **Emergency Deploy**
   ```bash
   git add requirements*.txt
   git commit -m "fix(security): patch <CVE-ID> in <package>

   - Upgraded <package> from vX.X.X to vY.Y.Y
   - Addresses CVE-YYYY-XXXXX (HIGH severity)
   - Minimal testing completed
   - Full regression testing in progress"

   git push -u origin hotfix/security-<package>-$(date +%Y-%m-%d)

   # Skip PR for critical security (if solo dev)
   git checkout main
   git merge hotfix/security-<package>-$(date +%Y-%m-%d) --no-ff
   git push origin main

   # Or create emergency PR
   gh pr create --title "[SECURITY] Patch <CVE-ID>" --label "security,urgent"
   ```

6. **Document and Monitor**
   - Create incident report issue
   - Schedule full regression testing
   - Monitor for related CVEs

---

## 🛠️ Local Testing Commands

### Pre-Update Baseline
```bash
# Capture current state
pip freeze > baseline-requirements.txt
python3 tests/test_all.py > baseline-tests.txt

# Run performance baseline
time python3 -c "from rag_system import HealthRAG; rag = HealthRAG(); rag.query('test')"
```

### Post-Update Validation
```bash
# Compare requirements
diff baseline-requirements.txt requirements.txt

# Compare test results
python3 tests/test_all.py > updated-tests.txt
diff baseline-tests.txt updated-tests.txt

# Performance regression check
time python3 -c "from rag_system import HealthRAG; rag = HealthRAG(); rag.query('test')"
# Should be within 10% of baseline
```

### Critical Path Tests
```bash
# 1. MLX/Ollama backends
python3 -c "from rag_system import HealthRAG; print(HealthRAG('mlx').query('test'))"
python3 -c "from rag_system import HealthRAG; print(HealthRAG('ollama').query('test'))"

# 2. Database operations
python3 -c "from food_logger import FoodLogger; logger = FoodLogger('data/test.db'); print('OK')"

# 3. API clients
USDA_FDC_API_KEY=$(grep USDA_FDC_API_KEY data/.env | cut -d '=' -f2)
python3 src/food_api_fdc.py

# 4. Barcode scanning
python3 -c "from pyzbar import pyzbar; from PIL import Image; print('OK')"

# 5. Program generation
python3 -c "from program_generator import ProgramGenerator; print('OK')"

# 6. Full meal prep workflow
python3 tests/test_meal_prep_workflow.py

# 7. Streamlit UI (manual)
streamlit run src/main.py --server.port 8503
# Test all tabs, especially camera scanning
```

---

## 📊 Monitoring & Alerts

### Weekly Health Check

Run before Monday's dependency update:

```bash
#!/bin/bash
# scripts/dependency_health_check.sh

echo "=== Dependency Health Check ==="
echo ""

echo "1. Outdated Packages:"
pip list --outdated --format=columns | head -20

echo ""
echo "2. Security Vulnerabilities:"
pip-audit --desc | grep -E "CRITICAL|HIGH" || echo "None found"

echo ""
echo "3. Dependency Tree Issues:"
pipdeptree --warn silence | grep -E "Warning|Error" || echo "No issues"

echo ""
echo "4. Package Conflicts:"
pip check

echo ""
echo "5. Disk Usage:"
du -sh ~/.cache/pip
du -sh ~/.cache/huggingface

echo ""
echo "✅ Health check complete!"
```

### Set Up Alerts

**Option 1: GitHub Notifications**
- Settings → Notifications → Enable for "Dependencies"
- Email alerts for security issues

**Option 2: Slack/Discord (Future)**
```yaml
# Add to workflow:
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "⚠️ Security vulnerabilities found in HealthRAG dependencies",
        "attachments": [...]
      }
```

---

## 🎯 Best Practices

### ✅ DO:
- ✅ Review security updates within 24 hours
- ✅ Test updates in development branch first
- ✅ Update one major dependency at a time
- ✅ Read changelogs for major version bumps
- ✅ Pin versions that break compatibility (document why)
- ✅ Keep requirements.txt under version control
- ✅ Run full test suite before merging

### ❌ DON'T:
- ❌ Update production without testing
- ❌ Ignore security vulnerabilities
- ❌ Update all packages at once blindly
- ❌ Skip test suite "to save time"
- ❌ Deploy on Friday afternoon
- ❌ Force-push to main branch
- ❌ Update during active development

---

## 🔧 Troubleshooting

### Issue: Dependabot Not Running

**Check:**
```bash
# Verify file exists and is valid YAML
cat .github/dependabot.yml | yaml-lint

# Check GitHub settings
gh api repos/:owner/:repo/automated-security-fixes
```

**Fix:**
- Enable Dependabot in: Settings → Security → Dependabot

### Issue: Workflow Failing

**Check Logs:**
```bash
gh run list --workflow=weekly-dependency-check
gh run view <run-id> --log
```

**Common Causes:**
- Rate limiting (GitHub API or PyPI)
- Timeout (increase `timeout-minutes`)
- Permissions (add `contents: write` to workflow)

### Issue: Conflicting Dependencies

**Investigate:**
```bash
pipdeptree --packages <package-name>
pip show <package-name>
```

**Resolve:**
```bash
# Option 1: Pin conflicting package
echo "<package>==<version>" >> requirements.txt

# Option 2: Upgrade/downgrade dependency
pip install <package>==<compatible-version>

# Option 3: Use virtual environment isolation
# (Already using venv, but ensure clean state)
```

---

## 📚 Resources

### Tools:
- **pip-audit**: https://github.com/pypa/pip-audit
- **pipdeptree**: https://github.com/tox-dev/pipdeptree
- **Dependabot**: https://docs.github.com/en/code-security/dependabot
- **GitHub Actions**: https://docs.github.com/en/actions

### Security Databases:
- **CVE Database**: https://cve.mitre.org/
- **PyPI Advisory DB**: https://github.com/pypa/advisory-database
- **Snyk Vulnerability DB**: https://security.snyk.io/

### Dependency Docs:
- **MLX**: https://ml-explore.github.io/mlx/
- **LangChain**: https://python.langchain.com/docs/changelog
- **Streamlit**: https://docs.streamlit.io/library/changelog
- **ChromaDB**: https://docs.trychroma.com/

---

## 📅 Maintenance Schedule

| Day | Task | Time | Priority |
|-----|------|------|----------|
| Monday 2am | Automated dependency check (GH Actions) | Auto | High |
| Monday 3am | Dependabot PRs created | Auto | Medium |
| Monday 9am | Review issues & PRs (YOU) | 1-2h | High |
| Monday EOD | Merge updates & close issue (YOU) | 30m | High |
| Daily | Monitor security alerts | 5m | Critical |
| Monthly | Deep dependency audit | 2-3h | Medium |
| Quarterly | Clean unused dependencies | 1-2h | Low |

---

## ✅ Success Metrics

**Weekly Goals:**
- [ ] Zero HIGH/CRITICAL security vulnerabilities
- [ ] <10 outdated packages at week end
- [ ] <2 hours time spent on updates
- [ ] 100% test pass rate after updates
- [ ] Zero production incidents from updates

**Monthly Review:**
- Total packages updated: X
- Security patches applied: X
- Breaking changes handled: X
- Average update time: X hours/week
- Incidents caused by updates: X (goal: 0)

---

## 🚀 Next Steps

1. **Enable Dependabot:**
   - Go to: https://github.com/[username]/HealthRAG/settings/security_analysis
   - Enable "Dependabot alerts" and "Dependabot security updates"

2. **Test Workflows:**
   ```bash
   # Trigger workflow manually
   gh workflow run weekly-dependency-check.yml

   # Watch progress
   gh run watch
   ```

3. **First Weekly Update:**
   - Wait for Monday 2am UTC (or trigger manually)
   - Follow issue template step-by-step
   - Document time spent for future estimation

4. **Configure Notifications:**
   - Set up email alerts for security issues
   - Consider Slack integration for team (future)

5. **Schedule Calendar Reminder:**
   - Add "Dependency Review" to Monday morning routine
   - Block 1-2 hours for maintenance

---

**Questions?** See `.github/ISSUE_TEMPLATE/weekly-dependency-update.md` for detailed procedures.
