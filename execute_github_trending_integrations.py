# -*- coding: utf-8 -*-
"""
执行所有 GitHub Trending 整合任务 - Execute All GitHub Trending Integration Tasks
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_trending_integration_to_erbing import (
    get_github_trending_integration_to_erbing,
    execute_all_github_trending_integrations,
)


def main():
    """主函数"""
    print("=" * 60)
    print("Execute All GitHub Trending Integration Tasks")
    print("=" * 60)

    try:
        # 执行所有 GitHub Trending 整合任务
        success = execute_all_github_trending_integrations()

        if success:
            print("\n" + "=" * 60)
            print("[PASS] All GitHub Trending integration tasks executed successfully!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("[FAIL] Some GitHub Trending integration tasks failed")
            print("=" * 60)

        return success

    except Exception as e:
        print(f"\n[FAIL] Execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
