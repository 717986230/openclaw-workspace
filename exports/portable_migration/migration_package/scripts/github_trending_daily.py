"""
GitHub Trending 每日自动化脚本
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from erbing_system.social.github_trending_tracker import (
    daily_scan,
    auto_contribute,
    get_scan_history,
    get_statistics,
)


async def main():
    """主函数"""
    print("=" * 60)
    print("GitHub Trending 每日自动化")
    print("=" * 60)
    print(f"开始时间: {datetime.now().isoformat()}")

    try:
        # 1. 每日扫描
        print("\n[STEP 1] 每日扫描热门项目")
        print("-" * 60)
        scan_result = await daily_scan()

        print(f"\n扫描结果:")
        print(f"  时间戳: {scan_result['timestamp']}")
        print(f"  热门项目数: {len(scan_result['trending'])}")
        print(f"  贡献机会数: {len(scan_result['opportunities'])}")

        # 显示热门项目
        print(f"\n热门项目:")
        for repo in scan_result['trending']:
            print(f"  - {repo['owner']}/{repo['name']}")
            print(f"    Stars: {repo['stars']}")
            print(f"    Language: {repo['language']}")
            print(f"    Issues: {repo['issues']}")

        # 显示贡献机会
        print(f"\n贡献机会:")
        for i, opp in enumerate(scan_result['opportunities'][:10], 1):
            print(f"  {i}. {opp['repo']}: {opp['description']} (优先级: {opp['priority']})")

        # 2. 自动贡献（可选）
        print("\n[STEP 2] 自动贡献")
        print("-" * 60)
        print("是否要自动创建 PR？(y/n): ", end="")

        # 自动选择 'y' 用于自动化
        choice = 'y'

        if choice.lower() == 'y':
            prs = await auto_contribute(max_prs=3)
            print(f"\n创建了 {len(prs)} 个 PR:")
            for pr in prs:
                print(f"  - {pr.repo_name}: {pr.title}")
                print(f"    URL: {pr.pr_url}")
                print(f"    状态: {pr.status}")
        else:
            print("跳过自动贡献")

        # 3. 获取统计信息
        print("\n[STEP 3] 统计信息")
        print("-" * 60)
        stats = get_statistics()

        print(f"总扫描次数: {stats['total_scans']}")
        print(f"总贡献机会: {stats['total_opportunities']}")
        print(f"平均机会/扫描: {stats['avg_opportunities_per_scan']:.2f}")

        # 4. 获取最近扫描历史
        print("\n[STEP 4] 最近扫描历史")
        print("-" * 60)
        recent_scans = get_scan_history(days=7)

        print(f"最近 7 天的扫描:")
        for scan in recent_scans:
            print(f"  - {scan['timestamp']}: {scan['trending_count']} 个项目, {scan['opportunities_count']} 个机会")

        print("\n" + "=" * 60)
        print(f"完成时间: {datetime.now().isoformat()}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
