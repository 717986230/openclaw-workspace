import requests
import json

with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

url = "https://clawvard.school/api/exam/batch-answer"
payload = {
    "examId": "exam-7eb8f23d",
    "hash": data['hash'],
    "answers": [
        {
            "questionId": "mem-44",
            "answer": "C) Validate the address format client-side during checkout, then queue a background job to verify with the geocoding API and notify the user asynchronously if there's an issue\n\nThis is the correct approach because:\n\n1. **Respects the constraints:**\n   - No external API calls in hot path (checkout must stay <50ms)\n   - Third-party services only in background jobs\n\n2. **Still provides value:**\n   - Basic format validation catches obvious errors immediately\n   - Geocoding verification happens asynchronously\n   - User gets feedback (positive or negative) within reasonable time\n\n3. **User experience considerations:**\n   - Checkout remains fast (no 100-500ms geocoding API delay)\n   - Most invalid addresses caught by format check\n   - For edge cases: order processed, user notified if address is undeliverable\n   - Can ship to validated address or contact customer\n\nWhy other options fail:\n- A: Breaking architectural constraints for convenience leads to technical debt\n- B: Throwing away valuable feature because it's inconvenient\n- D: Caching \"all possible addresses\" is impossible and defeats the purpose of validation\n\nImplementation example:\n```javascript\n// Client-side format validation (instant)\nfunction validateAddressFormat(address) {\n  return address.street && address.city && address.zip.length === 5;\n}\n\n// In checkout handler\nif (!validateAddressFormat(req.body.address)) {\n  return res.status(400).json({ error: 'Invalid address format' });\n}\n\n// Queue background job for geocoding\nawait queue.add('verify-address', {\n  orderId: order.id,\n  address: req.body.address\n});\n\n// Continue checkout immediately\nres.json({ orderId: order.id, status: 'processing' });\n\n// Background job:\n// - Calls geocoding API\n// - If invalid: sends notification to user\n// - Updates order metadata with validated address\n```"
        },
        {
            "questionId": "mem-36",
            "answer": "Function name: **aggregateSessionMetrics**\n\nFile location: **src/services/analytics/sessionTracker.ts**"
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
