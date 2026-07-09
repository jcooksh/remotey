# Remotey - Simple SSH Remote Access

Windows SSH remote access tool. Connect and control Windows machines via SSH.

## SSH into Windows from your Mac (over the internet)

**On your Mac**, run:

```bash
./remotey
```

It prints one command. **Paste that command into PowerShell on the Windows
machine** and click *Yes* on the admin prompt. Your Mac detects when it's live
and **connects you automatically** — no address to copy by hand.

- Only your Mac can log in (your key is baked into the command).
- No router setup, no account, no files to copy onto Windows.

Full guide: [TUNNEL.md](TUNNEL.md).

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
