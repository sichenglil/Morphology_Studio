@echo off
setlocal
cd /d %~dp0
set "MODE=%~1"
if "%MODE%"=="" set "MODE=release"
if /I not "%MODE%"=="release" if /I not "%MODE%"=="debug" exit /b 2
python -m pip install -r requirements-dev.txt || exit /b 1
pnpm --dir web/frontend install --frozen-lockfile || exit /b 1
pnpm --dir web/frontend build || exit /b 1
python scripts\generate_urdf_gifs.py || exit /b 1
python scripts\verify_resources.py || exit /b 1
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest || exit /b 1
set "PACKAGING_PYTHON=build\packaging-venv\Scripts\python.exe"
if not exist "%PACKAGING_PYTHON%" python -m venv build\packaging-venv || exit /b 1
"%PACKAGING_PYTHON%" -m pip install --disable-pip-version-check -r requirements.txt PyInstaller==6.21.0 || exit /b 1
set MORPHOLOGY_BUILD_MODE=%MODE%
"%PACKAGING_PYTHON%" -m PyInstaller packaging\MorphologyStudio.spec --noconfirm --clean || exit /b 1
"%PACKAGING_PYTHON%" scripts\prepare_release.py || exit /b 1
endlocal
