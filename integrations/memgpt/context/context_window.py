"""
上下文窗口 - Context Window
管理上下文窗口的内容和令牌预算
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import tiktoken


@dataclass
class ContextBlock:
    """上下文块"""
    role: str  # system, user, assistant
    content: str
    token_count: int
    priority: int = 1  # 1-3, 越高越重要
    compressible: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextWindow:
    """
    上下文窗口管理器
    
    特点：
    - 精确令牌计数
    - 动态内容管理
    - 支持滑动窗口
    - 令牌预算控制
    """
    
    def __init__(
        self,
        max_tokens: int = 8192,
        encoding_name: str = "cl100k_base",
        reserved_tokens: int = 500
    ):
        """
        初始化上下文窗口
        
        Args:
            max_tokens: 最大令牌数
            encoding_name: 编码名称
            reserved_tokens: 为输出保留的令牌数
        """
        self.max_tokens = max_tokens
        self.reserved_tokens = reserved_tokens
        self.available_tokens = max_tokens - reserved_tokens
        
        # 初始化编码器
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            # 降级到简单估算
            self.encoding = None
        
        self.blocks: List[ContextBlock] = []
        self._current_tokens = 0
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的令牌数
        
        Args:
            text: 输入文本
            
        Returns:
            令牌数
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # 简单估算：中文约2字符/令牌，英文约4字符/令牌
            chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            other_chars = len(text) - chinese_chars
            return chinese_chars // 2 + other_chars // 4 + 1
    
    def add(
        self,
        role: str,
        content: str,
        priority: int = 1,
        compressible: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加内容到上下文窗口
        
        Args:
            role: 角色
            content: 内容
            priority: 优先级 (1-3)
            compressible: 是否可压缩
            metadata: 元数据
            
        Returns:
            是否成功添加
        """
        token_count = self.count_tokens(content)
        
        # 检查是否超出预算
        if token_count > self.available_tokens:
            return False
        
        # 如果当前超出，尝试腾出空间
        while (
            self._current_tokens + token_count > self.available_tokens
            and len(self.blocks) > 0
        ):
            if not self._remove_lowest_priority():
                break
        
        # 再次检查
        if self._current_tokens + token_count > self.available_tokens:
            return False
        
        block = ContextBlock(
            role=role,
            content=content,
            token_count=token_count,
            priority=max(1, min(3, priority)),
            compressible=compressible,
            metadata=metadata or {}
        )
        
        self.blocks.append(block)
        self._current_tokens += token_count
        
        return True
    
    def _remove_lowest_priority(self) -> bool:
        """移除最低优先级的块"""
        if not self.blocks:
            return False
        
        # 找到最低优先级且可移除的块
        for i, block in enumerate(self.blocks):
            if block.compressible and block.priority < 3:
                self._current_tokens -= block.token_count
                self.blocks.pop(i)
                return True
        
        return False
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文内容（对话格式）
        
        Returns:
            [{"role": "...", "content": "..."}, ...]
        """
        return [
            {"role": block.role, "content": block.content}
            for block in self.blocks
        ]
    
    def get_text(self) -> str:
        """获取上下文文本"""
        return "\n".join(
            f"[{block.role}]: {block.content}"
            for block in self.blocks
        )
    
    def get_recent(self, n: int = 5) -> List[ContextBlock]:
        """获取最近的n个块"""
        return self.blocks[-n:]
    
    def clear_except_system(self):
        """清空除系统消息外的所有内容"""
        self.blocks = [
            block for block in self.blocks
            if block.role == "system"
        ]
        self._current_tokens = sum(
            block.token_count for block in self.blocks
        )
    
    def clear(self):
        """清空所有内容"""
        self.blocks.clear()
        self._current_tokens = 0
    
    def get_token_usage(self) -> Dict[str, int]:
        """获取令牌使用情况"""
        return {
            "current": self._current_tokens,
            "available": self.available_tokens,
            "max": self.max_tokens,
            "reserved": self.reserved_tokens,
            "utilization": self._current_tokens / self.available_tokens if self.available_tokens > 0 else 0
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        role_counts = {}
        for block in self.blocks:
            role_counts[block.role] = role_counts.get(block.role, 0) + 1
        
        priority_counts = {}
        for block in self.blocks:
            priority_counts[f"priority_{block.priority}"] = priority_counts.get(f"priority_{block.priority}", 0) + 1
        
        return {
            "total_blocks": len(self.blocks),
            "total_tokens": self._current_tokens,
            "token_usage": self.get_token_usage(),
            "by_role": role_counts,
            "by_priority": priority_counts
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "max_tokens": self.max_tokens,
            "reserved_tokens": self.reserved_tokens,
            "current_tokens": self._current_tokens,
            "blocks": [
                {
                    "role": block.role,
                    "content": block.content,
                    "token_count": block.token_count,
                    "priority": block.priority,
                    "compressible": block.compressible,
                    "timestamp": block.timestamp.isoformat(),
                    "metadata": block.metadata
                }
                for block in self.blocks
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextWindow":
        """反序列化"""
        window = cls(
            max_tokens=data["max_tokens"],
            reserved_tokens=data["reserved_tokens"]
        )
        
        for block_data in data.get("blocks", []):
            block = ContextBlock(
                role=block_data["role"],
                content=block_data["content"],
                token_count=block_data["token_count"],
                priority=block_data["priority"],
                compressible=block_data["compressible"],
                timestamp=datetime.fromisoformat(block_data["timestamp"]),
                metadata=block_data["metadata"]
            )
            window.blocks.append(block)
        
        window._current_tokens = data["current_tokens"]
        return window
