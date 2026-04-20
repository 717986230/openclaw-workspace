"""
SWE-agent Example Usage - 示例代码
演示如何使用 SWE-agent 处理 GitHub Issue 和创建 PR
"""

import sys
sys.path.insert(0, '..')

from swe_agent.core.agent import SWEAgent
from swe_agent.github import IssueHandler
from swe_agent.pr import PRCreator, CodeReviewer


def example_handle_issue():
    """示例：处理 GitHub Issue"""
    print("=" * 60)
    print("示例 1: 处理 GitHub Issue")
    print("=" * 60)
    
    # 创建 Agent
    agent = SWEAgent()
    
    # 处理 Issue
    repo = "owner/repository"  # 替换为实际仓库
    issue_number = 1
    
    print(f"\n处理 Issue #{issue_number} 在 {repo}...")
    print(f"Agent 状态: {agent.get_status()}")
    
    # 实际使用时取消注释
    # result = agent.handle_issue(repo, issue_number, auto_fix=False)
    # print(f"结果: {result.message}")
    # print(f"数据: {result.data}")
    
    print("\n提示: 取消注释上面的代码来实际执行")


def example_classify_issue():
    """示例：Issue 分类"""
    print("\n" + "=" * 60)
    print("示例 2: Issue 分类")
    print("=" * 60)
    
    from swe_agent.issues import IssueClassifier
    
    classifier = IssueClassifier()
    
    # 测试 Issue
    title = "应用程序在启动时崩溃"
    body = """
    应用程序在启动时立即崩溃，显示以下错误：
    
    Error: NullPointerException at line 42
    
    复现步骤：
    1. 启动应用程序
    2. 观察崩溃
    """
    
    print(f"\n标题: {title}")
    print(f"内容: {body[:100]}...")
    
    # 实际使用时取消注释
    # result = classifier.classify(title, body)
    # print(f"\n分类结果:")
    # print(f"  类型: {result.category}")
    # print(f"  子类型: {result.subcategory}")
    # print(f"  置信度: {result.confidence}")
    # print(f"  关键词: {result.keywords}")
    
    print("\n提示: 取消注释上面的代码来实际执行")


def example_detect_bug():
    """示例：Bug 检测"""
    print("\n" + "=" * 60)
    print("示例 3: Bug 检测")
    print("=" * 60)
    
    from swe_agent.issues import BugDetector
    
    detector = BugDetector()
    
    # 测试 Bug 报告
    title = "SQL 注入漏洞"
    body = """
    在登录功能中发现 SQL 注入漏洞：
    
    错误信息: Error: SQL syntax error
    堆栈跟踪: 
      File "login.py", line 42
        query = "SELECT * FROM users WHERE username = '" + username + "'"
    
    复现步骤：
    1. 输入用户名: ' OR '1'='1
    2. 观察异常行为
    """
    
    print(f"\n标题: {title}")
    print(f"内容: {body[:100]}...")
    
    # 实际使用时取消注释
    # bug_info = detector.detect_bug(title, body)
    # print(f"\nBug 信息:")
    # print(f"  类型: {bug_info.bug_type.value}")
    # print(f"  严重程度: {bug_info.severity.value}")
    # print(f"  错误消息: {bug_info.error_message}")
    # print(f"  受影响组件: {bug_info.affected_components}")
    
    print("\n提示: 取消注释上面的代码来实际执行")


def example_create_pr():
    """示例：创建 PR"""
    print("\n" + "=" * 60)
    print("示例 4: 创建 Pull Request")
    print("=" * 60)
    
    creator = PRCreator()
    
    print("\n从 Bug 修复创建 PR...")
    
    # 实际使用时取消注释
    # pr_data = creator.create_from_fix(
    #     repo="owner/repository",
    #     issue_number=1,
    #     files_changed=["src/main.py", "tests/test_main.py"],
    #     commit_message="Fix: 修复 SQL 注入漏洞"
    # )
    # 
    # print(f"\nPR 数据:")
    # print(f"  标题: {pr_data['title']}")
    # print(f"  分支: {pr_data['head']}")
    # print(f"  关联 Issue: #{pr_data['issue_number']}")
    
    print("\n提示: 取消注释上面的代码来实际执行")


