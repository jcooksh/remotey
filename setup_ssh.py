#!/usr/bin/env python3
"""
Remotey - Simple SSH Remote Access Setup for Windows
Configures OpenSSH Server on Windows for remote access
"""

import subprocess
import sys
import os

def is_admin():
    """Check if script is running with admin privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def run_command(cmd, check=True):
    """Run PowerShell command"""
    result = subprocess.run(
        ["powershell", "-Command", cmd],
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return result.stdout.strip()

def install_openssh():
    """Install OpenSSH Server on Windows"""
    print("[+] Checking OpenSSH Server installation...")

    # Check if already installed
    check_cmd = "Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'"
    result = run_command(check_cmd)

    if "Installed" in result:
        print("[+] OpenSSH Server already installed")
        return True

    print("[+] Installing OpenSSH Server...")
    install_cmd = "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
    if run_command(install_cmd):
        print("[+] OpenSSH Server installed successfully")
        return True
    return False

def configure_ssh():
    """Configure SSH service"""
    print("[+] Configuring SSH service...")

    # Start SSH service
    run_command("Start-Service sshd")

    # Set to automatic startup
    run_command("Set-Service -Name sshd -StartupType 'Automatic'")

    print("[+] SSH service configured and started")
    return True

def configure_firewall():
    """Configure Windows Firewall for SSH"""
    print("[+] Configuring firewall...")

    # Check if rule exists
    check_rule = "Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue"
    result = run_command(check_rule, check=False)

    if result:
        print("[+] Firewall rule already exists")
    else:
        # Create firewall rule
        rule_cmd = "New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22"
        run_command(rule_cmd)
        print("[+] Firewall rule created")

    return True

def get_connection_info():
    """Display connection information"""
    print("\n" + "="*50)
    print("SSH Remote Access Setup Complete!")
    print("="*50)

    # Get hostname
    hostname = run_command("hostname")

    # Get IP addresses
    ip_cmd = "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*'}).IPAddress"
    ips = run_command(ip_cmd)

    # Get username
    username = run_command("$env:USERNAME")

    print(f"\nHostname: {hostname}")
    print(f"Username: {username}")
    print(f"IP Address(es): {ips}")
    print(f"\nTo connect from another machine:")
    print(f"  ssh {username}@{hostname}")
    print(f"  or")
    print(f"  ssh {username}@{ips.split()[0] if ips else 'YOUR_IP'}")
    print("\nYou will be prompted for your Windows password.")
    print("="*50 + "\n")

def main():
    """Main setup function"""
    print("Remotey - SSH Remote Access Setup for Windows\n")

    if not is_admin():
        print("[!] This script requires administrator privileges.")
        print("[!] Please run as administrator.")
        sys.exit(1)

    try:
        if not install_openssh():
            print("[!] Failed to install OpenSSH Server")
            sys.exit(1)

        if not configure_ssh():
            print("[!] Failed to configure SSH service")
            sys.exit(1)

        if not configure_firewall():
            print("[!] Failed to configure firewall")
            sys.exit(1)

        get_connection_info()

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
