# Build and release

## Development

Install Python 3.9-3.13, Node.js 20-24 and pnpm 10-11. Run `python -m pip install -r project/requirements-dev.txt`, `pnpm --dir web/frontend install --frozen-lockfile`, then `project/run_app.bat`.

Regenerate the real-model preview with `python scripts/render/generate_urdf_gifs.py`. Add `--force` to bypass the digest cache. Validate resources with `python scripts/validation/verify_resources.py`.

## Windows build

Use `project/build_exe.bat release` for a windowed build or `project/build_exe.bat debug` for a console build. The script builds the frontend, validates the model and GIF, runs tests, executes `scripts/build/packaging/MorphologyStudio.spec`, and prepares `release/MorphologyStudio`.

This is an onedir release, not a single-file EXE. Keep `MorphologyStudio.exe`, `_internal`, `assets`, and `config` together. Models and configuration are external beside the EXE so resource lookup is independent of the launch working directory. Logs are written to `logs/MorphologyStudio.log`.

The GIF generator dependencies (Pillow, NumPy, trimesh and pycollada) are development-only and explicitly excluded from the executable.
