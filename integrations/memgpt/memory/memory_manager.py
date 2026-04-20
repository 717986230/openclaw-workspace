"""
记忆管理器 - Memory Manager
统一管理三层记忆架构
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path
import json

from .core_memory import CoreMemory, CoreMemoryEntry
from .working_memory import WorkingMemory, WorkingMemoryEntry
from .archival_memory import ArchivalMemory, ArchivalMemoryEntry


class MemoryManager:
    """
    三层记忆管理器
    
    协调核心记忆、工作记忆和归档记忆之间的数据流动
    """
    
    def __init__(
        self,
        agent_id: str,
        db_path: str = "memory/memgpt.db",
        core_max_tokens: int = 512,
        working_max_tokens: int = 2048,
        working_max_entries: int = 100
    ):
        """
        初始化记忆管理器
        
        Args:
            agent_id: 代理ID
            db_path: 数据库路径
            core_max_tokens: 核心记忆最大令牌
            working_max_tokens: 工作记忆最大令牌
            working_max_entries: 工作记忆最大条目数
        """
        self.agent_id = agent_id
        self.db_path = db_path
        
        # 初始化三层记忆
        self.core_memory = CoreMemory(max_tokens=core_max_tokens)
        self.working_memory = WorkingMemory(
            max_tokens=working_max_tokens,
            max_entries=working_max_entries
        )
        self.archival_memory = ArchivalMemory(
            db_path=db_path,
            agent_id=agent_id
        )
        
        # 配置
        self.config = {
            "auto_archive_threshold": 0.9,
            "auto_summarize": True,
            "importance_decay": 0.95
        }
    
    def remember(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        to_core: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        存储新记忆
        
        Args:
            content: 记忆内容
            category: 类别
            importance: 重要性
            to_core: 是否存储到核心记忆
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        if to_core:
            # 存储到核心记忆
            entry_id = f"core_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            success = self.core_memory.add(
                id=entry_id,
                content=content,
                category=category,
                importance=importance,
                metadata=metadata
            )
            if success:
                return entry_id
            # 如果核心记忆已满，降级到工作记忆
            importance *= 0.8
        
        # 存储到工作记忆
        entry = self.working_memory.add(
            content=content,
            importance=importance,
            metadata={"category": category, **(metadata or {})}
        )
        
        # 检查是否需要自动归档
        self._check_auto_archive()
        
        return entry.id
    
    def recall(
        self,
        query: str,
        top_k: int = 5,
        search_archival: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索记忆
        
        Args:
            query: 查询文本
            top_k: 返回数量
            search_archival: 是否搜索归档
            filters: 过滤条件
            
        Returns:
            记忆列表
        """
        results = []
        
        # 1. 从核心记忆搜索
        for entry in self.core_memory.get_all():
            if query.lower() in entry.content.lower():
                results.append({
                    "layer": "core",
                    "id": entry.id,
                    "content": entry.content,
                    "category": entry.category,
                    "importance": entry.importance,
                    "score": entry.importance
                })
        
        # 2. 从工作记忆搜索
        working_results = self.working_memory.search(query)
        for entry in working_results:
            results.append({
                "layer": "working",
                "id": entry.id,
                "content": entry.content,
                "importance": entry.importance,
                "score": entry.importance * 0.8
            })
        
        # 3. 从归档记忆搜索
        if search_archival:
            archival_results = self.archival_memory.search(
                query=query,
                top_k=top_k,
                category=filters.get("category") if filters else None
            )
            for entry, score in archival_results:
                results.append({
                    "layer": "archival",
                    "id": entry.id,
                    "content": entry.content,
                    "summary": entry.summary,
                    "category": entry.category,
                    "importance": entry.importance,
                    "score": score * 0.6
                })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_context(
        self,
        max_tokens: int = 4096,
        include_core: bool = True,
        include_working: bool = True,
        include_archival: bool = False,
        archival_limit: int = 3
    ) -> str:
        """
        获取上下文窗口内容
        
        Args:
            max_tokens: 最大令牌数
            include_core: 包含核心记忆
            include_working: 包含工作记忆
            include_archival: 包含归档记忆
            archival_limit: 归档记忆条目数限制
            
        Returns:
            上下文文本
        """
        sections = []
        current_tokens = 0
        
        # 核心记忆
        if include_core:
            core_text = self.core_memory.to_prompt()
            core_tokens = len(core_text) // 4
            if current_tokens + core_tokens <= max_tokens:
                sections.append(core_text)
                current_tokens += core_tokens
        
        # 工作记忆（转换为对话格式）
        if include_working:
            messages = self.working_memory.to_conversation()
            working_text = "\n".join(
                f"[{m['role']}]: {m['content']}"
                for m in messages
            )
            working_tokens = len(working_text) // 4
            
            # 动态截断
            if current_tokens + working_tokens > max_tokens:
                available = max_tokens - current_tokens
                # 从最新消息开始取
                messages = messages[-(available // 50):]
                working_text = "\n".join(
                    f"[{m['role']}]: {m['content']}"
                    for m in messages
                )
            
            if working_text:
                sections.append(f"\n# 当前会话\n{working_text}")
        
        # 归档记忆（按需检索）
        if include_archival:
            # 获取最近的高重要性归档
            recent_archival = self.archival_memory.get_recent(days=7, limit=archival_limit)
            if recent_archival:
                archival_text = "\n".join(
                    f"- [{a.category}] {a.summary or a.content[:100]}"
                    for a in recent_archival
                )
                archival_tokens = len(archival_text) // 4
                
                if current_tokens + archival_tokens <= max_tokens:
                    sections.append(f"\n# 相关历史记忆\n{archival_text}")
        
        return "\n".join(sections)
    
    def archive_session(self) -> List[str]:
        """
        归档当前会话的工作记忆
        
        Returns:
            归档的记忆ID列表
        """
        # 获取工作记忆内容
        entries = self.working_memory.get_recent(n=1000)
        
        if not entries:
            return []
        
        # 创建会话摘要
        session_content = "\n".join(
            f"[{e.message_type}]: {e.content}"
            for e in entries
        )
        
        # 存储到归档
        archived_ids = []
        
        # 整体归档
        summary_id = self.archival_memory.add(
            content=session_content,
            summary=f"会话 {self.working_memory.session_id} 的完整记录",
            source_session=self.working_memory.session_id,
            category="session",
            importance=0.5,
            tags=["session", self.working_memory.session_id]
        )
        archived_ids.append(summary_id)
        
        # 清空工作记忆
        self.working_memory.clear()
        
        return archived_ids
    
    def promote_to_core(self, entry_id: str, from_layer: str = "working") -> bool:
        """
        将记忆提升到核心记忆
        
        Args:
            entry_id: 条目ID
            from_layer: 来源层级
            
        Returns:
            是否成功
        """
        entry = None
        
        if from_layer == "working":
            entry = self.working_memory.get(entry_id)
            if entry:
                content = entry.content
                importance = entry.importance
                category = entry.metadata.get("category", "general")
        elif from_layer == "archival":
            entry = self.archival_memory.get(entry_id)
            if entry:
                content = entry.summary or entry.content
                importance = entry.importance
                category = entry.category
        else:
            return False
        
        if not entry:
            return False
        
        # 添加到核心记忆
        success = self.core_memory.add(
            id=f"promoted_{entry_id}",
            content=content,
            category=category,
            importance=min(importance + 0.2, 1.0)
        )
        
        return success
    
    def _check_auto_archive(self):
        """检查是否需要自动归档"""
        stats = self.working_memory.get_summary()
        utilization = stats["utilization"]
        
        if utilization >= self.config["auto_archive_threshold"]:
            # 压缩工作记忆
            removed = self.working_memory.compress()
            
            # 将移除的内容归档
            for entry in removed:
                self.archival_memory.add(
                    content=entry.content,
                    source_session=entry.session_id,
                    category=entry.metadata.get("category", "general"),
                    importance=entry.importance * self.config["importance_decay"],
                    metadata=entry.metadata
                )
    
    def load_from_memory_md(self, path: str = "MEMORY.md") -> int:
        """
        从 MEMORY.md 加载核心记忆
        
        Args:
            path: MEMORY.md 路径
            
        Returns:
            加载的条目数
        """
        if not Path(path).exists():
            return 0
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 简单解析（按标题分段）
        sections = content.split("\n## ")
        loaded = 0
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.strip().split("\n")
            if not lines:
                continue
            
            # 第一行可能是标题
            title = lines[0].replace("#", "").strip()
            
            # 添加为核心记忆
            section_content = "\n".join(lines[1:]).strip()
            if section_content:
                self.remember(
                    content=section_content[:500],  # 限制长度
                    category=title,
                    importance=0.8,
                    to_core=True
                )
                loaded += 1
        
        return loaded
    
    def export_to_memory_md(self, path: str = "MEMORY.md") -> bool:
        """
        导出核心记忆到 MEMORY.md
        
        Args:
            path: 输出路径
            
        Returns:
            是否成功
        """
        entries = self.core_memory.get_all()
        
        if not entries:
            return False
        
        # 按类别组织
        categories = {}
        for entry in entries:
            if entry.category not in categories:
                categories[entry.category] = []
            categories[entry.category].append(entry.content)
        
        # 生成 Markdown
        lines = ["# Memory\n"]
        
        for category, contents in categories.items():
            lines.append(f"\n## {category}\n")
            for content in contents:
                lines.append(f"{content}\n")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取完整统计信息"""
        return {
            "agent_id": self.agent_id,
            "core_memory": self.core_memory.stats(),
            "working_memory": self.working_memory.get_summary(),
            "archival_memory": self.archival_memory.stats()
        }
    
    def save_state(self, path: str):
        """保存状态到文件"""
        state = {
            "agent_id": self.agent_id,
            "config": self.config,
            "core_memory": self.core_memory.to_dict(),
            "working_memory": self.working_memory.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self, path: str):
        """从文件加载状态"""
        if not Path(path).exists():
            return False
        
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        self.config = state.get("config", self.config)
        self.core_memory = CoreMemory.from_dict(state["core_memory"])
        self.working_memory = WorkingMemory.from_dict(state["working_memory"])
        
        return True
