# Setup SSH Server on Windows
# Run as Administrator

Write-Host "=== Remotey SSH Server Setup ===" -ForegroundColor Cyan

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nInstalling OpenSSH Server..." -ForegroundColor Green

# Install OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start SSH service
Write-Host "Starting SSH service..." -ForegroundColor Green
Start-Service sshd

# Set service to start automatically
Write-Host "Setting SSH service to start automatically..." -ForegroundColor Green
Set-Service -Name sshd -StartupType 'Automatic'

# Configure firewall
Write-Host "Configuring firewall..." -ForegroundColor Green
if (Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue) {
    Write-Host "Firewall rule already exists" -ForegroundColor Yellow
} else {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
    Write-Host "Firewall rule created" -ForegroundColor Green
}

# Test service status
$sshStatus = Get-Service sshd
Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "SSH Server Status: $($sshStatus.Status)" -ForegroundColor $(if ($sshStatus.Status -eq 'Running') { 'Green' } else { 'Red' })

if ($sshStatus.Status -eq 'Running') {
    Write-Host "`nYou can now run remotey.py to create connections" -ForegroundColor Green
} else {
    Write-Host "`nWARNING: SSH service is not running" -ForegroundColor Red
    Write-Host "Try running: Start-Service sshd" -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
