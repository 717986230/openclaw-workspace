"""
Erbing 统一进化系统 - 整合版本
整合三个系统：
1. erbing-evolution - 宏观进化框架
2. erbing-gbrain-evolution - GBrain架构概念
3. virtual_world_advanced - 虚拟世界训练环境
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

# 添加路径
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root / "erbing-evolution"))
sys.path.insert(0, str(workspace_root / "erbing-gbrain-evolution"))
sys.path.insert(0, str(workspace_root / "virtual_world_advanced"))

# 导入各系统组件
try:
    from evolution_engine import EvolutionEngine, EvolutionPhase, SystemMetrics, EvolutionState
    from self_evaluator import SelfEvaluator
    from self_regulator import SelfRegulator
    EVOLUTION_AVAILABLE = True
except ImportError:
    EVOLUTION_AVAILABLE = False
    print("[WARNING] erbing-evolution components not available")

try:
    from gbrain_implementation import ErbingGBrainEvolution
    GBRAIN_AVAILABLE = True
except ImportError:
    GBRAIN_AVAILABLE = False
    print("[WARNING] erbing-gbrain-evolution components not available")

try:
    from complete_evolution_manager import CompleteVirtualWorld
    VIRTUAL_WORLD_AVAILABLE = True
except ImportError:
    VIRTUAL_WORLD_AVAILABLE = False
    print("[WARNING] virtual_world_advanced components not available")


class UnifiedEvolutionSystem:
    """
    统一进化系统
    整合宏观框架、架构概念和训练环境
    """

    def __init__(self):
        print("=" * 70)
        print("  Erbing 统一进化系统 - Unified Evolution System")
        print("=" * 70)
        print(f"启动时间: {datetime.now().isoformat()}")
        print()

        # 系统状态
        self.systems_status = {
            'evolution_framework': EVOLUTION_AVAILABLE,
            'gbrain_architecture': GBRAIN_AVAILABLE,
            'virtual_world': VIRTUAL_WORLD_AVAILABLE
        }

        # 初始化各系统
        self._init_systems()

        # 统一状态
        self.unified_state = {
            'agent_id': 'erbing',
            'version': '3.0.0-unified',
            'start_time': datetime.now().isoformat(),
            'active_systems': [k for k, v in self.systems_status.items() if v],
            'evolution_phase': 'PHASE_1',
            'training_cycles': 0,
            'total_xp': 0,
            'current_level': 1
        }

        print("=" * 70)
        print("  系统初始化完成")
        print("=" * 70)
        print()

    def _init_systems(self):
        """初始化各子系统"""
        # 1. 进化框架
        if EVOLUTION_AVAILABLE:
            print("[1/3] 初始化进化框架...")
            try:
                self.evolution_engine = EvolutionEngine()
                self.evaluator = SelfEvaluator()
                self.regulator = SelfRegulator()
                print("      [OK] 进化框架就绪")
            except Exception as e:
                print(f"      [ERROR] 进化框架初始化失败: {e}")
                self.evolution_engine = None
        else:
            self.evolution_engine = None
            print("[1/3] 进化框架不可用")

        # 2. GBrain架构
        if GBRAIN_AVAILABLE:
            print("[2/3] 初始化GBrain架构...")
            try:
                self.gbrain = ErbingGBrainEvolution()
                print("      [OK] GBrain架构就绪")
            except Exception as e:
                print(f"      [ERROR] GBrain架构初始化失败: {e}")
                self.gbrain = None
        else:
            self.gbrain = None
            print("[2/3] GBrain架构不可用")

        # 3. 虚拟世界
        if VIRTUAL_WORLD_AVAILABLE:
            print("[3/3] 初始化虚拟世界...")
            try:
                self.virtual_world = CompleteVirtualWorld()
                print("      [OK] 虚拟世界就绪")
            except Exception as e:
                print(f"      [ERROR] 虚拟世界初始化失败: {e}")
                self.virtual_world = None
        else:
            self.virtual_world = None
            print("[3/3] 虚拟世界不可用")

        print()

    def start_unified_evolution(self, agent_id: str = "erbing") -> Dict:
        """
        启动统一进化流程
        """
        print("\n" + "=" * 70)
        print("  >> 启动统一进化流程")
        print("=" * 70)
        print()

        results = {}

        # 1. 进化框架评估
        if self.evolution_engine:
            print("[Step 1/4] 执行进化框架评估...")
            try:
                report = self.evaluator.generate_report()
                results['evolution_report'] = report
                print(f"          评估完成: {report.get('overall_score', 0):.1f}/100")
            except Exception as e:
                print(f"          评估失败: {e}")
                results['evolution_report'] = None
            print()

        # 2. GBrain架构初始化
        if self.gbrain:
            print("[Step 2/4] 初始化GBrain架构...")
            try:
                # 创建编译真相页面
                truth_page = self.gbrain.create_compiled_truth_page(
                    entity_type="agent",
                    entity_name="Erbing"
                )
                results['gbrain_page'] = truth_page
                print(f"          真相页面创建完成")
            except Exception as e:
                print(f"          初始化失败: {e}")
                results['gbrain_page'] = None
            print()

        # 3. 虚拟世界启动
        if self.virtual_world:
            print("[Step 3/4] 启动虚拟世界训练环境...")
            try:
                world_result = self.virtual_world.start_evolution(agent_id)
                results['virtual_world'] = world_result
                self.unified_state['capsule_id'] = world_result.get('capsule_id')
                print(f"          虚拟世界启动完成")
                print(f"          Capsule ID: {world_result.get('capsule_id')}")
            except Exception as e:
                print(f"          启动失败: {e}")
                results['virtual_world'] = None
            print()

        # 4. 统一状态同步
        print("[Step 4/4] 同步统一状态...")
        self._sync_unified_state(results)
        print("          状态同步完成")
        print()

        print("=" * 70)
        print("  [SUCCESS] 统一进化流程启动完成!")
        print("=" * 70)
        print()

        return results

    def run_unified_training_cycle(self) -> Dict:
        """
        运行统一训练周期
        """
        print("\n" + "=" * 70)
        print("  >> 运行统一训练周期")
        print("=" * 70)
        print()

        results = {}

        # 1. 虚拟世界训练
        if self.virtual_world and self.unified_state.get('capsule_id'):
            print("[Training 1/3] 虚拟世界训练...")
            try:
                capsule_id = self.unified_state['capsule_id']
                training_result = self.virtual_world.run_training_cycle(capsule_id)
                results['virtual_world_training'] = training_result

                # 更新XP和等级
                mission_xp = training_result['mission'].get('xp', 0)
                arena_xp = training_result['arena'].get('xp', 0)
                total_xp = mission_xp + arena_xp

                self.unified_state['total_xp'] += total_xp
                self.unified_state['training_cycles'] += 1

                # 计算等级 (每1000XP升一级)
                new_level = 1 + self.unified_state['total_xp'] // 1000
                if new_level > self.unified_state['current_level']:
                    self.unified_state['current_level'] = new_level
                    print(f"          🎉 升级! 当前等级: {new_level}")

                print(f"          训练完成: 任务XP={mission_xp}, 对战XP={arena_xp}")
            except Exception as e:
                print(f"          训练失败: {e}")
                results['virtual_world_training'] = None
            print()

        # 2. 进化框架调节
        if self.evolution_engine:
            print("[Training 2/3] 进化框架调节...")
            try:
                adjustments = self.regulator.auto_regulate({})
                results['evolution_adjustments'] = adjustments
                print(f"          调节完成: {len(adjustments)}项调整")
            except Exception as e:
                print(f"          调节失败: {e}")
                results['evolution_adjustments'] = None
            print()

        # 3. GBrain知识更新
        if self.gbrain:
            print("[Training 3/3] GBrain知识更新...")
            try:
                # 添加时间线条目
                if results.get('gbrain_page'):
                    timeline_entry = self.gbrain.add_timeline_entry(
                        page=results['gbrain_page'],
                        event_type="training_cycle",
                        description=f"完成训练周期 #{self.unified_state['training_cycles']}",
                        metadata={
                            'xp_gained': self.unified_state['total_xp'],
                            'level': self.unified_state['current_level']
                        }
                    )
                    results['gbrain_timeline'] = timeline_entry
                    print(f"          知识更新完成")
            except Exception as e:
                print(f"          更新失败: {e}")
                results['gbrain_timeline'] = None
            print()

        print("=" * 70)
        print("  [SUCCESS] 统一训练周期完成!")
        print("=" * 70)
        print()

        return results

    def get_unified_status(self) -> Dict:
        """
        获取统一状态
        """
        status = {
            'unified_state': self.unified_state.copy(),
            'systems_status': self.systems_status.copy()
        }

        # 获取各子系统状态
        if self.evolution_engine:
            try:
                status['evolution_status'] = self.evolution_engine.get_status()
            except:
                status['evolution_status'] = None

        if self.virtual_world and self.unified_state.get('capsule_id'):
            try:
                capsule_id = self.unified_state['capsule_id']
                status['virtual_world_status'] = self.virtual_world.get_complete_status(capsule_id)
            except:
                status['virtual_world_status'] = None

        if self.gbrain:
            try:
                status['gbrain_status'] = {
                    'active': True,
                    'pages_created': 1  # 简化统计
                }
            except:
                status['gbrain_status'] = None

        return status

    def _sync_unified_state(self, results: Dict):
        """同步统一状态"""
        # 从各子系统结果中提取关键信息
        if results.get('virtual_world'):
            self.unified_state['capsule_id'] = results['virtual_world'].get('capsule_id')
            self.unified_state['sandbox_id'] = results['virtual_world'].get('sandbox_id')

        if results.get('evolution_report'):
            self.unified_state['evolution_score'] = results['evolution_report'].get('overall_score', 0)

        if results.get('gbrain_page'):
            self.unified_state['gbrain_initialized'] = True

    def save_unified_state(self):
        """保存统一状态"""
        state_file = workspace_root / "unified_evolution_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.unified_state, f, indent=2, ensure_ascii=False)
        print(f"统一状态已保存到: {state_file}")

    def load_unified_state(self):
        """加载统一状态"""
        state_file = workspace_root / "unified_evolution_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                self.unified_state = json.load(f)
            print(f"统一状态已从 {state_file} 加载")
            return True
        return False


def interactive_menu():
    """
    交互式菜单
    """
    system = UnifiedEvolutionSystem()

    while True:
        print("\n" + "-" * 70)
        print("  Erbing 统一进化系统")
        print("-" * 70)
        print()
        print("  [1] 启动统一进化")
        print("  [2] 运行训练周期")
        print("  [3] 查看统一状态")
        print("  [4] 查看系统状态")
        print("  [5] 保存状态")
        print("  [6] 加载状态")
        print("  [0] 退出")
        print()

        choice = input("  选择操作 > ").strip()

        if choice == '1':
            agent_id = input("  输入代理ID (默认: erbing) > ").strip()
            if not agent_id:
                agent_id = "erbing"
            result = system.start_unified_evolution(agent_id)
            print(f"\n  启动结果: {len([k for k, v in result.items() if v is not None])} 个系统已启动")

        elif choice == '2':
            result = system.run_unified_training_cycle()
            print(f"\n  训练结果: XP={system.unified_state['total_xp']}, 等级={system.unified_state['current_level']}")

        elif choice == '3':
            status = system.get_unified_status()
            print(f"\n  统一状态:")
            print(f"  代理ID: {status['unified_state']['agent_id']}")
            print(f"  版本: {status['unified_state']['version']}")
            print(f"  当前等级: {status['unified_state']['current_level']}")
            print(f"  总XP: {status['unified_state']['total_xp']}")
            print(f"  训练周期: {status['unified_state']['training_cycles']}")
            print(f"  活跃系统: {', '.join(status['unified_state']['active_systems'])}")

        elif choice == '4':
            print(f"\n  系统状态:")
            print(f"  进化框架: {'[OK]' if system.systems_status['evolution_framework'] else '[FAIL]'}")
            print(f"  GBrain架构: {'[OK]' if system.systems_status['gbrain_architecture'] else '[FAIL]'}")
            print(f"  虚拟世界: {'[OK]' if system.systems_status['virtual_world'] else '[FAIL]'}")

        elif choice == '5':
            system.save_unified_state()

        elif choice == '6':
            if system.load_unified_state():
                print("  状态加载成功")
            else:
                print("  状态文件不存在")

        elif choice == '0':
            print("\n  退出统一进化系统...")
            break

        else:
            print("  [ERROR] 无效选项")


def main():
    """主入口"""
    # 设置控制台编码为UTF-8
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print()
    print("=" * 70)
    print("  欢迎使用 Erbing 统一进化系统")
    print("=" * 70)
    print()
    print("  整合组件:")
    print(f"  - 进化框架: {'✅' if EVOLUTION_AVAILABLE else '❌'}")
    print(f"  - GBrain架构: {'✅' if GBRAIN_AVAILABLE else '❌'}")
    print(f"  - 虚拟世界: {'✅' if VIRTUAL_WORLD_AVAILABLE else '❌'}")
    print()

    interactive_menu()


if __name__ == "__main__":
    main()
