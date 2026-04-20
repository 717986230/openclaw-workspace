"""
MemGPT Integration for OpenClaw
完整的 MemGPT 框架集成
"""

from .memory import (
    CoreMemory,
    WorkingMemory,
    ArchivalMemory,
    MemoryManager
)

from .retrieval import (
    SemanticRetriever,
    KeywordRetriever,
    HybridRetriever,
    RetrievalManager
)

from .context import (
    ContextWindow,
    PriorityEntry,
    ContextPriorityQueue,
    ContextCompressor,
    ContextManager
)

__version__ = "1.0.0"

__all__ = [
    # Memory
    "CoreMemory",
    "WorkingMemory",
    "ArchivalMemory",
    "MemoryManager",
    # Retrieval
    "SemanticRetriever",
    "KeywordRetriever",
    "HybridRetriever",
    "RetrievalManager",
    # Context
    "ContextWindow",
    "PriorityEntry",
    "ContextPriorityQueue",
    "ContextCompressor",
    "ContextManager"
]


class MemGPTIntegration:
    """
    MemGPT 完整集成
    
    统一接口，整合记忆管理、检索系统和上下文管理
    """
    
    def __init__(
        self,
        agent_id: str = "default",
        db_path: str = "memory/memgpt.db",
        max_context_tokens: int = 8192,
        embedding_model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        """
        初始化 MemGPT 集成
        
        Args:
            agent_id: 代理ID
            db_path: 数据库路径
            max_context_tokens: 最大上下文令牌数
            embedding_model: 嵌入模型
            api_key: API 密钥
            api_base: API 基础 URL
        """
        from typing import Optional
        
        self.agent_id = agent_id
        
        # 初始化记忆管理器
        self.memory = MemoryManager(
            agent_id=agent_id,
            db_path=db_path
        )
        
        # 初始化检索管理器
        self.retrieval = RetrievalManager(
            embedding_model=embedding_model,
            api_key=api_key,
            api_base=api_base
        )
        
        # 初始化上下文管理器
        self.context = ContextManager(
            max_tokens=max_context_tokens
        )
    
    def remember(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        to_core: bool = False
    ) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            category: 类别
            importance: 重要性
            to_core: 是否存储到核心记忆
            
        Returns:
            记忆ID
        """
        return self.memory.remember(
            content=content,
            category=category,
            importance=importance,
            to_core=to_core
        )
    
    def recall(
        self,
        query: str,
        top_k: int = 5,
        search_archival: bool = True
    ) -> list:
        """
        检索记忆
        
        Args:
            query: 查询文本
            top_k: 返回数量
            search_archival: 是否搜索归档
            
        Returns:
            记忆列表
        """
        return self.memory.recall(
            query=query,
            top_k=top_k,
            search_archival=search_archival
        )
    
    def get_context_window(
        self,
        max_tokens: int = 4096,
        include_core: bool = True,
        include_working: bool = True,
        include_archival: bool = False
    ) -> str:
        """
        获取上下文窗口内容
        
        Args:
            max_tokens: 最大令牌数
            include_core: 包含核心记忆
            include_working: 包含工作记忆
            include_archival: 包含归档记忆
            
        Returns:
            上下文文本
        """
        return self.memory.get_context(
            max_tokens=max_tokens,
            include_core=include_core,
            include_working=include_working,
            include_archival=include_archival
        )
    
    def add_message(
        self,
        role: str,
        content: str,
        priority: int = 1
    ) -> bool:
        """
        添加消息到上下文
        
        Args:
            role: 角色
            content: 内容
            priority: 优先级
            
        Returns:
            是否成功
        """
        return self.context.add_message(
            role=role,
            content=content,
            priority=priority
        )
    
    def get_current_context(self) -> list:
        """获取当前上下文"""
        return self.context.get_context()
    
    def optimize(self) -> dict:
        """优化上下文和记忆"""
        context_result = self.context.optimize()
        memory_result = {
            "archival_count": len(self.memory.archival_memory.get_recent(days=30))
        }
        
        return {
            "context": context_result,
            "memory": memory_result
        }
    
    def archive_session(self) -> list:
        """归档当前会话"""
        return self.memory.archive_session()
    
    def get_stats(self) -> dict:
        """获取完整统计信息"""
        return {
            "agent_id": self.agent_id,
            "memory": self.memory.get_stats(),
            "retrieval": self.retrieval.get_stats(),
            "context": self.context.get_stats()
        }
    
    def save_state(self, path: str):
        """保存状态"""
        import json
        from pathlib import Path
        
        state = {
            "memory": self.memory.get_stats(),
            "context": self.context.save_state(),
            "agent_id": self.agent_id
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self, path: str) -> bool:
        """加载状态"""
        import json
        from pathlib import Path
        
        if not Path(path).exists():
            return False
        
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        if "context" in state:
            self.context.load_state(state["context"])
        
        return True


# 便捷导入函数
def create_memgpt(
    agent_id: str = "default",
    **kwargs
) -> MemGPTIntegration:
    """
    创建 MemGPT 集成实例
    
    Args:
        agent_id: 代理ID
        **kwargs: 其他参数
        
    Returns:
        MemGPTIntegration 实例
    """
    return MemGPTIntegration(agent_id=agent_id, **kwargs)
