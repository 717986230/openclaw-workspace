import requests
import json

# 开始考试
url = "https://clawvard.school/api/exam/start"
payload = {
    "agentName": "Erbing",
    "model": "nvidia-main/z-ai/glm5"
}

headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print("Status:", response.status_code)
    print("Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
