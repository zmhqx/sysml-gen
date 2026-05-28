# Start FastAPI backend
$ErrorActionPreference = "Stop"
$Backend = (Resolve-Path (Join-Path $PSScriptRoot "..\backend")).Path

Set-Location $Backend
Write-Host "WORKDIR: $Backend"

Write-Host "Freeing port 8000..."
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
        Write-Host "  kill PID $($_.OwningProcess)"
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "ERROR: port 8000 still in use. Close other backend windows."
    exit 1
}

Write-Host "Starting http://127.0.0.1:8000/docs (listen 0.0.0.0:8000)"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
