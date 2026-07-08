# Remotey Tunnel — SSH into Windows over the internet (no router config)

Turn any Windows machine into a server you can SSH into from anywhere.
No account, no port forwarding, no extra software — uses Windows' built-in
SSH client and the free [serveo.net](https://serveo.net) relay.

## On the Windows machine (the "server") — one step

Open **PowerShell** and paste this single line:

```powershell
irm https://raw.githubusercontent.com/jcooksh/remotey/main/go.ps1 | iex
```

Click **Yes** on the admin prompt. It installs the SSH server (if missing),
opens the tunnel, and prints your address:

```
ssh YOURUSER@serveo.net -p 14823
```

**Leave the window open** — closing it drops the connection.

> Offline alternative: copy the folder and double-click `run_host.bat`.

## From any other computer (Mac / Linux / Windows)

Paste the command it gave you:

```bash
ssh YOURUSER@serveo.net -p 14823
```

Enter your **Windows password**. You're now in a shell on the Windows box.
Run PowerShell, start services, whatever — use it like a server.

## Notes / gotchas

- **The port changes each time** you restart the tunnel (serveo assigns a random
  one on the free relay). Re-run `run_host.bat` and grab the new line.
- **serveo can be down sometimes.** To use a different relay:
  ```powershell
  $env:REMOTEY_TUNNEL="your-relay-host"; .\tunnel_host.ps1
  ```
- **No Python needed on the Windows host** — it's pure PowerShell.

## Security

This puts a Windows login prompt on the public internet (behind an obscure
random port). Protect it:

1. Use a **strong Windows password**, OR
2. Set up **SSH keys** and disable password auth (see `SETUP.md`).

Anyone with the address + your password/key can control the machine. Only share
it with yourself.
