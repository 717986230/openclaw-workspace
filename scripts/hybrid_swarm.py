#!/usr/bin/env python3
"""
混合群体智能系统 - Hybrid Swarm Intelligence
结合: 蚁群(ACO) + 蜂群(ABC) + 粒子群(PSO)
功能: 多策略协同，解决复杂优化问题
"""
import random
import math
import json
from datetime import datetime
from typing import List, Dict, Any

# ========== 基础类 ==========

class Particle:
    """粒子 (PSO)"""
    def __init__(self, dim=2):
        self.position = [random.random() * 10 for _ in range(dim)]
        self.velocity = [random.random() - 0.5 for _ in range(dim)]
        self.pbest = self.position.copy()
        self.pbest_fitness = float('inf')
    
    def update(self, gbest, w=0.7, c1=1.5, c2=1.5):
        """更新粒子位置"""
        for i in range(len(self.position)):
            r1, r2 = random.random(), random.random()
            # 认知 + 社会
            cognitive = c1 * r1 * (self.pbest[i] - self.position[i])
            social = c2 * r2 * (gbest[i] - self.position[i])
            
            self.velocity[i] = w * self.velocity[i] + cognitive + social
            self.position[i] += self.velocity[i]
        
        # 更新个体最优
        fitness = self.fitness()
        if fitness < self.pbest_fitness:
            self.pbest = self.position.copy()
            self.pbest_fitness = fitness
    
    def fitness(self) -> float:
        """适应度函数 (Rosenbrock)"""
        return sum(100 * (self.position[i+1] - self.position[i]**2)**2 + 
                   (1 - self.position[i])**2 for i in range(len(self.position)-1))


class Ant:
    """蚂蚁 (ACO)"""
    def __init__(self, name: str):
        self.name = name
        self.path = []
        self.fitness = 0
    
    def explore(self, nodes: List[str]) -> str:
        """探索节点"""
        return random.choice(nodes)


class Bee:
    """蜜蜂 (ABC)"""
    def __init__(self, role: str):
        self.role = role  # scout, employed, onlooker
        self.fitness = 0
        self.food_source = None
    
    def dance(self, fitness: float) -> float:
        """舞蹈传递信息"""
        # 适应度越高，跳舞越久（招募更多跟随蜂）
        return max(1, 10 - fitness)


