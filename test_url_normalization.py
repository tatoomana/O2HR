#!/usr/bin/env python3
"""
Test to understand URL normalization behavior
"""
import requests
from urllib.parse import urljoin, quote

base_url = "https://devops-docker-ai.preview.emergentagent.com"

# Test different ways of making the request
test_cases = [
    ("Normal request", f"{base_url}/api/files/../../../etc/passwd"),
    ("With quote", f"{base_url}/api/files/{quote('../../../etc/passwd', safe='')}"),
    ("Manual construction", f"{base_url}/api/files/../../../etc/passwd"),
]

print("Testing URL normalization behavior:\n")

for name, url in test_cases:
    print(f"\n{name}:")
    print(f"  Requested URL: {url}")
    
    try:
        # Use PreparedRequest to see what's actually sent
        req = requests.Request('GET', url)
        prepared = req.prepare()
        print(f"  Prepared URL:  {prepared.url}")
        
        resp = requests.get(url, allow_redirects=False, timeout=10)
        print(f"  Response: {resp.status_code}")
        
        if resp.status_code in [301, 302, 307, 308]:
            print(f"  Redirect to: {resp.headers.get('Location', 'N/A')}")
            
        # Check what content we got
        content_type = resp.headers.get('Content-Type', '')
        if 'json' in content_type:
            print(f"  Content-Type: JSON (API response)")
        elif 'html' in content_type:
            print(f"  Content-Type: HTML (likely SPA fallback)")
        else:
            print(f"  Content-Type: {content_type}")
            
    except Exception as e:
        print(f"  Error: {e}")

# Test the actual API endpoint directly
print("\n\nDirect API test (should work):")
resp = requests.get(f"{base_url}/api/files/docker-compose.yml", timeout=10)
print(f"  /api/files/docker-compose.yml: {resp.status_code}")

print("\n\nTest nonexistent file (should be 404):")
resp = requests.get(f"{base_url}/api/files/nonexistent.txt", timeout=10)
print(f"  /api/files/nonexistent.txt: {resp.status_code}")
