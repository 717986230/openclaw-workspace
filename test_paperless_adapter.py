# -*- coding: utf-8 -*-
"""
测试 Paperless-ngx 适配器 - Test Paperless-ngx Adapter
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from erbing_system.paperless_adapter import (
    get_paperless_adapter,
    Document,
    DocumentStatus,
    DocumentType,
)


def test_paperless_adapter():
    """测试 Paperless-ngx 适配器"""
    print("=" * 60)
    print("Testing Paperless-ngx Adapter")
    print("=" * 60)

    try:
        # 获取适配器实例
        adapter = get_paperless_adapter()

        # 测试 1: 添加文档
        print("\n[Test 1] Adding document...")
        document = Document(
            id="test_doc",
            title="Test Document",
            content="This is a test document for testing purposes.",
            document_type=DocumentType.TEXT,
            status=DocumentStatus.PENDING,
            tags=["test", "document"],
        )
        success = adapter.add_document(document)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 2: 获取文档
        print("\n[Test 2] Getting document...")
        retrieved_doc = adapter.get_document("test_doc")
        print(f"  Result: {'PASS' if retrieved_doc is not None else 'FAIL'}")

        # 测试 3: 列出文档
        print("\n[Test 3] Listing documents...")
        documents = adapter.list_documents()
        print(f"  Result: {'PASS' if len(documents) > 0 else 'FAIL'}")

        # 测试 4: 更新文档
        print("\n[Test 4] Updating document...")
        success = adapter.update_document("test_doc", title="Updated Test Document")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 5: 执行 OCR
        print("\n[Test 5] Performing OCR...")
        success = adapter.perform_ocr("test_doc")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 6: 搜索文档
        print("\n[Test 6] Searching documents...")
        results = adapter.search_documents("test")
        print(f"  Result: {'PASS' if len(results) > 0 else 'FAIL'}")

        # 测试 7: 获取状态
        print("\n[Test 7] Getting status...")
        status = adapter.get_status()
        print(f"  Result: {'PASS' if status['initialized'] else 'FAIL'}")

        # 测试 8: 移除文档
        print("\n[Test 8] Removing document...")
        success = adapter.remove_document("test_doc")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        print("\n" + "=" * 60)
        print("[PASS] All Paperless-ngx Adapter tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_paperless_adapter()
    sys.exit(0 if success else 1)
