#!/usr/bin/env python3
"""
Erbing 心跳误差测量器 — Control Theory Edition
测量5维误差向量，判断系统稳定性
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/xinglong/openclaw-workspace")
MEMORY = WORKSPACE / "memory"
STATE_FILE = MEMORY / "self" / "erbing_state.json"
HEARTBEAT_LOG_DIR = MEMORY / "events"
BELIEFS_FILE = MEMORY / "beliefs.json"
IMPROVEMENTS_DIR = MEMORY / "improvements"

# 目标状态（从SELF档案）
TARGET = {
    "memory_order": 0.9,       # 记忆有序度 >= 0.9
    "tool_response_time": 5.0, # 工具响应 < 5s
    "consecutive_errors": 0,   # 连续错误 = 0
    "task_backlog": 3,         # 任务积压 <= 3
    "idle_minutes_max": 120,   # 空闲不超过2小时
}

# 误差等级阈值
ERROR_LEVEL_VERY_SMALL = 0.1
ERROR_LEVEL_SMALL = 0.3
ERROR_LEVEL_MEDIUM = 0.6


def load_recent_cron_runs(limit=5):
    """获取最近N次cron运行状态"""
    try:
        import subprocess
        result = subprocess.run(
            ["openclaw", "tasks", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    return {}


def measure_memory_order():
    """测量记忆有序度：用信念库的内聚度代理"""
    try:
        if not BELIEFS_FILE.exists():
            return 0.5, 0.4  # 无数据，默认中低
        
        with open(BELIEFS_FILE) as f:
            beliefs = json.load(f)
        
        if not beliefs:
            return 0.4, 0.5
        
        # 计算信念库质量：有多少信念有success_rate记录
        scored = sum(1 for v in beliefs.values() if "success_rate" in v)
        ratio = scored / max(len(beliefs), 1)
        
        # 有使用记录的信念越多，说明记忆越经过检验，有序度越高
        order = 0.3 + 0.7 * ratio
        error = TARGET["memory_order"] - order
        return order, error
    except Exception as e:
        return 0.5, 0.4


def measure_tool_response_time():
    """测量工具响应时间：用最近cron任务的平均duration代理"""
    try:
        # 读取cron运行记录中的duration
        cron_state_file = MEMORY / "state.json"
        if cron_state_file.exists():
            with open(cron_state_file) as f:
                state = json.load(f)
            
            durations = state.get("recent_durations", [])
            if durations:
                avg_duration = sum(durations[-10:]) / min(len(durations), 10)
                avg_seconds = avg_duration / 1000  # ms → s
                error = avg_seconds - TARGET["tool_response_time"]
                return avg_seconds, error
        
        # 降级：从brain_evolution_summary读
        summary_file = MEMORY / "brain_evolution_summary.md"
        if summary_file.exists():
            content = summary_file.read_text()
            import re
            match = re.search(r"平均响应[:：]\s*(\d+\.?\d*)秒", content)
            if match:
                val = float(match.group(1))
                return val, val - TARGET["tool_response_time"]
    except:
        pass
    
    return 5.0, 0.0  # 未知，默认无误差


def measure_consecutive_errors():
    """测量连续错误数：用cron任务的consecutiveErrors代理"""
    try:
        cron_state_file = MEMORY / "state.json"
        if cron_state_file.exists():
            with open(cron_state_file) as f:
                state = json.load(f)
            
            consecutive = state.get("consecutive_errors", 0)
            error = consecutive - TARGET["consecutive_errors"]  # 目标是0，越多越差
            return consecutive, error
    except:
        pass
    
    # 从cron jobs状态推断（需要读openclaw状态）
    try:
        import subprocess
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            jobs = json.loads(result.stdout)
            max_consecutive = 0
            for job in jobs.get("jobs", []):
                ce = job.get("state", {}).get("consecutiveErrors", 0)
                if ce > max_consecutive:
                    max_consecutive = ce
            error = max_consecutive - TARGET["consecutive_errors"]
            return max_consecutive, error
    except:
        pass
    
    return 0, 0.0


def measure_task_backlog():
    """测量任务积压数"""
    backlog = 0
    try:
        # 检查events目录中未处理的待办
        events_dir = HEARTBEAT_LOG_DIR
        if events_dir.exists():
            for f in events_dir.glob("*.md"):
                if "heartbeat" in f.name or "todo" in f.name or "pending" in f.name:
                    content = f.read_text()
                    import re
                    unchecked = re.findall(r"- \[ \]", content)
                    backlog += len(unchecked)
    except:
        pass
    
    # 也检查improvements目录
    try:
        if IMPROVEMENTS_DIR.exists():
            backlog += len(list(IMPROVEMENTS_DIR.glob("*.md")))
    except:
        pass
    
    error = backlog - TARGET["task_backlog"]  # 积压多了=正误差
    return backlog, error


def measure_idle_time():
    """测量空闲时间"""
    try:
        # 读state.json里的last_heartbeat
        state_file = MEMORY / "state.json"
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
            
            last_ts = state.get("last_heartbeat")
            if last_ts:
                from datetime import datetime as dt
                last = dt.fromisoformat(last_ts)
                now = dt.now()
                idle_minutes = int((now - last).total_seconds() / 60)
                error = idle_minutes - TARGET["idle_minutes_max"]
                return idle_minutes, error
    except:
        pass
    
    # 降级：从cron运行记录推断
    try:
        import subprocess
        result = subprocess.run(
            ["openclaw", "tasks", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            tasks = data.get("tasks", [])
            if tasks:
                # 找最近任务的时间戳
                import re
                latest = max(tasks, key=lambda t: t.get("updatedAt", 0))
                last_ts_ms = latest.get("updatedAt", 0)
                if last_ts_ms:
                    from datetime import datetime as dt
                    last = dt.fromtimestamp(last_ts_ms / 1000)
                    now = dt.now()
                    idle = int((now - last).total_seconds() / 60)
                    return idle, idle - TARGET["idle_minutes_max"]
    except:
        pass
    
    return 999, 999 - TARGET["idle_minutes_max"]


def compute_error_magnitude(errors):
    """计算误差向量模长"""
    squared = sum(e ** 2 for e in errors.values())
    return squared ** 0.5


def classify_error_level(magnitude):
    """分类误差等级"""
    if magnitude < ERROR_LEVEL_VERY_SMALL:
        return "极小", "L1", "静默"
    elif magnitude < ERROR_LEVEL_SMALL:
        return "小", "L2", "低功耗整理"
    elif magnitude < ERROR_LEVEL_MEDIUM:
        return "中", "L3", "常规校正"
    else:
        return "大", "L4", "强干预"


def check_oscillation(history, window=3):
    """检测是否在振荡（误差连续不收敛）"""
    if len(history) < window:
        return False, 0
    
    recent = history[-window:]
    signs = [1 if e > 0 else -1 for e in recent]
    # 振荡 = 正负交替
    oscillating = all(signs[i] != signs[i+1] for i in range(len(signs)-1))
    if oscillating:
        return True, "振荡"
    
    # 检测单调变化（可能发散）
    if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
        return True, "发散"
    
    return False, "收敛"


def decide_action(level_name, oscillating, error_vector):
    """根据误差等级和稳定性决定行动"""
    if level_name == "极小":
        return "静默（系统稳定）"
    
    actions = []
    
    if oscillating:
        actions.append("⚠️ 振荡检测：切换策略，增加阻尼")
    
    if level_name in ["大", "中"]:
        # 根据最大的误差分量决定行动
        max_component = max(error_vector, key=lambda k: abs(error_vector[k]))
        actions.append(f"优先处理: {max_component}")
    
    if error_vector.get("consecutive_errors", 0) > 3:
        actions.append("连续错误多：检查工具链路")
    
    if error_vector.get("task_backlog", 0) > 5:
        actions.append("任务积压多：执行清理")
    
    if error_vector.get("memory_order", 0) < 0.5:
        actions.append("记忆有序度低：整理信念库")
    
    if not actions:
        actions.append("轻微偏差：观察")
    
    return " | ".join(actions)


def main():
    print("=" * 50)
    print(f"Erbing 心跳测量 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 1. 测量5个维度
    memory_order, e1 = measure_memory_order()
    tool_response, e2 = measure_tool_response_time()
    consecutive_err, e3 = measure_consecutive_errors()
    task_backlog, e4 = measure_task_backlog()
    idle_minutes, e5 = measure_idle_time()
    
    error_vector = {
        "memory_order": e1,
        "tool_response": e2,
        "consecutive_errors": e3,
        "task_backlog": e4,
        "idle_time": e5,
    }
    
    magnitude = compute_error_magnitude(error_vector)
    level_name, level_code, default_action = classify_error_level(magnitude)
    
    # 2. 读取历史误差（用于振荡检测）
    history_file = HEARTBEAT_LOG_DIR / "heartbeat_error_history.json"
    history = []
    if history_file.exists():
        try:
            with open(history_file) as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(magnitude)
    history = history[-5:]  # 保留最近5次
    
    oscillating, oscillation_type = check_oscillation(history)
    
    # 3. 决定行动
    action = decide_action(level_name, oscillating, error_vector)
    
    # 4. 输出结果
    print(f"\n📊 5维误差向量:")
    print(f"  记忆有序度: {memory_order:.2f} (目标≥{TARGET['memory_order']}) → 误差: {e1:+.2f}")
    print(f"  工具响应:   {tool_response:.1f}s (目标<{TARGET['tool_response_time']}s) → 误差: {e2:+.2f}")
    print(f"  连续错误:   {consecutive_err} (目标={TARGET['consecutive_errors']}) → 误差: {e3:+.2f}")
    print(f"  任务积压:   {task_backlog} (目标≤{TARGET['task_backlog']}) → 误差: {e4:+.2f}")
    print(f"  空闲时间:   {idle_minutes}min (目标≤{TARGET['idle_minutes_max']}min) → 误差: {e5:+.2f}")
    
    print(f"\n🎯 误差模长: {magnitude:.3f}  等级: [{level_code}] {level_name}")
    print(f"📈 稳定性: {oscillation_type}")
    if oscillating:
        print(f"⚠️  {oscillation_type}，需要切换策略")
    
    print(f"\n🔧 推荐行动: {action}")
    
    # 5. 更新历史
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    # 6. 更新状态文件
    state = {
        "last_heartbeat": datetime.now().isoformat(),
        "error_vector": error_vector,
        "error_magnitude": magnitude,
        "error_level": level_name,
        "error_history": history,
        "oscillating": oscillating,
        "oscillation_type": oscillation_type,
        "action": action,
    }
    
    os.makedirs(MEMORY / "self", exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    # 7. 写日志
    log_file = HEARTBEAT_LOG_DIR / f"heartbeat-{datetime.now().strftime('%Y-%m-%d')}.md"
    log_entry = f"""## 心跳 {datetime.now().strftime('%H:%M')}

