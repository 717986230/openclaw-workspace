# -*- coding: utf-8 -*-
"""
执行所有项目 - Execute All Projects
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from all_projects_implementation import (
    get_all_projects_implementation,
    execute_all_projects,
)


def main():
    """主函数"""
    print("=" * 60)
    print("All Projects Execution")
    print("=" * 60)

    try:
        # 执行所有项目
        success = execute_all_projects()

        if success:
            print("\n" + "=" * 60)
            print("[PASS] All projects executed successfully!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("[FAIL] Some projects failed")
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
