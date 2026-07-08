#!/usr/bin/env python3
"""
Setup script for Windows host machine
Installs and configures OpenSSH Server
"""
import subprocess
import sys
import os
from pathlib import Path
import platform


def check_windows():
    """Verify running on Windows"""
    if platform.system() != "Windows":
        print("Error: This script must run on Windows")
        sys.exit(1)


def run_powershell(script):
    """Execute PowerShell command"""
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def install_openssh():
    """Install OpenSSH Server on Windows"""
    print("Installing OpenSSH Server...")

    script = """
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
    Start-Service sshd
    Set-Service -Name sshd -StartupType 'Automatic'
    """

    success, stdout, stderr = run_powershell(script)
    if not success:
        print(f"Installation failed: {stderr}")
        return False

    print("OpenSSH Server installed")
    return True


def configure_firewall():
    """Configure Windows Firewall for SSH"""
    print("Configuring firewall...")

    script = """
    New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
    """

    success, stdout, stderr = run_powershell(script)
    if success:
        print("Firewall configured")
    return success


def setup_ssh_keys():
    """Generate and configure SSH keys"""
    print("Setting up SSH keys...")

    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)

    key_path = ssh_dir / "remotey_key"
    pub_key_path = ssh_dir / "remotey_key.pub"

    # Generate key pair
    if not key_path.exists():
        cmd = [
            "ssh-keygen",
            "-t", "ed25519",
            "-f", str(key_path),
            "-N", "",
            "-C", "remotey-access"
        ]
        subprocess.run(cmd, check=True)
        print(f"Key generated: {key_path}")

    # Setup authorized_keys
    authorized_keys = ssh_dir / "authorized_keys"
    with open(pub_key_path, "r") as pub:
        pub_content = pub.read()

    with open(authorized_keys, "w") as auth:
        auth.write(pub_content)

    print("SSH keys configured")
    print(f"\nCopy {key_path} to client machine at ~/.ssh/remotey_key")
    return True


def get_ip():
    """Get local IP address"""
    script = """
    (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
    """
    success, stdout, stderr = run_powershell(script)
    if success:
        return stdout.strip()
    return "unknown"


def main():
    check_windows()

    print("=== Remotey Host Setup ===\n")

    if not install_openssh():
        sys.exit(1)

    configure_firewall()
    setup_ssh_keys()

    ip = get_ip()
    print(f"\n=== Setup Complete ===")
    print(f"Host IP: {ip}")
    print(f"\nConnect from client:")
    print(f"  python remotey.py {ip}")


if __name__ == "__main__":
    if os.name != 'nt':
        print("Error: Must run on Windows")
        sys.exit(1)
    main()
