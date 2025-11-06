# CI/CD Documentation

This document describes the GitHub Actions workflows configured for HealthRAG.

## Workflows Overview

### 1. Test Suite (`test.yml`)

**Purpose:** Run automated tests on every push and pull request to ensure code quality and prevent regressions.

**Triggers:**
- Push to `main` branch
- Push to `feat/**` branches
- Pull requests to `main`

**Jobs:**

#### `test` (Matrix: Python 3.10, 3.11)
- Install dependencies (with pip caching)
- Run unit tests with coverage
- Run integration tests (excluding slow tests)
- Check coverage threshold (≥75%)
- Upload coverage to Codecov
- Upload test results and HTML reports

**Key Features:**
- Matrix testing across Python 3.10 and 3.11
- Fail-fast disabled (all versions tested even if one fails)
- Coverage reports uploaded to Codecov
- Test results uploaded as artifacts (30-day retention)
- Coverage threshold: 75% minimum

#### `slow-tests` (Python 3.10 only)
- Runs only on push to `main` (not on PRs)
- Executes tests marked with `@pytest.mark.slow`
- Separate from main test job to keep PR checks fast

#### `test-summary`
- Downloads all test artifacts
- Posts coverage summary to PR comments
- Provides links to detailed reports

**Artifacts Generated:**
- `coverage-report-{version}/` - HTML coverage reports
- `test-results-{version}/` - JUnit XML test results
- `slow-test-results/` - Slow test results (main branch only)

**Status Badge:**
```markdown
[![Test Suite](https://github.com/jasonlws/HealthRAG/actions/workflows/test.yml/badge.svg)](https://github.com/jasonlws/HealthRAG/actions/workflows/test.yml)
```

---

### 2. Code Quality (`lint.yml`)

**Purpose:** Enforce code style, formatting, and quality standards.

**Triggers:**
- Push to `main` branch
- Push to `feat/**` branches
- Pull requests to `main`

**Jobs:**

#### `lint`
1. **Flake8** - Python linting
   - Checks for syntax errors, undefined names, unused imports
   - Max line length: 100 characters
   - Max complexity: 15
   - Configuration: `.flake8`

2. **Black** - Code formatting
   - Checks if code follows Black's opinionated style
   - Fails if any files need reformatting
   - Configuration: `pyproject.toml`

3. **isort** - Import sorting
   - Ensures imports are properly organized
   - Compatible with Black
   - Configuration: `pyproject.toml`

4. **MyPy** - Type checking (non-blocking)
   - Static type analysis
   - Continues even if type errors found (warnings only)
   - Configuration: `pyproject.toml`

#### `security-scan`
1. **Trivy** - Vulnerability scanner
   - Scans filesystem for known vulnerabilities
   - Uploads results to GitHub Security tab

2. **Bandit** - Security linter for Python
   - Detects common security issues in Python code
   - Reports uploaded as artifacts

**Artifacts Generated:**
- `lint-reports/` - Flake8, Black, isort, MyPy reports
- `security-reports/` - Trivy SARIF, Bandit JSON

**Fix Commands:**
```bash
# Fix formatting issues
black src/ tests/
isort src/ tests/

# Check for remaining issues
flake8 src/ tests/
```

**Status Badge:**
```markdown
[![Code Quality](https://github.com/jasonlws/HealthRAG/actions/workflows/lint.yml/badge.svg)](https://github.com/jasonlws/HealthRAG/actions/workflows/lint.yml)
```

---

### 3. Browser Tests (`browser-tests.yml`)

**Purpose:** End-to-end testing with Playwright for critical user flows.

**Triggers:**
- **Manual workflow dispatch** (recommended)
- **Weekly schedule** (Monday 3 AM UTC)

**Why Manual?**
Browser tests are expensive and slow (~10-30 minutes). Run them:
- Before major releases
- After significant UI changes
- Weekly via scheduled run
- When debugging browser-specific issues

**Jobs:**

#### `browser-tests` (Matrix: Chromium, Firefox, Webkit)
1. Install Playwright browsers
2. Start Streamlit app in background
3. Wait for app health check
4. Run Playwright tests
5. Stop Streamlit app
6. Upload test artifacts

**Playwright Configuration:**
- Headed mode: `false` (headless)
- Slow motion: 100ms (for better video capture)
- Video: Always recorded
- Screenshots: On failure only
- Tracing: On failure only

