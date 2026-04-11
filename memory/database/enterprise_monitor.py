"""
企业级监控脚本
支持系统监控、性能监控、告警通知
"""

import psutil
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EnterpriseMonitor:
    """企业级监控器"""
    
    def __init__(self, config: Dict):
        """初始化监控器"""
        self.config = config
        
        # 监控间隔
        self.monitor_interval = config.get("monitor_interval", 60)
        
        # 告警配置
        self.alert_config = config.get("alerts", {})
        
        # 通知配置
        self.notification_config = config.get("notifications", {})
        
        # 历史数据
        self.history = []
        self.max_history_size = config.get("max_history_size", 1000)
        
        # 运行状态
        self.running = False
    
    async def start(self):
        """启动监控"""
        self.running = True
        
        while self.running:
            # 收集指标
            metrics = await self.collect_metrics()
            
            # 检查告警
            alerts = self.check_alerts(metrics)
            
            # 发送通知
            if alerts:
                await self.send_alerts(alerts)
            
            # 保存历史数据
            self.save_history(metrics)
            
            # 等待下一次监控
            await asyncio.sleep(self.monitor_interval)
    
    def stop(self):
        """停止监控"""
        self.running = False
    
    async def collect_metrics(self) -> Dict:
        """收集指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self.collect_system_metrics(),
            "performance": self.collect_performance_metrics(),
            "application": self.collect_application_metrics(),
            "database": self.collect_database_metrics(),
            "cache": self.collect_cache_metrics()
        }
        
        return metrics
    
    def collect_system_metrics(self) -> Dict:
        """收集系统指标"""
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        
        # 网络使用
        network = psutil.net_io_counters()
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
    
    def collect_performance_metrics(self) -> Dict:
        """收集性能指标"""
        # 进程信息
        process = psutil.Process()
        
        return {
            "process": {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0
            },
            "response_time": self.measure_response_time(),
            "throughput": self.measure_throughput()
        }
    
    def collect_application_metrics(self) -> Dict:
        """收集应用指标"""
        # 这里应该从应用中收集指标
        return {
            "active_connections": 0,
            "requests_per_second": 0,
            "error_rate": 0.0,
            "queue_size": 0
        }
    
    def collect_database_metrics(self) -> Dict:
        """收集数据库指标"""
        # 这里应该从数据库中收集指标
        return {
            "connections": 0,
            "queries_per_second": 0,
            "slow_queries": 0,
            "cache_hit_rate": 0.0
        }
    
    def collect_cache_metrics(self) -> Dict:
        """收集缓存指标"""
        # 这里应该从缓存中收集指标
        return {
            "size": 0,
            "hit_rate": 0.0,
            "miss_rate": 0.0,
            "evictions": 0
        }
    
    def measure_response_time(self) -> float:
        """测量响应时间"""
        start_time = time.time()
        # 执行一个简单的操作
        time.sleep(0.01)
        return time.time() - start_time
    
    def measure_throughput(self) -> float:
        """测量吞吐量"""
        # 简化实现
        return 100.0
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """检查告警"""
        alerts = []
        
        # 检查 CPU 使用率
        cpu_percent = metrics["system"]["cpu"]["percent"]
        if cpu_percent > self.alert_config.get("cpu_threshold", 80):
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "message": f"CPU usage is {cpu_percent}%",
                "value": cpu_percent,
                "threshold": self.alert_config.get("cpu_threshold", 80)
            })
        
        # 检查内存使用率
        memory_percent = metrics["system"]["memory"]["percent"]
        if memory_percent > self.alert_config.get("memory_threshold", 80):
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "message": f"Memory usage is {memory_percent}%",
                "value": memory_percent,
                "threshold": self.alert_config.get("memory_threshold", 80)
            })
        
        # 检查磁盘使用率
        disk_percent = metrics["system"]["disk"]["percent"]
        if disk_percent > self.alert_config.get("disk_threshold", 90):
            alerts.append({
                "type": "disk_high",
                "severity": "critical",
                "message": f"Disk usage is {disk_percent}%",
                "value": disk_percent,
                "threshold": self.alert_config.get("disk_threshold", 90)
            })
        
        # 检查响应时间
        response_time = metrics["performance"]["response_time"]
        if response_time > self.alert_config.get("response_time_threshold", 1.0):
            alerts.append({
                "type": "response_time_high",
                "severity": "warning",
                "message": f"Response time is {response_time}s",
                "value": response_time,
                "threshold": self.alert_config.get("response_time_threshold", 1.0)
            })
        
        return alerts
    
    async def send_alerts(self, alerts: List[Dict]):
        """发送告警"""
        for alert in alerts:
            # 发送邮件
            if self.notification_config.get("email_enabled", False):
                await self.send_email_alert(alert)
            
            # 发送 Slack
            if self.notification_config.get("slack_enabled", False):
                await self.send_slack_alert(alert)
            
            # 发送 PagerDuty
            if self.notification_config.get("pagerduty_enabled", False):
                await self.send_pagerduty_alert(alert)
    
    async def send_email_alert(self, alert: Dict):
        """发送邮件告警"""
        try:
            # 配置邮件
            msg = MIMEMultipart()
            msg['From'] = self.notification_config.get("email_from")
            msg['To'] = self.notification_config.get("email_to")
            msg['Subject'] = f"Alert: {alert['type']}"
            
            # 邮件内容
            body = f"""
            Alert Type: {alert['type']}
            Severity: {alert['severity']}
            Message: {alert['message']}
            Value: {alert['value']}
            Threshold: {alert['threshold']}
            Timestamp: {datetime.now().isoformat()}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # 发送邮件
            with smtplib.SMTP(
                self.notification_config.get("smtp_server"),
                self.notification_config.get("smtp_port", 587)
            ) as server:
                server.starttls()
                server.login(
                    self.notification_config.get("smtp_username"),
                    self.notification_config.get("smtp_password")
                )
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    async def send_slack_alert(self, alert: Dict):
        """发送 Slack 告警"""
        try:
            webhook_url = self.notification_config.get("slack_webhook_url")
            
            payload = {
                "text": f"Alert: {alert['type']}",
                "attachments": [
                    {
                        "color": "danger" if alert['severity'] == "critical" else "warning",
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert['severity']
                            },
                            {
                                "title": "Message",
                                "value": alert['message']
                            },
                            {
                                "title": "Value",
                                "value": str(alert['value'])
                            },
                            {
                                "title": "Threshold",
                                "value": str(alert['threshold'])
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    response.raise_for_status()
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    async def send_pagerduty_alert(self, alert: Dict):
        """发送 PagerDuty 告警"""
        try:
            api_key = self.notification_config.get("pagerduty_api_key")
            routing_key = self.notification_config.get("pagerduty_routing_key")
            
            payload = {
                "routing_key": routing_key,
                "event_action": "trigger",
                "payload": {
                    "summary": alert['message'],
                    "severity": alert['severity'],
                    "source": "erbing-monitor",
                    "custom_details": alert
                }
            }
            
            url = "https://events.pagerduty.com/v2/enqueue"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token token={api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    response.raise_for_status()
        except Exception as e:
            print(f"Failed to send PagerDuty alert: {e}")
    
    def save_history(self, metrics: Dict):
        """保存历史数据"""
        self.history.append(metrics)
        
        # 限制历史数据大小
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取历史数据"""
        return self.history[-limit:]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.history:
            return {}
        
        # 计算平均值
        cpu_values = [m["system"]["cpu"]["percent"] for m in self.history]
        memory_values = [m["system"]["memory"]["percent"] for m in self.history]
        response_time_values = [m["performance"]["response_time"] for m in self.history]
        
        return {
            "avg_cpu": sum(cpu_values) / len(cpu_values),
            "avg_memory": sum(memory_values) / len(memory_values),
            "avg_response_time": sum(response_time_values) / len(response_time_values),
            "max_cpu": max(cpu_values),
            "max_memory": max(memory_values),
            "max_response_time": max(response_time_values),
            "min_cpu": min(cpu_values),
            "min_memory": min(memory_values),
            "min_response_time": min(response_time_values)
        }


# 使用示例
if __name__ == "__main__":
    async def main():
        # 配置
        config = {
            "monitor_interval": 10,
            "alerts": {
                "cpu_threshold": 80,
                "memory_threshold": 80,
                "disk_threshold": 90,
                "response_time_threshold": 1.0
            },
            "notifications": {
                "email_enabled": False,
                "slack_enabled": False,
                "pagerduty_enabled": False
            },
            "max_history_size": 100
        }
        
        # 初始化监控器
        monitor = EnterpriseMonitor(config)
        
        # 启动监控
        monitor_task = asyncio.create_task(monitor.start())
        
        # 运行一段时间
        await asyncio.sleep(30)
        
        # 停止监控
        monitor.stop()
        await monitor_task
        
        # 获取统计信息
        stats = monitor.get_stats()
        print(f"Stats: {stats}")
    
    asyncio.run(main())
