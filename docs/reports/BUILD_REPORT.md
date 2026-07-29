# Build Report

- Platform: Windows 10/11 x64
- Python: 3.9.13
- Build mode: PyInstaller onedir, release/no-console
- Command: `project/build_exe.bat release`
- Result: PASS
- Executable: `release/MorphologyStudio/MorphologyStudio.exe`
- Executable size: 5,100,213 bytes
- Robot models: 1 (`ur5e_hx5_right`)
- Operation GIF: 960 x 540, 49 frames, 4,736,652 bytes
- Resource validation: 40 links, 39 joints, 56 mesh references, 0 missing
- Release smoke test: PASS from `artifacts/temporary/中文 启动目录`
- Intermediate cleanup: `build` and `dist` absent after validation
- External source dependency: none

PyInstaller reported the non-fatal optional warning `Hidden import "tzdata" not found`; the
packaged application and resource endpoints passed the release smoke test.
