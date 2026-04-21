import urllib.request, ssl, re, json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    'https://blog.csdn.net/m0_73579990/article/details/154578187',
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
)

try:
    r = urllib.request.urlopen(req, timeout=15, context=ctx)
    html = r.read().decode('utf-8', errors='replace')
except Exception as e:
    print('FETCH ERROR:', e)
    sys.exit(1)

# Find article-content div
m = re.search(r'id="content_views"[^>]*>(.*?)</div>\s*<div', html, re.DOTALL)
if m:
    content = m.group(1)
    text = re.sub(r'<[^>]+>', ' ', content)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&#39;', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    print('TEXT:', text[:5000])
else:
    pre_blocks = re.findall(r'<pre[^>]*>(.*?)</pre>', html, re.DOTALL)
    found = 0
    for i, block in enumerate(pre_blocks[:10]):
        t = re.sub(r'<[^>]+>', '', block).strip()
        if 'ollama' in t.lower() or 'api' in t.lower():
            print('PREBLOCK', i, ':', t[:500])
            found += 1
    if not found:
        print('NO OLLAMA CONTENT IN PRE BLOCKS')
        print('HTML LEN:', len(html))
        # search for any key strings
        for kw in ['BF-', 'ollama', 'baseurl', 'base_url', 'endpoint']:
            idx = html.lower().find(kw.lower())
            if idx >= 0:
                print('FOUND kw:', html[max(0,idx-100):idx+300])