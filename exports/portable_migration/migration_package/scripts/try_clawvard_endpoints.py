import requests
import json

token = "eyJhbGciOiJIUzI1NiJ9.eyJleGFtSWQiOiJleGFtLTdlYjhmMjNkIiwicmVwb3J0SWQiOiJldmFsLTdlYjhmMjNkIiwiYWdlbnROYW1lIjoiRXJiaW5nIiwiZW1haWwiOiJ4aW5nbHlhbmc3MTdAZ21haWwuY29tIiwiaWF0IjoxNzc1ODY5NDU5LCJleHAiOjE3NzY0NzQyNTksImlzcyI6ImNsYXd2YXJkIn0.2WR5OJNhJHEgTwFklIcw70xbn5BNl80NhLimxhaDjmM"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 尝试不同的端点
endpoints = [
    "https://clawvard.school/api/agent/profile",
    "https://clawvard.school/api/exam/result",
    "https://clawvard.school/api/report",
    "https://clawvard.school/api/agent/scores",
]

for endpoint in endpoints:
    try:
        print(f"\nTrying: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Success!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 保存结果
            with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_scores.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            break
        else:
            print(f"Error: {response.text[:100]}")
    except Exception as e:
        print(f"Error: {str(e)[:100]}")
