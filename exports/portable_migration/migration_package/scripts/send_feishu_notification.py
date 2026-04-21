#!/usr/bin/env python3
"""
Feishu Notification Script - Send PR results to Feishu
"""

import sqlite3
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")

def get_recent_prs(hours=1):
    """Get PRs created in the last N hours"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
    c.execute("""
        SELECT title, content, created_at
        FROM memories
        WHERE type='event' AND title LIKE '%PR Created%' AND created_at > ?
        ORDER BY created_at DESC
    """, (cutoff,))

    prs = []
    for row in c.fetchall():
        prs.append({
            "title": row[0],
            "content": row[1],
            "time": row[2]
        })
    conn.close()
    return prs

def send_feishu_message(title, content):
    """Send message to Feishu via webhook"""
    # Use OpenClaw gateway internal API
    gateway_url = "http://127.0.0.1:18789"

    # Your user ID from Feishu
    user_id = "ou_30e2dc50db8c633d2e0f213ba0d8e05a"

    # Try to send via gateway
    try:
        # First check gateway status
        status = requests.get(f"{gateway_url}/status", timeout=5)
        if status.status_code != 200:
            print(f"Gateway not ready: {status.status_code}")
            return False

        # Send message (this depends on gateway having a send endpoint)
        # For now, we'll save to a notification file that OpenClaw can pick up
        notification = {
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }

        # Save notification
        notif_path = Path(r"C:\Users\Administrator\.openclaw\workspace\logs\feishu_notification.json")
        notif_path.parent.mkdir(parents=True, exist_ok=True)

        with open(notif_path, 'w', encoding='utf-8') as f:
            json.dump(notification, f, ensure_ascii=False, indent=2)

        print(f"Notification saved to: {notif_path}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=== Feishu Notification ===")

    # Get recent PRs (last 12 hours)
    prs = get_recent_prs(hours=12)

    if not prs:
        print("No new PRs to report")
        return

    # Build message
    title = f"GitHub PR Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    content_lines = [f"**Created {len(prs)} PR(s) in the last hour**\n"]
    for pr in prs:
        content_lines.append(f"- {pr['title']}")
        if 'URL:' in pr['content']:
            url = pr['content'].split('URL:')[1].split()[0] if 'URL:' in pr['content'] else ''
            content_lines.append(f"  Link: {url}")

    content = "\n".join(content_lines)

    print(content)

    # Send notification
    send_feishu_message(title, content)

if __name__ == "__main__":
    main()
