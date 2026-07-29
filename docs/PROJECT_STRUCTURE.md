# Project structure

- `desktop_entry.py`: Windows desktop entry point.
- `src/morphology_toolkit`: FastAPI backend, pywebview host, model services and resource paths.
- `web/frontend`: Vue 3, Element Plus and Three.js interface.
- `assets/robot_models/ur5e_hx5_right`: the single self-contained merged robot.
- `assets/previews/ur5e_hx5_right`: generated GIF and PNG.
- `config/robot_models.json`: runtime model registry.
- `scripts`: preview generation, resource verification and release preparation.
- `packaging/MorphologyStudio.spec`: PyInstaller onedir definition.
- `tests`: Python unit/integration/documentation tests.
- `_archive`: retained legacy or uncertain files, excluded from release.
- `release/MorphologyStudio`: portable end-user output.
