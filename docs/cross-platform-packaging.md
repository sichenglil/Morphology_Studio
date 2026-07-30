# Cross-platform desktop packaging

Morphology Studio uses one Python/FastAPI backend and one Vue/Three.js frontend on every platform.
PyInstaller bundles those resources, while pywebview selects the native renderer:

| Platform | Native renderer | Artifact |
|---|---|---|
| Windows x64 | Edge WebView2 | Single `.exe` |
| Linux x86_64 | GTK 3 + WebKitGTK 4.1 | `.tar.gz` portable directory |
| macOS Intel | WKWebView (Cocoa) | Unsigned `.app` in `.zip` |
| macOS Apple Silicon | WKWebView (Cocoa) | Unsigned `.app` in `.zip` |

The build embeds the compiled frontend, OpenCascade WASM and Worker, configuration, licenses, and
the packaged example model. It never resolves resources from the current working directory.

## Minimum runnable unit

- **Windows:** one versioned `.exe`; all application resources are extracted internally at startup.
- **Linux:** the complete extracted `MorphologyStudio/` directory, including `_internal/`.
- **macOS:** the complete `MorphologyStudio.app` Bundle. Finder displays it as one application, but
  its `Contents` directory must remain intact.

The `.tar.gz` and `.zip` files are download containers. They must be extracted before use. User
models and export results are not part of the minimum runnable unit.

## Install and run

### Windows

Download the x64 EXE and run it from any writable or read-only directory. Microsoft Edge WebView2
Runtime is required. Configuration and logs are stored under `%APPDATA%\MorphologyStudio`; cache is
stored under `%LOCALAPPDATA%\MorphologyStudio\Cache`.

### Linux

Install the native GUI runtime on Ubuntu/Debian, extract the archive, and launch the executable:

```bash
sudo apt install libgtk-3-0 libwebkit2gtk-4.1-0
tar -xzf MorphologyStudio-0.1.0-linux-x86_64.tar.gz
chmod +x MorphologyStudio/MorphologyStudio
./MorphologyStudio/MorphologyStudio
```

Configuration and logs use `${XDG_DATA_HOME:-~/.local/share}/MorphologyStudio`; cache uses
`${XDG_CACHE_HOME:-~/.cache}/MorphologyStudio`. A graphical X11 or Wayland session is required.

### macOS

Download the package matching the Mac processor, unzip it, and move `MorphologyStudio.app` to
`Applications`. Current CI packages are unsigned. On first launch, use **System Settings → Privacy &
Security → Open Anyway** if Gatekeeper blocks the application. Do not disable Gatekeeper globally.
Configuration and logs use `~/Library/Application Support/MorphologyStudio`; cache uses
`~/Library/Caches/MorphologyStudio`.

## Native local build

Use Python 3.11, Node.js 22, pnpm 11, and PyInstaller 6.21 on the target operating system:

```bash
python -m pip install -e ".[dev,desktop]" "pyinstaller==6.21.0"
pnpm --dir web/frontend install --frozen-lockfile
pnpm --dir web/frontend build
python scripts/build/build_native.py
python scripts/validation/verify_native_build.py
```

Linux additionally needs the GTK/WebKitGTK development packages used in
`.github/workflows/build-release.yml`. Cross-compilation is not supported: each package must be built
and verified on its matching native runner.

## CI and releases

The **Cross-platform Build and Release** workflow runs all four native jobs on manual dispatch and
pull requests affecting packaging. A semantic version tag such as `v0.1.0` runs the same matrix and,
only after every job succeeds, publishes the packages plus `SHA256SUMS.txt` to GitHub Releases.

The verification mode starts the packaged backend without opening a GUI, checks the HTML, WASM,
Worker and configuration, writes a cache probe, creates the API, and verifies required routes. It does
not claim interactive GUI testing on macOS runners. Windows is locally verified; Linux and macOS
remain CI-runner verification until their jobs have actually completed.
