"""
MetaGPT 集成示例 - 简单应用开发

演示如何使用 MetaGPT 多智能体协作开发一个简单的应用。
"""

import asyncio
from integrations.metagpt.workflows import SoftwareDevelopmentWorkflow
from integrations.metagpt.roles import ProductManager, Architect, Engineer


async def example_simple_app():
    """
    示例：开发一个简单的待办事项应用
    
    展示完整的软件开发流程。
    """
    
    # 定义需求
    requirement = """
    创建一个简单的命令行待办事项（Todo）应用，支持以下功能：
    
    1. 添加待办事项
    2. 列出所有待办事项
    3. 标记待办事项为完成
    4. 删除待办事项
    5. 数据持久化到文件
    
    技术要求：
    - 使用 Python
    - 数据存储使用 JSON 文件
    - 提供清晰的命令行界面
    """
    
    # 创建软件开发工作流
    workflow = SoftwareDevelopmentWorkflow()
    
    # 运行工作流
    print("🚀 开始软件开发流程...")
    print("=" * 60)
    
    result = await workflow.run(
        requirement=requirement,
        project_name="todo_app"
    )
    
    # 查看结果
    print("\n📊 开发结果:")
    print(f"状态: {result['status']}")
    
    if result['status'] == 'success':
        print("\n📦 交付物:")
        for key, value in result['deliverables'].items():
            print(f"\n{key.upper()}:")
            print("-" * 40)
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"  {k}: {len(str(v))} 字符")
            else:
                print(value[:500] if len(str(value)) > 500 else value)
    
    return result


async def example_code_review():
    """
    示例：代码审查
    
    展示如何使用代码审查工作流。
    """
    from integrations.metagpt.workflows import CodeReviewWorkflow
    
    # 待审查的代码
    source_code = {
        "todo.py": '''
class TodoList:
    def __init__(self):
        self.items = []
    
    def add(self, item):
        self.items.append({"text": item, "completed": False})
    
    def list(self):
        return self.items
    
    def complete(self, index):
        if 0 <= index < len(self.items):
            self.items[index]["completed"] = True
    
    def delete(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
''',
        "main.py": '''
from todo import TodoList

def main():
    todo = TodoList()
    todo.add("Buy groceries")
    todo.add("Read book")
    print(todo.list())

if __name__ == "__main__":
    main()
'''
    }
    
    # 创建代码审查工作流
    workflow = CodeReviewWorkflow()
    
    # 运行审查
    print("\n🔍 开始代码审查...")
    print("=" * 60)
    
    result = await workflow.run(
        source_code=source_code,
        project_name="todo_app"
    )
    
    # 查看结果
    print("\n📊 审查结果:")
    print(f"状态: {result['status']}")
    
    if result['status'] == 'success':
        print("\n📄 审查报告:")
        print(result['report'])
    
    return result


async def example_code_generation():
    """
    示例：代码生成
    
    展示如何使用代码生成器。
    """
    from integrations.metagpt.code_gen import CodeGenerator
    
    # 创建代码生成器
    generator = CodeGenerator()
    
    # 生成类代码
    print("\n⚙️ 生成类代码:")
    print("=" * 60)
    
    class_code = await generator.generate_class(
        class_name="UserManager",
        attributes=[
            {"name": "users", "type": "List[User]"},
            {"name": "current_user", "type": "Optional[User]"}
        ],
        methods=[
            {
                "name": "add_user",
                "params": [{"name": "user", "type": "User"}],
                "return_type": "None",
                "body": "self.users.append(user)"
            },
            {
                "name": "get_user",
                "params": [{"name": "user_id", "type": "int"}],
                "return_type": "Optional[User]",
                "body": "for user in self.users:\n    if user.id == user_id:\n        return user\nreturn None"
            }
        ]
    )
    
    print(class_code)
    
    # 生成测试代码
    print("\n🧪 生成测试代码:")
    print("=" * 60)
    
    test_code = await generator.generate_test(
        target="user_manager",
        test_type="unit"
    )
    
    print(test_code)
    
    return {
        "class_code": class_code,
        "test_code": test_code
    }


async def example_role_collaboration():
    """
    示例：角色协作
    
    展示不同角色如何协作完成一个任务。
    """
    print("\n👥 角色协作示例:")
    print("=" * 60)
    
    # 创建角色
    pm = ProductManager()
    architect = Architect()
    engineer = Engineer()
    
    # 查看角色信息
    print("\n产品经理:")
    print(f"  名称: {pm.name}")
    print(f"  目标: {pm.goal}")
    
    print("\n架构师:")
    print(f"  名称: {architect.name}")
    print(f"  目标: {architect.goal}")
    
    print("\n工程师:")
    print(f"  名称: {engineer.name}")
    print(f"  目标: {engineer.goal}")
    
    # 模拟协作流程
    print("\n🔄 协作流程:")
    print("1. 产品经理分析需求 -> 编写 PRD")
    print("2. 架构师阅读 PRD -> 设计系统架构")
    print("3. 工程师根据设计 -> 实现代码")
    print("4. QA 工程师测试代码 -> 报告结果")
    print("5. 项目经理汇总 -> 交付项目")


async def main():
    """运行所有示例"""
    print("=" * 60)
    print("MetaGPT 集成示例")
    print("=" * 60)
    
    # 示例 1: 完整软件开发流程
    await example_simple_app()
    
    # 示例 2: 代码审查
    await example_code_review()
    
    # 示例 3: 代码生成
    await example_code_generation()
    
    # 示例 4: 角色协作
    await example_role_collaboration()
    
    print("\n✅ 所有示例完成！")


if __name__ == "__main__":
    asyncio.run(main())
