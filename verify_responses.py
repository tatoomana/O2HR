#!/usr/bin/env python3
"""
Verify that "200" responses from traversal attempts are SPA HTML, not actual files
"""
import requests

base_url = "https://devops-docker-ai.preview.emergentagent.com"

print("Comparing responses:\n")

# 1. Valid API request (should return JSON with file content)
print("1. Valid API request: /api/files/docker-compose.yml")
resp1 = requests.get(f"{base_url}/api/files/docker-compose.yml", timeout=10)
print(f"   Status: {resp1.status_code}")
print(f"   Content-Type: {resp1.headers.get('Content-Type')}")
print(f"   Is JSON: {'application/json' in resp1.headers.get('Content-Type', '')}")
if resp1.status_code == 200:
    try:
        data = resp1.json()
        print(f"   Has 'content' field: {'content' in data}")
        print(f"   Has 'language' field: {'language' in data}")
        if 'content' in data:
            print(f"   Content preview: {data['content'][:100]}...")
    except Exception:
        print(f"   Response is not JSON")

# 2. Traversal attempt (client normalizes to /etc/passwd, hits SPA)
print("\n2. Traversal attempt: /api/files/../../../etc/passwd")
resp2 = requests.get(f"{base_url}/api/files/../../../etc/passwd", allow_redirects=False, timeout=10)
print(f"   Status: {resp2.status_code}")
print(f"   Content-Type: {resp2.headers.get('Content-Type')}")
print(f"   Is HTML: {'text/html' in resp2.headers.get('Content-Type', '')}")
print(f"   Response length: {len(resp2.text)} bytes")
if resp2.status_code == 200:
    # Check if it's the React SPA
    is_react_app = '<div id="root">' in resp2.text or 'react' in resp2.text.lower()
    print(f"   Contains React app markers: {is_react_app}")
    print(f"   First 200 chars: {resp2.text[:200]}")

# 3. URL-encoded traversal (reaches backend, should be 404)
print("\n3. URL-encoded traversal: /api/files/..%2F..%2F..%2Fetc%2Fpasswd")
resp3 = requests.get(f"{base_url}/api/files/..%2F..%2F..%2Fetc%2Fpasswd", timeout=10)
print(f"   Status: {resp3.status_code}")
print(f"   Content-Type: {resp3.headers.get('Content-Type')}")
if resp3.status_code == 404:
    print(f"   ✅ Backend correctly blocked the traversal attempt!")
    try:
        error_data = resp3.json()
        print(f"   Error detail: {error_data.get('detail', 'N/A')}")
    except Exception:
        pass

# 4. Another traversal pattern
print("\n4. Relative path: /api/files/./docker-compose.yml")
resp4 = requests.get(f"{base_url}/api/files/./docker-compose.yml", allow_redirects=False, timeout=10)
print(f"   Status: {resp4.status_code}")
print(f"   Content-Type: {resp4.headers.get('Content-Type')}")
if resp4.status_code == 200:
    is_html = 'text/html' in resp4.headers.get('Content-Type', '')
    is_json = 'application/json' in resp4.headers.get('Content-Type', '')
    print(f"   Is HTML (SPA): {is_html}")
    print(f"   Is JSON (API): {is_json}")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("If traversal attempts return HTML (SPA), the backend is secure.")
print("If they return JSON with file content, there's a security issue.")
