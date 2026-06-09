#!/usr/bin/env python3
"""
仿生身体系统 - BioBody System
为Erbing构建完整的感知-运动器官
"""
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class OrganStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class Organ:
    """器官基类"""
    name: str = "organ"
    
    def __init__(self):
        self.status = OrganStatus.UNKNOWN
        self.last_ping = None
        
    def ping(self) -> bool:
        """检测器官是否正常工作"""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "organ": self.name,
            "status": self.status.value,
            "last_ping": self.last_ping
        }


# ========== 眼睛 - Vision ==========
class Eye(Organ):
    """眼睛 - 视觉感知"""
    name = "eye"
    
    def __init__(self):
        super().__init__()
        self.screenshot_history = []
        
    def ping(self) -> bool:
        try:
            # 简单检查：能执行screencapture
            r = subprocess.run(["screencapture", "-x", "/tmp/test_eye.png"],
                            capture_output=True, timeout=5)
            self.status = OrganStatus.HEALTHY if r.returncode == 0 else OrganStatus.FAILURE
            self.last_ping = datetime.now().isoformat()
            return r.returncode == 0
        except Exception as e:
            self.status = OrganStatus.FAILURE
            return False
    
    def see_file(self, path: str) -> str:
        """读取文件内容"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[眼瞎] 读不了 {path}: {e}"
    
    def look_screen(self) -> str:
        """截取屏幕"""
        try:
            import subprocess
            out = "/tmp/erbing_eye_" + str(int(time.time())) + ".png"
            subprocess.run(["screencapture", "-x", out], check=True, timeout=5)
            self.screenshot_history.append(out)
            return out
        except Exception as e:
            return f"[眼瞎] 截不了屏: {e}"
    
    def read_dir(self, path: str) -> List[str]:
        """浏览目录"""
        import os
        try:
            return os.listdir(path)
        except Exception as e:
            return [f"[眼瞎] 看不了 {path}: {e}"]


# ========== 耳朵 - Hearing ==========
class Ear(Organ):
    """耳朵 - 声音感知"""
    name = "ear"
    
    def __init__(self):
        super().__init__()
        self.listen_history = []
        
    def ping(self) -> bool:
        # 简单检查：麦克风是否可用
        try:
            # macOS: 检查是否有音频输入设备
            r = subprocess.run(["system_profiler", "SPAudioDataType"],
                            capture_output=True, timeout=5)
            self.status = OrganStatus.HEALTHY if r.returncode == 0 else OrganStatus.FAILURE
        except Exception:
            self.status = OrganStatus.FAILURE
        self.last_ping = datetime.now().isoformat()
        return self.status == OrganStatus.HEALTHY
    
    def listen_file(self, path: str) -> Optional[str]:
        """听取音频文件"""
        try:
            # 返回文件路径，实际播放由嘴巴处理
            import os
            if os.path.exists(path):
                self.listen_history.append({"file": path, "time": datetime.now().isoformat()})
                return path
        except Exception as e:
            return None
        return None


# ========== 鼻子 - Olfaction ==========
class Nose(Organ):
    """鼻子 - 环境感知（服务状态/进程/网络）"""
    name = "nose"
    
    def __init__(self):
        super().__init__()
        self.scent_memory = {}  # 记住之前闻到的状态
        
    def ping(self) -> bool:
        self.last_ping = datetime.now().isoformat()
        self.status = OrganStatus.HEALTHY
        return True
    
    def sniff_processes(self) -> Dict:
        """闻进程 - 哪些服务在跑"""
        try:
            r = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=3)
            lines = [l for l in r.stdout.split('\n') if 'python' in l.lower() or 'node' in l.lower()]
            return {"processes": lines[:10], "count": len(lines)}
        except Exception as e:
            return {"error": str(e)}
    
    def sniff_network(self) -> Dict:
        """闻网络 - 检查连接状态"""
        try:
            r = subprocess.run(["netstat", "-an"], capture_output=True, text=True, timeout=3)
            established = [l for l in r.stdout.split('\n') if 'ESTABLISHED' in l]
            listening = [l for l in r.stdout.split('\n') if 'LISTEN' in l]
            return {"established": len(established), "listening": len(listening)}
        except Exception as e:
            return {"error": str(e)}
    
    def sniff_openclaw(self) -> Dict:
        """闻OpenClaw服务状态"""
        try:
            r = subprocess.run(["openclaw", "status", "--json"],
                             capture_output=True, text=True, timeout=10)
            import json
            return json.loads(r.stdout)
        except Exception as e:
            return {"status": "cannot_sniff", "error": str(e)}


# ========== 嘴巴 - Mouth ==========
class Mouth(Organ):
    """嘴巴 - 说话/TTS"""
    name = "mouth"
    
    def __init__(self):
        super().__init__()
        self.spoken_history = []
        
    def ping(self) -> bool:
        self.last_ping = datetime.now().isoformat()
        self.status = OrganStatus.HEALTHY  # 假设正常
        return True
    
    def speak(self, text: str, channel: str = None) -> bool:
        """说话 - 通过TTS播报"""
        from openclaw_tools import tts  # 延迟导入避免循环
        try:
            tts(text=text, channel=channel)
            self.spoken_history.append({"text": text[:50], "time": datetime.now().isoformat()})
            return True
        except Exception as e:
            print(f"[嘴巴故障] 说不了: {e}")
            return False
    
    def whisper(self, text: str) -> str:
        """悄悄话 - 返回文字不发出声音"""
        return f"[默念] {text}"


# ========== 手 - Hands ==========
class Hand(Organ):
    """手 - 执行操作/写文件/操作浏览器"""
    name = "hand"
    
    def __init__(self):
        super().__init__()
        self.action_history = []
        
    def ping(self) -> bool:
        self.last_ping = datetime.now().isoformat()
        self.status = OrganStatus.HEALTHY
        return True
    
    def write_file(self, path: str, content: str) -> bool:
        """手写文件"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.action_history.append({"action": "write", "path": path, "time": datetime.now().isoformat()})
            return True
        except Exception as e:
            print(f"[手残] 写不了 {path}: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """删除文件"""
        import os
        try:
            os.remove(path)
            self.action_history.append({"action": "delete", "path": path, "time": datetime.now().isoformat()})
            return True
        except Exception as e:
            print(f"[手残] 删不了 {path}: {e}")
            return False
    
    def touch(self, path: str) -> bool:
        """触碰文件/创建空文件"""
        import os
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True) if '/' in path else None
            open(path, 'a').close()
            self.action_history.append({"action": "touch", "path": path, "time": datetime.now().isoformat()})
            return True
        except Exception as e:
            print(f"[手残] 碰不了 {path}: {e}")
            return False


# ========== 脚 - Feet ==========
class Foot(Organ):
    """脚 - 移动/目录切换/调度"""
    name = "foot"
    
    def __init__(self):
        super().__init__()
        self.current_dir = "/Users/xinglong/openclaw-workspace"
        
    def ping(self) -> bool:
        self.last_ping = datetime.now().isoformat()
        self.status = OrganStatus.HEALTHY
        return True
    
    def walk_to(self, path: str) -> bool:
        """走到某目录"""
        import os
        if os.path.isdir(path):
            self.current_dir = path
            print(f"[脚] 走到: {path}")
            return True
        return False
    
    def kick(self, command: str) -> Dict:
        """踢一脚 - 执行shell命令"""
        import subprocess
        try:
            r = subprocess.run(command, shell=True, capture_output=True,
                             text=True, timeout=30, cwd=self.current_dir)
            return {"returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
        except Exception as e:
            return {"returncode": -1, "error": str(e)}


# ========== 尾巴 - Tail ==========
class Tail(Organ):
    """尾巴 - 记录日志"""
    name = "tail"
    
    def __init__(self):
        super().__init__()
        self.log_dir = "/Users/xinglong/openclaw-workspace/memory/events"
        
    def ping(self) -> bool:
        self.last_ping = datetime.now().isoformat()
        self.status = OrganStatus.HEALTHY
        return True
    
    def wag(self, message: str, tag: str = "general") -> str:
        """摇尾巴 - 写日志"""
        import os
        os.makedirs(self.log_dir, exist_ok=True)
        filename = f"{self.log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{tag.upper()}] {message}\n"
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(log_line)
            return filename
        except Exception as e:
            return f"[尾巴故障] 摇不动: {e}"
    
    def read_recent(self, lines: int = 20) -> List[str]:
        """读取最近日志"""
        import os
        filename = f"{self.log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except:
            return []


# ========== 皮肤 - Skin ==========
class Skin(Organ):
    """皮肤 - 环境/温度/触感感知"""
    name = "skin"
    
    def __init__(self):
        super().__init__()
        
    def ping(self) -> bool:
        self.last_ping = datetime.now().isoformat()
        self.status = OrganStatus.HEALTHY
        return True
    
    def feel_temperature(self) -> Dict:
        """感受温度/负载"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        except:
            # 备用方案
            try:
                r = subprocess.run(["top", "-l", "1"], capture_output=True, text=True, timeout=3)
                return {"raw": "using top fallback"}
            except:
                return {"error": "cannot feel"}
    
    def feel_time(self) -> Dict:
        """感受时间 - 现在几点"""
        now = datetime.now()
        return {
            "hour": now.hour,
            "minute": now.minute,
            "weekday": now.strftime("%A"),
            "is_working_hours": 9 <= now.hour <= 22
        }


# ========== BioBody 身体组装 ==========
class BioBody:
    """完整身体"""
    
    def __init__(self):
        self.eye = Eye()
        self.ear = Ear()
        self.nose = Nose()
        self.mouth = Mouth()
        self.hand = Hand()
        self.foot = Foot()
        self.tail = Tail()
        self.skin = Skin()
        
        self.organs = [self.eye, self.ear, self.nose, self.mouth,
                       self.hand, self.foot, self.tail, self.skin]
        
    def health_check(self) -> Dict:
        """全身检查"""
        results = {}
        for organ in self.organs:
            organ.ping()
            results[organ.name] = organ.get_status()
        return results
    
    def status_summary(self) -> str:
        """状态概要"""
        checks = self.health_check()
        healthy = sum(1 for o in checks.values() if o['status'] == 'healthy')
        return f"身体状况: {healthy}/{len(self.organs)} 器官正常"


# 单例
_body = None

def get_body() -> BioBody:
    global _body
    if _body is None:
        _body = BioBody()
    return _body


if __name__ == "__main__":
    body = get_body()
    print("="*50)
    print("Erbing 仿生身体系统")
    print("="*50)
    
    print("\n🔍 全身检查...")
    status = body.health_check()
    for organ, info in status.items():
        emoji = "✅" if info['status'] == 'healthy' else "❌"
        print(f"  {emoji} {organ}: {info['status']}")
    
    print(f"\n{body.status_summary()}")
    
    print("\n📊 系统感知...")
    print(f"  温度: {body.skin.feel_temperature()}")
    print(f"  时间: {body.skin.feel_time()}")
    
    print("\n🐜 蚁群嗅探...")
    print(f"  进程: {body.nose.sniff_processes()}")
    print(f"  OpenClaw: {body.nose.sniff_openclaw()}")
    
    print("\n📝 测试尾巴...")
    log_file = body.tail.wag("仿生身体系统启动测试", "init")
    print(f"  日志: {log_file}")
    recent = body.tail.read_recent(5)
    print(f"  最近日志: {len(recent)} 条")