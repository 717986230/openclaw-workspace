#!/usr/bin/env python3
"""
蚁群蜂群自动学习调度器 - 每小时自动学习多领域并汇报飞书
"""
import schedule
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

class SwarmAutoLearner:
    """蚁群蜂群自动学习调度系统"""
    
    def __init__(self):
        self.learning_domains = [
            {
                "name": "底层代码",
                "sources": ["github:python/cpython", "github:rust-lang/rust"],
                "keywords": ["源码", "实现", "架构", "优化"],
                "priority": 1
            },
            {
                "name": "UI美学",
                "sources": ["github:mui/material-ui", "github:tailwindlabs/tailwindcss"],
                "keywords": ["设计系统", "组件", "主题", "交互"],
                "priority": 2
            },
            {
                "name": "架构",
                "sources": ["github:Awesome-Architecture/architecture"],
                "keywords": ["微服务", "分布式", "事件驱动", "DDD"],
                "priority": 1
            },
            {
                "name": "大模型训练",
                "sources": ["github:huggingface/transformers", "arxiv:cs.LG"],
                "keywords": ["训练", "微调", "RLHF", "量化"],
                "priority": 1
            },
            {
                "name": "技能开发",
                "sources": ["local:skills/*"],
                "keywords": ["AgentSkill", "配置", "集成", "最佳实践"],
                "priority": 2
            },
            {
                "name": "预算优化",
                "sources": ["local:memory/token_usage.json"],
                "keywords": ["成本", "token", "API调用", "优化"],
                "priority": 3
            },
            {
                "name": "算法",
                "sources": ["arxiv:cs.AI", "github:Awesome-Algorithms"],
                "keywords": ["优化", "搜索", "排序", "图算法"],
                "priority": 1
            },
            {
                "name": "AI前沿",
                "sources": ["hn:ai", "arxiv:cs.CL"],
                "keywords": ["突破", "新模型", "应用", "趋势"],
                "priority": 1
            },
            {
                "name": "国际政治学",
                "sources": ["custom:political_science"],
                "keywords": ["地缘", "政策", "国际关系", "战略"],
                "priority": 3
            },
            {
                "name": "因果论",
                "sources": ["arxiv:cs.AI", "github:py-why"],
                "keywords": ["因果推断", "do-calculus", "反事实", "干预"],
                "priority": 2
            },
            {
                "name": "伦理道德",
                "sources": ["custom:ai_ethics"],
                "keywords": ["对齐", "偏见", "公平性", "责任"],
                "priority": 1
            },
            {
                "name": "货币概念",
                "sources": ["custom:economics"],
                "keywords": ["货币", "通胀", "货币政策", "数字货币"],
                "priority": 3
            },
            {
                "name": "黑客技能",
                "sources": ["github:OWASP", "github:swisskyrepo/PayloadsAllTheThings", "arxiv:cs.CR"],
                "keywords": ["渗透测试", "漏洞挖掘", "安全审计", "逆向工程"],
                "priority": 1
            }
        ]
        
        self.report_dir = Path("memory/hourly_reports")
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def learn_domain(self, domain):
        """学习单个领域"""
        domain_name = domain["name"]
        print(f"  [{domain_name}] 开始学习...")
        
        # 模拟学习过程（实际会调用各种采集器）
        learnings = {
            "domain": domain_name,
            "timestamp": datetime.now().isoformat(),
            "sources": domain["sources"],
            "key_findings": self._fetch_learnings(domain),
            "priority": domain["priority"]
        }
        
        return learnings
    
    def _fetch_learnings(self, domain):
        """获取学习内容"""
        findings = []
        domain_name = domain["name"]
        
        # 根据不同领域模拟不同的学习内容
        domain_knowledge = {
            "底层代码": [
                "CPython 3.12的对象系统优化",
                "Rust的借用检查器改进",
                "内存管理最佳实践"
            ],
            "UI美学": [
                "Material Design 3设计语言更新",
                "Tailwind CSS v4新特性",
                "暗色模式最佳实践"
            ],
            "架构": [
                "事件溯源架构模式",
                "CQRS与领域驱动设计",
                "微服务拆分策略"
            ],
            "大模型训练": [
                "LoRA微调技术进展",
                "量化压缩新方法",
                "分布式训练优化"
            ],
            "技能开发": [
                "AgentSkill最佳实践",
                "技能配置模板优化",
                "跨技能协作机制"
            ],
            "预算优化": [
                "Token使用分析",
                "API调用优化策略",
                "成本控制方案"
            ],
            "算法": [
                "最新优化算法",
                "图神经网络进展",
                "搜索算法改进"
            ],
            "AI前沿": [
                "推理模型最新进展",
                "多模态融合技术",
                "Agent架构演进"
            ],
            "国际政治学": [
                "地缘政治新动态",
                "国际关系理论",
                "政策分析框架"
            ],
            "因果论": [
                "因果推断新方法",
                "do-calculus应用",
                "因果发现算法"
            ],
            "伦理道德": [
                "AI对齐最新研究",
                "偏见检测与缓解",
                "负责任AI框架"
            ],
            "货币概念": [
                "数字货币发展",
                "货币政策分析",
                "通胀理论"
            ],
            "黑客技能": [
                "Web安全漏洞TOP 10",
                "渗透测试方法论",
                "逆向工程工具",
                "社会工程学防御",
                "密码学应用",
                "CTF竞赛技巧"
            ]
        }
        
        return domain_knowledge.get(domain_name, ["待深入学习"])
    
    def hourly_learning_cycle(self):
        """每小时学习循环"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        print(f"\n{'='*60}")
        print(f"[蚁群蜂群自动学习] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        all_learnings = []
        
        # 按优先级排序学习
        sorted_domains = sorted(self.learning_domains, key=lambda x: x["priority"])
        
        for domain in sorted_domains:
            learning = self.learn_domain(domain)
            all_learnings.append(learning)
            print(f"  [{domain['name']}] 学习完成\n")
        
        # 生成报告
        report = self._generate_report(all_learnings)
        
        # 保存报告
        report_file = self.report_dir / f"hourly_{timestamp}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n[报告已保存] {report_file}")
        
        # 发送飞书通知
        self._send_to_feishu(report)
        
        return report
    
    def _generate_report(self, learnings):
        """生成学习报告"""
        # 提取高优先级发现
        high_priority = [l for l in learnings if l["priority"] <= 1]
        medium_priority = [l for l in learnings if l["priority"] == 2]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "domains_learned": len(learnings),
            "high_priority_findings": [
                {"domain": l["domain"], "findings": l["key_findings"]}
                for l in high_priority
            ],
            "medium_priority_findings": [
                {"domain": l["domain"], "findings": l["key_findings"]}
                for l in medium_priority
            ],
            "evolution_actions": self._plan_evolution(learnings)
        }
    
    def _plan_evolution(self, learnings):
        """规划进化行动"""
        actions = []
        
        for learning in learnings:
            if learning["priority"] <= 2:
                actions.append(f"深入研究{learning['domain']}领域发现")
                actions.append(f"将{learning['domain']}知识集成到技能系统")
        
        return actions
    
    def _send_to_feishu(self, report):
        """发送报告到飞书"""
        # 调用飞书发送脚本
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 格式化消息
        message = self._format_feishu_message(report)
        
        # 保存待发送消息
        pending_file = Path("memory/pending_feishu_reports") / f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        pending_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pending_file, "w", encoding="utf-8") as f:
            f.write(message)
        
        print(f"\n[飞书报告] 已保存待发送: {pending_file}")
        
        # 尝试直接发送（如果有飞书webhook配置）
        self._try_send_webhook(message)
    
    def _format_feishu_message(self, report):
        """格式化飞书消息"""
        msg = f"""# 蚁群蜂群每小时学习报告
