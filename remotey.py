#!/usr/bin/env python3
"""
Remotey - Simple SSH remote access client
"""
import sys
import subprocess
import os
from pathlib import Path


def connect(host, username="remotey", port=22):
    """Connect to remote Windows host via SSH"""
    key_path = Path.home() / ".ssh" / "remotey_key"

    if not key_path.exists():
        print("Error: SSH key not found. Run setup_host.py on target machine first.")
        sys.exit(1)

    print(f"Connecting to {username}@{host}:{port}...")

    cmd = [
        "ssh",
        "-i", str(key_path),
        "-o", "StrictHostKeyChecking=no",
        f"{username}@{host}",
        "-p", str(port)
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDisconnected.")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: remotey.py <host-ip> [username] [port]")
        sys.exit(1)

    host = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "remotey"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 22

    connect(host, username, port)


if __name__ == "__main__":
    main()
