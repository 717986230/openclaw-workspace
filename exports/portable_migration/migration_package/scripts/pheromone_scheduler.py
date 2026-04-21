#!/usr/bin/env python3
"""信息素任务调度器 - 基于swarms信息素机制"""
import json
from datetime import datetime, timedelta
from pathlib import Path

class PheromoneScheduler:
    """基于信息素的任务优先级调度"""
    
    def __init__(self, db_path="memory/pheromone_tasks.json"):
        self.db_path = Path(db_path)
        self.tasks = self._load_tasks()
        self.pheromone_types = {
            "quality": {"decay": 0.1, "threshold": 0.5},
            "trail": {"decay": 0.2, "threshold": 0.3},
            "alarm": {"decay": 0.5, "threshold": 0.7}
        }
    
    def add_task(self, task_id, task_type, priority=0.5):
        """添加任务"""
        self.tasks[task_id] = {
            "type": task_type,
            "pheromone": priority,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._save_tasks()
    
    def complete_task(self, task_id, quality_score):
        """任务完成，沉积信息素"""
        if task_id in self.tasks:
            # 根据质量更新信息素强度
            pheromone = min(1.0, quality_score)
            self.tasks[task_id]["pheromone"] = pheromone
            self.tasks[task_id]["completed"] = True
            self._save_tasks()
    
    def get_next_task(self):
        """获取下一个最高信息素强度的任务"""
        if not self.tasks:
            return None
        
        # 按信息素强度排序
        sorted_tasks = sorted(
            [(k, v) for k, v in self.tasks.items() if not v.get("completed")],
            key=lambda x: x[1]["pheromone"],
            reverse=True
        )
        
        if sorted_tasks:
            return sorted_tasks[0][0]
        return None
    
    def decay_pheromones(self):
        """信息素挥发"""
        for task_id, task in self.tasks.items():
            if not task.get("completed"):
                task["pheromone"] *= (1 - 0.1)  # 10%挥发率
                task["last_updated"] = datetime.now().isoformat()
        
        self._save_tasks()
    
    def _load_tasks(self):
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_tasks(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scheduler = PheromoneScheduler()
    scheduler.add_task("task_001", "news_collection", 0.8)
    print(f"下一个任务: {scheduler.get_next_task()}")
