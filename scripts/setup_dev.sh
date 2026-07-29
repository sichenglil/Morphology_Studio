#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install --upgrade pip
python -m pip install -e '.[dev,web,docs]'
corepack enable
pnpm --dir web/frontend install --frozen-lockfile
pnpm --dir web/frontend exec playwright install chromium
