#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD/src" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m compileall -q src tests
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m pytest -p pytest_cov --cov=src/morphology_toolkit --cov-report=term-missing
pnpm --dir web/frontend type-check
pnpm --dir web/frontend lint
pnpm --dir web/frontend test
pnpm --dir web/frontend build
pnpm --dir web/frontend exec playwright test
python scripts/validation/check_docs_links.py
python scripts/validation/check_readme_format.py
python -m mkdocs build --strict
python -m reuse lint
python scripts/validation/check_repository_health.py
git diff --check
