#!/usr/bin/env python3
"""
统一命令行接口 - 所有脚本的快速入口（精简版）
"""

# 核心命令（只保留必要的）
CORE_COMMANDS = {
    "collect": {"script": "swarm_news_collector.py", "desc": "采集", "usage": "collect"},
    "learn": {"script": "swarm_auto_learner.py", "desc": "学习", "usage": "learn --now"},
    "evolve": {"script": "swarm_co_evolver.py", "desc": "进化", "usage": "evolve --once"},
    "decompose": {"script": "autogpt_task_decomposer.py", "desc": "分解", "usage": "decompose \"任务\""},
    "reflect": {"script": "continuous_reflector.py", "desc": "反思", "usage": "reflect"},
    "deps": {"script": "uv_package_manager.py", "desc": "依赖", "usage": "deps"},
    "md": {"script": "md_formatter.py", "desc": "MD格式化", "usage": "md <模板>"}
}

def show_help():
    """精简帮助"""
    print("""
========================================
     快速命令（精简版）
========================================

python run.py <命令> [参数]

核心命令:
  collect    统一采集（新闻/GitHub）
  learn      学习系统（13领域）
  evolve     进化系统
  decompose  任务分解
  reflect    自我反思
  deps       依赖管理（Uv）

查看详情: python run.py --help
========================================
""")

def main():
    import sys
    from pathlib import Path
    
    if len(sys.argv) == 1 or sys.argv[1] in ["--help", "-h", "help"]:
        show_help()
        return 0
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command in CORE_COMMANDS:
        script_file = CORE_COMMANDS[command]["script"]
        script_path = Path("scripts") / script_file
        
        if script_path.exists():
            import subprocess
            cmd = [sys.executable, str(script_path)] + args
            result = subprocess.run(cmd)
            return result.returncode
        else:
            print(f"[错误] 脚本不存在: {script_path}")
            return 1
    else:
        print(f"[错误] 未知命令: {command}")
        print("使用 --help 查看可用命令")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
