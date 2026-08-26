import subprocess
import ipaddress
import concurrent.futures
import platform
import sys

print("=" * 60)
print("     LOCAL NETWORK DEVICE DISCOVERY TOOL")
print("=" * 60)

# Get local network prefix (e.g., 192.168.1.)
network_input = input("Enter network prefix (e.g., 192.168.1): ").strip()
if not network_input.endswith('.'):
    network_input += '.'

subnet = network_input + '0/24'
print(f"\n[+] Scanning subnet: {subnet}")
print("-" * 60)

def ping_host(ip_addr):
    # Determine the ping command flag based on OS (Linux/Windows)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", "-W", "1", str(ip_addr)]
    
    try:
        # Run ping command silently
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            print(f"[ACTIVE] Device found at IP: {ip_addr}")
    except Exception:
        pass

# Use multi-threading to sweep the entire /24 subnet instantly
try:
    network = ipaddress.ip_network(subnet, strict=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(ping_host, network.hosts())
except ValueError:
    print("[-] Invalid network prefix entered.")
    sys.exit()

print("-" * 60)
print("Network discovery complete.")
print("=" * 60)
