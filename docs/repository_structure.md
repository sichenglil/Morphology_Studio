# Repository structure

The root contains only standard project entry files and the major source, documentation, packaging, configuration, and automation directories.

| Path | Contents | Generated? |
| --- | --- | --- |
| `.github/` | Workflows and community templates | No |
| `.reuse/`, `LICENSES/` | REUSE attribution and license texts | No |
| `packaging/windows/` | PyInstaller specification | No |
| `src/morphology_toolkit/` | Python package, API, importers, validators, exporters | No |
| `web/frontend/` | Vue/TypeScript/Three.js source and frontend tests | No |
| `tests/` | Python unit, integration, and documentation tests | No |
| `examples/` | Small generic model fixtures | No |
| `docs/` | User, maintainer, architecture, audit, and image documentation | No |
| `scripts/dev/` | Optional conversion and model-maintenance helpers | No |
| `scripts/migrations/` | Deprecated compatibility forwarders | No |
| `build/`, `dist/`, `site/` | Reports, desktop artifacts, documentation output | Yes; ignored |

`desktop_entry.py` remains as a small discoverable compatibility entry; its implementation delegates to `morphology_toolkit.desktop`. The editable frontend exists only under `web/frontend`; packaged static assets are build input for the offline desktop distribution, not a second source tree.

