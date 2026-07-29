$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

pnpm --dir web/frontend install
if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed" }
pnpm --dir web/frontend build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }

$Venv = Join-Path $Root "build\packaging-venv"
$Python = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
  python -m venv $Venv
  if ($LASTEXITCODE -ne 0) { throw "Packaging virtual environment creation failed" }
}
& $Python -m pip install --disable-pip-version-check "pyinstaller>=6" "fastapi>=0.110" "uvicorn>=0.27" "pywebview>=5.4" "xacro==2.1.1" "PyYAML>=6"
if ($LASTEXITCODE -ne 0) { throw "Desktop packaging dependencies failed" }

& $Python -m PyInstaller --noconfirm --clean scripts/build/packaging/MorphologyStudio.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
$Exe = Join-Path $Root "dist\MorphologyStudio\MorphologyStudio.exe"
if (-not (Test-Path -LiteralPath $Exe)) { throw "Expected executable missing: $Exe" }
Write-Output "Built: $Exe"
