# OverBabel operational regression (run after code changes)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
python test.py @args
exit $LASTEXITCODE
