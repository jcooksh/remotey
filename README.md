# Remotey - Simple SSH Remote Access

Windows SSH remote access tool. Connect and control Windows machines via SSH.

## One step: SSH over the internet

On the Windows machine, open **PowerShell** and paste this one line:

```powershell
irm https://raw.githubusercontent.com/jcooksh/remotey/main/go.ps1 | iex
```

Click **Yes** on the admin prompt. It prints an address like:

```
ssh you@serveo.net -p 14823
```

Run that from any other computer — you're in. No files to copy, no router
setup, no account. Full guide: [TUNNEL.md](TUNNEL.md).

## Quick Start (same network)

**Host (Windows machine to control):**
```bash
python setup_host.py
```

**Client (your machine):**
```bash
python remotey.py <host-ip>
```

## Features

- Automatic SSH server setup on Windows
- Secure key-based authentication
- Simple one-command connection
- No ID codes or complex setup

## Requirements

- Python 3.7+
- Windows 10/11 (host)
- OpenSSH

## License

MIT
