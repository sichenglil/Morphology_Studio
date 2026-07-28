# Desktop troubleshooting

## `Unable to configure formatter 'default'`

In a PyInstaller `console=False` process, `sys.stdout` and `sys.stderr` may be `None`. Uvicorn's default
formatter calls `sys.stdout.isatty()`, so the application previously failed before showing a window.

The desktop host now creates `uvicorn.Config` with `log_config=None`, `access_log=False`, and
`use_colors=False`, then uses `uvicorn.Server` directly. Application logs use a UTF-8 rotating file
handler (5 MB, five backups) and add a stream handler only when a writable stream exists.

Logs are stored at `%LOCALAPPDATA%\MorphologyStudio\logs\morphology-studio.log`, or
`~/.morphology_studio/logs/` when `LOCALAPPDATA` is unavailable.

Run from source with `python desktop_entry.py`, or use `morphology-tool desktop`. Rebuild with
`powershell -ExecutionPolicy Bypass -File scripts/build_desktop.ps1`. If WebView2/pywebview is missing,
the program displays an error dialog containing the log path; `morphology-tool desktop --browser`
is the explicit browser fallback.
