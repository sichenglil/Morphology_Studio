@echo off
setlocal
cd /d "%~dp0.."
set "MODE=%~1"
if "%MODE%"=="" set "MODE=release"
if /I not "%MODE%"=="release" if /I not "%MODE%"=="debug" exit /b 2
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
python -m pip install -r project\requirements-dev.txt || exit /b 1
call pnpm --dir web/frontend install --frozen-lockfile || exit /b 1
call pnpm --dir web/frontend build || exit /b 1
python scripts\render\generate_urdf_gifs.py || exit /b 1
python scripts\validation\verify_resources.py || exit /b 1
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest || exit /b 1
set "PACKAGING_PYTHON=build\packaging-venv\Scripts\python.exe"
python -m venv build\packaging-venv || exit /b 1
"%PACKAGING_PYTHON%" -m pip install --disable-pip-version-check -r project\requirements.txt PyInstaller==6.21.0 || exit /b 1
set MORPHOLOGY_BUILD_MODE=%MODE%
"%PACKAGING_PYTHON%" -m PyInstaller scripts\build\packaging\MorphologyStudio.spec --noconfirm --clean || exit /b 1
"%PACKAGING_PYTHON%" scripts\build\prepare_release.py || exit /b 1
python scripts\validation\smoke_release.py || exit /b 1
if /I "%MODE%"=="release" (
  rmdir /s /q build
  rmdir /s /q dist
)
endlocal