**Artifacts Generated:**
- `browser-test-results-{browser}/` - Test results and reports
- `browser-test-videos-{browser}/` - Video recordings (14-day retention)
- `browser-test-screenshots-{browser}/` - Failure screenshots (14-day retention)
- `streamlit.log` - Application logs

#### `report`
- Aggregates results from all browsers
- Creates summary table
- Links to artifacts

#### `notify-on-failure`
- Creates GitHub issue if weekly scheduled run fails
- Labels: `bug`, `testing`, `ci/cd`

**Manual Trigger Options:**
- **Test Pattern:** Specify which tests to run (default: `tests/browser/`)
- **Browser:** Choose browser (chromium, firefox, webkit, or all)

**Example Manual Trigger:**
```bash
# Via GitHub UI: Actions → Browser Tests (E2E) → Run workflow
# Or via GitHub CLI:
gh workflow run browser-tests.yml -f browser=chromium -f test_pattern=tests/browser/test_phase4_comprehensive.py
```

---

### 4. Deploy (`deploy.yml`)

**Purpose:** Automated deployment pipeline with testing, building, and release management.

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Jobs:**

#### `pre-deploy-tests`
- Runs fast unit tests as smoke test
- Skippable via manual trigger input (not recommended)

#### `build`
1. Set up Docker Buildx
2. Log in to GitHub Container Registry (GHCR)
3. Build and push Docker image
4. Tag with multiple strategies:
   - `main` branch → `latest`
   - Git SHA → `main-{sha}`
   - Semver tags → `v1.2.3`, `v1.2`

**Image Tags:**
- `ghcr.io/jasonlws/healthrag:latest` (main branch)
- `ghcr.io/jasonlws/healthrag:main-{sha}` (commit SHA)

#### `test-image`
- Pull built Docker image
- Run container smoke test
- Check health endpoint
- Verify container starts successfully

#### `deploy`
- Environment: `production` or `staging`
- **PLACEHOLDER:** Add your deployment commands here
- Examples:
  - Render.com: Trigger deploy webhook
  - Heroku: `heroku container:push web`
  - AWS ECS: Update task definition
  - Google Cloud Run: `gcloud run deploy`

**To configure deployment:**
1. Add your deployment platform credentials to GitHub Secrets
2. Update the "Placeholder Deploy Step" with actual commands
3. Configure GitHub Environments (Settings → Environments)

#### `create-release`
- Runs only on `main` branch pushes
- Generates semantic version: `v0.4.{commit_count}`
- Creates Git tag
- Generates changelog from commits
- Creates GitHub Release

#### `notify`
- Success: Adds summary to workflow
- Failure: Creates GitHub issue with alert

**Manual Trigger Options:**
- **Environment:** production or staging
- **Skip Tests:** Skip pre-deploy tests (not recommended)

**GitHub Environments:**
Configure protection rules in Settings → Environments:
- `production`: Require approval, restrict to main branch
- `staging`: Auto-deploy, allow any branch

---

### 5. Weekly Dependency Check (`weekly-dependency-check.yml`)

**Purpose:** Automated dependency monitoring and security auditing.

**Triggers:**
- Weekly schedule (Monday 2 AM UTC)
- Manual workflow dispatch

**What It Does:**
1. Checks for outdated packages
2. Runs security audit (`pip-audit`)
3. Generates dependency tree
4. Creates GitHub issue if updates needed
5. Labels issues by priority (security vs routine)

**Issue Labels:**
- High priority: Security vulnerabilities found
- Medium priority: Routine updates only

---

## Best Practices

### For Pull Requests

1. **All checks must pass** before merging
2. **Coverage must be ≥75%** or PR fails
3. **No linting errors** allowed
4. **Fix formatting** before pushing:
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

### For Deployments

1. **Never skip tests** in production
2. **Use staging environment** for testing
3. **Monitor post-deploy health checks**
4. **Review release notes** before deploying

### For Browser Tests

1. **Run manually** before major releases
2. **Check videos** if tests fail
3. **Update tests** when UI changes
4. **Don't run on every PR** (too slow)

---

## Troubleshooting

### Test Failures

