# Windows packaging

Two PyInstaller 6.21.0 configurations are retained:

- `scripts/build/packaging/MorphologyStudio.onedir.spec` for faster internal launches.
- `scripts/build/packaging/MorphologyStudio.onefile.spec` for final single-file delivery.

Build with `scripts/build_onedir.ps1` or `scripts/build_onefile.ps1`. The onefile script validates the
Vite production output, OpenCascade WASM, STEP Worker and bundled robot before packaging. It writes
`release/MorphologyStudio.exe`, an optional SHA-256 file and a build report. Only the EXE is needed at
runtime.

Read-only resources resolve from the source root, onedir root, or `sys._MEIPASS`. No resource lookup
uses the current working directory. Logs, caches and future mutable settings use
`%LOCALAPPDATA%\MorphologyStudio`; the application never modifies `_MEI*` or writes sidecars.

The EXE uses the system Microsoft Edge WebView2 Runtime. A quick check provides a Chinese diagnostic
when it is missing. A fixed runtime is not bundled because that would substantially increase extract
time, size and security maintenance.

OpenCascade.js is bundled as WASM. The UI becomes interactive first, then one persistent Worker is
prewarmed after a 750 ms idle delay and reused by STEP imports. UPX is disabled to favor compatibility,
startup consistency and lower antivirus risk.
