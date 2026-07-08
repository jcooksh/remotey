# Remotey Setup Guide

## Quick Start

### Setting Up the Remote Windows Machine

1. **Download this repository** to the Windows machine you want to access remotely

2. **Open PowerShell as Administrator**:
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

3. **Navigate to the remotey folder**:
   ```powershell
   cd path\to\remotey
   ```

4. **Run the setup script**:
   ```powershell
   .\setup-ssh-server.ps1
   ```

5. **Note your IP address** displayed at the end of the setup

### Connecting from Another Computer

From any computer with SSH client (Windows, Mac, Linux):

```bash
ssh your-windows-username@remote-ip-address
```

Example:
```bash
ssh john@192.168.1.100
```

Enter your Windows password when prompted.

## Advanced Configuration

### Using SSH Keys (Recommended)

On your client machine, generate an SSH key:

```bash
ssh-keygen -t ed25519
```

Copy the public key to the Windows machine:

```bash
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh your-username@remote-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

On Linux/Mac:
```bash
ssh-copy-id your-username@remote-ip
```

### Changing the SSH Port

1. Edit `C:\ProgramData\ssh\sshd_config` on the Windows machine
2. Uncomment and change the line: `Port 22` to your desired port
3. Restart SSH service:
   ```powershell
   Restart-Service sshd
   ```
4. Update firewall rule for the new port

### Port Forwarding for Remote Access

If accessing from outside your local network, configure port forwarding on your router:
- Forward external port 22 (or custom port) to the Windows machine's local IP
- **Security Warning**: Only do this if you use strong passwords or key-based authentication

## Troubleshooting

### Connection Refused

Check if SSH service is running:
```powershell
Get-Service sshd
```

Start it if stopped:
```powershell
Start-Service sshd
```

### Firewall Issues

Verify firewall rule:
```powershell
Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP"
```

### Authentication Failed

- Verify username matches Windows account name exactly
- Check password is correct
- Ensure account has login rights

### Find Your IP Address

```powershell
ipconfig
```

Look for "IPv4 Address" under your active network adapter.

## Uninstall

To remove SSH server:

```powershell
Stop-Service sshd
Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Remove-NetFirewallRule -Name "OpenSSH-Server-In-TCP"
```

## Security Best Practices

1. ✅ Use SSH keys instead of passwords
2. ✅ Change default SSH port
3. ✅ Disable password authentication (after setting up keys)
4. ✅ Use firewall rules to restrict access by IP
5. ✅ Keep Windows updated
6. ⚠️ Never expose SSH directly to internet without strong authentication
