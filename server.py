#!/usr/bin/env python3
"""
SSH Remote Access Server
Simple SSH server that generates a join link for remote access
"""
import socket
import secrets
import paramiko
import threading
import argparse
from pathlib import Path

class SSHServer(paramiko.ServerInterface):
    def __init__(self, session_id):
        self.session_id = session_id
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # Accept any password for demo - in production use proper auth
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        return True

def generate_session_link(host, port, session_id):
    """Generate join link for client"""
    return f"remotey://{host}:{port}/{session_id}"

def start_server(host='0.0.0.0', port=2222):
    """Start SSH server and wait for connections"""

    # Generate or load host key
    key_path = Path.home() / '.remotey' / 'host_key'
    key_path.parent.mkdir(exist_ok=True)

    if not key_path.exists():
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(str(key_path))
    else:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)

    session_id = secrets.token_urlsafe(16)

    # Get public IP for link
    public_ip = socket.gethostbyname(socket.gethostname())
    link = generate_session_link(public_ip, port, session_id)

    print(f"[+] Server started on {host}:{port}")
    print(f"[+] Session ID: {session_id}")
    print(f"[+] Join link: {link}")
    print(f"[+] Waiting for connections...")

    while True:
        client, addr = sock.accept()
        print(f"[+] Connection from {addr}")

        transport = paramiko.Transport(client)
        transport.add_server_key(key)

        server = SSHServer(session_id)
        transport.start_server(server=server)

        channel = transport.accept(20)
        if channel is None:
            print("[-] No channel")
            continue

        print(f"[+] Channel opened")
        server.event.wait(10)

        if not server.event.is_set():
            print("[-] Client never asked for shell")
            continue

        # Handle commands
        channel.send("Welcome to Remotey SSH Server!\r\n")
        channel.send("Type commands or 'exit' to disconnect\r\n\r\n")

        try:
            import subprocess
            while True:
                channel.send("remotey> ")
                command = ""
                while not command.endswith('\r') and not command.endswith('\n'):
                    data = channel.recv(1024).decode('utf-8')
                    if not data:
                        break
                    command += data
                    channel.send(data)  # Echo

                command = command.strip()
                if not command:
                    continue

                if command.lower() == 'exit':
                    channel.send("\r\nGoodbye!\r\n")
                    break

                # Execute command
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    output = result.stdout + result.stderr
                    channel.send(f"\r\n{output}\r\n")
                except Exception as e:
                    channel.send(f"\r\nError: {str(e)}\r\n")

        except Exception as e:
            print(f"[-] Error: {e}")
        finally:
            channel.close()
            transport.close()
            print(f"[-] Connection closed from {addr}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remotey SSH Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=2222, help='Port to listen on')
    args = parser.parse_args()

    start_server(args.host, args.port)
