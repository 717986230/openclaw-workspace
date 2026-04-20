"""
核心记忆层 - Core Memory Layer
始终保持在上下文中的关键记忆
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import json


class CoreMemoryEntry(BaseModel):
    """核心记忆条目"""
    id: str
    content: str
    category: str = Field(default="identity")
    importance: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_prompt_text(self) -> str:
        """转换为提示文本"""
        return f"[{self.category}] {self.content}"
    
    def estimate_tokens(self) -> int:
        """估算令牌数 (粗略估计：每4字符约1令牌)"""
        return len(self.content) // 4 + 1


class CoreMemory:
    """
    核心记忆管理器
    
    特点：
    - 始终保持在上下文窗口中
    - 存储代理身份、关键偏好、重要规则
    - 大小有限，需要精心选择
    """
    
    def __init__(self, max_tokens: int = 512):
        """
        初始化核心记忆
        
        Args:
            max_tokens: 最大令牌数限制
        """
        self.max_tokens = max_tokens
        self.entries: Dict[str, CoreMemoryEntry] = {}
        self._token_count = 0
        
    def add(
        self,
        id: str,
        content: str,
        category: str = "identity",
        importance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加核心记忆条目
        
        Args:
            id: 唯一标识符
            content: 记忆内容
            category: 类别 (identity, preference, rule, fact)
            importance: 重要性 (0-1)
            metadata: 额外元数据
            
        Returns:
            是否成功添加（可能因令牌限制失败）
        """
        entry = CoreMemoryEntry(
            id=id,
            content=content,
            category=category,
            importance=importance,
            metadata=metadata or {}
        )
        
        # 检查令牌限制
        new_tokens = entry.estimate_tokens()
        if self._token_count + new_tokens > self.max_tokens:
            # 尝试腾出空间
            if not self._make_space(new_tokens):
                return False
        
        self.entries[id] = entry
        self._token_count += new_tokens
        return True
    
    def get(self, id: str) -> Optional[CoreMemoryEntry]:
        """获取指定条目"""
        return self.entries.get(id)
    
    def update(self, id: str, content: str) -> bool:
        """更新条目内容"""
        if id not in self.entries:
            return False
        
        old_entry = self.entries[id]
        old_tokens = old_entry.estimate_tokens()
        new_entry = CoreMemoryEntry(
            id=id,
            content=content,
            category=old_entry.category,
            importance=old_entry.importance,
            created_at=old_entry.created_at,
            metadata=old_entry.metadata
        )
        new_tokens = new_entry.estimate_tokens()
        
        # 检查是否有足够空间
        if self._token_count - old_tokens + new_tokens > self.max_tokens:
            return False
        
        self.entries[id] = new_entry
        self._token_count = self._token_count - old_tokens + new_tokens
        return True
    
    def remove(self, id: str) -> bool:
        """移除条目"""
        if id not in self.entries:
            return False
        
        entry = self.entries.pop(id)
        self._token_count -= entry.estimate_tokens()
        return True
    
    def _make_space(self, needed_tokens: int) -> bool:
        """
        通过移除低优先级条目腾出空间
        
        Args:
            needed_tokens: 需要的令牌数
            
        Returns:
            是否成功腾出空间
        """
        # 按重要性排序，移除最低重要性的
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda x: x.importance
        )
        
        freed = 0
        to_remove = []
        
        for entry in sorted_entries:
            if freed >= needed_tokens:
                break
            to_remove.append(entry.id)
            freed += entry.estimate_tokens()
        
        # 不移除所有条目
        if len(to_remove) >= len(self.entries):
            return False
        
        for id in to_remove:
            self.remove(id)
        
        return freed >= needed_tokens
    
    def get_all(self) -> List[CoreMemoryEntry]:
        """获取所有条目"""
        return list(self.entries.values())
    
    def get_by_category(self, category: str) -> List[CoreMemoryEntry]:
        """按类别获取条目"""
        return [
            entry for entry in self.entries.values()
            if entry.category == category
        ]
    
    def to_prompt(self) -> str:
        """转换为系统提示文本"""
        if not self.entries:
            return ""
        
        lines = ["# 核心记忆\n"]
        
        # 按类别组织
        categories = {}
        for entry in self.entries.values():
            if entry.category not in categories:
                categories[entry.category] = []
            categories[entry.category].append(entry)
        
        for category, entries in categories.items():
            lines.append(f"## {category.upper()}")
            for entry in entries:
                lines.append(f"- {entry.content}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "max_tokens": self.max_tokens,
            "current_tokens": self._token_count,
            "entries": {
                id: entry.model_dump()
                for id, entry in self.entries.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoreMemory":
        """从字典反序列化"""
        core = cls(max_tokens=data["max_tokens"])
        for id, entry_data in data.get("entries", {}).items():
            entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
            entry_data["updated_at"] = datetime.fromisoformat(entry_data["updated_at"])
            entry = CoreMemoryEntry(**entry_data)
            core.entries[id] = entry
            core._token_count += entry.estimate_tokens()
        return core
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        categories = {}
        for entry in self.entries.values():
            categories[entry.category] = categories.get(entry.category, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "total_tokens": self._token_count,
            "max_tokens": self.max_tokens,
            "utilization": self._token_count / self.max_tokens,
            "by_category": categories
        }
