#!/usr/bin/env python3
"""
定时任务调度器 - 自动化采集-研究-回流
修复版：适配 macOS/Linux 路径 + 集成本地混合群体
"""
import time
import json
import os
import sys
import importlib
import importlib.util
from datetime import datetime
from pathlib import Path

# 路径配置（适配 macOS）
WORKSPACE = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = WORKSPACE / "scripts"
MEMORY_DIR = WORKSPACE / "memory"
DB_PATH = MEMORY_DIR / "database" / "xiaozhi_memory.db"

sys.path.insert(0, str(SCRIPTS_DIR))


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_collector():
    """运行蚁群采集员（基于 r.jina.ai 真实数据）"""
    log("🐜 启动采集员（蚁群·r.jina.ai）...")
    try:
        import importlib
        import urllib.parse  # 确保 jina_collector 能用
        spec = importlib.util.spec_from_file_location("jina_collector", SCRIPTS_DIR / "jina_collector.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.run_ant_colony()
        total = result.get("total_findings", 0)
        log(f"   采集完成: {total} 条发现")
        return result
    except Exception as e:
        log(f"   ❌ 采集失败: {e}")
        return {"error": str(e)}


def run_researcher(collector_result: dict = None):
    """运行研究员（蜂群），接收并处理采集结果"""
    log("🐝 启动研究员（蜂群）...")
    try:
        bee_path = SCRIPTS_DIR / "bee_colony.py"
        if bee_path.exists():
            spec = importlib.util.spec_from_file_location("bee_colony", bee_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = module.run_researcher(collector_result)
        else:
            spec = importlib.util.spec_from_file_location("hybrid_swarm", SCRIPTS_DIR / "hybrid_swarm.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            swarm = module.HybridSwarm("Erbing研究员")
            result = swarm.run("市场研究任务")
        log(f"   研究完成")
        return result
    except Exception as e:
        log(f"   ❌ 研究失败: {e}")
        return {"error": str(e)}


def save_log(result: dict):
    log_file = MEMORY_DIR / "swarm_log.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append({
        "time": datetime.now().isoformat(),
        "collector": result.get("collector", {}).get("total_findings", 0),
        "researcher": result.get("researcher", {}).get("total", 0),
        "status": "ok" if "error" not in str(result) else "partial"
    })
    history = history[-30:]
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def run_full_cycle():
    """完整运行周期"""
    print(f"\n{'='*60}")
    print(f"🧬 群体智能系统 - 自动化运行")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    result = {}

    log("="*40)
    log("Step 1: 采集员工作 (蚁群)")
    log("="*40)
    result["collector"] = run_collector()

    log("="*40)
    log("Step 2: 研究员工作 (蜂群)")
    log("="*40)
    result["researcher"] = run_researcher(result["collector"])

    save_log(result)

    total = result.get("collector", {}).get("total_findings", 0)
    processed = result.get("researcher", {}).get("total", 0) or result.get("researcher", {}).get("swarm_size", 0)

    print(f"\n{'='*60}")
    print(f"✅ 完整周期完成!")
    print(f"   采集: {total} 条")
    print(f"   处理: {processed} 条")
    print(f"{'='*60}")
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="群体智能定时任务")
    parser.add_argument("--once", "-o", action="store_true", help="运行一次")
    parser.add_argument("--loop", "-l", type=int, default=1, help="循环次数")
    parser.add_argument("--interval", "-i", type=int, default=60, help="间隔秒数")
    args = parser.parse_args()

    if args.once:
        run_full_cycle()
    else:
        for i in range(args.loop):
            print(f"\n🔄 第 {i+1}/{args.loop} 次运行")
            run_full_cycle()
            if i < args.loop - 1:
                log(f"⏳ 等待 {args.interval} 秒...")
                time.sleep(args.interval)


if __name__ == "__main__":
    main()