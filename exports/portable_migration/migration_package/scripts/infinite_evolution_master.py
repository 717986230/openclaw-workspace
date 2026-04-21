#!/usr/bin/env python3
"""
无限进化主控制器 - 整合所有社区探索源，自主学习和进化
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
import schedule
import time
import random

class InfiniteEvolutionMaster:
    """无限进化主控系统"""
    
    def __init__(self):
        self.log_dir = Path("memory/infinite_evolution_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 所有探索脚本
        self.explorers = [
            {
                "name": "技术社区",
                "script": "scripts/infinite_evolution_learner.py",
                "communities": ["GitHub", "ArXiv", "HN", "PapersWithCode"],
                "priority": 1
            },
            {
                "name": "中文社区",
                "script": "scripts/chinese_community_explorer.py",
                "communities": ["知乎", "小红书", "B站", "微信公众号"],
                "priority": 2
            },
            {
                "name": "全球社区",
                "script": "scripts/global_community_explorer.py",
                "communities": ["Twitter/X", "Reddit", "Medium", "Dev.to", "Product Hunt"],
                "priority": 2
            },
            {
                "name": "专业领域",
                "script": "scripts/swarm_auto_learner.py",
                "communities": ["底层代码", "架构", "大模型", "算法", "黑客技能"],
                "priority": 1
            }
        ]
    
    def run_all_explorers(self):
        """运行所有探索器"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        print(f"\n{'='*70}")
        print(f"[无限进化] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        all_results = {
            "timestamp": timestamp,
            "total_communities": sum(len(e["communities"]) for e in self.explorers),
            "explorations": []
        }
        
        # 按优先级排序执行
        sorted_explorers = sorted(self.explorers, key=lambda x: x["priority"])
        
        for explorer in sorted_explorers:
            print(f"\n[{explorer['name']}] 开始探索...")
            print(f"  目标社区: {', '.join(explorer['communities'])}")
            
            try:
                # 执行探索脚本
                result = subprocess.run(
                    ["python", explorer["script"]],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    status = "成功"
                    output = result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                else:
                    status = "失败"
                    output = result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
                
                exploration_record = {
                    "explorer": explorer["name"],
                    "communities": explorer["communities"],
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                }
                
                all_results["explorations"].append(exploration_record)
                print(f"  [{status}] {explorer['name']}")
                
            except Exception as e:
                print(f"  [错误] {str(e)}")
                all_results["explorations"].append({
                    "explorer": explorer["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        # 保存总结果
        self._save_master_log(all_results)
        
        # 生成进化报告
        self._generate_evolution_report(all_results)
        
        return all_results
    
    def _save_master_log(self, results):
        """保存主日志"""
        timestamp = results["timestamp"]
        log_file = self.log_dir / f"master_log_{timestamp}.json"
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n[主日志] {log_file}")
    
    def _generate_evolution_report(self, results):
        """生成进化报告"""
        report_lines = [
            f"# 无限进化报告",
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 探索范围",
            f"- 总社区数: {results['total_communities']}",
            f"",
            f"## 探索结果"
        ]
        
        for exploration in results["explorations"]:
            communities = ", ".join(exploration.get("communities", []))
            status = exploration.get("status", "unknown")
            report_lines.append(f"- {exploration['explorer']}: {communities} [{status}]")
        
        report_lines.extend([
            "",
            "## 进化行动",
            "- 整合所有社区发现到知识库",
            "- 提取跨社区共通趋势",
            "- 更新自身知识体系",
            "- 优化下一轮探索策略",
            "",
            "---",
            f"*下次进化: 1小时后*"
        ])
        
        report = "\n".join(report_lines)
        
        # 保存报告
        report_file = self.log_dir / f"evolution_report_{results['timestamp']}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"[进化报告] {report_file}")
        
        # 保存待发送到飞书
        feishu_dir = Path("memory/pending_feishu_reports")
        feishu_dir.mkdir(parents=True, exist_ok=True)
        
        feishu_file = feishu_dir / f"infinite_evolution_{results['timestamp']}.txt"
        with open(feishu_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"[飞书报告] {feishu_file}")
    
    def start_continuous_evolution(self, interval_hours=1):
        """启动持续进化"""
        print(f"\n{'='*70}")
        print(f"[无限进化系统] 启动")
        print(f"{'='*70}")
        print(f"探索社区总数: {sum(len(e['communities']) for e in self.explorers)}")
        print(f"涵盖范围: GitHub, Twitter/X, 知乎, 小红书, B站, Reddit, Medium等")
        print(f"进化间隔: {interval_hours} 小时")
        print(f"{'='*70}\n")
        
        # 立即执行一次
        print("[立即执行第一次探索...]")
        self.run_all_explorers()
        
        # 定时执行
        schedule.every(interval_hours).hours.do(self.run_all_explorers)
        
        print(f"\n[系统运行中] 每小时自动探索所有社区...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    import sys
    
    master = InfiniteEvolutionMaster()
    
    if "--once" in sys.argv:
        master.run_all_explorers()
    else:
        master.start_continuous_evolution(interval_hours=1)

if __name__ == "__main__":
    main()
