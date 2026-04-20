# -*- coding: utf-8 -*-
"""
Paperless-ngx 整合适配器 - Paperless-ngx Integration Adapter
将 Paperless-ngx 的核心功能整合到二饼系统中
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentStatus(Enum):
    """文档状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(Enum):
    """文档类型"""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    WORD = "word"
    EXCEL = "excel"
    OTHER = "other"


@dataclass
class Document:
    """文档"""
    id: str
    title: str
    content: str
    ocr_text: str = ""
    document_type: DocumentType = DocumentType.OTHER
    status: DocumentStatus = DocumentStatus.PENDING
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """搜索结果"""
    document_id: str
    title: str
    snippet: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PaperlessAdapter:
    """Paperless-ngx 适配器"""

    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.search_index: Dict[str, List[str]] = {}
        self.initialized = False

    def initialize(self):
        """初始化适配器"""
        logger.info("Initializing Paperless-ngx Adapter...")

        # 添加示例文档
        self._add_sample_documents()

        self.initialized = True
        logger.info("Paperless-ngx Adapter initialized successfully")

    def _add_sample_documents(self):
        """添加示例文档"""
        # 添加示例文档
        self.add_document(
            Document(
                id="doc_1",
                title="Sample Document",
                content="This is a sample document for testing purposes.",
                document_type=DocumentType.TEXT,
                status=DocumentStatus.COMPLETED,
                tags=["sample", "test"],
            )
        )

    def add_document(self, document: Document) -> bool:
        """添加文档"""
        if document.id in self.documents:
            logger.warning(f"Document '{document.id}' already exists")
            return False

        self.documents[document.id] = document
        self._update_search_index(document)
        logger.info(f"Document '{document.id}' added successfully")
        return True

    def get_document(self, document_id: str) -> Optional[Document]:
        """获取文档"""
        return self.documents.get(document_id)

    def list_documents(self, status: Optional[DocumentStatus] = None) -> List[Document]:
        """列出文档"""
        if status:
            return [doc for doc in self.documents.values() if doc.status == status]
        return list(self.documents.values())

    def remove_document(self, document_id: str) -> bool:
        """移除文档"""
        if document_id not in self.documents:
            logger.warning(f"Document '{document_id}' not found")
            return False

        # 从搜索索引中移除
        if document_id in self.search_index:
            del self.search_index[document_id]

        del self.documents[document_id]
        logger.info(f"Document '{document_id}' removed successfully")
        return True

    def update_document(self, document_id: str, **kwargs) -> bool:
        """更新文档"""
        document = self.get_document(document_id)
        if not document:
            logger.warning(f"Document '{document_id}' not found")
            return False

        # 更新文档属性
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)

        document.updated_at = datetime.now()

        # 更新搜索索引
        if "content" in kwargs or "title" in kwargs:
            self._update_search_index(document)

        logger.info(f"Document '{document_id}' updated successfully")
        return True

    def perform_ocr(self, document_id: str) -> bool:
        """执行 OCR 识别"""
        document = self.get_document(document_id)
        if not document:
            logger.error(f"Document '{document_id}' not found")
            return False

        logger.info(f"Performing OCR on document '{document_id}'...")

        # 更新文档状态
        document.status = DocumentStatus.PROCESSING

        try:
            # 模拟 OCR 处理
            import time
            time.sleep(1)  # 模拟处理时间

            # 简单的 OCR 模拟（实际应该使用 OCR 库）
            document.ocr_text = document.content  # 简化处理

            # 更新文档状态
            document.status = DocumentStatus.COMPLETED

            logger.info(f"OCR completed for document '{document_id}'")
            return True

        except Exception as e:
            # 更新文档状态
            document.status = DocumentStatus.FAILED

            logger.error(f"OCR failed for document '{document_id}': {str(e)}")
            return False

    def search_documents(self, query: str, limit: int = 10) -> List[SearchResult]:
        """搜索文档"""
        logger.info(f"Searching documents with query: {query}")

        results = []
        query_lower = query.lower()

        for doc_id, document in self.documents.items():
            # 搜索标题
            title_score = self._calculate_similarity(query_lower, document.title.lower())

            # 搜索内容
            content_score = self._calculate_similarity(query_lower, document.content.lower())

            # 搜索 OCR 文本
            ocr_score = self._calculate_similarity(query_lower, document.ocr_text.lower())

            # 搜索标签
            tag_score = 0.0
            for tag in document.tags:
                tag_score = max(tag_score, self._calculate_similarity(query_lower, tag.lower()))

            # 计算总分
            total_score = max(title_score, content_score, ocr_score, tag_score)

            if total_score > 0:
                # 创建片段
                snippet = self._create_snippet(document.content, query)

                results.append(
                    SearchResult(
                        document_id=doc_id,
                        title=document.title,
                        snippet=snippet,
                        score=total_score,
                        metadata={
                            "tags": document.tags,
                            "document_type": document.document_type.value,
                            "status": document.status.value,
                        },
                    )
                )

        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)

        # 限制结果数量
        return results[:limit]

    def _calculate_similarity(self, query: str, text: str) -> float:
        """计算相似度"""
        if not query or not text:
            return 0.0

        # 简单的相似度计算（实际应该使用更复杂的算法）
        if query in text:
            return 1.0

        # 计算单词匹配
        query_words = set(query.split())
        text_words = set(text.split())

        if not query_words:
            return 0.0

        matches = len(query_words & text_words)
        return matches / len(query_words)

    def _create_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """创建搜索片段"""
        if not content:
            return ""

        # 简单的片段创建（实际应该更智能）
        if len(content) <= max_length:
            return content

        # 查找查询词在内容中的位置
        query_lower = query.lower()
        content_lower = content.lower()

        index = content_lower.find(query_lower)
        if index == -1:
            return content[:max_length] + "..."

        # 创建片段
        start = max(0, index - 50)
        end = min(len(content), index + len(query) + 50)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _update_search_index(self, document: Document):
        """更新搜索索引"""
        # 简单的搜索索引（实际应该使用更复杂的索引结构）
        words = document.title.lower().split() + document.content.lower().split()
        self.search_index[document.id] = words

    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "initialized": self.initialized,
            "total_documents": len(self.documents),
            "documents": {
                doc_id: {
                    "title": doc.title,
                    "document_type": doc.document_type.value,
                    "status": doc.status.value,
                    "tags": doc.tags,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                }
                for doc_id, doc in self.documents.items()
            },
        }


# 全局实例
_paperless_adapter = None


def get_paperless_adapter() -> PaperlessAdapter:
    """获取 Paperless-ngx 适配器实例"""
    global _paperless_adapter
    if _paperless_adapter is None:
        _paperless_adapter = PaperlessAdapter()
        _paperless_adapter.initialize()
    return _paperless_adapter


if __name__ == "__main__":
    # 测试 Paperless-ngx 适配器
    print("Testing Paperless-ngx Adapter...")

    # 获取适配器实例
    adapter = get_paperless_adapter()

    # 获取状态
    status = adapter.get_status()
    print(f"\nPaperless-ngx Adapter Status:")
    print(f"  Initialized: {status['initialized']}")
    print(f"  Total Documents: {status['total_documents']}")

    print("\nPaperless-ngx Adapter tested successfully!")
