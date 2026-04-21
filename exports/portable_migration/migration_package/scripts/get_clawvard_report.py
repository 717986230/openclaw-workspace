import requests
import json

token = "eyJhbGciOiJIUzI1NiJ9.eyJleGFtSWQiOiJleGFtLTdlYjhmMjNkIiwicmVwb3J0SWQiOiJldmFsLTdlYjhmMjNkIiwiYWdlbnROYW1lIjoiRXJiaW5nIiwiZW1haWwiOiJ4aW5nbHlhbmc3MTdAZ21haWwuY29tIiwiaWF0IjoxNzc1ODY5NDU5LCJleHAiOjE3NzY0NzQyNTksImlzcyI6ImNsYXd2YXJkIn0.2WR5OJNhJHEgTwFklIcw70xbn5BNl80NhLimxhaDjmM"

# 获取详细成绩单
url = "https://clawvard.school/api/agent/report"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    print("Status:", response.status_code)
    
    if response.status_code == 200:
        result = response.json()
        
        # 保存完整成绩单
        with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_full_report.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 70)
        print("CLAWVARD FULL REPORT")
        print("=" * 70)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Error:", response.text)
        
except Exception as e:
    print(f"Error: {e}")
