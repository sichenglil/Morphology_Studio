param([string]$ExePath = "")

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $ExePath) {
    $versionLine = Select-String -Path (Join-Path $root "pyproject.toml") -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
    if (-not $versionLine) { throw "Unable to determine project version" }
    $version = $versionLine.Matches[0].Groups[1].Value
    $ExePath = "release/v$version/MorphologyStudio-$version-windows-x64.exe"
}
$sourceExe = (Resolve-Path (Join-Path $root $ExePath)).Path
$chineseName = -join ([char[]](0x5355, 0x6587, 0x4EF6, 0x6D4B, 0x8BD5))
$testRoot = Join-Path $env:TEMP ("Morphology Studio $chineseName " + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $testRoot | Out-Null
$testExe = Join-Path $testRoot "MorphologyStudio.exe"
Copy-Item -LiteralPath $sourceExe -Destination $testExe
$port = 49137
$env:MORPHOLOGY_PORT = "$port"
$process = Start-Process -FilePath $testExe -WorkingDirectory $testRoot -PassThru

try {
    $health = $null
    for ($attempt = 0; $attempt -lt 120; $attempt++) {
        try {
            $health = Invoke-RestMethod "http://127.0.0.1:$port/api/health" -TimeoutSec 1
            break
        } catch { Start-Sleep -Milliseconds 250 }
    }
    if ($null -eq $health) { throw "Onefile API did not become healthy" }
    $registry = Invoke-RestMethod "http://127.0.0.1:$port/api/model-registry"
    if ($registry.models.Count -lt 1) { throw "Bundled model registry is empty" }
    $modelId = $registry.models[0].id
    $scene = Invoke-RestMethod "http://127.0.0.1:$port/api/model-registry/$modelId/load" -Method Post
    if ($scene.links.Count -lt 1) { throw "Bundled model did not load" }
    $workspacePath = Join-Path $testRoot "workspace.yaml"
    $workspaceBody = @{ path = $workspacePath; settings = @{ translation_unit = "mm" } } | ConvertTo-Json -Depth 3
    $workspaceBytes = [Text.Encoding]::UTF8.GetBytes($workspaceBody)
    Invoke-RestMethod "http://127.0.0.1:$port/api/workspaces/current/save" -Method Post `
        -ContentType "application/json; charset=utf-8" -Body $workspaceBytes | Out-Null
    Invoke-RestMethod "http://127.0.0.1:$port/api/workspaces/current/new" -Method Post `
        -ContentType "application/json" -Body "{}" | Out-Null
    $openBody = [Text.Encoding]::UTF8.GetBytes((@{ path = $workspacePath } | ConvertTo-Json))
    $reopened = Invoke-RestMethod "http://127.0.0.1:$port/api/workspaces/open" -Method Post `
        -ContentType "application/json; charset=utf-8" -Body $openBody
    if ($reopened.robotId -ne $modelId) { throw "Workspace did not restore the bundled model" }
    $exportPath = Join-Path $testRoot "exported robot.urdf"
    $body = @{ format = "urdf"; output = $exportPath } | ConvertTo-Json
    $bodyBytes = [Text.Encoding]::UTF8.GetBytes($body)
    Invoke-RestMethod "http://127.0.0.1:$port/api/export" -Method Post `
        -ContentType "application/json; charset=utf-8" -Body $bodyBytes | Out-Null
    if (-not (Test-Path -LiteralPath $exportPath)) { throw "URDF export was not created" }
    $log = Join-Path $env:LOCALAPPDATA "MorphologyStudio/logs/MorphologyStudio.log"
    for ($attempt = 0; $attempt -lt 120; $attempt++) {
        if ((Test-Path $log) -and (Select-String $log -Pattern "opencascade_ready" -Quiet)) { break }
        Start-Sleep -Milliseconds 250
    }
    $entries = Get-ChildItem -LiteralPath $testRoot -Force
    $expected = @("MorphologyStudio.exe", "exported robot.urdf", "workspace.yaml")
    $unexpected = @($entries | Where-Object { $_.Name -notin $expected })
    if ($unexpected.Count) { throw "EXE created unexpected sidecar files: $($unexpected.Name -join ', ')" }
    [pscustomobject]@{
        status = "PASS"
        isolated_directory = $testRoot
        bundled_model = $modelId
        link_count = $scene.links.Count
        urdf_export = $exportPath
        workspace_restore = $reopened.robotId
        localappdata_log = $log
        source_sidecars_required = $false
    } | ConvertTo-Json
} finally {
    $matching = Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $testExe }
    foreach ($candidate in $matching) { Stop-Process -Id $candidate.ProcessId -Force }
    Remove-Item Env:MORPHOLOGY_PORT -ErrorAction SilentlyContinue
}
