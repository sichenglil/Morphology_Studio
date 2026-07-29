#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD/src"
python -m uvicorn morphology_toolkit.webapp:app --host 127.0.0.1 --port 8000
