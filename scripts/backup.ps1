# SOC Log Lab - Backup Script
# Run this regularly (e.g., via Task Scheduler) to backup the platform

param(
    [string]$BackupDir = "C:\student-login\soc-log-platform\backups",
    [int]$RetentionDays = 7
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$source = "C:\student-login\soc-log-platform"
$backupFile = "$BackupDir\soclab_backup_$timestamp.zip"

Write-Host "[Backup] Starting backup..." -ForegroundColor Cyan

# Ensure backup directory exists
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

# Files to exclude
$exclude = @(
    "__pycache__",
    "*.pyc",
    ".env",
    "logs\*",
    "server_*.txt",
    "backups\*"
)

# Create backup
Compress-Archive -Path "$source\*" -DestinationPath $backupFile -Force
Write-Host "[Backup] Created: $backupFile" -ForegroundColor Green

# Calculate size
$size = (Get-Item $backupFile).Length / 1MB
Write-Host "[Backup] Size: $([math]::Round($size, 2)) MB" -ForegroundColor Gray

# Cleanup old backups
$oldFiles = Get-ChildItem -Path $BackupDir -Filter "*.zip" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays)
}

foreach ($file in $oldFiles) {
    Remove-Item -Path $file.FullName -Force
    Write-Host "[Backup] Removed old: $($file.Name)" -ForegroundColor Yellow
}

Write-Host "[Backup] Complete! Retaining last $RetentionDays days." -ForegroundColor Green
