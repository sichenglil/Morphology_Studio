# Startup performance

## Method

Measurements used Windows 11 build 22631 and PyInstaller 6.21.0. `scripts/benchmark_startup.ps1` ran
each executable five times with Defender and normal filesystem caching enabled. It measured process
creation to backend-ready log and first native window handle. The first run after a build is a
cold-like observation, not a true post-reboot cold start.

| Build | Metric | Average | Median | Minimum | Maximum | First after build |
|---|---:|---:|---:|---:|---:|---:|
| Existing onedir | Window visible | 2.287 | 2.348 | 1.658 | 2.718 | 2.718 |
| Existing onedir | Backend ready | 1.506 | 1.561 | 0.971 | 1.868 | 1.868 |
| Baseline onefile | Window visible | 4.428 | 4.014 | 3.914 | 5.897 | 5.897 |
| Baseline onefile | Backend ready | 3.513 | 3.214 | 3.014 | 4.760 | 4.760 |
| Optimized onefile | Window visible | 4.352 | 4.251 | 3.825 | 5.159 | 5.159 |
| Optimized onefile | Backend ready | 3.582 | 3.467 | 3.295 | 4.227 | 4.227 |

An isolated onefile run reported UI interactive 1.664 seconds and OpenCascade ready 4.999 seconds
after backend app creation. A real STEP run reported 1.691 and 4.944 seconds. Those internal values
exclude bootloader extraction.

The window average improved by 0.076 seconds (1.7%); backend-ready changed by +0.069 seconds, within
normal launch variation. The cold-like first observation improved by 0.738 seconds. A real cold value
requires a reboot and was not fabricated.

Implemented work includes post-UI OpenCascade prewarm, one reusable Worker/WASM instance, lazy model
loading, scientific/test exclusions, no source maps, disabled UPX and stage logging. The main remaining
bottleneck is extraction: the 43.34 MB EXE contains a 47.97 MB uncompressed WASM plus Python/WebView
libraries. Onefile is therefore still slower than onedir. A fixed WebView2 runtime, eager model parsing
and claims of extraction-free PyInstaller startup were deliberately rejected.
