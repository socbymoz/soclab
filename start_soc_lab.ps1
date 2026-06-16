# SOC Log Lab + DNS Launcher - auto elevates to admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Set-Location "C:\student-login\soc-log-platform"

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "   SOC Log Lab - Starting..." -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Access at: http://soclab-forlogs" -ForegroundColor Yellow
Write-Host "           http://192.168.220.3" -ForegroundColor Yellow
Write-Host ""
Write-Host " DNS Server running for name resolution" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Start DNS server in background
$dnsJob = Start-Job -ScriptBlock {
    Set-Location "C:\student-login\soc-log-platform"
    C:\Users\mozpc\AppData\Local\Programs\Python\Python312\python.exe dns_server.py
}

Start-Sleep -Seconds 1

# Start Flask app in foreground
C:\Users\mozpc\AppData\Local\Programs\Python\Python312\python.exe app.py

# Cleanup
Stop-Job $dnsJob -ErrorAction SilentlyContinue
Remove-Job $dnsJob -ErrorAction SilentlyContinue

Read-Host "`nPress Enter to exit"
