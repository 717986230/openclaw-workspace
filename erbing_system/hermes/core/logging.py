"""
全栈日志系统（整合 Hermes 全栈日志）
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import uuid


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """日志类别"""
    THINKING = "thinking"
    EXECUTION = "execution"
    MEMORY = "memory"
    EVOLUTION = "evolution"
    SKILL = "skill"
    ERROR = "error"


@dataclass
class LogEntry:
    """日志条目"""
    id: str
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    metadata: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class FullStackLogger:
    """全栈日志器"""

    def __init__(self):
        self.logs: List[LogEntry] = []
        self.session_id: str = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return str(uuid.uuid4())

    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """记录日志"""
        entry = LogEntry(
            id=self._generate_log_id(),
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            metadata=metadata or {},
            context=context,
        )
        self.logs.append(entry)

    def _generate_log_id(self) -> str:
        """生成日志 ID"""
        return str(uuid.uuid4())

    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """获取日志"""
        filtered_logs = self.logs

        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]

        if category:
            filtered_logs = [log for log in filtered_logs if log.category == category]

        return filtered_logs[-limit:]

    def get_thinking_logs(self) -> List[LogEntry]:
        """获取思考日志"""
        return self.get_logs(category=LogCategory.THINKING)

    def get_execution_logs(self) -> List[LogEntry]:
        """获取执行日志"""
        return self.get_logs(category=LogCategory.EXECUTION)

    def get_memory_logs(self) -> List[LogEntry]:
        """获取记忆日志"""
        return self.get_logs(category=LogCategory.MEMORY)

    def get_evolution_logs(self) -> List[LogEntry]:
        """获取进化日志"""
        return self.get_logs(category=LogCategory.EVOLUTION)

    def get_skill_logs(self) -> List[LogEntry]:
        """获取技能日志"""
        return self.get_logs(category=LogCategory.SKILL)

    def get_error_logs(self) -> List[LogEntry]:
        """获取错误日志"""
        return self.get_logs(level=LogLevel.ERROR)

    def get_summary(self) -> Dict[str, Any]:
        """获取日志摘要"""
        return {
            "session_id": self.session_id,
            "total_logs": len(self.logs),
            "by_level": {
                level.value: len([log for log in self.logs if log.level == level])
                for level in LogLevel
            },
            "by_category": {
                category.value: len([log for log in self.logs if log.category == category])
                for category in LogCategory
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level.value,
                    "category": log.category.value,
                    "message": log.message,
                    "metadata": log.metadata,
                    "context": log.context,
                }
                for log in self.logs
            ],
            "summary": self.get_summary(),
        }
