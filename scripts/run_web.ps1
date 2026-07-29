$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = (Join-Path $PWD 'src')
python -m uvicorn morphology_toolkit.webapp:app --host 127.0.0.1 --port 8000
