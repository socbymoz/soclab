# SOC Log Lab Production Launcher
# Run this as Administrator to start in production mode

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Set-Location "C:\student-login\soc-log-platform"

# Load .env
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#].+?)\s*=\s*(.+)\s*$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SOC Log Lab - PRODUCTION MODE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Application : SOC Log Analysis Platform" -ForegroundColor White
Write-Host " Mode        : PRODUCTION (Waitress)" -ForegroundColor Yellow
Write-Host " URL         : http://0.0.0.0:8000" -ForegroundColor Yellow
Write-Host " Logs        : logs/soclab.log" -ForegroundColor Gray
Write-Host ""
Write-Host " Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verify dependencies
$deps = @("waitress", "dotenv")
foreach ($dep in $deps) {
    $check = python -c "import $dep" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing missing dependency: $dep" -ForegroundColor Yellow
        python -m pip install $dep 2>&1 | Out-Null
    }
}

# Start with Waitress (production WSGI for Windows)
python -c "
import waitress
from app import app
import os

host = os.getenv('HOST', '0.0.0.0')
port = int(os.getenv('PORT', 8000))
print(f'[Waitress] Serving on http://{host}:{port}')
waitress.serve(app, host=host, port=port, threads=8, connection_limit=1000)
"

Read-Host "`nPress Enter to exit"
