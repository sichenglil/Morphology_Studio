# Third-party notices

Morphology Studio source is Apache-2.0 licensed. Dependencies are installed from their upstream packages and are not relicensed by this project. The generated frontend bundle contains compiled dependency code; its source packages and license metadata are locked in `web/frontend/pnpm-lock.yaml`.

| Project | Use | License | Source | Modified/copied scope |
| --- | --- | --- | --- | --- |
| FastAPI | HTTP API | MIT | <https://github.com/fastapi/fastapi> | Dependency only |
| Uvicorn | Local ASGI server | BSD-3-Clause | <https://github.com/encode/uvicorn> | Dependency only |
| PyYAML | Configuration/workspaces | MIT | <https://github.com/yaml/pyyaml> | Dependency only |
| pywebview | Desktop window | BSD-3-Clause | <https://github.com/r0x0r/pywebview> | Dependency only |
| PyInstaller | Windows packaging | GPL-2.0-or-later with bootloader exception | <https://github.com/pyinstaller/pyinstaller> | Build dependency only |
| trimesh | Optional mesh inspection | MIT | <https://github.com/mikedh/trimesh> | Dependency only |
| Vue | Frontend framework | MIT | <https://github.com/vuejs/core> | Bundled build output |
| Three.js | 3D rendering | MIT | <https://github.com/mrdoob/three.js> | Bundled build output |
| Element Plus | UI components | MIT | <https://github.com/element-plus/element-plus> | Bundled build output |
| Pinia | State management | MIT | <https://github.com/vuejs/pinia> | Bundled build output |
| Vite, Vitest, Playwright, ESLint | Build and test tools | MIT / Apache-2.0 | Their locked package metadata | Development only |
| step2urdf | Optional external adapter reference | Apache-2.0 | <https://github.com/Democratizing-Dexterous/step2urdf> | No source copied; invoked only when separately installed |

No upstream UR5e, ROBOTIS, or user model repositories are distributed. The primitive-only files under `examples/` are original project fixtures under Apache-2.0. Exact transitive versions are recorded by the lockfile and installed Python environment; maintainers must re-audit notices when dependencies change.
