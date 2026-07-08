"""SSH Remote Client - Connect to Windows host"""
import subprocess
import sys
import argparse

def connect_ssh(host, username=None, port=22):
    """Connect to SSH server"""
    if username:
        target = f"{username}@{host}"
    else:
        target = host

    cmd = ['ssh', '-p', str(port), target]

    print(f"Connecting to {target}...")
    print("Enter password when prompted")
    print("-" * 50)

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nConnection closed")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='SSH Remote Client')
    parser.add_argument('host', help='Host IP or hostname')
    parser.add_argument('-u', '--username', help='Username for SSH connection')
    parser.add_argument('-p', '--port', type=int, default=22, help='SSH port (default: 22)')

    args = parser.parse_args()

    connect_ssh(args.host, args.username, args.port)

if __name__ == "__main__":
    main()
