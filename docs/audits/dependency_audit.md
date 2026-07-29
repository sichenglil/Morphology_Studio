# Dependency audit

Python dependencies are separated into runtime, web, desktop, mesh, development, and documentation extras. Python is bounded to 3.9–3.13. Node and pnpm ranges are declared; pnpm remains the locked frontend installer. No confirmed unused runtime dependency was removed.

Most runtime/frontend dependencies use permissive licenses. PyInstaller's bootloader exception is compatible with distributing the built application. `step2urdf` is not vendored. Model repositories are not dependencies or distributable assets. Transitive license scanning and REUSE lint results are recorded during acceptance and must not be inferred from this document.