**Check coverage report:**
```bash
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

**Run specific test:**
```bash
pytest tests/test_profile.py::test_create_profile -v
```

**Run with debugging:**
```bash
pytest tests/ -v -s --tb=long
```

### Linting Failures

**Auto-fix formatting:**
```bash
black src/ tests/
isort src/ tests/
```

**Check flake8 errors:**
```bash
flake8 src/ tests/ --show-source
```

**Type check with mypy:**
```bash
mypy src/ --show-error-codes
```

### Browser Test Failures

**Run locally:**
```bash
pytest tests/browser/ --headed --slowmo=1000
```

**Debug with screenshots:**
```bash
pytest tests/browser/ --screenshot=on --video=on
```

**Check Streamlit logs:**
```bash
streamlit run src/main.py --server.port=8501
# In another terminal:
pytest tests/browser/
```

### Deployment Failures

**Check Docker build:**
```bash
docker build -t healthrag:test .
docker run -p 8501:8501 healthrag:test
```

**Check health endpoint:**
```bash
curl http://localhost:8501/_stcore/health
```

**View container logs:**
```bash
docker logs -f <container_id>
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/*.yml` | GitHub Actions workflows |
| `.flake8` | Flake8 linting configuration |
| `pyproject.toml` | Black, isort, mypy, pytest configuration |
| `pytest.ini` | Pytest test discovery and markers |
| `requirements.txt` | Production dependencies |
| `requirements-dev.txt` | Development dependencies |
| `.codecov.yml` | Codecov coverage configuration (optional) |

---

## Security

### Secrets Management

**Required secrets:**
- `GITHUB_TOKEN` (auto-provided)
- `CODECOV_TOKEN` (optional, for Codecov)
- Add deployment-specific secrets as needed

**Configure secrets:**
1. Go to Settings → Secrets and variables → Actions
2. Add repository secrets
3. Use in workflows: `${{ secrets.SECRET_NAME }}`

### Security Scanning

**Trivy:** Scans for vulnerabilities in dependencies and filesystem
**Bandit:** Detects common security issues in Python code
**pip-audit:** Checks for known vulnerabilities in Python packages

**View results:**
- Trivy: Security tab → Code scanning alerts
- Bandit: Download artifacts from lint workflow
- pip-audit: Weekly dependency check issues

---

## Monitoring

### Workflow Status

**Dashboard:** https://github.com/jasonlws/HealthRAG/actions

**Badges in README:**
- Test Suite: Shows if tests are passing
- Code Quality: Shows if linting is passing
- Codecov: Shows current coverage percentage

### Email Notifications

**Configure in GitHub Settings:**
1. Settings → Notifications
2. Enable "Actions" notifications
3. Choose: Email, Web, or Mobile

---

## Cost Optimization

### GitHub Actions Minutes

**Free tier:** 2,000 minutes/month for private repos
**Public repos:** Unlimited

**Tips to save minutes:**
1. ✅ Use caching for pip packages
2. ✅ Run slow tests only on main branch
3. ✅ Make browser tests manual trigger
4. ✅ Use fail-fast in matrix jobs (when appropriate)
5. ✅ Skip redundant jobs (e.g., deploy tests if pre-deploy failed)

**Current estimated usage:**
- Test Suite: ~8 minutes per run
- Code Quality: ~3 minutes per run
- Browser Tests: ~15 minutes per run (manual only)
- Deploy: ~12 minutes per run (main branch only)

**Monthly estimate:**
- ~30 PRs/month × 11 minutes = 330 minutes
- ~30 main pushes × 35 minutes = 1,050 minutes
- **Total: ~1,400 minutes/month** (well within free tier)

---

## Future Enhancements

### Planned Improvements

1. **Codecov integration** - Better coverage visualization
2. **Performance testing** - Benchmark regression detection
3. **Dependabot** - Automated dependency updates
4. **Deployment environments** - Staging and production
5. **Automated rollback** - On deployment failure
6. **Slack notifications** - Team alerts
7. **Release notes automation** - Generate from commits

### Contributing

When adding new workflows:
1. Document in this file
2. Add status badge to README
3. Test manually before merging
4. Configure secrets if needed
5. Add to troubleshooting section

---

## Support

**Issues:** https://github.com/jasonlws/HealthRAG/issues
**Workflow runs:** https://github.com/jasonlws/HealthRAG/actions
**Documentation:** This file and individual workflow comments
