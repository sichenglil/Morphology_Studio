# Cleanup report

## Original state

The repository included multiple example robots, legacy screenshots, duplicate packaging specifications, Python caches, historical `build`/`dist` output, and a complete packaging virtual environment. The original inventory is recorded in `artifacts/reports/project_tree_before.txt`.

## Actions

- Copied only the merged UR5e + HX5 Right portable package into runtime assets.
- Moved example models, old screenshots, uncertain documentation, package metadata, and the superseded Windows spec to `_archive`.
- Removed regenerable `__pycache__`, pytest/ruff caches, egg metadata, and historical tracked `build`/`dist` products after making a full backup.
- Kept governance, licence, dependency, CI, maintainer and robot-agnostic core files because repository-health checks or current workflows use them.
- Replaced old example paths in tests and workflows with the packaged combined robot.

## Compatibility and risk

The backend remains robot-agnostic; the new registry adds a packaged default without removing arbitrary URDF import. `_archive` is intentionally excluded from packaging. The main size contributors are the real meshes, pywebview runtime, and frontend JavaScript bundle.
