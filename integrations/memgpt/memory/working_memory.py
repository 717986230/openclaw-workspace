"""
工作记忆层 - Working Memory Layer
当前会话相关的动态记忆
"""

from typing import Optional, Dict, Any, List, Deque
from datetime import datetime
from collections import deque
from pydantic import BaseModel, Field
import hashlib
import json


class WorkingMemoryEntry(BaseModel):
    """工作记忆条目"""
    id: str
    content: str
    session_id: str
    message_type: str = Field(default="user")  # user, assistant, system
    importance: float = Field(default=0.5)
    created_at: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0)
    last_accessed: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def estimate_tokens(self) -> int:
        """估算令牌数"""
        return len(self.content) // 4 + 1
    
    def access(self):
        """标记访问"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class WorkingMemory:
    """
    工作记忆管理器
    
    特点：
    - 会话级别的记忆存储
    - 动态加载和卸载
    - 支持优先级淘汰
    - 访问频率跟踪
    """
    
    def __init__(
        self,
        max_tokens: int = 2048,
        max_entries: int = 100,
        session_id: Optional[str] = None
    ):
        """
        初始化工作记忆
        
        Args:
            max_tokens: 最大令牌数
            max_entries: 最大条目数
            session_id: 会话ID
        """
        self.max_tokens = max_tokens
        self.max_entries = max_entries
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.entries: Deque[WorkingMemoryEntry] = deque(maxlen=max_entries)
        self._token_count = 0
        self._id_counter = 0
        
    def _generate_id(self) -> str:
        """生成唯一ID"""
        self._id_counter += 1
        return f"work_{self.session_id}_{self._id_counter}"
    
    def add(
        self,
        content: str,
        message_type: str = "user",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkingMemoryEntry:
        """
        添加工作记忆条目
        
        Args:
            content: 记忆内容
            message_type: 消息类型
            importance: 重要性
            metadata: 元数据
            
        Returns:
            创建的条目
        """
        entry = WorkingMemoryEntry(
            id=self._generate_id(),
            content=content,
            session_id=self.session_id,
            message_type=message_type,
            importance=importance,
            metadata=metadata or {}
        )
        
        new_tokens = entry.estimate_tokens()
        
        # 如果超出限制，移除旧条目
        while (
            self._token_count + new_tokens > self.max_tokens 
            and len(self.entries) > 0
        ):
            removed = self.entries.popleft()
            self._token_count -= removed.estimate_tokens()
        
        self.entries.append(entry)
        self._token_count += new_tokens
        return entry
    
    def get(self, id: str) -> Optional[WorkingMemoryEntry]:
        """获取并标记访问"""
        for entry in self.entries:
            if entry.id == id:
                entry.access()
                return entry
        return None
    
    def get_recent(self, n: int = 10) -> List[WorkingMemoryEntry]:
        """获取最近的n个条目"""
        return list(self.entries)[-n:]
    
    def get_by_type(self, message_type: str) -> List[WorkingMemoryEntry]:
        """按类型获取条目"""
        return [
            entry for entry in self.entries
            if entry.message_type == message_type
        ]
    
    def search(self, query: str) -> List[WorkingMemoryEntry]:
        """简单文本搜索"""
        query_lower = query.lower()
        results = []
        for entry in self.entries:
            if query_lower in entry.content.lower():
                entry.access()
                results.append(entry)
        return results
    
    def compress(self, keep_recent: int = 20) -> List[WorkingMemoryEntry]:
        """
        压缩工作记忆，保留重要和最近的条目
        
        Args:
            keep_recent: 保持最近的条目数
            
        Returns:
            被移除的条目（可用于归档）
        """
        if len(self.entries) <= keep_recent:
            return []
        
        # 计算保留条目
        recent_entries = list(self.entries)[-keep_recent:]
        recent_ids = {e.id for e in recent_entries}
        
        # 计算要移除的条目（按重要性排序）
        old_entries = [
            e for e in self.entries if e.id not in recent_ids
        ]
        old_entries.sort(key=lambda x: (x.importance, x.access_count))
        
        # 移除低重要性条目
        to_remove = old_entries[:len(old_entries) // 2]
        remove_ids = {e.id for e in to_remove}
        
        # 更新队列
        new_entries = deque(maxlen=self.max_entries)
        removed = []
        
        for entry in self.entries:
            if entry.id in remove_ids:
                removed.append(entry)
                self._token_count -= entry.estimate_tokens()
            else:
                new_entries.append(entry)
        
        self.entries = new_entries
        return removed
    
    def to_conversation(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        转换为对话格式
        
        Returns:
            [{"role": "user/assistant", "content": "..."}]
        """
        messages = []
        for entry in self.entries:
            if entry.message_type == "system" and not include_system:
                continue
            messages.append({
                "role": entry.message_type,
                "content": entry.content
            })
        return messages
    
    def get_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        user_messages = len(self.get_by_type("user"))
        assistant_messages = len(self.get_by_type("assistant"))
        system_messages = len(self.get_by_type("system"))
        
        total_access = sum(e.access_count for e in self.entries)
        
        return {
            "session_id": self.session_id,
            "total_messages": len(self.entries),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": system_messages,
            "total_tokens": self._token_count,
            "utilization": self._token_count / self.max_tokens,
            "total_access_count": total_access
        }
    
    def clear(self) -> List[WorkingMemoryEntry]:
        """
        清空工作记忆
        
        Returns:
            被清空的条目（可用于归档）
        """
        removed = list(self.entries)
        self.entries.clear()
        self._token_count = 0
        return removed
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "max_tokens": self.max_tokens,
            "max_entries": self.max_entries,
            "session_id": self.session_id,
            "current_tokens": self._token_count,
            "entries": [e.model_dump() for e in self.entries]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemory":
        """反序列化"""
        working = cls(
            max_tokens=data["max_tokens"],
            max_entries=data["max_entries"],
            session_id=data["session_id"]
        )
        for entry_data in data.get("entries", []):
            entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
            entry_data["last_accessed"] = datetime.fromisoformat(entry_data["last_accessed"])
            entry = WorkingMemoryEntry(**entry_data)
            working.entries.append(entry)
            working._token_count += entry.estimate_tokens()
        return working
