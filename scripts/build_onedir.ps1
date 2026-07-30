$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root
pnpm --dir web/frontend install --frozen-lockfile
pnpm --dir web/frontend build
python scripts/validation/verify_resources.py
$venv = Join-Path $root "build/onedir-venv"
if (-not (Test-Path "$venv/Scripts/python.exe")) { python -m venv $venv }
& "$venv/Scripts/python.exe" -m pip install --disable-pip-version-check -r project/requirements.txt PyInstaller==6.21.0
& "$venv/Scripts/python.exe" -m PyInstaller scripts/build/packaging/MorphologyStudio.onedir.spec `
    --noconfirm --clean --distpath dist/onedir --workpath build/onedir
Write-Host "ONEDIR_OK $root/dist/onedir/MorphologyStudio/MorphologyStudio.exe"