class HybridSwarm:
    """混合群体系统"""
    def __init__(self, name: str = "混合 swarm"):
        self.name = name
        self.particles = []  # PSO
        self.ants = []       # ACO
        self.bees = []       # ABC
        self.gbest = None
        self.gbest_fitness = float('inf')
        self.history = []
        
        # 系统参数
        self.pso_count = 10
        self.aco_count = 5
        self.abc_count = 10
        
        self._init_swarm()
    
    def _init_swarm(self):
        """初始化群体"""
        # PSO 粒子
        for i in range(self.pso_count):
            p = Particle(dim=3)
            self.particles.append(p)
        
        # ACO 蚂蚁
        for i in range(self.aco_count):
            self.ants.append(Ant(f"蚂蚁{i+1}"))
        
        # ABC 蜜蜂
        role_dist = ["scout"] * 2 + ["employed"] * 5 + ["onlooker"] * 3
        for i, role in enumerate(role_dist):
            self.bees.append(Bee(role))
        
        print(f"🐜 混合群体初始化完成:")
        print(f"   粒子群(PSO): {self.pso_count} 个")
        print(f"   蚁群(ACO): {self.aco_count} 个")
        print(f"   蜂群(ABC): {self.bees.count({2})}")
    
    def run_pso(self, iterations: int = 10):
        """运行PSO"""
        print("\n🐦 PSO 粒子群迭代...")
        for i in range(iterations):
            for p in self.particles:
                p.update([0, 0, 0])
                if p.pbest_fitness < self.gbest_fitness:
                    self.gbest = p.pbest.copy()
                    self.gbest_fitness = p.pbest_fitness
            if i % 3 == 0:
                print(f"   迭代 {i}: 最佳适应度 = {self.gbest_fitness:.4f}")
    
    def run_aco(self, nodes: List[str]):
        """运行ACO"""
        print("\n🐜 ACO 蚁群探索...")
        for ant in self.ants:
            path = ant.explore(nodes)
            ant.path.append(path)
            ant.fitness = random.random()
            print(f"   {ant.name} 探索 {path}, 质量={ant.fitness:.2f}")
        
        # 返回最佳蚂蚁
        best_ant = max(self.ants, key=lambda a: a.fitness)
        return best_ant.path, best_ant.fitness
    
    def run_abc(self, food_sources: int = 5):
        """运行ABC"""
        print("\n🐝 ABC 蜂群采蜜...")
        
        # 侦查蜂搜索
        scouts = [b for b in self.bees if b.role == "scout"]
        for scout in scouts:
            scout.fitness = random.random()
            print(f"   侦查蜂 发现食物源, 适应度={scout.fitness:.2f}")
        
        # 采蜜蜂/跟随蜂
        workers = [b for b in self.bees if b.role in ["employed", "onlooker"]]
        for w in workers:
            # 跟随概率
            prob = random.random()
            w.fitness = prob * 0.8
            print(f"   {'采蜜蜂' if w.role == 'employed' else '跟随蜂'} 开采, 适应度={w.fitness:.2f}")
    
    def hybridize(self) -> Dict:
        """混合策略协同"""
        print("\n🔄 混合策略协同...")
        
        # 1. PSO 提供全局最优方向
        pso_best = self.gbest_fitness if self.gbest else 0
        
        # 2. ACO 提供探索路径
        aco_fitness = max(a.fitness for a in self.ants) if self.ants else 0
        
        # 3. ABC 提供局部优化
        abc_fitness = max(b.fitness for b in self.bees) if self.bees else 0
        
        # 综合评分
        hybrid_score = (pso_best * 0.4 + aco_fitness * 0.3 + abc_fitness * 0.3)
        
        print(f"   PSO贡献: {pso_best:.4f} (权重40%)")
        print(f"   ACO贡献: {aco_fitness:.4f} (权重30%)")
        print(f"   ABC贡献: {abc_fitness:.4f} (权重30%)")
        print(f"   综合评分: {hybrid_score:.4f}")
        
        return {
            "pso_best": pso_best,
            "aco_fitness": aco_fitness,
            "abc_fitness": abc_fitness,
            "hybrid_score": hybrid_score,
            "timestamp": datetime.now().isoformat()
        }
    
    def run(self, task: str, iterations: int = 10) -> Dict:
        """完整运行流程"""
        print(f"\n{'='*60}")
        print(f"🧬 混合群体智能系统启动")
        print(f"📋 任务: {task}")
        print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Step 1: 并行运行各算法
        self.run_pso(iterations)
        self.run_aco(["节点A", "节点B", "节点C", "节点D"])
        self.run_abc()
        
        # Step 2: 混合协同
        result = self.hybridize()
        result["task"] = task
        result["swarm_size"] = self.pso_count + self.aco_count + self.abc_count
        
        self.history.append(result)
        
        print(f"\n{'='*60}")
        print(f"✅ 任务完成! 综合评分: {result['hybrid_score']:.4f}")
        print(f"{'='*60}")
        
        return result


def main():
    """测试运行"""
    swarm = HybridSwarm("Erbing混合脑")
    
    tasks = [
        "搜索今日期货要闻",
        "优化PTA分析策略",
        "监控市场异常"
    ]
    
    results = []
    for task in tasks:
        result = swarm.run(task)
        results.append(result)
    
    print(f"\n📊 共完成任务: {len(results)}")
    print(f"📈 平均评分: {sum(r['hybrid_score'] for r in results)/len(results):.4f}")


if __name__ == "__main__":
    main()