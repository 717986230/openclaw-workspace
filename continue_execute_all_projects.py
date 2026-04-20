# -*- coding: utf-8 -*-
"""
继续执行所有项目 - Continue Execute All Projects
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from all_projects_implementation import get_all_projects_implementation


def main():
    """主函数"""
    print("=" * 60)
    print("Continue Execute All Projects")
    print("=" * 60)

    # 获取系统实例
    system = get_all_projects_implementation()

    # 获取状态
    status = system.get_status()
    print(f"\nCurrent Status:")
    print(f"  Total Projects: {status['total_projects']}")
    print(f"  Completed: {status['completed_projects']}")
    print(f"  In Progress: {status['in_progress_projects']}")
    print(f"  Not Started: {status['not_started_projects']}")
    print(f"  Overall Progress: {status['overall_progress']:.1f}%")

    # 列出所有项目
    print(f"\nAll Projects:")
    for project in system.list_projects():
        print(f"  - {project.name}: {project.description} ({project.status.value})")

    # 继续执行未完成的项目
    print(f"\nContinuing execution...")

    # 执行未完成的项目
    for project in system.list_projects():
        if project.status.value in ["not_started", "in_progress"]:
            print(f"\nExecuting project: {project.name}")
            success = system.execute_project(project.name)
            if success:
                print(f"  [PASS] {project.name} completed")
            else:
                print(f"  [FAIL] {project.name} failed")

    # 获取最终状态
    status = system.get_status()
    print(f"\nFinal Status:")
    print(f"  Overall Progress: {status['overall_progress']:.1f}%")
    print(f"  Completed: {status['completed_projects']}")
    print(f"  Failed: {status['failed_projects']}")

    print("\n" + "=" * 60)
    print("Execution completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
