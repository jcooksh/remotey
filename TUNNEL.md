# Remotey Tunnel — SSH into Windows from your Mac (no router setup)

You drive everything from your Mac. It hands you one command to run on the
Windows machine, then connects you automatically when that machine comes online.

## How it works

1. **Mac:** `./remotey` makes your SSH key (once), picks a port it owns, and
   prints a single PowerShell command with your public key + that port baked in.
   Then it waits.
2. **Windows:** you paste that command into PowerShell. It installs the SSH
   server, downloads a tiny tunnel tool ([bore](https://github.com/ekzhang/bore)),
   trusts only your Mac's key, and opens a tunnel on the port your Mac chose.
3. **Mac:** detects the port is live and drops you straight into a shell.

Because the Mac picks the port, it already knows the exact address — no copying
the connection string from the Windows screen.

## Use it

**On your Mac:**

```bash
./remotey                # asks your Windows username the first time
```

Copy the command it prints. **On the Windows machine**, open PowerShell, paste
it, click **Yes** on the admin prompt. Back on the Mac it connects by itself.

## Notes

- **Only your Mac can connect.** The Windows side trusts just the key
  `~/.ssh/remotey_key` that lives on your Mac. Nobody else can log in even if
  they find the port.
- **The port is fixed** to your Mac, saved in `~/.remotey/port`. Want a new one:
  `./remotey "" --new`.
- **Keep the Windows PowerShell window open** — closing it drops the tunnel.
  Re-paste the command to bring it back.
- **Different relay:** `bore.pub` is a free public server. If it's down you can
  run your own bore server and set `REMOTEY_TUNNEL` / edit `go.ps1`.
- **Password login stays on** as a backup so you can't lock yourself out
  remotely. To go key-only, set `PasswordAuthentication no` in
  `C:\ProgramData\ssh\sshd_config` and `Restart-Service sshd`.
