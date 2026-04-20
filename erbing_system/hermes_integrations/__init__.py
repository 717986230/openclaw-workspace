# -*- coding: utf-8 -*-
"""
Hermes 整合模块 - Hermes Integrations
将 Hermes Agent 的各个功能整合到二饼系统中
"""

from .insights import InsightsIntegration
from .error_classifier import ErrorClassifierIntegration
from .context_compressor import ContextCompressorIntegration
from .credential_pool import CredentialPoolIntegration
from .prompt_builder import PromptBuilderIntegration
from .browser_tool import BrowserToolIntegration
from .mcp_tool import MCPToolIntegration
from .skills_tool import SkillsToolIntegration
from .terminal_tool import TerminalToolIntegration
from .tts_tool import TTSToolIntegration
from .delivery_system import DeliverySystemIntegration
from .hooks_system import HooksSystemIntegration
from .session_management import SessionManagementIntegration
from .cron_jobs import CronJobsIntegration
from .context_engine_plugin import ContextEnginePluginIntegration
from .memory_plugin import MemoryPluginIntegration
from .rate_limit_tracker import RateLimitTrackerIntegration
from .retry_utils import RetryUtilsIntegration
from .title_generator import TitleGeneratorIntegration
from .trajectory_saving import TrajectorySavingIntegration

__all__ = [
    "InsightsIntegration",
    "ErrorClassifierIntegration",
    "ContextCompressorIntegration",
    "CredentialPoolIntegration",
    "PromptBuilderIntegration",
    "BrowserToolIntegration",
    "MCPToolIntegration",
    "SkillsToolIntegration",
    "TerminalToolIntegration",
    "TTSToolIntegration",
    "DeliverySystemIntegration",
    "HooksSystemIntegration",
    "SessionManagementIntegration",
    "CronJobsIntegration",
    "ContextEnginePluginIntegration",
    "MemoryPluginIntegration",
    "RateLimitTrackerIntegration",
    "RetryUtilsIntegration",
    "TitleGeneratorIntegration",
    "TrajectorySavingIntegration",
]
