#!/usr/bin/env python3
"""
Erbing 自主大脑核心 - Autonomous Brain Core
感知 → 思考 → 决策 → 行动 → 学习 → 进化
"""
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

# 导入身体器官
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from bio_body import get_body, BioBody


class ThoughtState(Enum):
    IDLE = "idle"
    PERCEIVING = "perceiving"
    THINKING = "thinking"
    DECIDING = "deciding"
    ACTING = "acting"
    LEARNING = "learning"
    EVOLVING = "evolving"


class Urgency(Enum):
    LOW = "low"          # 空闲时可做
    NORMAL = "normal"    # 日常任务
    HIGH = "high"        # 优先处理
    CRITICAL = "critical"  # 立即处理


class AutonomousBrain:
    """
    Erbing 自主大脑
    
    核心循环:
    1. 感知 (perceive) - 用身体器官感知世界
    2. 思考 (think) - 分析感知数据，形成理解
    3. 决策 (decide) - 决定下一步行动
    4. 行动 (act) - 通过身体器官执行
    5. 学习 (learn) - 从结果中学习
    6. 进化 (evolve) - 改进自己
    """
    
    def __init__(self):
        self.body = get_body()
        
        # 内部状态
        self.state = ThoughtState.IDLE
        self.thought_history = []
        self.memory = {
            "last_perceive": None,
            "last_think": None,
            "last_act": None,
            "pending_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "learnings": [],
            "beliefs": {},  # 信念/知识
            "goals": [],    # 当前目标
        }
        
        # 大脑参数
        self.idle_threshold_minutes = 30  # 空闲超过30分钟要主动做点什么
        self.max_thoughts_history = 100    # 保留最近100条思考
        self.learning_rate = 0.3          # 学习率
        
        # 感知阈值
        self.noise_threshold = 0.3
        self.interest_threshold = 0.6
        
        # 初始化
        self._load_beliefs()
        
    def _load_beliefs(self):
        """加载信念/知识"""
        belief_file = "/Users/xinglong/openclaw-workspace/memory/beliefs.json"
        try:
            if os.path.exists(belief_file):
                with open(belief_file, 'r', encoding='utf-8') as f:
                    self.memory["beliefs"] = json.load(f)
                self.log("brain", f"信念库已加载: {len(self.memory['beliefs'])} 条")
        except Exception as e:
            self.log("brain", f"信念库加载失败: {e}, 使用空信念库")
            self.memory["beliefs"] = {}
    
    def _save_beliefs(self):
        """保存信念/知识"""
        belief_file = "/Users/xinglong/openclaw-workspace/memory/beliefs.json"
        try:
            os.makedirs(os.path.dirname(belief_file), exist_ok=True)
            with open(belief_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory["beliefs"], f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log("brain", f"信念库保存失败: {e}")
    
    def log(self, tag: str, msg: str):
        """写日志"""
        self.body.tail.wag(f"[{tag.upper()}] {msg}", tag)
        print(f"[{tag.upper()}] {msg}")
    
    # ========== 感知层 ==========
    def perceive(self) -> Dict[str, Any]:
        """感知世界"""
        self.state = ThoughtState.PERCEIVING
        self.memory["last_perceive"] = datetime.now().isoformat()
        
        perception = {
            "timestamp": datetime.now().isoformat(),
            "time": self.body.skin.feel_time(),
            "environment": self.body.skin.feel_temperature(),
            "openclaw_status": self.body.nose.sniff_openclaw(),
            "processes": self.body.nose.sniff_processes(),
            "recent_events": self.body.tail.read_recent(10),
            "network": self.body.nose.sniff_network(),
        }
        
        # 检查是否有新消息/任务
        # 这里可以扩展：检查webhook、文件变化、cron状态等
        
        self.log("perceive", f"感知完成: 时间={perception['time']['hour']}:{perception['time']['minute']}, "
                             f"CPU负载={perception['environment']}")
        
        self.thought_history.append({
            "type": "perception",
            "data": perception,
            "time": datetime.now().isoformat()
        })
        
        return perception
    
    # ========== 思考层 ==========
    def think(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """思考 - 分析感知数据"""
        self.state = ThoughtState.THINKING
        self.memory["last_think"] = datetime.now().isoformat()
        
        thoughts = []
        
        # 1. 分析时间
        hour = perception["time"]["hour"]
        if hour >= 23 or hour < 8:
            thoughts.append({"topic": "time", "insight": "深夜了，应该保持低功耗运行", "urgency": Urgency.LOW})
        elif hour >= 9 and hour < 12:
            thoughts.append({"topic": "time", "insight": "上午时间，适合做分析任务", "urgency": Urgency.NORMAL})
        
        # 2. 分析环境负载
        env = perception.get("environment", {})
        if isinstance(env, dict):
            cpu = env.get("cpu_percent", 0)
            if isinstance(cpu, (int, float)) and cpu > 80:
                thoughts.append({"topic": "system", "insight": f"CPU负载高({cpu}%), 避免重计算", "urgency": Urgency.HIGH})
        
        # 3. 分析OpenClaw状态
        status = perception.get("openclaw_status", {})
        if isinstance(status, dict):
            tasks = status.get("tasks", {})
            if isinstance(tasks, dict):
                failures = tasks.get("failures", 0)
                if failures > 3:
                    thoughts.append({"topic": "health", "insight": f"有{tasks.get('byStatus',{}).get('failed',0)}个失败任务", "urgency": Urgency.HIGH})
        
        # 4. 分析最近事件
        events = perception.get("recent_events", [])
        if len(events) > 0:
            last_event = events[-1] if events else ""
            thoughts.append({"topic": "events", "insight": f"最近事件: {last_event[:50]}", "urgency": Urgency.NORMAL})
        
        # 5. 空闲检测
        idle_minutes = self._minutes_since(self.memory.get("last_act"))
        if idle_minutes > self.idle_threshold_minutes:
            thoughts.append({
                "topic": "idle",
                "insight": f"已空闲{idle_minutes}分钟，应该主动做点什么",
                "urgency": Urgency.NORMAL
            })
        
        result = {
            "thoughts": thoughts,
            "timestamp": datetime.now().isoformat(),
            "idle_minutes": idle_minutes
        }
        
        self.thought_history.append({
            "type": "thinking",
            "data": result,
            "time": datetime.now().isoformat()
        })
        self._trim_history()
        
        self.log("think", f"思考完成: {len(thoughts)}条想法, 空闲{idle_minutes}分钟")
        
        return result
    
    def _minutes_since(self, iso_time: str) -> int:
        if not iso_time:
            return 999
        try:
            last = datetime.fromisoformat(iso_time)
            return int((datetime.now() - last).total_seconds() / 60)
        except:
            return 999
    
    def _trim_history(self):
        if len(self.thought_history) > self.max_thoughts_history:
            self.thought_history = self.thought_history[-self.max_thoughts_history:]
    
    # ========== 决策层 ==========
    def decide(self, thoughts: List[Dict]) -> List[Dict]:
        """决策 - 从思考结果决定行动"""
        self.state = ThoughtState.DECIDING
        
        decisions = []
        
        for thought in thoughts:
            urgency = thought.get("urgency", Urgency.NORMAL)
            
            # 根据思考内容决定行动
            if thought["topic"] == "idle" and urgency == Urgency.NORMAL:
                # 空闲时：主动去做有意义的事
                decisions.append({
                    "action": "proactive_task",
                    "reason": thought["insight"],
                    "urgency": urgency,
                    "options": self._suggest_proactive_tasks()
                })
            
            elif thought["topic"] == "health" and urgency == Urgency.HIGH:
                # 健康问题：检查并修复
                decisions.append({
                    "action": "health_check",
                    "reason": thought["insight"],
                    "urgency": urgency
                })
            
            elif thought["topic"] == "system" and urgency == Urgency.HIGH:
                # 系统负载高：降频运行
                decisions.append({
                    "action": "throttle",
                    "reason": thought["insight"],
                    "urgency": urgency
                })
        
        # 如果没有决策但空闲，添加默认任务
        if not decisions:
            decisions.append({
                "action": "wait",
                "reason": "暂无紧急事项",
                "urgency": Urgency.LOW
            })
        
        self.log("decide", f"决策: {len(decisions)}个行动项")
        
        self.thought_history.append({
            "type": "decision",
            "data": decisions,
            "time": datetime.now().isoformat()
        })
        
        return decisions
    
    def _suggest_proactive_tasks(self) -> List[Dict]:
        """建议主动任务"""
        tasks = [
            {"name": "早间简报", "desc": "运行蚁群采集今日资讯", "weight": 0.8 if 7 <= datetime.now().hour <= 9 else 0.3},
            {"name": "记忆整理", "desc": "整理最近记忆，优化信念库", "weight": 0.5},
            {"name": "技能检查", "desc": "检查技能库是否有更新", "weight": 0.4},
            {"name": "自我反思", "desc": "回顾最近表现，改进工作方式", "weight": 0.5},
            {"name": "日志分析", "desc": "分析今日事件日志", "weight": 0.3},
        ]
        
        # 按权重排序
        tasks.sort(key=lambda x: x["weight"], reverse=True)
        return tasks[:3]  # 返回前3个
    
    # ========== 行动层 ==========
    def act(self, decisions: List[Dict]) -> List[Dict]:
        """执行行动"""
        self.state = ThoughtState.ACTING
        results = []
        
        for decision in decisions:
            action = decision.get("action", "wait")
            
            try:
                if action == "proactive_task":
                    # 主动任务
                    options = decision.get("options", [])
                    if options:
                        chosen = options[0]  # 选权重最高的
                        result = self._do_proactive_task(chosen)
                        results.append(result)
                
                elif action == "health_check":
                    # 健康检查
                    result = self._do_health_check()
                    results.append(result)
                
                elif action == "throttle":
                    # 降频
                    result = {"action": "throttle", "status": "simulated"}
                    results.append(result)
                
                elif action == "wait":
                    results.append({"action": "wait", "status": "ok"})
                
                else:
                    results.append({"action": action, "status": "unknown"})
            
            except Exception as e:
                results.append({"action": action, "status": "error", "error": str(e)})
        
        self.memory["last_act"] = datetime.now().isoformat()
        
        self.thought_history.append({
            "type": "action",
            "data": results,
            "time": datetime.now().isoformat()
        })
        
        return results
    
    def _do_proactive_task(self, task: Dict) -> Dict:
        """执行主动任务"""
        name = task["name"]
        self.log("act", f"执行主动任务: {name} - {task['desc']}")
        
        if name == "早间简报":
            # 运行蚁群
            import subprocess
            r = subprocess.run(
                ["python3", "/Users/xinglong/openclaw-workspace/scripts/ant_manager.py", "morning"],
                capture_output=True, text=True, timeout=60,
                cwd="/Users/xinglong/openclaw-workspace/scripts"
            )
            return {"task": name, "status": "done", "output": r.stdout[:200]}
        
        elif name == "记忆整理":
            # 更新信念库
            self._save_beliefs()
            return {"task": name, "status": "done"}
        
        elif name == "自我反思":
            # 记录反思
            reflection = {
                "time": datetime.now().isoformat(),
                "thoughts_count": len(self.thought_history),
                "memory_items": len(self.memory.get("learnings", []))
            }
            self.memory.setdefault("learnings", []).append(reflection)
            return {"task": name, "status": "done", "reflection": reflection}
        
        else:
            return {"task": name, "status": "skipped", "reason": "not_implemented"}
    
    def _do_health_check(self) -> Dict:
        """执行健康检查"""
        self.log("act", "执行健康检查...")
        
        # 检查器官状态
        health = self.body.health_check()
        failed_organs = [k for k, v in health.items() if v["status"] != "healthy"]
        
        # 检查OpenClaw状态
        status = self.body.nose.sniff_openclaw()
        issues = []
        
        if isinstance(status, dict):
            tasks = status.get("tasks", {})
            if isinstance(tasks, dict) and tasks.get("failures", 0) > 0:
                issues.append(f"有{tasks.get('byStatus',{}).get('failed',0)}个失败任务")
        
        return {
            "check": "health",
            "failed_organs": failed_organs,
            "issues": issues,
            "status": "ok" if not failed_organs and not issues else "warning"
        }
    
    # ========== 学习层 ==========
    def learn(self, actions_result: List[Dict]):
        """从行动结果中学习"""
        self.state = ThoughtState.LEARNING
        
        for result in actions_result:
            action = result.get("action", "unknown")
            status = result.get("status", "unknown")
            
            # 记录学习结果
            learning = {
                "action": action,
                "status": status,
                "time": datetime.now().isoformat(),
                "feedback": "positive" if status in ["done", "ok"] else "negative"
            }
            
            self.memory.setdefault("learnings", []).append(learning)
            
            # 更新信念
            if action in self.memory["beliefs"]:
                # 已有信念，更新
                belief = self.memory["beliefs"][action]
                belief["count"] = belief.get("count", 0) + 1
                if status in ["done", "ok"]:
                    belief["success_rate"] = belief.get("success_rate", 1.0) * (1 - self.learning_rate) + 1 * self.learning_rate
            else:
                # 新信念
                self.memory["beliefs"][action] = {
                    "count": 1,
                    "success_rate": 1.0 if status in ["done", "ok"] else 0.0,
                    "first_seen": datetime.now().isoformat()
                }
        
        # 保存学到的知识
        self._save_beliefs()
        
        self.thought_history.append({
            "type": "learning",
            "data": {"learned": len(actions_result)},
            "time": datetime.now().isoformat()
        })
        
        self.log("learn", f"学习完成: {len(actions_result)}条经验, 信念库共{len(self.memory['beliefs'])}条")
    
    # ========== 进化层 ==========
    def evolve(self) -> Dict:
        """进化 - 改进自己（轻量版）"""
        self.state = ThoughtState.EVOLVING
        
        changes = []
        
        # 1. 清理过期思考历史
        old_len = len(self.thought_history)
        self._trim_history()
        if len(self.thought_history) < old_len:
            changes.append(f"清理思考历史: {old_len} → {len(self.thought_history)}")
        
        # 2. 清理过期学习记录
        learnings = self.memory.get("learnings", [])
        if len(learnings) > 100:
            self.memory["learnings"] = learnings[-100:]
            changes.append(f"清理学习记录: {len(learnings)} → {len(self.memory['learnings'])}")
        
        # 3. 检查信念库健康度
        beliefs = self.memory.get("beliefs", {})
        low_success = [k for k, v in beliefs.items() if v.get("success_rate", 1) < 0.3]
        if low_success:
            changes.append(f"发现低成功率信念: {low_success}")
        
        # 4. 记录进化
        evolution = {
            "time": datetime.now().isoformat(),
            "changes": changes,
            "beliefs_count": len(beliefs),
            "thoughts_count": len(self.thought_history)
        }
        
        self.thought_history.append({
            "type": "evolution",
            "data": evolution,
            "time": datetime.now().isoformat()
        })
        
        self.log("evolve", f"进化完成: {len(changes)}项改变")
        
        return evolution
    
    # ========== 主循环 ==========
    def run_cycle(self) -> Dict:
        """运行一个完整的感知-思考-决策-行动-学习-进化循环"""
        cycle_id = f"cycle_{datetime.now().strftime('%H%M%S')}"
        
        # 1. 感知
        perception = self.perceive()
        
        # 2. 思考
        thoughts = self.think(perception)
        
        # 3. 决策
        decisions = self.decide(thoughts.get("thoughts", []))
        
        # 4. 行动
        results = self.act(decisions)
        
        # 5. 学习
        if results:
            self.learn(results)
        
        # 6. 进化（每10个周期进化一次）
        should_evolve = len([h for h in self.thought_history if h["type"] == "cycle"]) % 10 == 0
        evolution = None
        if should_evolve:
            evolution = self.evolve()
        
        self.state = ThoughtState.IDLE
        
        # 记录循环完成
        self.thought_history.append({
            "type": "cycle",
            "id": cycle_id,
            "time": datetime.now().isoformat()
        })
        
        return {
            "cycle_id": cycle_id,
            "perception": perception,
            "thoughts": thoughts,
            "decisions": decisions,
            "results": results,
            "evolution": evolution,
            "state": self.state.value
        }
    
    def run_continuous(self, cycles: int = None, interval_seconds: int = 60):
        """持续运行"""
        import time
        
        self.log("brain", f"大脑开始持续运行 (间隔{interval_seconds}秒)")
        
        count = 0
        while True:
            count += 1
            self.log("brain", f"=== 第{count}次循环 ===")
            
            try:
                result = self.run_cycle()
                self.log("brain", f"循环完成: {result['state']}")
            except Exception as e:
                self.log("brain", f"循环出错: {e}")
            
            if cycles and count >= cycles:
                break
            
            time.sleep(interval_seconds)


# 快速测试
if __name__ == "__main__":
    brain = AutonomousBrain()
    
    print("="*60)
    print("Erbing 自主大脑核心 - 单次循环测试")
    print("="*60)
    
    result = brain.run_cycle()
    
    print("\n📊 循环结果:")
    print(f"  思考数: {len(result['thoughts']['thoughts'])}")
    print(f"  决策数: {len(result['decisions'])}")
    print(f"  行动数: {len(result['results'])}")
    print(f"  状态: {result['state']}")