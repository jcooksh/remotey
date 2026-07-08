"""SSH Remote Server - Windows Host Setup"""
import subprocess
import sys
import os
import socket

def check_openssh_installed():
    """Check if OpenSSH Server is installed on Windows"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"'],
            capture_output=True,
            text=True
        )
        return "Installed" in result.stdout
    except Exception as e:
        print(f"Error checking OpenSSH: {e}")
        return False

def install_openssh_server():
    """Install OpenSSH Server on Windows"""
    print("Installing OpenSSH Server...")
    try:
        subprocess.run(
            ['powershell', '-Command', 'Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'],
            check=True
        )
        print("OpenSSH Server installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install OpenSSH Server: {e}")
        return False

def start_ssh_service():
    """Start and enable SSH service"""
    print("Starting SSH service...")
    try:
        # Start the service
        subprocess.run(['powershell', '-Command', 'Start-Service sshd'], check=True)
        # Set to automatic startup
        subprocess.run(['powershell', '-Command', 'Set-Service -Name sshd -StartupType "Automatic"'], check=True)
        print("SSH service started and enabled")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to start SSH service: {e}")
        return False

def configure_firewall():
    """Configure Windows Firewall for SSH"""
    print("Configuring firewall...")
    try:
        subprocess.run([
            'powershell', '-Command',
            'New-NetFirewallRule -Name sshd -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22'
        ], check=True)
        print("Firewall configured for SSH")
        return True
    except subprocess.CalledProcessError:
        print("Firewall rule may already exist or failed to create")
        return True  # Continue anyway

def get_connection_info():
    """Get connection information"""
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Unable to determine"

    username = os.getenv('USERNAME')

    return {
        'hostname': hostname,
        'ip': ip_address,
        'username': username
    }

def main():
    print("=== SSH Remote Server Setup (Windows) ===\n")

    # Check if running as admin
    try:
        is_admin = subprocess.run(
            ['powershell', '-Command', '[Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains "S-1-5-32-544"'],
            capture_output=True,
            text=True
        ).stdout.strip() == "True"

        if not is_admin:
            print("ERROR: This script must be run as Administrator")
            print("Right-click PowerShell/CMD and select 'Run as Administrator'")
            sys.exit(1)
    except:
        print("Warning: Could not verify admin privileges")

    # Check if OpenSSH is installed
    if not check_openssh_installed():
        print("OpenSSH Server not found. Installing...")
        if not install_openssh_server():
            print("Failed to install OpenSSH Server")
            sys.exit(1)
    else:
        print("OpenSSH Server already installed")

    # Start SSH service
    if not start_ssh_service():
        print("Failed to start SSH service")
        sys.exit(1)

    # Configure firewall
    configure_firewall()

    # Display connection info
    info = get_connection_info()
    print("\n" + "="*50)
    print("SSH Server is ready!")
    print("="*50)
    print(f"Hostname: {info['hostname']}")
    print(f"IP Address: {info['ip']}")
    print(f"Username: {info['username']}")
    print(f"Port: 22")
    print("\nConnect from another machine:")
    print(f"  ssh {info['username']}@{info['ip']}")
    print("\nNote: Use your Windows login password when connecting")
    print("="*50)

if __name__ == "__main__":
    main()
