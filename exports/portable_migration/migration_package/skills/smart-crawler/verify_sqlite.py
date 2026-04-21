"""
快速验证 SQLite 数据库功能
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from database_storage import DatabaseStorage

def main():
    print("=" * 60)
    print("SQLite 数据库功能验证")
    print("=" * 60)
    print()

    try:
        # 测试 SQLite 连接
        print("1. 测试 SQLite 连接...")
        db = DatabaseStorage(db_type="sqlite", db_path="verification_test.db")
        print("   ✅ SQLite 连接成功！")

        # 测试创建任务
        print()
        print("2. 测试创建任务...")
        task_id = db.create_task("验证测试", "https://example.com")
        print(f"   ✅ 创建任务成功！ID: {task_id}")

        # 测试保存结果
        print()
        print("3. 测试保存结果...")
        result_id = db.save_result(
            task_id=task_id,
            url="https://example.com",
            title="验证页面",
            extracted_data={"test": "data", "number": 123}
        )
        print(f"   ✅ 保存结果成功！ID: {result_id}")

        # 测试查询结果
        print()
        print("4. 测试查询结果...")
        results = db.get_results(task_id=task_id)
        print(f"   ✅ 查询结果成功！找到 {len(results)} 条记录")

        if results:
            result = results[0]
            print(f"   - URL: {result['url']}")
            print(f"   - 标题: {result['title']}")
            print(f"   - 数据: {result['extracted_data']}")

        # 测试统计
        print()
        print("5. 测试统计信息...")
        stats = db.get_statistics()
        print(f"   ✅ 统计信息: {stats}")

        # 测试导出
        print()
        print("6. 测试导出功能...")
        csv_path = db.export_to_csv(task_id, "verification_results.csv")
        print(f"   ✅ CSV 导出成功: {csv_path}")

        db.close()

        print()
        print("=" * 60)
        print("✅ 所有验证通过！SQLite 数据库功能正常！")
        print("=" * 60)
        print()

        print("生成的文件：")
        print("  - verification_test.db (SQLite 数据库)")
        print("  - verification_results.csv (导出的 CSV 文件)")
        print()

        print("下一步：")
        print("  1. 安装 MySQL（可选）")
        print("  2. 开始使用爬虫存储功能")
        print("  3. 查看 QUICK_START_DATABASE.md 了解详细用法")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 验证失败！")
        print("=" * 60)
        print()
        print(f"错误信息: {e}")
        print()

        import traceback
        traceback.print_exc()

        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