def example_code_review():
    """示例：代码审查"""
    print("\n" + "=" * 60)
    print("示例 5: 代码审查")
    print("=" * 60)
    
    reviewer = CodeReviewer()
    
    # 测试代码
    code_changes = {
        "main.py": """
def login(username, password):
    # 潜在的 SQL 注入
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    
    # 硬编码密码
    admin_password = "admin123"
    
    return execute_query(query)
"""
    }
    
    print("\n审查代码变更...")
    print(f"文件: {list(code_changes.keys())[0]}")
    
    # 实际使用时取消注释
    # result = reviewer.review_pr(
    #     repo="owner/repository",
    #     pr_number=1,
    #     code_changes=code_changes
    # )
    # 
    # print(f"\n审查结果:")
    # print(f"  总分: {result.overall_score}/10")
    # print(f"  安全评分: {result.security_score}/10")
    # print(f"  质量评分: {result.quality_score}/10")
    # print(f"  批准: {'是' if result.approve else '否'}")
    # print(f"\n总结:")
    # print(result.summary)
    # 
    # if result.recommendations:
    #     print(f"\n建议:")
    #     for rec in result.recommendations:
    #         print(f"  - {rec}")
    
    print("\n提示: 取消注释上面的代码来实际执行")


def example_batch_process():
    """示例：批量处理"""
    print("\n" + "=" * 60)
    print("示例 6: 批量处理 Issues")
    print("=" * 60)
    
    agent = SWEAgent()
    
    # Issue 列表
    issues = [1, 2, 3, 4, 5]
    
    print(f"\n批量处理 {len(issues)} 个 Issues...")
    
    # 实际使用时取消注释
    # results = agent.batch_process_issues(
    #     repo="owner/repository",
    #     issue_numbers=issues
    # )
    # 
    # success_count = sum(1 for r in results if r.success)
    # print(f"\n处理完成: {success_count}/{len(issues)} 成功")
    # 
    # for i, result in enumerate(results):
    #     status = "✓" if result.success else "✗"
    #     print(f"  {status} Issue #{issues[i]}: {result.message}")
    
    print("\n提示: 取消注释上面的代码来实际执行")


def example_integration_with_openclaw():
    """示例：与 OpenClaw 集成"""
    print("\n" + "=" * 60)
    print("示例 7: 与 OpenClaw 集成")
    print("=" * 60)
    
    print("\n使用 OpenClaw LLM 路由:")
    print("  - ask_local_ai_routed(prompt, mode='claude_only')")
    print("  - ask_local_ai_routed(prompt, mode='claude_then_codex_review')")
    print()
    print("使用 OpenClaw Memory:")
    print("  - memory_store.store(key, value, metadata)")
    print("  - memory_store.query(filters)")
    print("  - memory_store.search(query)")
    print()
    print("SWE-agent 自动使用这些 OpenClaw 功能进行:")
    print("  ✓ Issue 分类")
    print("  ✓ Bug 检测")
    print("  ✓ 代码审查")
    print("  ✓ 修复建议生成")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("SWE-agent 使用示例")
    print("=" * 60)
    
    example_handle_issue()
    example_classify_issue()
    example_detect_bug()
    example_create_pr()
    example_code_review()
    example_batch_process()
    example_integration_with_openclaw()
    
    print("\n" + "=" * 60)
    print("所有示例完成")
    print("=" * 60)
    print("\n提示: 取消注释各示例中的代码来实际执行")
    print("注意: 需要设置 GITHUB_TOKEN 环境变量才能访问 GitHub API")


if __name__ == "__main__":
    main()
