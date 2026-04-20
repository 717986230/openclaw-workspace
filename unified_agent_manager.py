# -*- coding: utf-8 -*-
"""
统一智能体管理系统 - Unified Agent Management System
统一管理所有智能体，包括原有179个和新增智能体，确保智能体池能够自动加载和调用
"""

import os
import sys
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import glob

logger = logging.getLogger(__name__)


class AgentCategory(Enum):
    """智能体分类"""
    MARKETING = "marketing"
    SPECIALIZED = "specialized"
    ENGINEERING = "engineering"
    GAME_DEVELOPMENT = "game-development"
    STRATEGY = "strategy"
    TESTING = "testing"
    SALES = "sales"
    DESIGN = "design"
    PAID_MEDIA = "paid-media"
    SUPPORT = "support"
    SPATIAL_COMPUTING = "spatial-computing"
    PROJECT_MANAGEMENT = "project-management"
    PRODUCT = "product"
    ACADEMIC = "academic"
    INTEGRATIONS = "integrations"
    AI_RESEARCH = "ai_research"
    DATA_SCIENCE = "data_science"
    SECURITY = "security"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    LEGAL = "legal"
    CONTENT_CREATION = "content_creation"
    AUTOMATION = "automation"
    ANALYSIS = "analysis"
    CONSULTING = "consulting"


