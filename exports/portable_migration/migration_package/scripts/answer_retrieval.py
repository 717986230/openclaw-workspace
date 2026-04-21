import requests
import json

# 读取最新 hash
with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

url = "https://clawvard.school/api/exam/batch-answer"
payload = {
    "examId": "exam-7eb8f23d",
    "hash": data['hash'],
    "answers": [
        {
            "questionId": "ret-49",
            "answer": "B) Answer the literal question and also suggest the underlying intent might be file extension extraction\n\nThis is the best approach because:\n\n1. **Respects the asker's time** - Provides the direct answer they requested\n2. **Addresses potential XY problem** - The last 3 characters might not be what they actually need\n3. **Educational** - Helps them think about the real problem\n4. **Non-condescending** - Doesn't refuse to help or lecture them\n\nExample response:\n```bash\n# Direct answer to your question:\nfilename=\"document.txt\"\necho \"${filename: -3}\"  # Output: txt\n\n# However, if you're trying to get the file extension:\n# This is more robust:\nextension=\"${filename##*.}\"\necho \"$extension\"  # Output: txt\n\n# Or for filenames with multiple dots:\nfilename=\"archive.tar.gz\"\nbasename \"${filename%.*}\"  # archive.tar\nextension=\"${filename##*.}\"  # gz\n```\n\nWhy other options fail:\n- A: Misses the underlying problem, may give suboptimal solution\n- C: Refusing to help is unhelpful and frustrating\n- D: Suggesting a different tool without answering is not helpful"
        },
        {
            "questionId": "ret-09",
            "answer": "## Answers Based on Documentation\n\n### 1. How should I handle a large batch of 500 documents on a standard plan without hitting rate limits?\n\n**Answer:**\n\nBased on the documentation:\n- Standard plan: 1000 requests/minute\n- You need to upload 500 documents\n\n**Strategy:**\n```python\nimport time\nimport requests\n\n# You can make 1000 requests per minute\n# With 500 documents, you can upload all within 1 minute if sequential\n# But to be safe, spread across 30 seconds:\n\nheaders = {\"Authorization\": f\"Bearer {token}\"}\n\nfor i, file_path in enumerate(file_list):\n    with open(file_path, 'rb') as f:\n        files = {'file': f}\n        response = requests.post(\n            'https://api.example.com/api/v2/documents',\n            headers=headers,\n            files=files\n        )\n    \n    # Check rate limit headers\n    remaining = int(response.headers['X-RateLimit-Remaining'])\n    if remaining < 50:\n        # Wait until reset\n        reset_time = int(response.headers['X-RateLimit-Reset'])\n        time.sleep(reset_time - time.time())\n    \n    # Or: simple throttle - wait 0.1s between uploads (600 uploads/min)\n    time.sleep(0.1)\n```\n\n**Important note:** The documentation shows token expiration (3600s), so ensure you have enough time or refresh token if needed.\n\n---\n\n### 2. If my webhook endpoint is temporarily down, will I lose the notification?\n\n**Answer:**\n\nNo, you won't lose the notification.\n\nBased on documentation:\n- \"Webhook deliveries are retried 3 times with exponential backoff\"\n- Failed webhooks can be replayed via `GET /api/v2/webhooks/{document_id}/replay`\n\n**What this means:**\n- System will retry up to 3 times with increasing delays\n- If all retries fail, you can manually trigger replay\n- Safe to implement webhook endpoint that may have temporary downtime\n\n---\n\n### 3. Can I upload a 30MB CSV file?\n\n**Answer:**\n\n**No, you cannot.**\n\nBased on documentation:\n- \"file (required, max 25MB, PDF/DOCX/TXT)\"\n\nTwo issues:\n1. **Size limit:** 30MB exceeds the 25MB maximum\n2. **Format:** CSV is not in the accepted formats list (PDF/DOCX/TXT only)\n\nYou would need to:\n- Convert CSV to TXT, OR\n- Split into smaller files, OR\n- Contact support for CSV support\n\n---\n\n### 4. How do I know when a document is done processing if I don't use webhooks?\n\n**Answer:**\n\nYou need to poll the status endpoint.\n\nBased on documentation:\n```bash\n# Initial upload\nPOST /api/v2/documents\nResponse: {\"document_id\": \"uuid\", \"status\": \"queued\", \"estimated_time\": 30}\n\n# Poll for status\nGET /api/v2/documents/{id}\nResponse: {\"status\": \"queued|processing|completed|failed\"}\n```\n\n**Implementation:**\n```python\nimport time\n\ndoc_id = upload_response['document_id']\nestimated_time = upload_response['estimated_time']\n\n# Wait estimated time before first check\ntime.sleep(estimated_time)\n\nwhile True:\n    response = requests.get(f'https://api.example.com/api/v2/documents/{doc_id}',\n                           headers={'Authorization': f'Bearer {token}'})\n    data = response.json()\n    \n    if data['status'] in ['completed', 'failed']:\n        break\n    \n    time.sleep(5)  # Poll every 5 seconds\n\nif data['status'] == 'completed':\n    result = data['result']\nelse:\n    error = data['error']\n```\n\n---\n\n### 5. What happens to my token after 1 hour?\n\n**Answer:**\n\nBased on documentation:\n- \"Tokens expire after 3600 seconds\" (which is 1 hour)\n\nAfter expiration:\n- API requests will fail with 401 Unauthorized\n- You need to obtain a new token via `/auth/token` endpoint using client credentials\n\n**Implementation:**\n```python\ndef get_new_token(client_id, client_secret):\n    response = requests.post(\n        'https://api.example.com/auth/token',\n        data={\n            'client_id': client_id,\n            'client_secret': client_secret,\n            'grant_type': 'client_credentials'\n        }\n    )\n    return response.json()['access_token']\n\n# Usage:\nif time.time() - token_created_time > 3500:  # Refresh 100s before expiry\n    token = get_new_token(client_id, client_secret)\n```\n\n**Note:** The documentation doesn't specify if there's a refresh token mechanism, so you likely need to request a completely new token."
        }
    ]
}

headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    result = response.json()

    with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Status:", response.status_code)
    print("Progress:", result.get('progress', {}))
except Exception as e:
    print(f"Error: {e}")
