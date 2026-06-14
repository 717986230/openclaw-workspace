#!/usr/bin/env python3
"""
Erbing 心跳控制脚本 — 纯脚本驱动，无LLM
运行测量 → 根据误差等级行动 → 更新状态
只在真正需要时才触发 AI 通知
"""
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

WORKSPACE = Path("/Users/xinglong/openclaw-workspace")
MEMORY = WORKSPACE / "memory"
STATE_FILE = MEMORY / "self" / "erbing_state.json"
EVENTS_DIR = MEMORY / "events"
BELIEFS_FILE = MEMORY / "beliefs.json"
STATE_JSON = MEMORY / "state.json"
HEARTBEAT_ERROR_HISTORY = EVENTS_DIR / "heartbeat_error_history.json"
NOTIFY_FLAG = MEMORY / "self" / "heartbeat_notify_needed.json"

# 目标状态
TARGET = {
    "memory_order": 0.9,
    "tool_response_time": 5.0,
    "consecutive_errors": 0,
    "task_backlog": 3,
    "idle_minutes_max": 120,
}

ERROR_LEVEL_VERY_SMALL = 0.1
ERROR_LEVEL_SMALL = 0.3
ERROR_LEVEL_MEDIUM = 0.6


def log(tag: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{tag}] {msg}")


# ========== 测量函数 ==========

def measure_all() -> Dict[str, float]:
    """测量5维误差向量"""
    memory_order = measure_memory_order()
    tool_response = measure_tool_response_time()
    consecutive_err = measure_consecutive_errors()
    task_backlog = measure_task_backlog()
    idle_minutes = measure_idle_time()

    errors = {
        "memory_order": TARGET["memory_order"] - memory_order,
        "tool_response": tool_response - TARGET["tool_response_time"],
        "consecutive_errors": consecutive_err - TARGET["consecutive_errors"],
        "task_backlog": task_backlog - TARGET["task_backlog"],
        "idle_time": max(0, idle_minutes - TARGET["idle_minutes_max"]),
    }

    return {
        "memory_order": memory_order,
        "tool_response": tool_response,
        "consecutive_errors": consecutive_err,
        "task_backlog": task_backlog,
        "idle_minutes": idle_minutes,
        "errors": errors,
    }


def measure_memory_order() -> float:
    try:
        if not BELIEFS_FILE.exists():
            return 0.5
        with open(BELIEFS_FILE) as f:
            beliefs = json.load(f)
        if not beliefs:
            return 0.4
        scored = sum(1 for v in beliefs.values() if "success_rate" in v)
        return 0.3 + 0.7 * (scored / max(len(beliefs), 1))
    except:
        return 0.5


def measure_tool_response_time() -> float:
    try:
        if STATE_JSON.exists():
            with open(STATE_JSON) as f:
                state = json.load(f)
            durations = state.get("recent_durations", [])
            if durations:
                return sum(durations[-10:]) / min(len(durations), 10) / 1000
    except:
        pass
    return 5.0


def measure_consecutive_errors() -> int:
    """从cron jobs状态获取consecutiveErrors"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            jobs = data.get("jobs", [])
            # 只看erbing相关的任务
            relevant = [j for j in jobs if "erbing" in j.get("name", "").lower() or "heartbeat" in j.get("name", "").lower()]
            if relevant:
                return max(j.get("state", {}).get("consecutiveErrors", 0) for j in relevant)
            return 0
    except:
        pass
    return 0


def measure_task_backlog() -> int:
    """数 events/ 里未完成的待办"""
    backlog = 0
    try:
        for f in EVENTS_DIR.glob("*.md"):
            if f.is_file():
                content = f.read_text()
                import re
                unchecked = re.findall(r"- \[ \]", content)
                backlog += len(unchecked)
    except:
        pass
    return backlog


def measure_idle_time() -> int:
    """从 state.json 读取上次心跳时间"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
            last_ts = state.get("last_heartbeat")
            if last_ts:
                last = datetime.fromisoformat(last_ts)
                return int((datetime.now() - last).total_seconds() / 60)
    except:
        pass
    return 999


def compute_magnitude(errors: Dict[str, float]) -> float:
    return sum(e ** 2 for e in errors.values()) ** 0.5


def classify_level(magnitude: float) -> Tuple[str, str, str]:
    if magnitude < ERROR_LEVEL_VERY_SMALL:
        return "极小", "L1", "静默"
    elif magnitude < ERROR_LEVEL_SMALL:
        return "小", "L2", "低功耗整理"
    elif magnitude < ERROR_LEVEL_MEDIUM:
        return "中", "L3", "常规校正"
    else:
        return "大", "L4", "强干预"


