# Remotey host side. You do NOT run this by hand.
# Your Mac's `remotey` command prints a one-liner that sets $env:RP / $env:RK
# and pipes this script into PowerShell. That one-liner is all you paste here.

$ErrorActionPreference = "Stop"
$SelfUrl = "https://raw.githubusercontent.com/jcooksh/remotey/main/go.ps1"
$Relay   = "bore.pub"
$Port    = $env:RP    # remote port your Mac chose
$PubKey  = $env:RK    # your Mac's public SSH key

if (-not $Port) {
    Write-Host "Missing setup. Run the `remotey` command on your Mac and paste the line it gives you." -ForegroundColor Red
    return
}

# --- Self-elevate (installing the SSH server needs admin), carrying RP/RK. ---
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting administrator (click Yes)..." -ForegroundColor Yellow
    $inner = "`$env:RP='$Port'; `$env:RK='$PubKey'; irm '$SelfUrl' | iex"
    $enc   = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($inner))
    Start-Process powershell -Verb RunAs -ArgumentList `
        "-NoProfile","-ExecutionPolicy","Bypass","-EncodedCommand",$enc
    return
}

Write-Host "=== Remotey ===" -ForegroundColor Cyan

# --- 1. OpenSSH Server on localhost:22 ---
Write-Host "[*] Setting up SSH server..."
if ((Get-WindowsCapability -Online -Name "OpenSSH.Server*").State -ne "Installed") {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
}
Start-Service sshd -ErrorAction SilentlyContinue
Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue
Write-Host "[+] SSH server running." -ForegroundColor Green

# --- 2. Trust only your Mac's key (so only you can connect) ---
if ($PubKey) {
    $ak = "$env:ProgramData\ssh\administrators_authorized_keys"
    Set-Content -Path $ak -Value $PubKey -Encoding ascii
    icacls $ak /inheritance:r /grant "Administrators:F" "SYSTEM:F" | Out-Null
    Write-Host "[+] Your Mac's key installed (only your Mac can log in)." -ForegroundColor Green
}

# --- 3. Get bore (tiny tunnel tool that lets your Mac pick the port) ---
$tools = "$env:LOCALAPPDATA\remotey"
New-Item -ItemType Directory -Force -Path $tools | Out-Null
$bore = "$tools\bore.exe"
if (-not (Test-Path $bore)) {
    Write-Host "[*] Downloading tunnel tool..."
    $rel   = Invoke-RestMethod "https://api.github.com/repos/ekzhang/bore/releases/latest" -Headers @{ "User-Agent" = "remotey" }
    $asset = $rel.assets | Where-Object { $_.name -match "x86_64-pc-windows" } | Select-Object -First 1
    $zip   = "$tools\bore.zip"
    Invoke-WebRequest $asset.browser_download_url -OutFile $zip -UseBasicParsing
    Expand-Archive $zip -DestinationPath $tools -Force
    Remove-Item $zip -Force
    $found = Get-ChildItem $tools -Recurse -Filter bore.exe | Select-Object -First 1
    if ($found -and $found.FullName -ne $bore) { Copy-Item $found.FullName $bore -Force }
}

# --- 4. Open the tunnel on the port your Mac is waiting on ---
$user = $env:USERNAME
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  ONLINE. Your Mac should connect automatically." -ForegroundColor Green
Write-Host "  If not, on the Mac run:  ssh $user@$Relay -p $Port" -ForegroundColor Cyan
Write-Host "  Keep this window open." -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

& $bore local 22 --to $Relay --port $Port

Write-Host "[x] Tunnel closed. Re-run the command from your Mac." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
