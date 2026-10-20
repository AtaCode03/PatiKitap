param([string]$PythonExecutable, [int]$Port=8000, [string]$BindAddress='127.0.0.1')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not $PythonExecutable) {
    $bundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path -LiteralPath $bundled) { $PythonExecutable = $bundled }
    elseif (Test-Path -LiteralPath '.venv/Scripts/python.exe') { $PythonExecutable = Join-Path $PSScriptRoot '.venv/Scripts/python.exe' }
    else { $PythonExecutable = 'python' }
}
if (Test-Path -LiteralPath '.packages') {
    $env:PYTHONPATH = Join-Path $PSScriptRoot '.packages'
}
& $PythonExecutable -m uvicorn main:app --host $BindAddress --port $Port --no-proxy-headers
exit $LASTEXITCODE
