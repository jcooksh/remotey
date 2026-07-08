#!/usr/bin/env python3
"""
SSH Remote Access Client
Connects to server using join link
"""
import paramiko
import argparse
import sys
from urllib.parse import urlparse

def parse_link(link):
    """Parse remotey:// link"""
    if link.startswith('remotey://'):
        parsed = urlparse(link)
        host = parsed.hostname
        port = parsed.port or 2222
        session_id = parsed.path.lstrip('/')
        return host, port, session_id
    else:
        raise ValueError("Invalid link format. Expected remotey://host:port/session_id")

def connect_client(link):
    """Connect to SSH server using link"""
    host, port, session_id = parse_link(link)

    print(f"[+] Connecting to {host}:{port}")
    print(f"[+] Session: {session_id}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            host,
            port=port,
            username='remotey',
            password=session_id,
            look_for_keys=False,
            allow_agent=False
        )

        print("[+] Connected!")
        print("[+] Starting interactive shell...")

        # Start interactive shell
        channel = client.invoke_shell()

        import select
        import tty
        import termios

        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            channel.settimeout(0.0)

            while True:
                r, w, e = select.select([channel, sys.stdin], [], [])
                if channel in r:
                    try:
                        x = channel.recv(1024)
                        if len(x) == 0:
                            print("\r\n[+] Connection closed")
                            break
                        sys.stdout.write(x.decode('utf-8'))
                        sys.stdout.flush()
                    except socket.timeout:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    channel.send(x)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False
    finally:
        client.close()

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remotey SSH Client')
    parser.add_argument('link', help='Join link (remotey://host:port/session_id)')
    args = parser.parse_args()

    connect_client(args.link)
