# Setup OpenSSH Server on Windows host
# Run as Administrator

Write-Host "Setting up OpenSSH Server on Windows..." -ForegroundColor Green

# Install OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start SSH service
Start-Service sshd

# Set service to automatic startup
Set-Service -Name sshd -StartupType 'Automatic'

# Configure firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

Write-Host "`nOpenSSH Server installed and running!" -ForegroundColor Green
Write-Host "SSH is now accepting connections on port 22" -ForegroundColor Cyan
Write-Host "`nYour IP addresses:" -ForegroundColor Yellow
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "169.254.*" -and $_.IPAddress -ne "127.0.0.1"} | Select-Object IPAddress, InterfaceAlias

Write-Host "`nTest connection from another machine with:" -ForegroundColor Yellow
Write-Host "ssh $env:USERNAME@<this-machine-ip>" -ForegroundColor Cyan
