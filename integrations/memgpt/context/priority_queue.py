"""
优先级队列 - Priority Queue
上下文内容的优先级管理
"""

from typing import List, Dict, Any, Optional, Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import heapq


T = TypeVar('T')


@dataclass
class PriorityEntry(Generic[T]):
    """优先级条目"""
    priority: int  # 越高越重要
    timestamp: datetime
    content: T
    entry_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """比较运算符（用于堆）"""
        # 先按优先级降序，再按时间升序
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.timestamp < other.timestamp


class ContextPriorityQueue:
    """
    上下文优先级队列
    
    特点：
    - 基于优先级的消息管理
    - 支持动态优先级调整
    - 支持过期策略
    - 时间感知的优先级衰减
    """
    
    def __init__(
        self,
        max_size: int = 100,
        decay_factor: float = 0.95,
        decay_interval_seconds: int = 3600
    ):
        """
        初始化优先级队列
        
        Args:
            max_size: 最大容量
            decay_factor: 优先级衰减因子
            decay_interval_seconds: 衰减间隔（秒）
        """
        self.max_size = max_size
        self.decay_factor = decay_factor
        self.decay_interval_seconds = decay_interval_seconds
        
        self._heap: List[PriorityEntry] = []
        self._entries: Dict[str, PriorityEntry] = {}
        self._id_counter = 0
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        self._id_counter += 1
        return f"entry_{self._id_counter}"
    
    def push(
        self,
        content: Any,
        priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        添加条目
        
        Args:
            content: 内容
            priority: 优先级 (1-5)
            metadata: 元数据
            
        Returns:
            条目ID
        """
        entry_id = self._generate_id()
        
        entry = PriorityEntry(
            priority=max(1, min(5, priority)),
            timestamp=datetime.now(),
            content=content,
            entry_id=entry_id,
            metadata=metadata or {}
        )
        
        # 如果超出容量，移除最低优先级的
        if len(self._entries) >= self.max_size:
            self._evict_lowest()
        
        heapq.heappush(self._heap, entry)
        self._entries[entry_id] = entry
        
        return entry_id
    
    def pop(self) -> Optional[Any]:
        """
        弹出最高优先级条目
        
        Returns:
            内容
        """
        while self._heap:
            entry = heapq.heappop(self._heap)
            if entry.entry_id in self._entries:
                del self._entries[entry.entry_id]
                return entry.content
        return None
    
    def peek(self) -> Optional[Any]:
        """查看最高优先级条目（不移除）"""
        self._rebuild_heap()
        if self._heap:
            return self._heap[0].content
        return None
    
    def _rebuild_heap(self):
        """重建堆（处理被删除的条目）"""
        valid_entries = [
            entry for entry in self._heap
            if entry.entry_id in self._entries
        ]
        heapq.heapify(valid_entries)
        self._heap = valid_entries
    
    def _evict_lowest(self):
        """驱逐最低优先级条目"""
        self._rebuild_heap()
        
        if not self._heap:
            return
        
        # 找到优先级最低的（堆的最后一个元素可能不是最低）
        min_entry = min(self._heap, key=lambda x: (x.priority, -x.timestamp.timestamp()))
        
        if min_entry.entry_id in self._entries:
            del self._entries[min_entry.entry_id]
            # 标记为删除，下次重建堆时移除
            self._heap = [
                e for e in self._heap
                if e.entry_id != min_entry.entry_id
            ]
            heapq.heapify(self._heap)
    
    def update_priority(self, entry_id: str, new_priority: int) -> bool:
        """
        更新条目优先级
        
        Args:
            entry_id: 条目ID
            new_priority: 新优先级
            
        Returns:
            是否成功
        """
        if entry_id not in self._entries:
            return False
        
        entry = self._entries[entry_id]
        entry.priority = max(1, min(5, new_priority))
        
        # 重建堆
        heapq.heapify(self._heap)
        
        return True
    
    def boost_priority(self, entry_id: str, boost: int = 1) -> bool:
        """提升优先级"""
        if entry_id not in self._entries:
            return False
        
        entry = self._entries[entry_id]
        return self.update_priority(entry_id, entry.priority + boost)
    
    def get(self, entry_id: str) -> Optional[Any]:
        """获取条目内容"""
        if entry_id in self._entries:
            return self._entries[entry_id].content
        return None
    
    def remove(self, entry_id: str) -> bool:
        """移除条目"""
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False
    
    def apply_decay(self):
        """应用时间衰减"""
        now = datetime.now()
        
        for entry in self._entries.values():
            age_seconds = (now - entry.timestamp).total_seconds()
            decay_intervals = age_seconds / self.decay_interval_seconds
            
            if decay_intervals >= 1:
                decay_amount = decay_intervals
                new_priority = entry.priority * (self.decay_factor ** decay_amount)
                entry.priority = max(1, round(new_priority))
        
        # 重建堆
        heapq.heapify(self._heap)
    
    def get_top(self, n: int = 10) -> List[Any]:
        """
        获取优先级最高的n个条目
        
        Args:
            n: 数量
            
        Returns:
            内容列表
        """
        self._rebuild_heap()
        
        sorted_entries = sorted(
            self._heap,
            key=lambda x: (-x.priority, x.timestamp)
        )
        
        return [e.content for e in sorted_entries[:n]]
    
    def get_by_priority(self, min_priority: int = 1) -> List[Any]:
        """按最小优先级获取"""
        return [
            entry.content
            for entry in self._entries.values()
            if entry.priority >= min_priority
        ]
    
    def size(self) -> int:
        """获取当前大小"""
        return len(self._entries)
    
    def clear(self):
        """清空队列"""
        self._heap.clear()
        self._entries.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        priority_counts = {}
        for entry in self._entries.values():
            priority_counts[f"priority_{entry.priority}"] = priority_counts.get(f"priority_{entry.priority}", 0) + 1
        
        return {
            "total_entries": len(self._entries),
            "max_size": self.max_size,
            "by_priority": priority_counts,
            "decay_factor": self.decay_factor
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "max_size": self.max_size,
            "decay_factor": self.decay_factor,
            "decay_interval_seconds": self.decay_interval_seconds,
            "entries": [
                {
                    "priority": entry.priority,
                    "timestamp": entry.timestamp.isoformat(),
                    "entry_id": entry.entry_id,
                    "metadata": entry.metadata
                }
                for entry in self._entries.values()
            ]
        }
