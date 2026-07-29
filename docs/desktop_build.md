# Desktop build

Run `powershell -ExecutionPolicy Bypass -File scripts/build_desktop.ps1`. The script builds frontend assets and the PyInstaller directory distribution at `dist/MorphologyStudio/`. Use `scripts/smoke_test_desktop.ps1` to verify health and shutdown behavior. Release archives must exclude models, workspaces, caches, Git data, and secrets.
