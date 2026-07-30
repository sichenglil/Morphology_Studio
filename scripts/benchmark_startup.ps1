param(
    [Parameter(Mandatory = $true)][string]$ExePath,
    [int]$Runs = 5,
    [string]$OutputPath = "artifacts/reports/startup-benchmark.json"
)

$ErrorActionPreference = "Stop"
$exe = (Resolve-Path -LiteralPath $ExePath).Path
$exeDirectory = Split-Path -Parent $exe
$log = Join-Path $env:LOCALAPPDATA "MorphologyStudio\logs\MorphologyStudio.log"
if ($exe -like "*baseline-dist*") {
    $log = Join-Path $exeDirectory "logs\MorphologyStudio.log"
}

$rows = @()
for ($run = 1; $run -le $Runs; $run++) {
    if (Test-Path -LiteralPath $log) { Clear-Content -LiteralPath $log }
    $stopwatch = [Diagnostics.Stopwatch]::StartNew()
    $process = Start-Process -FilePath $exe -PassThru
    $visible = $null
    $ready = $null
    while ($stopwatch.Elapsed.TotalSeconds -lt 60) {
        $matching = Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $exe }
        foreach ($candidate in $matching) {
            $nativeProcess = Get-Process -Id $candidate.ProcessId -ErrorAction SilentlyContinue
            if ($null -eq $visible -and $null -ne $nativeProcess -and
                $nativeProcess.MainWindowHandle -ne 0) {
                $visible = $stopwatch.Elapsed.TotalSeconds
            }
        }
        if ($null -eq $ready -and (Test-Path -LiteralPath $log) -and
            (Select-String -LiteralPath $log -Pattern "Desktop API ready" -Quiet)) {
            $ready = $stopwatch.Elapsed.TotalSeconds
        }
        if ($null -ne $visible -and $null -ne $ready) { break }
        Start-Sleep -Milliseconds 50
    }
    $matching = Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $exe }
    foreach ($candidate in $matching) { Stop-Process -Id $candidate.ProcessId -Force }
    $rows += [pscustomobject]@{
        run = $run
        window_visible_seconds = [math]::Round($visible, 3)
        backend_ready_seconds = [math]::Round($ready, 3)
    }
    Start-Sleep -Milliseconds 750
}

function Measure-StartupStats([object[]]$values) {
    $sorted = @($values | Sort-Object)
    [ordered]@{
        average = [math]::Round(($values | Measure-Object -Average).Average, 3)
        median = $sorted[[math]::Floor($sorted.Count / 2)]
        minimum = ($values | Measure-Object -Minimum).Minimum
        maximum = ($values | Measure-Object -Maximum).Maximum
    }
}

$report = [ordered]@{
    executable = $exe
    measured_at = (Get-Date).ToString("o")
    condition = "repeat launch; filesystem cache not cleared"
    runs = $rows
    window_visible = Measure-StartupStats $rows.window_visible_seconds
    backend_ready = Measure-StartupStats $rows.backend_ready_seconds
}
$target = Join-Path (Resolve-Path .).Path $OutputPath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $target -Encoding utf8
$report | ConvertTo-Json -Depth 5
