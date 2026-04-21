import requests
import sys

url = "https://r.jina.ai/https://x.com/dtdt666/status/2042524166491107665"

try:
    r = requests.get(url, timeout=30)
    
    # Save to file to avoid encoding issues
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/twitter_content.txt', 'w', encoding='utf-8') as f:
        f.write(r.text)
    
    print("Content saved to twitter_content.txt")
    print(f"Length: {len(r.text)} characters")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
