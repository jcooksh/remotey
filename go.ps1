# Remotey one-liner. Run on the Windows machine you want to reach:
#
#   irm https://raw.githubusercontent.com/jcooksh/remotey/main/go.ps1 | iex
#
# Installs/starts OpenSSH Server, opens an internet tunnel (serveo.net),
# and prints an ssh address you can use from anywhere. No account, no router.

$ErrorActionPreference = "Stop"
$SelfUrl     = "https://raw.githubusercontent.com/jcooksh/remotey/main/go.ps1"
$TunnelHost  = if ($env:REMOTEY_TUNNEL) { $env:REMOTEY_TUNNEL } else { "serveo.net" }
$LocalPort   = 22

# --- Self-elevate: installing the SSH server needs admin. ---
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting administrator (click Yes)..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList `
        "-NoProfile","-ExecutionPolicy","Bypass","-Command","irm $SelfUrl | iex"
    return
}

Write-Host "=== Remotey ===" -ForegroundColor Cyan

# --- 1. OpenSSH Server up on localhost:22 ---
Write-Host "[*] Setting up SSH server..."
try {
    if ((Get-WindowsCapability -Online -Name "OpenSSH.Server*").State -ne "Installed") {
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
    }
    Start-Service sshd -ErrorAction SilentlyContinue
    Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue
    Write-Host "[+] SSH server running." -ForegroundColor Green
} catch {
    Write-Host "[!] sshd setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"; exit 1
}

Write-Host "[!] This exposes Windows login to the internet. Use a strong password." -ForegroundColor Yellow

# --- 2. Open reverse tunnel, print the public address serveo assigns ---
$user = $env:USERNAME
Write-Host "[*] Opening tunnel via $TunnelHost (type 'yes' if asked to trust host)..."
Write-Host ""

$sshArgs = @(
    "-o","StrictHostKeyChecking=accept-new",
    "-o","ServerAliveInterval=30",
    "-o","ExitOnForwardFailure=yes",
    "-R","0:localhost:$LocalPort",
    $TunnelHost
)

& ssh @sshArgs 2>&1 | ForEach-Object {
    $line = "$_"
    Write-Host "   $line" -ForegroundColor DarkGray
    if ($line -match "from\s+(\S+):(\d+)") {
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host "  YOUR WINDOWS MACHINE IS LIVE" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Connect from any computer:" -ForegroundColor White
        Write-Host "      ssh $user@$($Matches[1]) -p $($Matches[2])" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  (enter your Windows password)" -ForegroundColor Gray
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host "  Keep this window open." -ForegroundColor Yellow
        Write-Host ""
    }
}

Write-Host "[x] Tunnel closed. Re-run the command for a new address." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
