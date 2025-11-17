# Pull Request

## Description

<!-- Briefly describe what this PR does -->

Fixes # (issue number, if applicable)

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🧪 Test coverage improvement
- [ ] 🔧 Configuration/infrastructure change

## Changes Made

<!-- List the main changes in bullet points -->

-
-
-

## Testing Checklist

### Automated Tests

- [ ] `./test-checklist.sh` passes (0 failures)
- [ ] All unit tests pass (`pytest tests/ -v`)
- [ ] No new test failures introduced
- [ ] Test coverage maintained or improved

### Manual Testing

- [ ] Streamlit loads without errors (`streamlit run src/main.py`)
- [ ] Tested critical user flows:
  - [ ] Profile creation
  - [ ] Weight logging
  - [ ] Food logging
  - [ ] Adaptive TDEE display (if 14+ days data)
- [ ] No console errors in browser DevTools
- [ ] UI renders correctly on desktop
- [ ] Mobile responsiveness checked (if UI changes)

### Integration Testing

- [ ] Docker build succeeds (`docker-compose build`)
- [ ] Docker containers start healthy (`docker-compose up -d`)
- [ ] Database migrations applied (if applicable)
- [ ] Environment variables configured in Render (if new ones added)

### Code Quality

- [ ] Code follows project style guidelines
- [ ] Comments added for complex logic
- [ ] No hardcoded credentials or secrets
- [ ] Imports organized and unused imports removed
- [ ] No `print()` debug statements left in code

## Deployment Readiness

- [ ] This PR is ready to be deployed to production
- [ ] Database migrations are backward-compatible (if applicable)
- [ ] No breaking changes to API contracts
- [ ] Feature flags used for risky changes (if applicable)
- [ ] Documentation updated (`README.md`, `CLAUDE.md`, etc.)

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->

## Additional Notes

<!-- Any additional information reviewers should know -->

## Checklist for Reviewer

- [ ] Code changes are clear and well-structured
- [ ] Tests adequately cover new functionality
- [ ] No obvious security vulnerabilities
- [ ] Performance impact is acceptable
- [ ] Documentation is sufficient

---

**Before merging**: Ensure all tests pass and manual validation is complete. Merging to `main` will trigger automatic deployment to Render.com.
