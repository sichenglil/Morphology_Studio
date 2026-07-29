$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = (Join-Path $PWD 'src')
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m ruff check src tests scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m ruff format --check src tests scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest -p pytest_cov --cov=src/morphology_toolkit --cov-report=term-missing
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pnpm --dir web/frontend type-check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pnpm --dir web/frontend lint
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pnpm --dir web/frontend test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pnpm --dir web/frontend build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pnpm --dir web/frontend exec playwright test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts/check_docs_links.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts/check_readme_format.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m mkdocs build --strict
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m reuse lint
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts/check_repository_health.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git diff --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
