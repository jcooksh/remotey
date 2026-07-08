# Remotey Windows Setup Script
# Installs OpenSSH Server and registers with relay

param(
    [string]$RelayServer = "relay.remotey.dev"
)

Write-Host "=== Remotey Setup ===" -ForegroundColor Cyan

# Check admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Run as Administrator"
    exit 1
}

# Install OpenSSH Server
Write-Host "[1/5] Installing OpenSSH Server..." -ForegroundColor Yellow
$sshService = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($sshService.State -ne "Installed") {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
}

# Start and set to automatic
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Firewall rule
Write-Host "[2/5] Configuring firewall..." -ForegroundColor Yellow
if (!(Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
}

# Generate session key
Write-Host "[3/5] Generating session key..." -ForegroundColor Yellow
$keyPath = "$env:ProgramData\ssh\remotey_session_key"
ssh-keygen -t ed25519 -f $keyPath -N '""' -C "remotey-session" -q

# Get public key
$pubKey = Get-Content "$keyPath.pub"

# Get machine info
$hostname = $env:COMPUTERNAME
$username = $env:USERNAME
$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" | Select-Object -First 1).IPAddress

# Register with relay server
Write-Host "[4/5] Registering with relay server..." -ForegroundColor Yellow
$body = @{
    hostname = $hostname
    username = $username
    ip = $ip
    pubkey = $pubKey
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://$RelayServer/register" -Method Post -Body $body -ContentType "application/json"
    $sessionId = $response.session_id

    Write-Host "`n=== CONNECTION READY ===" -ForegroundColor Green
    Write-Host "Session ID: " -NoNewline
    Write-Host $sessionId -ForegroundColor Cyan
    Write-Host "`nSend this to the person connecting:" -ForegroundColor Yellow
    Write-Host "  python remotey.py connect $sessionId" -ForegroundColor White

    # Keep session alive
    Write-Host "`n[5/5] Session active. Press Ctrl+C to end..." -ForegroundColor Yellow

    # Monitor for incoming connections
    while ($true) {
        Start-Sleep -Seconds 5
        # Check if sshd has active connections
        $connections = netstat -ano | Select-String ":22.*ESTABLISHED"
        if ($connections) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Active connection detected" -ForegroundColor Green
        }
    }

} catch {
    Write-Error "Failed to register with relay: $_"
    exit 1
}
