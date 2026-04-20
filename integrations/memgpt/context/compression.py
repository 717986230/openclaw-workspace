"""
上下文压缩器 - Context Compressor
自动总结和压缩旧消息
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CompressionResult:
    """压缩结果"""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    summary: str
    preserved_items: int


class ContextCompressor:
    """
    上下文压缩器
    
    特点：
    - 自动总结旧消息
    - 保留关键信息
    - 多级压缩策略
    - 可配置压缩阈值
    """
    
    def __init__(
        self,
        compression_threshold: float = 0.8,
        target_compression_ratio: float = 0.3,
        preserve_recent: int = 3
    ):
        """
        初始化压缩器
        
        Args:
            compression_threshold: 触发压缩的使用率阈值
            target_compression_ratio: 目标压缩比
            preserve_recent: 保留最近的消息数
        """
        self.compression_threshold = compression_threshold
        self.target_compression_ratio = target_compression_ratio
        self.preserve_recent = preserve_recent
    
    def should_compress(self, utilization: float) -> bool:
        """判断是否需要压缩"""
        return utilization >= self.compression_threshold
    
    def compress_messages(
        self,
        messages: List[Dict[str, str]],
        keep_full: int = None
    ) -> Tuple[List[Dict[str, str]], CompressionResult]:
        """
        压缩消息列表
        
        Args:
            messages: 消息列表
            keep_full: 保持完整的消息数
            
        Returns:
            (压缩后的消息, 压缩结果)
        """
        if not messages:
            return messages, CompressionResult(
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=1.0,
                summary="",
                preserved_items=0
            )
        
        keep_full = keep_full or self.preserve_recent
        
        # 分离要保留的和要压缩的
        to_compress = messages[:-keep_full] if keep_full < len(messages) else []
        to_keep = messages[-keep_full:] if keep_full < len(messages) else messages
        
        if not to_compress:
            # 无需压缩
            return messages, CompressionResult(
                original_tokens=self._estimate_tokens(messages),
                compressed_tokens=self._estimate_tokens(messages),
                compression_ratio=1.0,
                summary="No compression needed",
                preserved_items=len(messages)
            )
        
        # 生成摘要
        summary = self._generate_summary(to_compress)
        
        # 构建压缩后的消息
        compressed = []
        
        # 添加摘要作为系统消息
        if summary:
            compressed.append({
                "role": "system",
                "content": f"[Previous Context Summary]\n{summary}"
            })
        
        # 添加保留的消息
        compressed.extend(to_keep)
        
        # 计算压缩结果
        original_tokens = self._estimate_tokens(messages)
        compressed_tokens = self._estimate_tokens(compressed)
        
        result = CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            summary=summary,
            preserved_items=len(to_keep)
        )
        
        return compressed, result
    
    def _generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        生成消息摘要
        
        Args:
            messages: 要压缩的消息
            
        Returns:
            摘要文本
        """
        if not messages:
            return ""
        
        # 按角色分组
        user_messages = [m["content"] for m in messages if m["role"] == "user"]
        assistant_messages = [m["content"] for m in messages if m["role"] == "assistant"]
        
        summary_parts = []
        
        # 用户消息摘要
        if user_messages:
            user_summary = self._summarize_list(user_messages, "User")
            summary_parts.append(user_summary)
        
        # 助手消息摘要
        if assistant_messages:
            assistant_summary = self._summarize_list(assistant_messages, "Assistant")
            summary_parts.append(assistant_summary)
        
        return "\n".join(summary_parts)
    
    def _summarize_list(self, items: List[str], role: str) -> str:
        """
        总结列表项
        
        Args:
            items: 内容列表
            role: 角色名
            
        Returns:
            摘要
        """
        if not items:
            return ""
        
        if len(items) == 1:
            return f"{role}: {items[0][:200]}"
        
        # 多个项目的摘要
        total_content = " ".join(items)
        
        # 提取关键点
        key_points = self._extract_key_points(items)
        
        if key_points:
            return f"{role} discussed: {', '.join(key_points[:5])}"
        else:
            # 简单截断
            return f"{role} exchanged {len(items)} messages. Key: {total_content[:200]}"
    
    def _extract_key_points(self, items: List[str]) -> List[str]:
        """
        提取关键点
        
        Args:
            items: 内容列表
            
        Returns:
            关键点列表
        """
        key_points = []
        
        for item in items:
            # 提取句子
            sentences = item.replace("。", ".").replace("！", "!").replace("？", "?").split(".")
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # 简单的关键句检测
                if any(keyword in sentence.lower() for keyword in [
                    "important", "key", "note", "remember", "重要", "关键", "注意", "记住"
                ]):
                    key_points.append(sentence)
                elif len(sentence.split()) <= 10:  # 短句子可能更关键
                    key_points.append(sentence)
        
        return key_points[:10]
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """估算令牌数"""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            # 简单估算
            chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            other_chars = len(content) - chinese_chars
            total += chinese_chars // 2 + other_chars // 4 + 1
        return total
    
    def compress_with_priority(
        self,
        messages: List[Dict[str, Any]],
        priority_threshold: int = 2
    ) -> Tuple[List[Dict[str, str]], CompressionResult]:
        """
        基于优先级的压缩
        
        Args:
            messages: 带优先级的消息列表
            priority_threshold: 优先级阈值（低于此值的会被压缩）
            
        Returns:
            (压缩后的消息, 压缩结果)
        """
        high_priority = []
        low_priority = []
        
        for msg in messages:
            priority = msg.get("priority", 1)
            if priority >= priority_threshold:
                high_priority.append({"role": msg["role"], "content": msg["content"]})
            else:
                low_priority.append({"role": msg["role"], "content": msg["content"]})
        
        if not low_priority:
            return high_priority, CompressionResult(
                original_tokens=self._estimate_tokens(high_priority),
                compressed_tokens=self._estimate_tokens(high_priority),
                compression_ratio=1.0,
                summary="All messages high priority",
                preserved_items=len(high_priority)
            )
        
        # 压缩低优先级消息
        summary = self._generate_summary(low_priority)
        
        compressed = []
        if summary:
            compressed.append({
                "role": "system",
                "content": f"[Compressed Context]\n{summary}"
            })
        compressed.extend(high_priority)
        
        original_tokens = self._estimate_tokens(messages)
        compressed_tokens = self._estimate_tokens(compressed)
        
        return compressed, CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            summary=summary,
            preserved_items=len(high_priority)
        )
    
    def multi_level_compress(
        self,
        messages: List[Dict[str, str]],
        levels: int = 3
    ) -> Tuple[List[Dict[str, str]], List[CompressionResult]]:
        """
        多级压缩
        
        Args:
            messages: 消息列表
            levels: 压缩级别数
            
        Returns:
            (最终消息, 各级压缩结果)
        """
        results = []
        current_messages = messages
        
        for level in range(levels):
            # 每级保留更少的消息
            keep = max(self.preserve_recent - level, 1)
            
            compressed, result = self.compress_messages(current_messages, keep_full=keep)
            results.append(result)
            
            # 检查是否达到目标
            if result.compression_ratio <= self.target_compression_ratio:
                break
            
            current_messages = compressed
        
        return current_messages, results
    
    def get_compression_recommendation(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        current_tokens: int
    ) -> Dict[str, Any]:
        """
        获取压缩建议
        
        Args:
            messages: 消息列表
            max_tokens: 最大令牌数
            current_tokens: 当前令牌数
            
        Returns:
            建议信息
        """
        if current_tokens <= max_tokens:
            return {
                "need_compression": False,
                "utilization": current_tokens / max_tokens,
                "recommendation": "No compression needed"
            }
        
        # 模拟压缩
        compressed, result = self.compress_messages(messages)
        
        return {
            "need_compression": True,
            "utilization": current_tokens / max_tokens,
            "potential_ratio": result.compression_ratio,
            "potential_savings": result.original_tokens - result.compressed_tokens,
            "recommendation": f"Compress to save {result.original_tokens - result.compressed_tokens} tokens"
        }
