#!/usr/bin/env python3
"""
Send notification to Feishu via OpenClaw gateway
"""

import json
import requests
from pathlib import Path

# OpenClaw gateway endpoint
GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = "7f3237d931335aa96698261b132dd2fed199330e7bd6c49e"

def send_feishu_message(user_id: str, message: str):
    """Send message to Feishu user via OpenClaw gateway"""

    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": "feishu",
        "to": user_id,
        "message": message
    }

    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/send",
            headers=headers,
            json=payload,
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    # Your Feishu user ID (from the conversation)
    user_id = "ou_30e2dc50db8c633d2e0f213ba0d8e05a"

    # Get today's memories
    import sqlite3
    db_path = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    c.execute("""
        SELECT title, importance
        FROM memories
        WHERE type='event' AND date(created_at)=date('now')
        ORDER BY importance DESC, created_at DESC
        LIMIT 10
    """)

    events = c.fetchall()
    conn.close()

    # Build message
    message = "📊 **GitHub Trending Daily Report**\n\n"
    message += f"✅ 已完成分析 {len(events)} 个事件\n\n"

    if events:
        message += "**今日事件:**\n"
        for title, importance in events:
            message += f"- [{importance}] {title}\n"

    message += "\n*详情请查看数据库*"

    # Send
    if send_feishu_message(user_id, message):
        print("Notification sent successfully!")
    else:
        print("Failed to send notification")

if __name__ == "__main__":
    main()