@dataclass
class UnifiedAgent:
    """统一智能体"""
    id: str
    name: str
    category: AgentCategory
    description: str
    emoji: str = "🤖"
    color: str = "#3B82F6"
    tools: List[str] = field(default_factory=list)
    vibe: str = "professional"
    filepath: str = ""
    full_content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class UnifiedAgentManager:
    """统一智能体管理器"""

    def __init__(self, db_path: str = "memory/database/xiaozhi_memory.db"):
        self.db_path = db_path
        self.agents: Dict[str, UnifiedAgent] = {}
        self.initialized = False

    def initialize(self):
        """初始化管理器"""
        logger.info("Initializing Unified Agent Manager...")

        # 加载所有智能体
        self._load_all_agents()

        self.initialized = True
        logger.info(f"Unified Agent Manager initialized with {len(self.agents)} agents")

    def _load_all_agents(self):
        """加载所有智能体"""
        logger.info("Loading all agents from database...")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询所有智能体
            cursor.execute("SELECT * FROM agent_prompts")
            rows = cursor.fetchall()

            # 获取列名
            columns = [description[0] for description in cursor.description]

            for row in rows:
                agent_data = dict(zip(columns, row))

                try:
                    # 解析 JSON 字段
                    tools = json.loads(agent_data.get('tools', '[]'))
                    metadata = json.loads(agent_data.get('metadata', '{}'))
                except json.JSONDecodeError:
                    # 如果 JSON 解析失败，使用默认值
                    tools = []
                    metadata = {}

                # 创建统一智能体
                agent = UnifiedAgent(
                    id=str(agent_data.get('id', '')),
                    name=agent_data.get('name', ''),
                    category=AgentCategory(agent_data.get('category', 'specialized')),
                    description=agent_data.get('description', ''),
                    emoji=agent_data.get('emoji', '🤖'),
                    color=agent_data.get('color', '#3B82F6'),
                    tools=tools,
                    vibe=agent_data.get('vibe', 'professional'),
                    filepath=agent_data.get('filepath', ''),
                    full_content=agent_data.get('full_content', ''),
                    metadata=metadata,
                )

                self.agents[agent.id] = agent

            conn.close()
            logger.info(f"Loaded {len(self.agents)} agents")

        except Exception as e:
            logger.error(f"Error loading agents: {e}")

    def add_agent(self, agent: UnifiedAgent) -> bool:
        """添加智能体"""
        if agent.id in self.agents:
            logger.warning(f"Agent '{agent.id}' already exists")
            return False

        # 保存到数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 生成唯一的filepath（如果未提供）
            if not agent.filepath:
                agent.filepath = f"agents/{agent.category.value}/{agent.name.lower().replace(' ', '_')}.md"

            # 保存到数据库
            cursor.execute("""
                INSERT OR REPLACE INTO agent_prompts
                (id, name, category, description, emoji, color, tools, vibe, filepath, full_content, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(agent.id) if agent.id.isdigit() else None,
                agent.name,
                agent.category.value,
                agent.description,
                agent.emoji,
                agent.color,
                json.dumps(agent.tools),
                agent.vibe,
                agent.filepath,
                agent.full_content,
                json.dumps(agent.metadata),
                agent.created_at.isoformat(),
                agent.updated_at.isoformat(),
            ))

            conn.commit()
            conn.close()

            # 添加到内存
            self.agents[agent.id] = agent
            logger.info(f"Agent '{agent.name}' added successfully")

            return True

        except Exception as e:
            logger.error(f"Error adding agent: {e}")
            return False

    def update_agent(self, agent_id: str, **kwargs) -> bool:
        """更新智能体"""
        if agent_id not in self.agents:
            logger.warning(f"Agent '{agent_id}' not found")
            return False

        agent = self.agents[agent_id]

        # 更新属性
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)

        agent.updated_at = datetime.now()

        # 保存到数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE agent_prompts
                SET name=?, category=?, description=?, emoji=?, color=?, tools=?, vibe=?, filepath=?, full_content=?, metadata=?, updated_at=?
                WHERE id=?
            """, (
                agent.name,
                agent.category.value,
                agent.description,
                agent.emoji,
                agent.color,
                json.dumps(agent.tools),
                agent.vibe,
                agent.filepath,
                agent.full_content,
                json.dumps(agent.metadata),
                agent.updated_at.isoformat(),
                int(agent_id) if agent_id.isdigit() else agent_id,
            ))

            conn.commit()
            conn.close()

            logger.info(f"Agent '{agent.name}' updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return False

    def remove_agent(self, agent_id: str) -> bool:
        """移除智能体"""
        if agent_id not in self.agents:
            logger.warning(f" Agent '{agent_id}' not found")
            return False

        # 从数据库删除
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM agent_prompts WHERE id=?", (int(agent_id) if agent_id.isdigit() else agent_id,))
            conn.commit()
            conn.close()

            # 从内存删除
            del self.agents[agent_id]
            logger.info(f"Agent '{agent_id}' removed successfully")

            return True

        except Exception as e:
            logger.error(f"Error removing agent: {e}")
            return False

    def get_agent(self, agent_id: str) -> Optional[UnifiedAgent]:
        """获取智能体"""
        return self.agents.get(agent_id)

    def list_agents(self, category: Optional[AgentCategory] = None) -> List[UnifiedAgent]:
        """列出智能体"""
        if category:
            return [a for a in self.agents.values() if a.category == category]
        return list(self.agents.values())

    def search_agents(self, query: str) -> List[UnifiedAgent]:
        """搜索智能体"""
        query_lower = query.lower()
        return [
            a for a in self.agents.values()
            if query_lower in a.name.lower()
            or query_lower in a.description.lower()
            or query_lower in a.category.value
            or any(query_lower in tool.lower() for tool in a.tools)
        ]

    def get_categories(self) -> List[AgentCategory]:
        """获取所有分类"""
        return list(set(a.category for a in self.agents.values()))

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "initialized": self.initialized,
            "total_agents": len(self.agents),
            "categories": {
                category.value: len([a for a in self.agents.values() if a.category == category])
                for category in AgentCategory
            },
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "category": agent.category.value,
                    "description": agent.description,
                    "emoji": agent.emoji,
                    "color": agent.color,
                    "tools": agent.tools,
                    "vibe": agent.vibe,
                    "filepath": agent.filepath,
                }
                for agent_id, agent in self.agents.items()
            },
        }

    def reload_from_database(self):
        """从数据库重新加载所有智能体"""
        logger.info("Reloading agents from database...")
        self.agents.clear()
        self._load_all_agents()
        logger.info(f"Reloaded {len(self.agents)} agents")


# 全局实例
_unified_agent_manager = None


def get_unified_agent_manager() -> UnifiedAgentManager:
    """获取统一智能体管理器实例"""
    global _unified_agent_manager
    if _unified_agent_manager is None:
        _unified_agent_manager = UnifiedAgentManager()
        _unified_agent_manager.initialize()
    return _unified_agent_manager


if __name__ == "__main__":
    # 测试统一智能体管理器
    print("Testing Unified Agent Manager...")

    # 获取管理器实例
    manager = get_unified_agent_manager()

    # 获取状态
    status = manager.get_status()
    print(f"\nUnified Agent Manager Status:")
    print(f"  Initialized: {status['initialized']}")
    print(f"  Total Agents: {status['total_agents']}")
    print(f"\n  Categories:")
    for category, count in status['categories'].items():
        if count > 0:
            print(f"    {category}: {count}")

    # 搜索智能体
    print(f"\nSearching for 'AI' agents...")
    ai_agents = manager.search_agents("AI")
    print(f"  Found: {len(ai_agents)} agents")
    for agent in ai_agents[:5]:
        print(f"    - {agent.emoji} {agent.name}")

    print("\nUnified Agent Manager tested successfully!")
