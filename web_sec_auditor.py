import ssl
import socket
import sys
import requests
from datetime import datetime

print("=" * 60)
print("     REAL-WORLD WEB SECURITY & INFRASTRUCTURE AUDITOR")
print("=" * 60)

url = input("Enter target website URL (e.g., https://example.com): ").strip()

if not url.startswith("http"):
    url = "https://" + url

print(f"\n[+] Initializing security audit for: {url}")
print(f"[+] Scan Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 60)

# --- MODULE 1: HTTP Security Headers Check ---
print("\n[*] Checking HTTP Security Headers...")
try:
    response = requests.get(url, timeout=5)
    headers = response.headers
    
    security_headers = {
        "Strict-Transport-Security": "HSTS (Enforces secure HTTPS connections)",
        "Content-Security-Policy": "CSP (Prevents Cross-Site Scripting & Injection)",
        "X-Frame-Options": "Clickjacking Protection",
        "X-Content-Type-Options": "MIME-sniffing Protection"
    }

    for header, description in security_headers.items():
        if header in headers:
            print(f"    [PASS] {header}: Present")
        else:
            print(f"    [FAIL] {header}: MISSING! ({description})")

except requests.exceptions.RequestException as e:
    print(f"    [-] Could not fetch HTTP headers: {e}")

# --- MODULE 2: SSL/TLS Certificate Expiration Check ---
print("\n[*] Auditing SSL/TLS Certificate...")
try:
    # Extract domain name from URL for socket connection
    parsed_domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    
    context = ssl.create_default_context()
    with socket.create_connection((parsed_domain, 443), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=parsed_domain) as ssock:
            cert = ssock.getpeercert()
            
            # Extract expiration date
            not_after = cert.get('notAfter')
            expire_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            days_remaining = (expire_date - datetime.utcnow()).days
            
            print(f"    [INFO] Certificate Issuer: {dict(x[0] for x in cert['issuer']).get('commonName', 'Unknown')}")
            print(f"    [INFO] Expiration Date: {expire_date}")
            
            if days_remaining > 30:
                print(f"    [PASS] SSL Certificate is valid. ({days_remaining} days remaining)")
            elif 0 < days_remaining <= 30:
                print(f"    [WARNING] SSL Certificate expires soon! ({days_remaining} days remaining)")
            else:
                print(f"    [ALERT] SSL Certificate has EXPIRED!")

except Exception as e:
    print(f"    [-] Could not audit SSL certificate: {e}")

# --- MODULE 3: Sensitive File Exposure Check ---
print("\n[*] Scanning for Sensitive Exposed Files...")
sensitive_paths = ["/robots.txt", "/sitemap.xml", "/.git/HEAD", "/server-status"]

for path in sensitive_paths:
    target_endpoint = url.rstrip("/") + path
    try:
        res = requests.get(target_endpoint, timeout=3)
        if res.status_code == 200:
            print(f"    [ALERT] Accessible file/endpoint found: {target_endpoint} (Status 200)")
        else:
            print(f"    [SAFE] {path} protected or missing (Status {res.status_code})")
    except:
        pass

print("\n" + "=" * 60)
print("Audit complete. Ready for reporting.")
print("=" * 60)

