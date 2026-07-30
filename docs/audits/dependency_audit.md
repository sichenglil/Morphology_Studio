# Dependency audit

Python dependencies are separated into runtime, web, desktop, mesh, development, and documentation extras. Python is bounded to 3.9–3.13. Node and pnpm ranges are declared; pnpm remains the locked frontend installer. No confirmed unused runtime dependency was removed.

Most runtime/frontend dependencies use permissive licenses. PyInstaller's bootloader exception is compatible with distributing the built application. OpenCascade.js is bundled for offline STEP parsing; its approximately 50 MB WASM binary is the dominant new application-size cost. A reduced Worker is adapted from MIT-licensed step2urdf, while its external checkout and full UI are not distributed. Model repositories are not dependencies or distributable assets. Transitive license scanning and REUSE lint results are recorded during acceptance and must not be inferred from this document.