def check_stability(history: list) -> Tuple[bool, str]:
    if len(history) < 3:
        return False, "新数据"
    recent = history[-3:]
    # 振荡：正负交替
    signs = [1 if e > 0 else -1 for e in recent]
    if all(signs[i] != signs[i+1] for i in range(len(signs)-1)):
        return True, "振荡"
    # 发散：单调增
    if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
        return True, "发散"
    return False, "收敛"


# ========== 行动函数 ==========

def act_l1():
    """静默，什么都不做"""
    log("ACT", "L1静默：系统稳定，不干预")


def act_l2(data: Dict):
    """低功耗整理：写一行记录"""
    log("ACT", "L2：系统轻微偏离，写入观测记录")
    log_heartbeat(data, note="L2轻微偏差观察")


def act_l3(data: Dict) -> bool:
    """常规校正：清理积压"""
    log("ACT", "L3：执行常规校正")
    changes = []

    # 清理已完成的待办
    for f in EVENTS_DIR.glob("heartbeat-*.md"):
        content = f.read_text()
        # 把已完成的项目标记（不删除，只是记录）
        changes.append(f"观测: {f.name}")

    # 整理信念库低质量条目
    if data["errors"]["memory_order"] > 0:
        try:
            if BELIEFS_FILE.exists():
                with open(BELIEFS_FILE) as f:
                    beliefs = json.load(f)
                # 移除count很低且success_rate很低的条目
                cleaned = {k: v for k, v in beliefs.items()
                           if not (v.get("count", 0) < 3 and v.get("success_rate", 1) < 0.3)}
                if len(cleaned) < len(beliefs):
                    with open(BELIEFS_FILE, 'w') as f:
                        json.dump(cleaned, f, ensure_ascii=False, indent=2)
                    changes.append(f"清理信念库: {len(beliefs)} → {len(cleaned)} 条")
        except:
            pass

    # 检查cron失败任务
    ce = data["consecutive_errors"]
    if ce > 0:
        changes.append(f"发现{ce}个连续错误，需要进一步检查")

    log("ACT", f"校正完成: {changes if changes else '无'}")
    log_heartbeat(data, note=f"L3校正: {', '.join(changes) if changes else '无'}")
    return True


def act_l4(data: Dict):
    """强干预 + 标记需要通知主人"""
    log("ACT", "L4：强干预，标记需要通知主人")
    changes = []

    # 尝试修复cron任务
    ce = data["consecutive_errors"]
    if ce > 0:
        changes.append(f"有{ce}个连续错误的cron任务待检查")
        # 写通知标记
        save_notify_flag(data, f"连续错误数={ce}，需要人工检查")

    # 记录所有大误差
    errors = data["errors"]
    big_errors = [k for k, v in errors.items() if abs(v) > 0.5]
    if big_errors:
        changes.append(f"大误差分量: {big_errors}")
        save_notify_flag(data, f"大误差: {big_errors}")

    log("ACT", f"L4行动完成: {changes}")
    log_heartbeat(data, note=f"L4干预: {', '.join(changes)}")


def act_oscillation(data: Dict):
    """振荡时的策略切换"""
    log("ACT", "⚠️ 检测到振荡，执行策略切换")
    # 振荡时不做新行动，只记录
    save_notify_flag(data, "振荡检测：需要检查心跳策略是否有效")
    log_heartbeat(data, note="振荡：策略待检查")


def save_notify_flag(data: Dict, reason: str):
    """保存通知标记，供AI后续处理"""
    os.makedirs(MEMORY / "self", exist_ok=True)
    flag = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "error_magnitude": data.get("error_magnitude", 0),
        "error_level": data.get("error_level", "?"),
        "error_vector": data.get("errors", {}),
        "processed": False,
    }
    with open(NOTIFY_FLAG, 'w') as f:
        json.dump(flag, f, indent=2, ensure_ascii=False)
    log("NOTIFY", f"已标记需要AI关注: {reason}")


def log_heartbeat(data: Dict, note: str = ""):
    """追加心跳日志"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = EVENTS_DIR / f"heartbeat-{today}.md"
    errors = data["errors"]

    entry = f"""## 心跳 {datetime.now().strftime('%H:%M')}

