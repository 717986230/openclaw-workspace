
#!/usr/bin/env python3
import requests
import sys

print("Testing proxy...")
print(f"Python: {sys.version}")

proxies = {
    'http': 'http://127.0.0.1:7891',
    'https': 'http://127.0.0.1:7891',
}

try:
    print("Trying without proxy first...")
    r = requests.get('https://httpbin.org/get', timeout=5)
    print(f"Without proxy: {r.status_code}")
except Exception as e:
    print(f"Without proxy failed: {e}")

try:
    print("\nTrying with proxy...")
    r = requests.get('https://httpbin.org/get', proxies=proxies, timeout=10)
    print(f"With proxy: {r.status_code}")
    print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"With proxy failed: {e}")
    import traceback
    traceback.print_exc()