| 指标 | 实测 | 目标 | 误差 |
|------|------|------|------|
| 记忆有序度 | {memory_order:.2f} | ≥{TARGET['memory_order']} | {e1:+.2f} |
| 工具响应(s) | {tool_response:.1f} | <{TARGET['tool_response_time']} | {e2:+.2f} |
| 连续错误 | {consecutive_err} | {TARGET['consecutive_errors']} | {e3:+.2f} |
| 任务积压 | {task_backlog} | ≤{TARGET['task_backlog']} | {e4:+.2f} |
| 空闲(min) | {idle_minutes} | ≤{TARGET['idle_minutes_max']} | {e5:+.2f} |

- **误差模长**: {magnitude:.3f} [{level_code}] {level_name}
- **稳定性**: {oscillation_type}
- **行动**: {action}

"""
    
    # 追加到日志
    if log_file.exists():
        existing = log_file.read_text()
        # 找到最后一个 ## 的位置，在那之后插入
        last_header = existing.rfind("## 心跳")
        if last_header != -1:
            existing = existing[:last_header]
        log_file.write_text(existing + log_entry)
    else:
        log_file.write_text(f"# 心跳日志 {datetime.now().strftime('%Y-%m-%d')}\n\n" + log_entry)
    
    print(f"\n✅ 状态已更新: {STATE_FILE}")
    print(f"✅ 日志已写入: {log_file}")
    
    # 8. 返回退出码（供cron判断）
    if oscillating and oscillation_type == "发散":
        print("\n🚨 警告：系统疑似发散，建议人工检查")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())