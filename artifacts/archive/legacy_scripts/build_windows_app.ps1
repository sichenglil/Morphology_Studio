Write-Warning "build_windows_app.ps1 is deprecated; forwarding to scripts/build_desktop.ps1"
& (Join-Path (Split-Path -Parent $PSScriptRoot) "build_desktop.ps1")
exit $LASTEXITCODE
