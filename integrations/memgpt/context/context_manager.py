"""
上下文管理器 - Context Manager
统一管理上下文窗口、优先级队列和压缩
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .context_window import ContextWindow, ContextBlock
from .priority_queue import ContextPriorityQueue
from .compression import ContextCompressor, CompressionResult


class ContextManager:
    """
    上下文管理器
    
    协调上下文窗口、优先级队列和压缩策略
    """
    
    def __init__(
        self,
        max_tokens: int = 8192,
        reserved_tokens: int = 500,
        auto_compress: bool = True,
        compression_threshold: float = 0.8
    ):
        """
        初始化上下文管理器
        
        Args:
            max_tokens: 最大令牌数
            reserved_tokens: 保留令牌数
            auto_compress: 是否自动压缩
            compression_threshold: 压缩阈值
        """
        self.max_tokens = max_tokens
        self.reserved_tokens = reserved_tokens
        self.auto_compress = auto_compress
        
        # 初始化组件
        self.context_window = ContextWindow(
            max_tokens=max_tokens,
            reserved_tokens=reserved_tokens
        )
        self.priority_queue = ContextPriorityQueue()
        self.compressor = ContextCompressor(
            compression_threshold=compression_threshold
        )
        
        # 配置
        self.config = {
            "preserve_system": True,
            "preserve_recent": 3,
            "max_priority": 3,
            "enable_decay": True,
            "decay_interval_minutes": 60
        }
    
    def add_message(
        self,
        role: str,
        content: str,
        priority: int = 1,
        compressible: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加消息
        
        Args:
            role: 角色
            content: 内容
            priority: 优先级
            compressible: 是否可压缩
            metadata: 元数据
            
        Returns:
            是否成功添加
        """
        # 先添加到优先级队列
        entry_id = self.priority_queue.push(
            content={"role": role, "content": content},
            priority=priority,
            metadata=metadata
        )
        
        # 尝试添加到上下文窗口
        success = self.context_window.add(
            role=role,
            content=content,
            priority=priority,
            compressible=compressible,
            metadata={"entry_id": entry_id, **(metadata or {})}
        )
        
        # 如果失败且启用自动压缩
        if not success and self.auto_compress:
            self._auto_compress()
            success = self.context_window.add(
                role=role,
                content=content,
                priority=priority,
                compressible=compressible,
                metadata={"entry_id": entry_id, **(metadata or {})}
            )
        
        return success
    
    def add_system_message(self, content: str) -> bool:
        """添加系统消息（高优先级，不可压缩）"""
        return self.add_message(
            role="system",
            content=content,
            priority=3,
            compressible=False
        )
    
    def add_user_message(self, content: str, priority: int = 1) -> bool:
        """添加用户消息"""
        return self.add_message(
            role="user",
            content=content,
            priority=priority,
            compressible=True
        )
    
    def add_assistant_message(self, content: str, priority: int = 1) -> bool:
        """添加助手消息"""
        return self.add_message(
            role="assistant",
            content=content,
            priority=priority,
            compressible=True
        )
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取当前上下文"""
        return self.context_window.get_context()
    
    def get_context_text(self) -> str:
        """获取上下文文本"""
        return self.context_window.get_text()
    
    def compress(
        self,
        force: bool = False
    ) -> Optional[CompressionResult]:
        """
        手动触发压缩
        
        Args:
            force: 是否强制压缩
            
        Returns:
            压缩结果
        """
        utilization = self.context_window.get_token_usage()["utilization"]
        
        if not force and not self.compressor.should_compress(utilization):
            return None
        
        messages = self.get_context()
        compressed, result = self.compressor.compress_messages(
            messages,
            keep_full=self.config["preserve_recent"]
        )
        
        # 更新上下文窗口
        self.context_window.clear_except_system()
        
        for msg in compressed:
            if msg["role"] != "system" or not self.config["preserve_system"]:
                self.context_window.add(
                    role=msg["role"],
                    content=msg["content"],
                    priority=2 if msg["role"] == "system" else 1
                )
        
        return result
    
    def _auto_compress(self):
        """自动压缩"""
        utilization = self.context_window.get_token_usage()["utilization"]
        
        if self.compressor.should_compress(utilization):
            self.compress(force=True)
    
    def optimize(self) -> Dict[str, Any]:
        """
        优化上下文
        
        应用时间衰减、优先级调整和压缩
        
        Returns:
            优化结果
        """
        results = {}
        
        # 应用时间衰减
        if self.config["enable_decay"]:
            self.priority_queue.apply_decay()
            results["decay_applied"] = True
        
        # 获取高优先级内容
        high_priority = self.priority_queue.get_by_priority(min_priority=2)
        results["high_priority_count"] = len(high_priority)
        
        # 检查是否需要压缩
        utilization = self.context_window.get_token_usage()["utilization"]
        
        if utilization > 0.7:
            compression_result = self.compress()
            results["compression"] = {
                "performed": compression_result is not None,
                "ratio": compression_result.compression_ratio if compression_result else None
            }
        
        return results
    
    def clear_session(self, keep_system: bool = True):
        """
        清空会话
        
        Args:
            keep_system: 是否保留系统消息
        """
        if keep_system:
            self.context_window.clear_except_system()
        else:
            self.context_window.clear()
        
        self.priority_queue.clear()
    
    def get_token_usage(self) -> Dict[str, Any]:
        """获取令牌使用情况"""
        return self.context_window.get_token_usage()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取完整统计信息"""
        return {
            "max_tokens": self.max_tokens,
            "reserved_tokens": self.reserved_tokens,
            "auto_compress": self.auto_compress,
            "context_window": self.context_window.get_stats(),
            "priority_queue": self.priority_queue.get_stats(),
            "config": self.config
        }
    
    def save_state(self) -> Dict[str, Any]:
        """保存状态"""
        return {
            "context_window": self.context_window.to_dict(),
            "priority_queue": self.priority_queue.to_dict(),
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    def load_state(self, state: Dict[str, Any]):
        """加载状态"""
        if "context_window" in state:
            self.context_window = ContextWindow.from_dict(state["context_window"])
        
        if "config" in state:
            self.config.update(state["config"])
    
    def get_summary(self) -> str:
        """获取上下文摘要"""
        messages = self.get_context()
        
        if not messages:
            return "Empty context"
        
        user_count = sum(1 for m in messages if m["role"] == "user")
        assistant_count = sum(1 for m in messages if m["role"] == "assistant")
        system_count = sum(1 for m in messages if m["role"] == "system")
        
        usage = self.get_token_usage()
        
        return (
            f"Context: {len(messages)} messages "
            f"({system_count} system, {user_count} user, {assistant_count} assistant). "
            f"Tokens: {usage['current']}/{usage['available']} ({usage['utilization']:.1%})"
        )
    
    def get_recent_context(self, n: int = 5) -> List[Dict[str, str]]:
        """获取最近的上下文"""
        recent_blocks = self.context_window.get_recent(n)
        return [
            {"role": block.role, "content": block.content}
            for block in recent_blocks
        ]
    
    def set_priority(self, entry_id: str, priority: int) -> bool:
        """设置条目优先级"""
        return self.priority_queue.update_priority(entry_id, priority)
    
    def boost_priority(self, entry_id: str) -> bool:
        """提升条目优先级"""
        return self.priority_queue.boost_priority(entry_id)
