$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

foreach ($command in @("python", "pnpm")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "Missing build command: $command" }
}
python -m pip install -r project/requirements-dev.txt
pnpm --dir web/frontend install --frozen-lockfile
pnpm --dir web/frontend build
python scripts/validation/verify_resources.py
$wasm = Get-ChildItem src/morphology_toolkit/static/frontend/assets -Filter "opencascade.full-*.wasm"
$worker = Get-ChildItem src/morphology_toolkit/static/frontend/assets -Filter "StepWorker-*.js"
if (-not $wasm -or -not $worker) { throw "Frontend build is missing OpenCascade WASM or STEP Worker" }
if (-not (Test-Path assets/robot_models/ur5e_hx5_right/robot.urdf)) { throw "Bundled robot model is missing" }

$venv = Join-Path $root "build/onefile-venv"
if (-not (Test-Path "$venv/Scripts/python.exe")) { python -m venv $venv }
& "$venv/Scripts/python.exe" -m pip install --disable-pip-version-check -r project/requirements.txt PyInstaller==6.21.0
New-Item -ItemType Directory -Force release | Out-Null
& "$venv/Scripts/python.exe" scripts/build/build_native.py

$versionLine = Select-String -Path pyproject.toml -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
if (-not $versionLine) { throw "Unable to determine project version" }
$version = $versionLine.Matches[0].Groups[1].Value
$exeName = "MorphologyStudio-$version-windows-x64.exe"
$exe = Join-Path $root "release/$exeName"
if (-not (Test-Path $exe)) { throw "Onefile executable was not generated" }
$hash = (Get-FileHash -Algorithm SHA256 $exe).Hash.ToLowerInvariant()
@(
    "Build time: $((Get-Date).ToString('o'))"
    "Python: $(python --version 2>&1)"
    "PyInstaller: 6.21.0"
    "EXE: $exe"
    "Bytes: $((Get-Item $exe).Length)"
    "SHA-256: $hash"
    "UPX: disabled for startup speed and compatibility"
) | Set-Content release/build-report.txt -Encoding utf8
Write-Host "ONEFILE_OK $exe $hash"
