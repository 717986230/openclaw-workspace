#!/usr/bin/env python3
"""
顶级高并发分布式系统启动脚本
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from high_concurrency_ultimate import (
    UltimateDistributedSystem,
    Node,
    NodeStatus,
    LoadBalanceStrategy
)


async def main():
    """主函数"""
    # 加载配置
    config_path = Path(__file__).parent / "config_ultimate.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 60)
    print(f"🚀 启动 {config['system']['name']} v{config['system']['version']}")
    print(f"📊 环境: {config['system']['environment']}")
    print("=" * 60)
    
    # 创建系统实例
    system = UltimateDistributedSystem(config)
    
    # 初始化
    print("\n📡 正在初始化系统...")
    await system.initialize()
    print("✅ 系统初始化完成")
    
    # 注册节点
    print("\n🔗 正在注册节点...")
    for node_config in config['nodes']:
        node = Node(
            node_id=node_config['node_id'],
            host=node_config['host'],
            port=node_config['port'],
            weight=node_config.get('weight', 1)
        )
        system.service_discovery.register("main_service", node)
        print(f"  ✅ 节点 {node.node_id} 已注册")
    
    # 显示系统状态
    print("\n📊 系统状态:")
    stats = system.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 运行测试
    print("\n🧪 运行性能测试...")
    await system.run_performance_test()
    
    # 保持运行
    print("\n⏳ 系统运行中... (按 Ctrl+C 停止)")
    try:
        while True:
            await asyncio.sleep(10)
            
            # 定期显示状态
            current_stats = system.get_stats()
            print(f"\n📈 实时统计: {datetime.now().strftime('%H:%M:%S')}")
            print(f"  处理任务数: {current_stats.get('total_tasks_processed', 0)}")
            print(f"  活跃连接: {current_stats.get('active_connections', 0)}")
            print(f"  缓存命中率: {current_stats.get('cache_hit_rate', 0):.2%}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 正在关闭系统...")
        await system.shutdown()
        print("✅ 系统已关闭")


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())