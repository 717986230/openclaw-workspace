import urllib.request
import re
import json

tweet_id = '2045142797439922337'
screen_name = 'gittrend0x'

# Try the syndication endpoint
url = f'https://syndication.twitter.com/srv/timeline-profile/screen-name/{screen_name}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Extract OG tags
    title = re.search(r'property="og:title" content="([^"]+)"', html)
    desc = re.search(r'property="og:description" content="([^"]+)"', html)
    img = re.search(r'property="og:image" content="([^"]+)"', html)
    
    print('=== OG Meta ===')
    if title: print('Title:', title.group(1))
    if desc: print('Description:', desc.group(1))
    if img: print('Image:', img.group(1))
    
    # Look for timeline JSON data
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', html, re.DOTALL)
    if match:
        print('\nFound timeline JSON')
        data = json.loads(match.group(1))
        print(json.dumps(data, indent=2)[:2000])
    else:
        print('\nNo timeline JSON found, checking for embedded data...')
        # Try finding tweet entries
        entries = re.findall(r'"full_text":"([^"]+)"', html)
        print(f'Found {len(entries)} tweet entries:')
        for e in entries[:5]:
            print(' -', e[:200])
        
        print('\n--- Raw HTML excerpt (char 1500-4000) ---')
        print(html[1500:4000])
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()