| 指标 | 实测 | 目标 | 误差 |
|------|------|------|------|
| 记忆有序度 | {data['memory_order']:.2f} | ≥{TARGET['memory_order']} | {errors['memory_order']:+.2f} |
| 工具响应(s) | {data['tool_response']:.1f} | <{TARGET['tool_response_time']} | {errors['tool_response']:+.2f} |
| 连续错误 | {data['consecutive_errors']} | {TARGET['consecutive_errors']} | {errors['consecutive_errors']:+.2f} |
| 任务积压 | {data['task_backlog']} | ≤{TARGET['task_backlog']} | {errors['task_backlog']:+.2f} |
| 空闲(min) | {data['idle_minutes']} | ≤{TARGET['idle_minutes_max']} | {errors['idle_time']:+.2f} |

- **误差模长**: {data.get('error_magnitude', 0):.3f} [{data.get('error_level', '?')}]
- **稳定性**: {data.get('stability', '新数据')}
- **备注**: {note}

"""
    if log_file.exists():
        existing = log_file.read_text()
        last_header = existing.rfind("## 心跳")
        if last_header != -1:
            existing = existing[:last_header]
        log_file.write_text(existing + entry)
    else:
        log_file.write_text(f"# 心跳日志 {today}\n\n" + entry)


def update_state(data: Dict):
    """更新状态文件"""
    os.makedirs(MEMORY / "self", exist_ok=True)
    state = {
        "last_heartbeat": datetime.now().isoformat(),
        "memory_order": data["memory_order"],
        "tool_response": data["tool_response"],
        "consecutive_errors": data["consecutive_errors"],
        "task_backlog": data["task_backlog"],
        "idle_minutes": data["idle_minutes"],
        "error_vector": data["errors"],
        "error_magnitude": data["error_magnitude"],
        "error_level": data["error_level"],
        "error_history": data["error_history"],
        "oscillating": data["oscillating"],
        "stability": data["stability"],
        "action_taken": data["action_taken"],
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ========== 主循环 ==========

def main():
    log("HB", "=" * 40)
    log("HB", f"Erbing Heartbeat Start {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("HB", "=" * 40)

    # 1. 测量
    log("MEASURE", "运行5维误差测量...")
    data = measure_all()

    errors = data["errors"]
    data["error_magnitude"] = compute_magnitude(errors)

    # 2. 分类
    level_name, level_code, default_action = classify_level(data["error_magnitude"])
    data["error_level"] = level_name

    log("MEASURE", f"误差模长: {data['error_magnitude']:.3f} [{level_code}] {level_name}")
    log("MEASURE", f"  memory_order: {data['memory_order']:.2f} → 误差 {errors['memory_order']:+.2f}")
    log("MEASURE", f"  tool_response: {data['tool_response']:.1f}s → 误差 {errors['tool_response']:+.2f}")
    log("MEASURE", f"  consecutive_errors: {data['consecutive_errors']} → 误差 {errors['consecutive_errors']:+.2f}")
    log("MEASURE", f"  task_backlog: {data['task_backlog']} → 误差 {errors['task_backlog']:+.2f}")
    log("MEASURE", f"  idle_minutes: {data['idle_minutes']} → 误差 {errors['idle_time']:+.2f}")

    # 3. 稳定性检测
    history = []
    if HEARTBEAT_ERROR_HISTORY.exists():
        try:
            history = json.load(HEARTBEAT_ERROR_HISTORY)
        except:
            history = []

    history.append(data["error_magnitude"])
    history = history[-5:]
    with open(HEARTBEAT_ERROR_HISTORY, 'w') as f:
        json.dump(history, f)
    data["error_history"] = history

    oscillating, stability = check_stability(history)
    data["oscillating"] = oscillating
    data["stability"] = stability

    if oscillating:
        log("STABILITY", f"⚠️ {stability}，需要策略切换")
    else:
        log("STABILITY", f"✅ {stability}")

    # 4. 行动
    action_taken = ""
    if oscillating:
        act_oscillation(data)
        action_taken = f"振荡处理({stability})"
    elif level_code == "L1":
        act_l1()
        action_taken = "静默"
    elif level_code == "L2":
        act_l2(data)
        action_taken = "低功耗整理"
    elif level_code == "L3":
        act_l3(data)
        action_taken = "常规校正"
    else:  # L4
        act_l4(data)
        action_taken = "强干预+通知标记"

    data["action_taken"] = action_taken

    # 5. 更新状态
    update_state(data)
    log("STATE", f"状态已更新: {STATE_FILE}")

    log("HB", f"心跳完成。行动: {action_taken}")
    print()

    # 6. 返回退出码
    if data["error_level"] == "大":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())