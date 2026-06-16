# Create scheduled tasks for SOC Log Lab maintenance
# Run this script as Administrator once to set up auto-maintenance

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "Setting up SOC Log Lab scheduled tasks..." -ForegroundColor Cyan

# === Task 1: Daily Backup at 3:00 AM ===
$backupAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\student-login\soc-log-platform\scripts\backup.ps1"
$backupTrigger = New-ScheduledTaskTrigger -Daily -At 03:00AM
$backupSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "SOC Lab Backup" -Action $backupAction -Trigger $backupTrigger -Settings $backupSettings -User "SYSTEM" -RunLevel Highest -Force
Write-Host "[✓] Backup task created (daily at 3:00 AM)" -ForegroundColor Green

# === Task 2: Health Check every 5 minutes ===
$healthAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\student-login\soc-log-platform\scripts\healthcheck.ps1"
$healthTrigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365) -At (Get-Date) -Once
$healthSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "SOC Lab Health Check" -Action $healthAction -Trigger $healthTrigger -Settings $healthSettings -User "SYSTEM" -RunLevel Highest -Force
Write-Host "[✓] Health check task created (every 5 minutes)" -ForegroundColor Green

# === Task 3: App Auto-Start on Boot ===
$appAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\student-login\soc-log-platform\scripts\start_production.ps1"
$appTrigger = New-ScheduledTaskTrigger -AtStartup
$appSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$appPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "SOC Lab App" -Action $appAction -Trigger $appTrigger -Settings $appSettings -Principal $appPrincipal -Force
Write-Host "[✓] Auto-start task created (on boot)" -ForegroundColor Green

Write-Host ""
Write-Host "All tasks created successfully!" -ForegroundColor Cyan
Write-Host "Run 'Get-ScheduledTask -TaskName SOC*' to verify." -ForegroundColor Gray
