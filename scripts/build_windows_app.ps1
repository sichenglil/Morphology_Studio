Write-Warning "build_windows_app.ps1 is deprecated; forwarding to build_desktop.ps1"
& (Join-Path $PSScriptRoot "build_desktop.ps1")
exit $LASTEXITCODE
