# Project structure audit

Baseline: 231 non-build files and about 2.67 MB. Formal source lives in `src/morphology_toolkit`; the single editable frontend is `web/frontend`; the packaged frontend under `src/morphology_toolkit/static/frontend` is generated distribution input, not a second source tree. Tests are split into unit, integration, frontend unit/performance, and browser E2E.

Keep: source, tests, configs, migration notes, package static assets, and existing feature/acceptance documentation. Add: `examples`, community files, workflows, consolidated guides, and repository checks. Generated `build`, `dist`, caches, user `workspace`, upstream `models`, and `node_modules` remain ignored. No tracked user model or large binary was found. The packaged JS bundle is the largest tracked file (~1.65 MB) and is retained because offline desktop startup requires it.

Review items: `src/morphology_toolkit/static/index.html` is a compatibility fallback; scripts for STEP/USD are optional adapters and are retained with accurate local status. No deletion was justified before regression tests.
