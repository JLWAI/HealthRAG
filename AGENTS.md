# Repository Guidelines

> **📚 Note**: This file provides high-level repository guidelines. For detailed HealthRAG-specific development guidance, architecture, and current phase status, see [`CLAUDE.md`](CLAUDE.md). All agents must also follow the universal rules in [`../AGENTS.md`](../AGENTS.md) and [`../CLAUDE.md`](../CLAUDE.md).

## Project Structure & Module Organization
Primary application logic lives in `src/`, with `main.py` driving the Streamlit UI, `rag_system.py` orchestrating retrieval, and specialist modules (e.g., `workout_coach.py`, `food_logger.py`) encapsulating domain features. Configuration defaults sit in `config/settings.py`. Persisted assets belong under `data/`: PDFs in `data/pdfs/`, embeddings in `data/vectorstore/`, and sample artifacts in `src/data/`. Add developer-facing notes to `docs/` so operational guidance stays centralized.

## Build, Test, and Development Commands
- `./setup_dependencies.sh`: one-time Python environment bootstrap, including system packages.
- `source activate_venv.sh && streamlit run src/main.py`: launch the local Streamlit app against the default backend.
- `./start_healthrag.sh` or `docker-compose up --build`: build and run the Docker stack with Ollama.
- `./run_local_mlx.sh`: set up and run the Apple Silicon MLX path.
- `python process_pdfs.py`: ingest new PDFs into ChromaDB before querying.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation and descriptive, lowercase_with_underscores module names. New classes should use `PascalCase`; functions remain `snake_case`. Maintain type hints and docstrings consistent with existing modules, and prefer `dataclasses` for structured responses (see `src/workout_coach.py`). Use f-strings for formatting and route configuration through `config/settings.py` rather than hard-coding paths.

## Testing Guidelines
Tests live in `tests/` and mirror module names (e.g., `test_workout_coach.py`). Use `pytest` with the provided config: `pytest` for fast feedback and `pytest --cov=src --cov-report=html tests/` when validating coverage. Tag longer scenarios with `@pytest.mark.slow` or `@pytest.mark.integration` so they can be filtered (`pytest -m "not slow"`). Add fixtures under `tests/fixtures/` only when new personas or databases are essential.

## Commit & Pull Request Guidelines
History shows imperative, capitalized subject lines (e.g., "Add comprehensive nutrition tracking system…"); keep to ~72 characters and explain the "what" in one line. PRs should include: 1) a concise change summary, 2) references to issues or planning docs, 3) screenshots or terminal snippets for UI or ingestion changes, and 4) a test plan listing executed commands. Request a review before merging and confirm Docker and local paths still function when touching deployment scripts.

**⚠️ DEPLOYMENT FREQUENCY:** Pushes to `main` trigger Render.com deploys. **Target: ≤10 deploys per day, with one GitHub push per planned deploy window.** Collect local changes, run the full test checklist, then merge/push once so Render only builds once for that batch. Avoid rapid-fire fix pushes—stage fixes locally and include them in the next consolidated deploy. See `docs/TESTING.md` for local-first workflow details.

## Data & Configuration Tips
Sensitive health data stays local—do not commit derived vector stores or personal PDFs. Use `.env` files or `config/settings.py` overrides for machine-specific tweaks, and document new environment variables in `README.md`. When adjusting ingestion or model selection, update the relevant scripts and note the workflow change in `docs/`.
