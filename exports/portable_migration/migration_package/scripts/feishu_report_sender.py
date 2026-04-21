#!/usr/bin/env python3
"""
飞书报告发送器 - 发送每小时学习报告到飞书
用法: python feishu_report_sender.py --message "报告内容"
"""
import json
import sys
import requests
from pathlib import Path

class FeishuReportSender:
    """飞书报告发送器"""
    
    def __init__(self):
        self.config_file = Path("config/feishu_webhook.json")
        self.config = self._load_config()
    
    def _load_config(self):
        """加载飞书配置"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def send_message(self, title, content):
        """发送消息到飞书"""
        webhook_url = self.config.get("webhook_url")
        
        if not webhook_url:
            # 保存待发送
            return self._save_pending(title, content)
        
        # 构造飞书消息格式
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看详情"
                                },
                                "type": "primary"
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": "发送成功"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _save_pending(self, title, content):
        """保存待发送消息"""
        pending_dir = Path("memory/pending_feishu_reports")
        pending_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M')
        pending_file = pending_dir / f"pending_{timestamp}.json"
        
        with open(pending_file, "w", encoding="utf-8") as f:
            json.dump({
                "title": title,
                "content": content,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "pending",
            "message": f"已保存待发送: {pending_file}",
            "hint": "请配置 config/feishu_webhook.json 以自动发送"
        }
    
    def send_hourly_report(self, report_data):
        """发送每小时学习报告"""
        title = f"蚁群蜂群每小时学习报告 - {report_data.get('timestamp', '')}"
        
        # 格式化内容
        content = self._format_report_content(report_data)
        
        return self.send_message(title, content)
    
    def _format_report_content(self, report):
        """格式化报告内容"""
        lines = [f"**学习领域**: {report.get('domains_learned', 0)}个"]
        
        # 高优先级发现
        if report.get("high_priority_findings"):
            lines.append("\n**高优先级发现**:")
            for finding in report["high_priority_findings"][:3]:
                lines.append(f"- {finding['domain']}: {finding['findings'][0] if finding['findings'] else '无'}")
        
        # 进化行动
        if report.get("evolution_actions"):
            lines.append("\n**进化行动**:")
            for action in report["evolution_actions"][:3]:
                lines.append(f"- {action}")
        
        return "\n".join(lines)

def main():
    sender = FeishuReportSender()
    
    # 查找最新报告
    report_dir = Path("memory/hourly_reports")
    if not report_dir.exists():
        print("[错误] 未找到报告目录")
        return
    
    reports = sorted(report_dir.glob("hourly_*.json"), reverse=True)
    
    if not reports:
        print("[错误] 未找到报告文件")
        return
    
    latest_report = reports[0]
    print(f"[发送] 最新报告: {latest_report}")
    
    with open(latest_report, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    
    result = sender.send_hourly_report(report_data)
    print(f"[结果] {result['status']}: {result['message']}")
    
    if result['status'] == 'pending':
        print(f"\n提示: {result.get('hint', '')}")

if __name__ == "__main__":
    if "--test" in sys.argv:
        # 测试发送
        sender = FeishuReportSender()
        result = sender.send_message(
            "测试报告",
            "这是一条测试消息，来自蚁群蜂群自动学习系统。"
        )
        print(f"[测试] {result}")
    else:
        main()
