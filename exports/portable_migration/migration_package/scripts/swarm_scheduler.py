#!/usr/bin/env python3
"""
定时任务调度器 - 自动化采集-研究-回流
功能: 每天定时运行蚁群+蜂群系统
"""
import time
import json
from datetime import datetime, timedelta
import os
import sys

# 路径配置
WORKSPACE = "C:/Users/admin/.openclaw/workspace-bingbu"
COLLECTOR_DIR = "C:/Users/admin/.openclaw/agents/collector"
RESEARCHER_DIR = "C:/Users/admin/.openclaw/agents/researcher"


def log(msg: str):
    """日志"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_collector():
    """运行采集员"""
    log("🔄 启动采集员...")
    
    # 切换到collector目录运行
    sys.path.insert(0, COLLECTOR_DIR)
    
    # 动态导入
    import importlib.util
    spec = importlib.util.spec_from_file_location("ant_colony", f"{COLLECTOR_DIR}/ant_colony.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # 运行采集
    result = module.run_ant_colony()
    log(f"   采集完成: {result.get('total_findings', 0)} 条")
    return result


def run_researcher():
    """运行研究员"""
    log("🔄 启动研究员...")
    
    sys.path.insert(0, RESEARCHER_DIR)
    spec = importlib.util.spec_from_file_location("bee_colony", f"{RESEARCHER_DIR}/bee_colony.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    result = module.run_researcher()
    log(f"   处理完成，回流成功")
    return result


def save_log(result: dict):
    """保存运行日志"""
    log_file = f"{WORKSPACE}/memory/swarm_log.json"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 读取历史
    history = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    # 添加新记录
    history.append({
        "time": datetime.now().isoformat(),
        "collector": result.get("collector", {}).get("total_findings", 0),
        "researcher": result.get("researcher", {}).get("total", 0)
    })
    
    # 只保留最近30条
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
    
    # Step 1: 采集
    log("="*40)
    log("Step 1: 采集员工作")
    log("="*40)
    try:
        collector_result = run_collector()
        result["collector"] = collector_result
    except Exception as e:
        log(f"❌ 采集失败: {e}")
        result["collector"] = {"error": str(e)}
    
    # Step 2: 研究
    log("="*40)
    log("Step 2: 研究员工作")
    log("="*40)
    try:
        researcher_result = run_researcher()
        result["researcher"] = researcher_result
    except Exception as e:
        log(f"❌ 研究失败: {e}")
        result["researcher"] = {"error": str(e)}
    
    # Step 3: 记录
    save_log(result)
    
    # 汇总
    total = result.get("collector", {}).get("total_findings", 0)
    processed = result.get("researcher", {}).get("insights", {}).get("total", 0)
    
    print(f"\n{'='*60}")
    print(f"✅ 完整周期完成!")
    print(f"   采集: {total} 条")
    print(f"   处理: {processed} 条")
    print(f"   状态: {'成功' if total > 0 and processed > 0 else '有错误'}")
    print(f"{'='*60}")
    
    return result


def main():
    """主入口"""
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