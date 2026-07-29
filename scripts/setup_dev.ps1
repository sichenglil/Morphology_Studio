$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
python -m pip install --upgrade pip
python -m pip install -e '.[dev,desktop,docs]'
corepack enable
pnpm --dir web/frontend install --frozen-lockfile
pnpm --dir web/frontend exec playwright install chromium
