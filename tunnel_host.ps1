# Remotey - expose this Windows machine's SSH over the internet.
# Uses serveo.net: no account, no install, no router config.
# Run this, then use the printed address from any other machine.

param(
    [string]$TunnelHost = $(if ($env:REMOTEY_TUNNEL) { $env:REMOTEY_TUNNEL } else { "serveo.net" }),
    [int]$LocalPort = 22
)

$ErrorActionPreference = "Stop"

function Show-Banner($user, $addr, $port) {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  YOUR WINDOWS MACHINE IS LIVE" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Connect from any computer with:" -ForegroundColor White
    Write-Host ""
    Write-Host "      ssh $user@$addr -p $port" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  (enter your Windows password when asked)" -ForegroundColor Gray
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Keep THIS window open. Closing it kills the link." -ForegroundColor Yellow
    Write-Host ""
    # Save the address so client tools / you can find it later.
    "ssh $user@$addr -p $port" | Out-File -FilePath "$PSScriptRoot\last_link.txt" -Encoding ascii
}

Write-Host "=== Remotey Tunnel Host ===" -ForegroundColor Cyan

# 1. Make sure OpenSSH Server is installed and running (localhost:22).
Write-Host "[*] Checking OpenSSH Server..."
try {
    $state = (Get-WindowsCapability -Online -Name "OpenSSH.Server*").State
    if ($state -ne "Installed") {
        Write-Host "[*] Installing OpenSSH Server (needs admin)..."
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
    }
    Start-Service sshd -ErrorAction SilentlyContinue
    Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue
    Write-Host "[+] SSH server running on localhost:$LocalPort" -ForegroundColor Green
} catch {
    Write-Host "[!] Could not set up sshd. Run this as Administrator." -ForegroundColor Red
    Write-Host "    $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 2. Warn about exposing SSH publicly.
Write-Host ""
Write-Host "[!] SECURITY: this exposes Windows login to the internet." -ForegroundColor Yellow
Write-Host "    Use a STRONG Windows password, or set up SSH keys." -ForegroundColor Yellow
Write-Host ""

# 3. Open the reverse tunnel and watch for the public address serveo assigns.
$user = $env:USERNAME
Write-Host "[*] Opening tunnel via $TunnelHost ..."
Write-Host "    (first time: type 'yes' if asked to trust the host)"
Write-Host ""

$sshArgs = @(
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ServerAliveInterval=30",
    "-o", "ExitOnForwardFailure=yes",
    "-R", "0:localhost:$LocalPort",
    $TunnelHost
)

# Stream ssh output live; grab the "Forwarding TCP connections from HOST:PORT" line.
& ssh @sshArgs 2>&1 | ForEach-Object {
    $line = "$_"
    Write-Host "   $line" -ForegroundColor DarkGray
    if ($line -match "from\s+(\S+):(\d+)") {
        Show-Banner $user $Matches[1] $Matches[2]
    }
}

Write-Host ""
Write-Host "[x] Tunnel closed. Re-run to get a new link." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
