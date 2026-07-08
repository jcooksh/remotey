#!/usr/bin/env python3
"""
SSH Remote Tool for Windows
Simple SSH client for remote Windows server management
"""

import paramiko
import argparse
import sys
import getpass
from pathlib import Path


class SSHRemote:
    def __init__(self, host, port=22, username=None, password=None, key_file=None):
        self.host = host
        self.port = port
        self.username = username or getpass.getuser()
        self.password = password
        self.key_file = key_file
        self.client = None

    def connect(self):
        """Establish SSH connection"""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.key_file:
                key_path = Path(self.key_file).expanduser()
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=str(key_path)
                )
            elif self.password:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            else:
                password = getpass.getpass(f"Password for {self.username}@{self.host}: ")
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=password
                )
            print(f"Connected to {self.host}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}", file=sys.stderr)
            return False

    def execute(self, command):
        """Execute command on remote host"""
        if not self.client:
            print("Not connected", file=sys.stderr)
            return None

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()

            if output:
                print(output)
            if error:
                print(error, file=sys.stderr)

            return exit_code
        except Exception as e:
            print(f"Execution failed: {e}", file=sys.stderr)
            return None

    def upload(self, local_path, remote_path):
        """Upload file to remote host"""
        if not self.client:
            print("Not connected", file=sys.stderr)
            return False

        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"Uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            print(f"Upload failed: {e}", file=sys.stderr)
            return False

    def download(self, remote_path, local_path):
        """Download file from remote host"""
        if not self.client:
            print("Not connected", file=sys.stderr)
            return False

        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            print(f"Downloaded {remote_path} to {local_path}")
            return True
        except Exception as e:
            print(f"Download failed: {e}", file=sys.stderr)
            return False

    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print("Connection closed")


def main():
    parser = argparse.ArgumentParser(description="SSH Remote Tool for Windows")
    parser.add_argument("host", help="Remote host address")
    parser.add_argument("-p", "--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("-u", "--username", help="SSH username")
    parser.add_argument("-k", "--key-file", help="Path to SSH private key")
    parser.add_argument("-c", "--command", help="Command to execute")
    parser.add_argument("--upload", nargs=2, metavar=("LOCAL", "REMOTE"), help="Upload file")
    parser.add_argument("--download", nargs=2, metavar=("REMOTE", "LOCAL"), help="Download file")

    args = parser.parse_args()

    remote = SSHRemote(
        host=args.host,
        port=args.port,
        username=args.username,
        key_file=args.key_file
    )

    if not remote.connect():
        sys.exit(1)

    try:
        if args.command:
            exit_code = remote.execute(args.command)
            sys.exit(exit_code if exit_code is not None else 1)
        elif args.upload:
            success = remote.upload(args.upload[0], args.upload[1])
            sys.exit(0 if success else 1)
        elif args.download:
            success = remote.download(args.download[0], args.download[1])
            sys.exit(0 if success else 1)
        else:
            print("Interactive shell not implemented. Use -c to execute commands.")
            sys.exit(1)
    finally:
        remote.close()


if __name__ == "__main__":
    main()
