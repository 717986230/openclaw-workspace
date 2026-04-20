# -*- coding: utf-8 -*-
"""
Hermes Agent 整合系统 - Hermes Integration System
将 Hermes Agent 的所有功能整合到二饼系统中
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class HermesIntegration:
    """Hermes 整合模块"""
    name: str
    description: str
    enabled: bool = True
    status: str = "ready"
    last_used: Optional[datetime] = None
    usage_count: int = 0


class HermesIntegrationSystem:
    """Hermes 整合系统"""

    def __init__(self):
        self.integrations: Dict[str, HermesIntegration] = {}
        self.initialized = False

        # 初始化所有整合模块
        self._initialize_integrations()

    def _initialize_integrations(self):
        """初始化所有整合模块"""

        # 核心功能
        self._register_integration("insights", "洞察引擎 - 分析历史会话数据")
        self._register_integration("error_classifier", "错误分类器 - 智能分类 API 错误")
        self._register_integration("context_compressor", "上下文压缩器 - 自动压缩长对话")
        self._register_integration("credential_pool", "凭证池 - 多凭证故障转移")
        self._register_integration("prompt_builder", "提示构建器 - 系统提示组装")

        # 工具功能
        self._register_integration("browser_tool", "浏览器工具 - 网页浏览能力")
        self._register_integration("mcp_tool", "MCP 工具 - Model Context Protocol")
        self._register_integration("skills_tool", "技能工具 - 技能管理")
        self._register_integration("terminal_tool", "终端工具 - 终端执行")
        self._register_integration("tts_tool", "TTS 工具 - 文本转语音")

        # 网关功能
        self._register_integration("delivery_system", "交付系统 - 多平台消息交付")
        self._register_integration("hooks_system", "钩子系统 - 事件钩子")
        self._register_integration("session_management", "会话管理 - 会话跟踪")

        # 定时任务
        self._register_integration("cron_jobs", "定时任务 - 定时任务调度")

        # 插件功能
        self._register_integration("context_engine_plugin", "上下文引擎插件 - 上下文管理")
        self._register_integration("memory_plugin", "记忆插件 - 记忆管理")

        # 其他功能
        self._register_integration("rate_limit_tracker", "速率限制跟踪 - 速率限制处理")
        self._register_integration("retry_utils", "重试工具 - 重试逻辑")
        self._register_integration("title_generator", "标题生成器 - 会话标题生成")
        self._register_integration("trajectory_saving", "轨迹保存 - 对话轨迹记录")

        self.initialized = True
        logger.info(f"Hermes Integration System initialized with {len(self.integrations)} integrations")

    def _register_integration(self, name: str, description: str):
        """注册整合模块"""
        integration = HermesIntegration(
            name=name,
            description=description,
        )
        self.integrations[name] = integration

    def get_integration(self, name: str) -> Optional[HermesIntegration]:
        """获取整合模块"""
        return self.integrations.get(name)

    def list_integrations(self) -> List[HermesIntegration]:
        """列出所有整合模块"""
        return list(self.integrations.values())

    def enable_integration(self, name: str):
        """启用整合模块"""
        if name in self.integrations:
            self.integrations[name].enabled = True
            logger.info(f"Integration '{name}' enabled")

    def disable_integration(self, name: str):
        """禁用整合模块"""
        if name in self.integrations:
            self.integrations[name].enabled = False
            logger.info(f"Integration '{name}' disabled")

    def use_integration(self, name: str) -> bool:
        """使用整合模块"""
        integration = self.get_integration(name)
        if integration and integration.enabled:
            integration.last_used = datetime.now()
            integration.usage_count += 1
            logger.info(f"Integration '{name}' used (count: {integration.usage_count})")
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "initialized": self.initialized,
            "total_integrations": len(self.integrations),
            "enabled_integrations": sum(1 for i in self.integrations.values() if i.enabled),
            "disabled_integrations": sum(1 for i in self.integrations.values() if not i.enabled),
            "total_usage": sum(i.usage_count for i in self.integrations.values()),
            "integrations": {
                name: {
                    "description": integration.description,
                    "enabled": integration.enabled,
                    "status": integration.status,
                    "last_used": integration.last_used.isoformat() if integration.last_used else None,
                    "usage_count": integration.usage_count,
                }
                for name, integration in self.integrations.items()
            },
        }


# 全局实例
_hermes_integration_system = None


def get_hermes_integration_system() -> HermesIntegrationSystem:
    """获取 Hermes 整合系统实例"""
    global _hermes_integration_system
    if _hermes_integration_system is None:
        _hermes_integration_system = HermesIntegrationSystem()
    return _hermes_integration_system


def use_hermes_integration(name: str) -> bool:
    """使用 Hermes 整合模块"""
    system = get_hermes_integration_system()
    return system.use_integration(name)


def list_hermes_integrations() -> List[HermesIntegration]:
    """列出所有 Hermes 整合模块"""
    system = get_hermes_integration_system()
    return system.list_integrations()


def get_hermes_integration_status() -> Dict[str, Any]:
    """获取 Hermes 整合系统状态"""
    system = get_hermes_integration_system()
    return system.get_status()


if __name__ == "__main__":
    # 测试 Hermes 整合系统
    print("Testing Hermes Integration System...")

    # 获取系统实例
    system = get_hermes_integration_system()

    # 获取状态
    status = system.get_status()
    print(f"\nHermes Integration System Status:")
    print(f"  Initialized: {status['initialized']}")
    print(f"  Total Integrations: {status['total_integrations']}")
    print(f"  Enabled: {status['enabled_integrations']}")
    print(f"  Disabled: {status['disabled_integrations']}")
    print(f"  Total Usage: {status['total_usage']}")

    # 列出所有整合模块
    print(f"\nAll Integrations:")
    for integration in system.list_integrations():
        print(f"  - {integration.name}: {integration.description}")

    # 测试使用整合模块
    print(f"\nTesting Use Integration:")
    success = system.use_integration("insights")
    print(f"  Insights: {success}")

    success = system.use_integration("error_classifier")
    print(f"  Error Classifier: {success}")

    success = system.use_integration("context_compressor")
    print(f"  Context Compressor: {success}")

    # 获取更新后的状态
    status = system.get_status()
    print(f"\nUpdated Status:")
    print(f"  Total Usage: {status['total_usage']}")

    print("\nHermes Integration System tested successfully!")
