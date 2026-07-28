$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $Root "dist\MorphologyStudio\MorphologyStudio.exe"
if (-not (Test-Path -LiteralPath $Exe)) { throw "Build MorphologyStudio first" }
$Port = 8788
$env:MORPHOLOGY_PORT = "$Port"
$Process = Start-Process -FilePath $Exe -WorkingDirectory $Root -PassThru
try {
  $Deadline = (Get-Date).AddSeconds(15)
  $Healthy = $false
  while ((Get-Date) -lt $Deadline -and -not $Process.HasExited) {
    try {
      $Response = Invoke-RestMethod "http://127.0.0.1:$Port/api/health"
      if ($Response.status -eq "ok") { $Healthy = $true; break }
    } catch { Start-Sleep -Milliseconds 250 }
  }
  if (-not $Healthy) { throw "Desktop health check failed or timed out" }
  if ($Process.HasExited) { throw "Desktop process exited unexpectedly" }
  $Log = Join-Path $env:LOCALAPPDATA "MorphologyStudio\logs\morphology-studio.log"
  if (-not (Test-Path -LiteralPath $Log)) { throw "Desktop log was not created" }
  if (Select-String -LiteralPath $Log -Pattern "Unable to configure formatter|'NoneType'.*isatty" -Quiet) {
    throw "Unsafe Uvicorn formatter error found in desktop log"
  }
  Write-Output "PASS: native process, /api/health, and file logging"
} finally {
  if (-not $Process.HasExited) { Stop-Process -Id $Process.Id }
}
