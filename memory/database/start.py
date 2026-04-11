#!/usr/bin/env python3
"""
Erbing Phase 4: 企业级高级功能 - 快速启动脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from enterprise_erbing import EnterpriseErbing


async def main():
    """主函数"""
    print("=" * 60)
    print("Erbing Phase 4: 企业级高级功能")
    print("=" * 60)
    print()
    
    # 配置
    config = {
        "obsidian_vault_path": "./brain/obsidian_vault",
        "monitor": {
            "monitor_interval": 60,
            "alerts": {
                "cpu_threshold": 80,
                "memory_threshold": 80,
                "disk_threshold": 90,
                "response_time_threshold": 1.0
            },
            "notifications": {
                "email_enabled": False,
                "slack_enabled": False,
                "pagerduty_enabled": False
            },
            "max_history_size": 100
        }
    }
    
    # 初始化
    print("🚀 初始化 Enterprise Erbing...")
    erbing = EnterpriseErbing(config)
    await erbing.initialize()
    print("✅ 初始化完成!")
    print()
    
    # 示例消息
    example_messages = [
        "John Smith announced that TechCorp raised $50M in Series B funding led by Sequoia Capital.",
        "Jane Doe joined OpenAI as VP of Engineering.",
        "Google acquired DeepMind for $500M.",
        "Apple released new AI-powered features in iOS 18.",
        "Microsoft announced partnership with OpenAI."
    ]
    
    # 处理消息
    print("📝 处理示例消息...")
    for i, message in enumerate(example_messages, 1):
        print(f"\n[{i}/{len(example_messages)}] 处理消息...")
        print(f"消息: {message[:80]}...")
        
        result = await erbing.process_message(message)
        
        print(f"✅ 处理完成!")
        print(f"   - 实体类型: {len(result['entities'])}")
        print(f"   - 处理结果: {len(result['results'])}")
        print(f"   - 处理时间: {result['processed_at']}")
    
    print()
    print("📊 所有消息处理完成!")
    print()
    
    # 健康检查
    print("🔍 健康检查...")
    health = await erbing.health_check()
    print(f"✅ 状态: {health['status']}")
    print(f"   - 组件数量: {len(health['components'])}")
    print(f"   - 检查时间: {health['timestamp']}")
    print()
    
    # 统计信息
    print("📈 统计信息...")
    stats = erbing.get_stats()
    print(f"✅ 统计信息:")
    print(f"   - 并发配置: {stats['concurrency']['connection_pool_size']} 连接")
    print(f"   - 监控历史: {stats['monitor']['avg_cpu']:.2f}% CPU")
    print(f"   - Obsidian 实体: {stats['obsidian']['entities']} 个")
    print()
    
    # 交互式模式
    print("=" * 60)
    print("🎮 交互式模式")
    print("=" * 60)
    print("输入消息进行处理，输入 'quit' 退出")
    print()
    
    while True:
        try:
            # 获取用户输入
            user_input = input(">>> ").strip()
            
            # 退出
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
            
            # 空输入
            if not user_input:
                continue
            
            # 处理消息
            print("📝 处理消息...")
            result = await erbing.process_message(user_input)
            
            print(f"✅ 处理完成!")
            print(f"   - 实体类型: {len(result['entities'])}")
            print(f"   - 处理结果: {len(result['results'])}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            print()
    
    # 关闭
    print()
    print("🛑 关闭 Enterprise Erbing...")
    await erbing.shutdown()
    print("✅ 关闭完成!")
    print()
    print("=" * 60)
    print("感谢使用 Erbing Phase 4: 企业级高级功能!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
