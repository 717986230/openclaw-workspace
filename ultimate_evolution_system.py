"""
Erbing 统一进化系统 - 顶配版 (Ultimate Edition)
FastAPI微服务架构
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import asyncio
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# 添加路径
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root / "erbing-evolution"))
sys.path.insert(0, str(workspace_root / "erbing-gbrain-evolution"))
sys.path.insert(0, str(workspace_root / "virtual_world_advanced"))

# 导入各系统组件
try:
    from evolution_engine import EvolutionEngine
    from self_evaluator import SelfEvaluator
    from self_regulator import SelfRegulator
    EVOLUTION_AVAILABLE = True
except ImportError:
    EVOLUTION_AVAILABLE = False

try:
    from gbrain_implementation import ErbingGBrainEvolution
    GBRAIN_AVAILABLE = True
except ImportError:
    GBRAIN_AVAILABLE = False

try:
    from complete_evolution_manager import CompleteVirtualWorld
    VIRTUAL_WORLD_AVAILABLE = True
except ImportError:
    VIRTUAL_WORLD_AVAILABLE = False


# ==================== Pydantic Models ====================

class SystemStatus(BaseModel):
    """系统状态"""
    evolution_framework: bool = False
    gbrain_architecture: bool = False
    virtual_world: bool = False


class UnifiedState(BaseModel):
    """统一状态"""
    agent_id: str = "erbing"
    version: str = "4.0.0-ultimate"
    start_time: str = ""
    active_systems: List[str] = []
    evolution_phase: str = "PHASE_1"
    training_cycles: int = 0
    total_xp: int = 0
    current_level: int = 1
    capsule_id: Optional[str] = None
    sandbox_id: Optional[str] = None


class EvolutionRequest(BaseModel):
    """进化请求"""
    agent_id: str = Field(default="erbing", description="代理ID")


class TrainingRequest(BaseModel):
    """训练请求"""
    cycles: int = Field(default=1, ge=1, le=100, description="训练周期数")


class TrainingResult(BaseModel):
    """训练结果"""
    cycles_completed: int
    total_xp_gained: int
    current_level: int
    mission_results: List[Dict]
    arena_results: List[Dict]


# ==================== Ultimate Evolution System ====================

class UltimateEvolutionSystem:
    """
    顶配版统一进化系统
    FastAPI微服务架构
    """

    def __init__(self):
        self.systems_status = {
            'evolution_framework': EVOLUTION_AVAILABLE,
            'gbrain_architecture': GBRAIN_AVAILABLE,
            'virtual_world': VIRTUAL_WORLD_AVAILABLE
        }

        # 初始化各系统
        self._init_systems()

        # 统一状态
        self.unified_state = UnifiedState(
            agent_id='erbing',
            version='4.0.0-ultimate',
            start_time=datetime.now().isoformat(),
            active_systems=[k for k, v in self.systems_status.items() if v],
            evolution_phase='PHASE_1',
            training_cycles=0,
            total_xp=0,
            current_level=1
        )

        # 运行状态
        self.is_running = False
        self.is_training = False

    def _init_systems(self):
        """初始化各子系统"""
        # 进化框架
        if EVOLUTION_AVAILABLE:
            try:
                self.evolution_engine = EvolutionEngine()
                self.evaluator = SelfEvaluator()
                self.regulator = SelfRegulator()
            except Exception as e:
                print(f"[ERROR] Evolution framework init failed: {e}")
                self.evolution_engine = None
        else:
            self.evolution_engine = None

        # GBrain架构
        if GBRAIN_AVAILABLE:
            try:
                self.gbrain = ErbingGBrainEvolution()
            except Exception as e:
                print(f"[ERROR] GBrain architecture init failed: {e}")
                self.gbrain = None
        else:
            self.gbrain = None

        # 虚拟世界
        if VIRTUAL_WORLD_AVAILABLE:
            try:
                self.virtual_world = CompleteVirtualWorld()
            except Exception as e:
                print(f"[ERROR] Virtual world init failed: {e}")
                self.virtual_world = None
        else:
            self.virtual_world = None

    async def start_evolution(self, agent_id: str = "erbing") -> Dict:
        """启动进化流程"""
        results = {}

        # 进化框架评估
        if self.evolution_engine:
            try:
                report = self.evaluator.generate_report()
                results['evolution_report'] = report
            except Exception as e:
                results['evolution_report'] = {'error': str(e)}

        # GBrain架构初始化
        if self.gbrain:
            try:
                truth_page = self.gbrain.create_compiled_truth_page(
                    entity_type="agent",
                    entity_name="Erbing"
                )
                results['gbrain_page'] = truth_page
            except Exception as e:
                results['gbrain_page'] = {'error': str(e)}

        # 虚拟世界启动
        if self.virtual_world:
            try:
                world_result = self.virtual_world.start_evolution(agent_id)
                results['virtual_world'] = world_result
                self.unified_state.capsule_id = world_result.get('capsule_id')
            except Exception as e:
                results['virtual_world'] = {'error': str(e)}

        # 更新状态
        self.is_running = True
        self._sync_state(results)

        return results

    async def run_training_cycle(self, cycles: int = 1) -> Dict:
        """运行训练周期"""
        if not self.is_running:
            raise HTTPException(status_code=400, detail="Evolution not started")

        if self.is_training:
            raise HTTPException(status_code=400, detail="Training already in progress")

        self.is_training = True

        results = {
            'cycles_completed': 0,
            'total_xp_gained': 0,
            'mission_results': [],
            'arena_results': []
        }

        try:
            for i in range(cycles):
                # 虚拟世界训练
                if self.virtual_world and self.unified_state.capsule_id:
                    try:
                        training_result = self.virtual_world.run_training_cycle(
                            self.unified_state.capsule_id
                        )

                        # 计算XP
                        mission_xp = training_result['mission'].get('xp', 0)
                        arena_xp = training_result['arena'].get('xp', 0)
                        total_xp = mission_xp + arena_xp

                        self.unified_state.total_xp += total_xp
                        self.unified_state.training_cycles += 1

                        # 计算等级
                        new_level = 1 + self.unified_state.total_xp // 1000
                        if new_level > self.unified_state.current_level:
                            self.unified_state.current_level = new_level

                        results['cycles_completed'] += 1
                        results['total_xp_gained'] += total_xp
                        results['mission_results'].append(training_result['mission'])
                        results['arena_results'].append(training_result['arena'])

                    except Exception as e:
                        print(f"[ERROR] Training cycle {i+1} failed: {e}")

                # 进化框架调节
                if self.evolution_engine:
                    try:
                        adjustments = self.regulator.auto_regulate({})
                    except Exception as e:
                        print(f"[ERROR] Evolution regulation failed: {e}")

                # GBrain知识更新
                if self.gbrain:
                    try:
                        # 添加时间线条目
                        pass
                    except Exception as e:
                        print(f"[ERROR] GBrain update failed: {e}")

        finally:
            self.is_training = False

        # 更新当前等级
        results['current_level'] = self.unified_state.current_level

        return results

    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'unified_state': self.unified_state.model_dump(),
            'systems_status': self.systems_status,
            'is_running': self.is_running,
            'is_training': self.is_training
        }

    def _sync_state(self, results: Dict):
        """同步状态"""
        if results.get('virtual_world'):
            self.unified_state.capsule_id = results['virtual_world'].get('capsule_id')
            self.unified_state.sandbox_id = results['virtual_world'].get('sandbox_id')

        if results.get('evolution_report'):
            self.unified_state.evolution_score = results['evolution_report'].get('overall_score', 0)

        if results.get('gbrain_page'):
            self.unified_state.gbrain_initialized = True

    def save_state(self):
        """保存状态"""
        state_file = workspace_root / "ultimate_evolution_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.unified_state.model_dump(), f, indent=2, ensure_ascii=False)

    def load_state(self):
        """加载状态"""
        state_file = workspace_root / "ultimate_evolution_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                self.unified_state = UnifiedState(**state_data)
            return True
        return False


# ==================== FastAPI Application ====================

# 创建系统实例
ultimate_system = UltimateEvolutionSystem()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("=" * 70)
    print("  Erbing 统一进化系统 - 顶配版 (Ultimate Edition)")
    print("  Version: 4.0.0-ultimate")
    print("=" * 70)
    print()

    # 尝试加载状态
    if ultimate_system.load_state():
        print("状态已加载")
    else:
        print("使用初始状态")

    print()
    print("系统状态:")
    print(f"  进化框架: {'[OK]' if ultimate_system.systems_status['evolution_framework'] else '[FAIL]'}")
    print(f"  GBrain架构: {'[OK]' if ultimate_system.systems_status['gbrain_architecture'] else '[FAIL]'}")
    print(f"  虚拟世界: {'[OK]' if ultimate_system.systems_status['virtual_world'] else '[FAIL]'}")
    print()

    yield

    # 关闭时
    print()
    print("保存状态...")
    ultimate_system.save_state()
    print("系统关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Erbing 统一进化系统 - 顶配版",
    description="企业级AI进化平台",
    version="4.0.0-ultimate",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Erbing 统一进化系统 - 顶配版",
        "version": "4.0.0-ultimate",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "systems": ultimate_system.systems_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/status")
async def get_status():
    """获取系统状态"""
    return ultimate_system.get_status()


@app.get("/api/v1/systems")
async def get_systems_status():
    """获取各子系统状态"""
    return SystemStatus(**ultimate_system.systems_status)


@app.post("/api/v1/evolution/start")
async def start_evolution(request: EvolutionRequest):
    """启动进化流程"""
    try:
        results = await ultimate_system.start_evolution(request.agent_id)
        return {
            "status": "success",
            "message": "Evolution started successfully",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/training/run")
async def run_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """运行训练周期"""
    try:
        # 异步运行训练
        result = await ultimate_system.run_training_cycle(request.cycles)
        return {
            "status": "success",
            "message": f"Training completed: {result['cycles_completed']} cycles",
            "result": result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/training/status")
async def get_training_status():
    """获取训练状态"""
    return {
        "is_training": ultimate_system.is_training,
        "training_cycles": ultimate_system.unified_state.training_cycles,
        "total_xp": ultimate_system.unified_state.total_xp,
        "current_level": ultimate_system.unified_state.current_level
    }


@app.post("/api/v1/state/save")
async def save_state():
    """保存状态"""
    try:
        ultimate_system.save_state()
        return {
            "status": "success",
            "message": "State saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/state/load")
async def load_state():
    """加载状态"""
    try:
        success = ultimate_system.load_state()
        if success:
            return {
                "status": "success",
                "message": "State loaded successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="State file not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """获取系统指标"""
    return {
        "agent_id": ultimate_system.unified_state.agent_id,
        "version": ultimate_system.unified_state.version,
        "start_time": ultimate_system.unified_state.start_time,
        "training_cycles": ultimate_system.unified_state.training_cycles,
        "total_xp": ultimate_system.unified_state.total_xp,
        "current_level": ultimate_system.unified_state.current_level,
        "evolution_phase": ultimate_system.unified_state.evolution_phase,
        "active_systems": ultimate_system.unified_state.active_systems,
        "is_running": ultimate_system.is_running,
        "is_training": ultimate_system.is_training,
        "timestamp": datetime.now().isoformat()
    }


# ==================== Main Entry ====================

def main():
    """主入口"""
    print("=" * 70)
    print("  Erbing 统一进化系统 - 顶配版")
    print("  Ultimate Edition")
    print("=" * 70)
    print()
    print("启动FastAPI服务器...")
    print()

    # 运行服务器
    uvicorn.run(
        "ultimate_evolution_system:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
