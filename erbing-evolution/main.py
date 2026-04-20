# 二饼进化系统主程序
import json
from datetime import datetime
from evolution_engine import EvolutionEngine
from self_evaluator import SelfEvaluator
from self_regulator import SelfRegulator

def main():
    print("=" * 60)
    print("二饼进化系统 - Erbing Evolution System")
    print("=" * 60)
    print(f"启动时间: {datetime.now().isoformat()}")
    print(f"版本: 2.0.0-evolution-active")
    print(f"阶段: 第一阶段 - 基础能力建设")
    print("=" * 60)
    
    # 创建进化引擎
    engine = EvolutionEngine()
    evaluator = SelfEvaluator()
    regulator = SelfRegulator()
    
    # 执行评估
    print("执行系统评估...")
    report = evaluator.generate_report()
    
    # 自动调节
    print("执行自适应调节...")
    adjustments = regulator.auto_regulate(report)
    
    # 执行进化
    print("执行进化...")
    success = engine.evolve()
    
    # 保存状态
    engine.save_state()
    evaluator.save_report()
    regulator.save_state()
    
    # 生成总结
    status = engine.get_status()
    print("\n" + "=" * 60)
    print("进化完成")
    print("=" * 60)
    print(f"进化状态: {'成功' if success else '失败'}")
    print(f"当前阶段: {status['phase']}")
    print(f"当前版本: {status['version']}")
    print(f"应用调节数: {len(adjustments)}")
    
    return success

if __name__ == "__main__":
    main()
