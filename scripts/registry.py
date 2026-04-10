#!/usr/bin/env python3
"""
脚本注册表 - 快速查看和调用所有脚本
"""
SCRIPT_REGISTRY = {
    # 数据采集
    "collect-news": {
        "script": "swarm_news_collector.py",
        "usage": "run.bat collect-news --topic ai --limit 10",
        "description": "采集AI新闻并标记信息素"
    },
    "collect-github": {
        "script": "ant_github_code_analyzer.py",
        "usage": "python run.py collect-github",
        "description": "分析GitHub热门项目源码"
    },
    "collect-chinese": {
        "script": "chinese_community_explorer.py",
        "usage": "python run.py collect-chinese",
        "description": "探索中文社区（知乎、小红书、B站）"
    },
    "collect-global": {
        "script": "global_community_explorer.py",
        "usage": "python run.py collect-global",
        "description": "探索全球社区（Twitter、Reddit、Medium）"
    },
    
    # 学习进化
    "learn-hourly": {
        "script": "swarm_auto_learner.py",
        "usage": "python run.py learn-hourly --now",
        "description": "执行每小时自动学习（13个领域）"
    },
    "learn-infinite": {
        "script": "infinite_evolution_learner.py",
        "usage": "python run.py learn-infinite --once",
        "description": "无限进化自主学习（全网社区）"
    },
    "evolve-master": {
        "script": "infinite_evolution_master.py",
        "usage": "python run.py evolve-master --once",
        "description": "无限进化主控制器（整合所有社区）"
    },
    
    # 策略进化
    "evolve-ant": {
        "script": "ant_strategy_evolver.py",
        "usage": "python run.py evolve-ant",
        "description": "蚁群策略进化（信息素、采集策略）"
    },
    "evolve-bee": {
        "script": "bee_strategy_evolver.py",
        "usage": "python run.py evolve-bee",
        "description": "蜂群策略进化（分析策略、角色配置）"
    },
    "evolve-swarm": {
        "script": "swarm_co_evolver.py",
        "usage": "python run.py evolve-swarm --once",
        "description": "蚁群蜂群协同进化"
    },
    
    # AutoGPT风格
    "decompose": {
        "script": "autogpt_task_decomposer.py",
        "usage": "python run.py decompose \"任务描述\"",
        "description": "AutoGPT风格任务分解"
    },
    "reflect": {
        "script": "self_reflection_loop.py",
        "usage": "python run.py reflect",
        "description": "自我反思和持续改进"
    },
    
    # 工具
    "send-feishu": {
        "script": "feishu_report_sender.py",
        "usage": "python run.py send-feishu",
        "description": "发送报告到飞书"
    },
    "schedule": {
        "script": "pheromone_scheduler.py",
        "usage": "python run.py schedule",
        "description": "信息素任务调度器"
    },
    "evolve-code": {
        "script": "bee_code_evolution.py",
        "usage": "python run.py evolve-code --apply",
        "description": "蜂群代码进化器（从源码提炼模式）"
    }
}

def print_help():
    """打印帮助信息"""
    print("\n" + "="*70)
    print("快速脚本调用器 - 使用指南")
    print("="*70)
    print("\n用法:")
    print("  python run.py <命令> [参数]")
    print("\n可用命令:")
    print("-"*70)
    
    categories = {
        "数据采集": [k for k in SCRIPT_REGISTRY if k.startswith("collect-")],
        "学习进化": [k for k in SCRIPT_REGISTRY if k.startswith("learn-") or k.startswith("evolve-")],
        "AutoGPT": ["decompose", "reflect"],
        "工具": ["send-feishu", "schedule", "evolve-code"]
    }
    
    for category, commands in categories.items():
        print(f"\n[{category}]")
        for cmd in commands:
            if cmd in SCRIPT_REGISTRY:
                info = SCRIPT_REGISTRY[cmd]
                print(f"  {cmd:15s} - {info['description']}")
    
    print("\n" + "-"*70)
    print("示例:")
    print("  python run.py collect-news --topic ai --limit 10")
    print("  python run.py learn-hourly --now")
    print("  python run.py decompose \"构建自动化系统\"")
    print("="*70 + "\n")

def get_script(command):
    """获取脚本路径"""
    if command in SCRIPT_REGISTRY:
        return SCRIPT_REGISTRY[command]["script"]
    return None

if __name__ == "__main__":
    print_help()
