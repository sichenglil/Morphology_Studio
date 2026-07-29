# Project Structure Report

The second cleanup pass consolidates archived material and development logs under
`artifacts`, and keeps the PyInstaller specification beside the build scripts. The
root now contains only source, resources, documentation, tests, tooling metadata,
and the directly consumable release.

## Runtime architecture

- Entry point: `project/desktop_entry.py` -> `morphology_toolkit.desktop.main`.
- Desktop shell: pywebview.
- API and asset server: FastAPI/Uvicorn.
- User interface: Vue 3, Element Plus, and Three.js from `web/frontend`.
- Python package: the existing standard `src/morphology_toolkit` layout is retained.
- Frontend production output: `src/morphology_toolkit/static/frontend`.
- Model registry: `config/robot_models.json`.
- Deliverable: `release/MorphologyStudio`; `build` and `dist` are disposable.

## Maintained top-level layout

`src`, `assets`, `config`, `scripts`, `tests`, `web`, `docs`, `packaging`, `artifacts`,
`release` remains visible for end users; logs and archived material live under `artifacts`. MkDocs, pnpm, REUSE,
and the Web frontend are active and remain at repository scope.

The complete before/after trees are stored in `artifacts/reports/project_tree_before.txt`
and `artifacts/reports/project_tree_after.txt`.
