# -*- coding: utf-8 -*-
"""
错误分类器整合 - Error Classifier Integration
将 Hermes Agent 的错误分类器整合到二饼系统中
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class FailoverReason(Enum):
    """故障转移原因"""
    auth = "auth"
    auth_permanent = "auth_permanent"
    billing = "billing"
    rate_limit = "rate_limit"
    overloaded = "overloaded"
    server_error = "server_error"
    timeout = "timeout"
    context_overflow = "context_overflow"
    payload_too_large = "payload_too_large"
    model_not_found = "model_not_found"
    format_error = "format_error"


class ErrorClassifierIntegration:
    """错误分类器整合"""

    def __init__(self):
        self.enabled = True
        self.error_stats = {}

    def initialize(self):
        """初始化错误分类器"""
        logger.info("Error Classifier Integration initialized")

    def classify_error(self, error: Exception) -> Optional[FailoverReason]:
        """分类错误"""
        error_message = str(error).lower()

        # 认证错误
        if "401" in error_message or "403" in error_message or "unauthorized" in error_message:
            return FailoverReason.auth

        # 计费错误
        if "402" in error_message or "credit" in error_message or "billing" in error_message:
            return FailoverReason.billing

        # 速率限制
        if "429" in error_message or "rate limit" in error_message or "quota" in error_message:
            return FailoverReason.rate_limit

        # 服务器错误
        if "503" in error_message or "529" in error_message or "overloaded" in error_message:
            return FailoverReason.overloaded

        if "500" in error_message or "502" in error_message or "server error" in error_message:
            return FailoverReason.server_error

        # 超时错误
        if "timeout" in error_message or "timed out" in error_message:
            return FailoverReason.timeout

        # 上下文溢出
        if "context" in error_message and ("overflow" in error_message or "too large" in error_message):
            return FailoverReason.context_overflow

        # 模型未找到
        if "404" in error_message or "model not found" in error_message or "invalid model" in error_message:
            return FailoverReason.model_not_found

        # 格式错误
        if "400" in error_message or "bad request" in error_message or "format" in error_message:
            return FailoverReason.format_error

        return None

    def get_recovery_action(self, reason: FailoverReason) -> str:
        """获取恢复动作"""
        actions = {
            FailoverReason.auth: "refresh_token",
            FailoverReason.auth_permanent: "abort",
            FailoverReason.billing: "rotate_credential",
            FailoverReason.rate_limit: "backoff_then_rotate",
            FailoverReason.overloaded: "backoff",
            FailoverReason.server_error: "retry",
            FailoverReason.timeout: "rebuild_client_retry",
            FailoverReason.context_overflow: "compress_context",
            FailoverReason.payload_too_large: "compress_payload",
            FailoverReason.model_not_found: "fallback_model",
            FailoverReason.format_error: "strip_retry",
        }
        return actions.get(reason, "unknown")

    def should_retry(self, reason: FailoverReason) -> bool:
        """判断是否应该重试"""
        retryable = {
            FailoverReason.overloaded,
            FailoverReason.server_error,
            FailoverReason.timeout,
        }
        return reason in retryable

    def should_rotate_credential(self, reason: FailoverReason) -> bool:
        """判断是否应该轮换凭证"""
        rotatable = {
            FailoverReason.auth,
            FailoverReason.billing,
            FailoverReason.rate_limit,
        }
        return reason in rotatable

    def should_compress_context(self, reason: FailoverReason) -> bool:
        """判断是否应该压缩上下文"""
        compressible = {
            FailoverReason.context_overflow,
            FailoverReason.payload_too_large,
        }
        return reason in compressible

    def record_error(self, reason: FailoverReason):
        """记录错误"""
        if reason not in self.error_stats:
            self.error_stats[reason] = 0
        self.error_stats[reason] += 1

    def get_error_stats(self) -> Dict[str, int]:
        """获取错误统计"""
        return {reason.value: count for reason, count in self.error_stats.items()}

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "enabled": self.enabled,
            "error_stats": self.get_error_stats(),
        }


# 全局实例
_error_classifier_integration = None


def get_error_classifier_integration() -> ErrorClassifierIntegration:
    """获取错误分类器整合实例"""
    global _error_classifier_integration
    if _error_classifier_integration is None:
        _error_classifier_integration = ErrorClassifierIntegration()
    return _error_classifier_integration