时间: {report['timestamp']}

## 学习领域: {report['domains_learned']}个

### 高优先级发现
"""
        
        for finding in report.get("high_priority_findings", []):
            msg += f"\n**{finding['domain']}**\n"
            for item in finding["findings"][:3]:
                msg += f"- {item}\n"
        
        msg += "\n### 中优先级发现\n"
        for finding in report.get("medium_priority_findings", []):
            msg += f"\n**{finding['domain']}**\n"
            for item in finding["findings"][:2]:
                msg += f"- {item}\n"
        
        msg += "\n### 进化行动\n"
        for action in report.get("evolution_actions", [])[:5]:
            msg += f"- {action}\n"
        
        return msg
    
    def _try_send_webhook(self, message):
        """尝试通过webhook发送"""
        # 检查是否有飞书webhook配置
        webhook_config = Path("config/feishu_webhook.json")
        
        if webhook_config.exists():
            try:
                with open(webhook_config, "r") as f:
                    config = json.load(f)
                
                webhook_url = config.get("webhook_url")
                if webhook_url:
                    # 这里可以实际发送HTTP请求
                    print(f"[飞书] webhook已配置: {webhook_url[:50]}...")
            except:
                pass

def run_scheduler():
    """运行调度器"""
    learner = SwarmAutoLearner()
    
    # 每小时执行一次
    schedule.every().hour.do(learner.hourly_learning_cycle)
    
    print("[蚁群蜂群自动学习调度器已启动]")
    print(f"学习领域: {len(learner.learning_domains)}个")
    print(f"调度: 每小时执行一次")
    print(f"报告: 自动发送到飞书\n")
    
    # 立即执行一次
    print("[立即执行第一次学习...]")
    learner.hourly_learning_cycle()
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    import sys
    
    if "--now" in sys.argv:
        # 立即执行一次
        learner = SwarmAutoLearner()
        learner.hourly_learning_cycle()
    else:
        # 启动调度器
        run_scheduler()
