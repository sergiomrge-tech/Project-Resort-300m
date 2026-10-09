param(
    [string]$Editor = 'C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe',
    [string]$Project,
    [string]$Output
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
if (-not $Project) { $Project = Join-Path $taskRoot 'UnityProject' }
if (-not $Output) { $Output = Join-Path $taskRoot 'evidence' }
$Project = (Resolve-Path -LiteralPath $Project).Path
New-Item -ItemType Directory -Force $Output | Out-Null
$Output = (Resolve-Path -LiteralPath $Output).Path
if (-not (Test-Path -LiteralPath $Editor)) { throw 'Unity 6000.6.2f1 executable missing; pass -Editor.' }
$env:PROGRAMDATA = 'C:\ProgramData'
$taskServer = Join-Path (Split-Path -Parent $Editor) 'Data\Resources\PackageManager\Server\UnityPackageManager.exe'
$taskIpc = 'ResortQA-' + $PID
$taskUpmLog = Join-Path $Output 'upm.log'
$taskUnityLog = Join-Path $Output 'unity.log'
$taskUpm = Start-Process -FilePath $taskServer -ArgumentList "server --ipc-path Unity-Upm-$taskIpc -l 2 --log-file `"$taskUpmLog`"" -WindowStyle Hidden -PassThru
try {
    $taskProcess = Start-Process -FilePath $Editor -ArgumentList "-batchmode -force-d3d11 -upmIpcPath Upm-$taskIpc -projectPath `"$Project`" -executeMethod StandaloneQA.Run -qaOutput `"$Output`" -quit -logFile `"$taskUnityLog`"" -WindowStyle Hidden -PassThru
    while (-not $taskProcess.HasExited) { $taskProcess.WaitForExit(1000) | Out-Null }
    $taskLog = Get-Content -LiteralPath $taskUnityLog -Raw
    if ($taskProcess.ExitCode -ne 0 -or $taskLog -notmatch 'STANDALONE_IMPORT_GPU_PASS') { throw "Unity QA failed; inspect $taskUnityLog" }
    Write-Output 'Unity import and GPU QA passed. This does not test Player, PlayMode, NPC, saves or FPS.'
} finally {
    if (-not $taskUpm.HasExited) { Stop-Process -Id $taskUpm.Id }
}
