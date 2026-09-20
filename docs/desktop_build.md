# Desktop build

Run `project/build_exe.bat release` for the supported clean build, versioned `release/v<version>/` preparation, smoke test, and intermediate-directory cleanup. The lower-level helper is `scripts/build/build_desktop.ps1`; `scripts/validation/smoke_test_desktop.ps1` verifies health and shutdown behavior.
