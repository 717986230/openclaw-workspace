"""
蜂群/蚁群协作系统实现
基于 swarms 框架的多Agent协作
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import hashlib


class PheromoneType(Enum):
    """信息素类型"""
    QUALITY = "quality"      # 质量 - 标记高质量内容
    TRAIL = "trail"          # 路径 - 标记有效路径
    ALARM = "alarm"          # 警报 - 标记问题/风险
    SUCCESS = "success"      # 成功 - 标记成功结果


@dataclass
class Pheromone:
    """信息素"""
    type: PheromoneType
    location: str            # 标记位置（URL、任务ID等）
    strength: float = 1.0    # 强度 (0-1)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    
    def decay(self, rate: float = 0.1):
        """信息素挥发"""
        self.strength *= (1 - rate)
        return self.strength > 0.01  # 返回是否还有效


@dataclass
class Task:
    """任务"""
    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_to: Optional[str] = None
    result: Any = None
    pheromones: List[Pheromone] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class Agent:
    """基础智能体"""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.current_task: Optional[Task] = None
        self.pheromone_memory: Dict[str, float] = {}  # location -> strength
    
    def sense_pheromone(self, pheromones: List[Pheromone], ptype: PheromoneType) -> List[Pheromone]:
        """感知特定类型的信息素"""
        return [p for p in pheromones if p.type == ptype and p.strength > 0.01]
    
    def deposit_pheromone(self, task: Task, ptype: PheromoneType, strength: float = 1.0, metadata: Dict = None):
        """沉积信息素"""
        pheromone = Pheromone(
            type=ptype,
            location=task.id,
            strength=strength,
            metadata=metadata or {}
        )
        task.pheromones.append(pheromone)
        self.pheromone_memory[task.id] = strength
        return pheromone


class ScoutAnt(Agent):
    """侦查蚁 - 探索新领域"""
    def __init__(self, name: str):
        super().__init__(name, "scout_ant")
        self.explored_paths: List[str] = []
    
    async def explore(self, sources: List[str]) -> List[Dict]:
        """探索数据源"""
        results = []
        for source in sources:
            # 模拟探索
            result = {
                "source": source,
                "found": True,
                "quality": 0.5 + 0.5 * (hash(source) % 100) / 100,
                "timestamp": time.time()
            }
            results.append(result)
            self.explored_paths.append(source)
        return results


class ForagerAnt(Agent):
    """采集蚁 - 执行采集任务"""
    def __init__(self, name: str):
        super().__init__(name, "forager_ant")
        self.collected: List[Dict] = []
    
    async def forage(self, sources: List[Dict]) -> List[Dict]:
        """采集数据"""
        results = []
        for source in sources:
            # 模拟采集
            result = {
                "source": source["source"],
                "data": f"Collected data from {source['source']}",
                "quality": source.get("quality", 0.5),
                "timestamp": time.time()
            }
            results.append(result)
            self.collected.append(result)
        return results


class WorkerAnt(Agent):
    """工蚁 - 处理数据"""
    def __init__(self, name: str):
        super().__init__(name, "worker_ant")
        self.processed: List[Dict] = []
    
    async def process(self, data: List[Dict]) -> List[Dict]:
        """处理数据"""
        results = []
        for item in data:
            # 模拟处理（去重、分类、标记）
            processed = {
                **item,
                "processed": True,
                "hash": hashlib.md5(str(item).encode()).hexdigest()[:8]
            }
            results.append(processed)
            self.processed.append(processed)
        return results


class ScoutBee(Agent):
    """侦查蜂 - 发现新机会"""
    def __init__(self, name: str):
        super().__init__(name, "scout_bee")
        self.discoveries: List[Dict] = []
    
    async def scout(self, pheromones: List[Pheromone]) -> List[Dict]:
        """基于信息素发现机会"""
        # 找到质量信息素最强的位置
        quality_pheromones = self.sense_pheromone(pheromones, PheromoneType.QUALITY)
        quality_pheromones.sort(key=lambda p: p.strength, reverse=True)
        
        discoveries = []
        for p in quality_pheromones[:5]:  # 取前5个高质量位置
            discovery = {
                "location": p.location,
                "quality": p.strength,
                "metadata": p.metadata
            }
            discoveries.append(discovery)
            self.discoveries.append(discovery)
        return discoveries


class EmployedBee(Agent):
    """采蜜蜂 - 执行深度任务"""
    def __init__(self, name: str):
        super().__init__(name, "employed_bee")
        self.analyses: List[Dict] = []
    
    async def analyze(self, discoveries: List[Dict]) -> List[Dict]:
        """深度分析"""
        results = []
        for discovery in discoveries:
            # 模拟深度分析
            analysis = {
                "location": discovery["location"],
                "insights": [
                    f"Key insight 1 from {discovery['location']}",
                    f"Key insight 2 from {discovery['location']}"
                ],
                "score": discovery.get("quality", 0.5) * 0.9,
                "recommendations": ["recommendation 1", "recommendation 2"]
            }
            results.append(analysis)
            self.analyses.append(analysis)
        return results


class OnlookerBee(Agent):
    """观察蜂 - 评估选择"""
    def __init__(self, name: str):
        super().__init__(name, "onlooker_bee")
        self.evaluations: List[Dict] = []
    
    async def evaluate(self, analyses: List[Dict]) -> Dict:
        """评估并选择最佳结果"""
        if not analyses:
            return {"best": None, "reason": "no analyses to evaluate"}
        
        # 基于分数排序
        sorted_analyses = sorted(analyses, key=lambda a: a.get("score", 0), reverse=True)
        best = sorted_analyses[0]
        
        evaluation = {
            "best": best,
            "ranking": [(a["location"], a.get("score", 0)) for a in sorted_analyses],
            "confidence": best.get("score", 0) / (sorted_analyses[0].get("score", 1) + 0.001)
        }
        self.evaluations.append(evaluation)
        return evaluation


class Queen:
    """蜂后/蚁后 - 主控制器"""
    def __init__(self, name: str = "Queen"):
        self.name = name
        self.pheromones: List[Pheromone] = []
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, Any] = {}
    
    def create_task(self, description: str) -> Task:
        """创建任务"""
        task_id = hashlib.md5(f"{description}{time.time()}".encode()).hexdigest()[:8]
        task = Task(id=task_id, description=description)
        self.tasks[task_id] = task
        return task
    
    def deposit_global_pheromone(self, ptype: PheromoneType, location: str, strength: float, metadata: Dict = None):
        """沉积全局信息素"""
        pheromone = Pheromone(type=ptype, location=location, strength=strength, metadata=metadata or {})
        self.pheromones.append(pheromone)
    
    def evaporate_all(self, rate: float = 0.1):
        """所有信息素挥发"""
        self.pheromones = [p for p in self.pheromones if p.decay(rate)]
    
    def integrate_results(self, ant_results: List[Dict], bee_results: Dict) -> Dict:
        """整合蚁群和蜂群结果"""
        integrated = {
            "ant_colony": {
                "collected_count": len(ant_results),
                "sources": list(set(r.get("source", "unknown") for r in ant_results))
            },
            "bee_colony": {
                "best_analysis": bee_results.get("best"),
                "confidence": bee_results.get("confidence", 0)
            },
            "integrated_at": time.time(),
            "pheromone_summary": {
                p.type.value: p.strength for p in self.pheromones
            }
        }
        self.results["last_integration"] = integrated
        return integrated


class AntColony:
    """蚁群"""
    def __init__(self, scouts: int = 3, foragers: int = 5, workers: int = 2):
        self.scouts = [ScoutAnt(f"ScoutAnt_{i}") for i in range(scouts)]
        self.foragers = [ForagerAnt(f"ForagerAnt_{i}") for i in range(foragers)]
        self.workers = [WorkerAnt(f"WorkerAnt_{i}") for i in range(workers)]
        self.results: List[Dict] = []
    
    async def forage(self, sources: List[str], max_results: int = 20) -> List[Dict]:
        """蚁群采集流程"""
        # 1. 侦查蚁探索
        scout_tasks = [scout.explore(sources) for scout in self.scouts]
        scout_results = await asyncio.gather(*scout_tasks)
        
        # 合并侦查结果
        all_discoveries = []
        for results in scout_results:
            all_discoveries.extend(results)
        
        # 2. 采集蚁采集
        forager_tasks = [
            forager.forage(all_discoveries[i::len(self.foragers)])
            for i, forager in enumerate(self.foragers)
        ]
        forager_results = await asyncio.gather(*forager_tasks)
        
        # 合并采集结果
        all_collected = []
        for results in forager_results:
            all_collected.extend(results)
        
        # 3. 工蚁处理
        worker_tasks = [
            worker.process(all_collected[i::len(self.workers)])
            for i, worker in enumerate(self.workers)
        ]
        worker_results = await asyncio.gather(*worker_tasks)
        
        # 合并处理结果
        for results in worker_results:
            self.results.extend(results)
        
        return self.results[:max_results]


class BeeColony:
    """蜂群"""
    def __init__(self, scouts: int = 2, employed: int = 3, onlookers: int = 2):
        self.scouts = [ScoutBee(f"ScoutBee_{i}") for i in range(scouts)]
        self.employed = [EmployedBee(f"EmployedBee_{i}") for i in range(employed)]
        self.onlookers = [OnlookerBee(f"OnlookerBee_{i}") for i in range(onlookers)]
        self.results: Dict = {}
    
    async def optimize(self, pheromones: List[Pheromone], iterations: int = 3) -> Dict:
        """蜂群优化流程"""
        best_result = None
        
        for iteration in range(iterations):
            # 1. 侦查蜂发现
            scout_tasks = [scout.scout(pheromones) for scout in self.scouts]
            scout_results = await asyncio.gather(*scout_tasks)
            
            all_discoveries = []
            for results in scout_results:
                all_discoveries.extend(results)
            
            # 2. 采蜜蜂分析
            employed_tasks = [
                bee.analyze(all_discoveries[i::len(self.employed)])
                for i, bee in enumerate(self.employed)
            ]
            employed_results = await asyncio.gather(*employed_tasks)
            
            all_analyses = []
            for results in employed_results:
                all_analyses.extend(results)
            
            # 3. 观察蜂评估
            onlooker_tasks = [bee.evaluate(all_analyses) for bee in self.onlookers]
            onlooker_results = await asyncio.gather(*onlooker_tasks)
            
            # 投票选择最佳
            best_votes = {}
            for result in onlooker_results:
                best = result.get("best")
                if best:
                    key = best.get("location", "unknown")
                    best_votes[key] = best_votes.get(key, 0) + 1
            
            if best_votes:
                best_location = max(best_votes, key=best_votes.get)
                for result in onlooker_results:
                    if result.get("best", {}).get("location") == best_location:
                        best_result = result
                        break
        
        self.results = best_result or {}
        return self.results


class HybridSwarm:
    """蚁群+蜂群协同系统"""
    def __init__(
        self,
        ant_config: Dict = None,
        bee_config: Dict = None
    ):
        self.queen = Queen()
        
        ant_config = ant_config or {"scouts": 3, "foragers": 5, "workers": 2}
        bee_config = bee_config or {"scouts": 2, "employed": 3, "onlookers": 2}
        
        self.ant_colony = AntColony(**ant_config)
        self.bee_colony = BeeColony(**bee_config)
    
    async def collaborate(
        self,
        task: str,
        sources: List[str] = None,
        iterations: int = 3
    ) -> Dict:
        """协同工作流程"""
        sources = sources or ["hackernews", "reddit", "twitter", "github"]
        
        # 1. 创建任务
        main_task = self.queen.create_task(task)
        
        # 2. 蚁群采集
        ant_results = await self.ant_colony.forage(sources)
        
        # 3. 为高质量结果沉积信息素
        for result in ant_results:
            quality = result.get("quality", 0.5)
            if quality > 0.7:
                self.queen.deposit_global_pheromone(
                    PheromoneType.QUALITY,
                    result.get("hash", "unknown"),
                    quality,
                    {"source": result.get("source")}
                )
        
        # 4. 蜂群优化
        bee_results = await self.bee_colony.optimize(
            self.queen.pheromones,
            iterations
        )
        
        # 5. 信息素挥发
        self.queen.evaporate_all(0.1)
        
        # 6. 整合结果
        integrated = self.queen.integrate_results(ant_results, bee_results)
        
        return {
            "task_id": main_task.id,
            "task": task,
            "ant_results": ant_results,
            "bee_results": bee_results,
            "integrated": integrated,
            "pheromones": [
                {"type": p.type.value, "location": p.location, "strength": p.strength}
                for p in self.queen.pheromones
            ]
        }


# 便捷函数
async def run_ant_colony(task: str, sources: List[str] = None) -> List[Dict]:
    """运行蚁群采集"""
    colony = AntColony()
    sources = sources or ["hackernews", "reddit", "twitter"]
    return await colony.forage(sources)


async def run_bee_colony(pheromones: List[Pheromone] = None) -> Dict:
    """运行蜂群优化"""
    colony = BeeColony()
    pheromones = pheromones or []
    return await colony.optimize(pheromones)


async def run_hybrid_swarm(task: str, sources: List[str] = None) -> Dict:
    """运行协同系统"""
    swarm = HybridSwarm()
    return await swarm.collaborate(task, sources)


# 测试
if __name__ == "__main__":
    async def test():
        print("=== 测试蚁群采集 ===")
        ant_results = await run_ant_colony("采集AI新闻", ["hackernews", "reddit"])
        print(f"采集结果: {len(ant_results)} 条")
        
        print("\n=== 测试蜂群优化 ===")
        bee_results = await run_bee_colony()
        print(f"优化结果: {bee_results}")
        
        print("\n=== 测试协同系统 ===")
        hybrid_results = await run_hybrid_swarm("AI Agent 最新进展分析")
        print(f"协同结果: {json.dumps(hybrid_results['integrated'], indent=2, ensure_ascii=False)}")
    
    asyncio.run(test())
