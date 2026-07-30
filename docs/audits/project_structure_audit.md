# Project structure audit

Formal source lives in `src/morphology_toolkit`; the single editable frontend is `web/frontend`; the packaged frontend under `src/morphology_toolkit/static/frontend` is generated distribution input, not a second source tree. Tests are split into unit, integration, frontend unit/performance, and browser E2E.

Keep: source, tests, configs, migration notes, package static assets, and existing feature/acceptance documentation. Generated `build`, `dist`, caches, user `workspace`, upstream `models`, local reference checkouts and `node_modules` remain ignored. The packaged OpenCascade WASM (~50 MB) is retained because direct offline STEP import requires it.

Review items: `src/morphology_toolkit/static/index.html` is a compatibility fallback. The old STEP adapter launcher and local reference checkout are removed after direct-import regression testing; the USD helper remains optional with accurate local status.
