#!/usr/bin/env python3
"""
Erbing 扩展架构 - Reflection（反思机制）
实现自我批评和改进循环
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 数据库路径
sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ErbingReflection:
    """
    Reflection 架构实现

    流程：
    1. 生成初稿
    2. 自我批评
    3. 改进建议
    4. 生成最终版
    """

    def __init__(self, model_interface=None):
        self.memory = get_memory()
        self.model = model_interface
        self.max_iterations = 3  # 最多反思3轮

    def generate_with_reflection(
        self,
        query: str,
        context: str = "",
        reflection_mode: str = "balanced"
    ) -> Dict:
        """
        带反思的生成

        参数:
            query: 用户查询
            context: 上下文
            reflection_mode: 反思模式
                - "quick": 快速模式（1轮反思）
                - "balanced": 平衡模式（2轮反思）
                - "deep": 深度模式（3轮反思）

        返回:
            {
                "draft": 初稿,
                "critiques": 批评列表,
                "improvements": 改进列表,
                "final": 最终版本,
                "iterations": 实际迭代次数
            }
        """
        # 根据模式设置迭代次数
        iterations_map = {"quick": 1, "balanced": 2, "deep": 3}
        max_iterations = iterations_map.get(reflection_mode, 2)

        # 检索相关记忆作为上下文
        relevant_memories = self.memory.search(query, limit=5)
        memory_context = "\n".join([m["content"][:200] for m in relevant_memories[:3]])

        # 1. 生成初稿
        draft = self._generate_draft(query, context + "\n" + memory_context)

        current_output = draft
        critiques = []
        improvements = []

        # 2. 反思循环
        for i in range(max_iterations):
            # 批评
            critique = self._critique_output(query, current_output)
            critiques.append(critique)

            # 如果批评很轻，可以提前结束
            if critique["score"] >= 9:
                break

            # 改进
            improvement = self._improve_output(
                query, current_output, critique
            )
            improvements.append(improvement)

            # 更新当前输出
            current_output = improvement["output"]

        # 3. 保存反思记录到数据库
        self._save_reflection_to_memory(query, draft, critiques, current_output)

        return {
            "draft": draft,
            "critiques": critiques,
            "improvements": improvements,
            "final": current_output,
            "iterations": len(critiques)
        }

    def _generate_draft(self, query: str, context: str) -> str:
        """生成初稿"""
        # 如果有模型接口，调用模型
        if self.model:
            return self.model.generate(f"Context: {context}\n\nQuery: {query}")

        # 否则使用模板（模拟）
        return f"[初稿] 针对 '{query}' 的回答：\n基于当前上下文，我的初步建议是..."

    def _critique_output(self, query: str, output: str) -> Dict:
        """批评输出"""
        critique_prompt = f"""
请批评以下输出的质量：

查询: {query}

输出: {output}

批评维度:
1. 准确性（1-10分）
2. 完整性（1-10分）
3. 清晰度（1-10分）
4. 相关性（1-10分）

请指出具体问题并给出改进建议。
"""
        # 如果有模型接口
        if self.model:
            critique_text = self.model.generate(critique_prompt)
        else:
            # 模拟批评
            critique_text = f"""
批评分析：
1. 准确性：7/10 - 部分内容需要验证
2. 完整性：6/10 - 缺少细节说明
3. 清晰度：8/10 - 表达较为清晰
4. 相关性：9/10 - 与查询高度相关

改进建议：
- 补充具体实例
- 验证数据准确性
- 增加结构化输出
"""

        # 解析批评
        score = self._parse_critique_score(critique_text)

        return {
            "text": critique_text,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }

    def _parse_critique_score(self, critique_text: str) -> float:
        """解析批评分数"""
        import re

        # 提取所有分数（格式：数字/10）
        scores = re.findall(r'(\d+)/10', critique_text)

        if scores:
            return sum(int(s) for s in scores) / len(scores)
        return 7.0  # 默认分数

    def _improve_output(self, query: str, current_output: str, critique: Dict) -> Dict:
        """改进输出"""
        improve_prompt = f"""
根据批评改进输出：

查询: {query}

当前输出: {current_output}

批评: {critique['text']}

请提供改进后的输出：
"""

        # 如果有模型接口
        if self.model:
            improved_output = self.model.generate(improve_prompt)
        else:
            # 模拟改进
            improved_output = f"{current_output}\n\n[改进] {critique['text'][:100]}"

        return {
            "output": improved_output,
            "based_on_critique": critique["text"][:200],
            "timestamp": datetime.now().isoformat()
        }

    def _save_reflection_to_memory(self, query, draft, critiques, final):
        """保存反思记录到数据库"""
        conn = self.memory.sqlite_conn
        cursor = conn.cursor()

        # 提取关键信息
        avg_score = sum(c["score"] for c in critiques) / len(critiques) if critiques else 0

        content = f"""
查询: {query}

初稿:
{draft[:500]}

批评轮数: {len(critiques)}
平均分数: {avg_score:.1f}

最终版本:
{final[:500]}
"""

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            'reflection',
            f'Reflection: {query[:50]}',
            content,
            'reflection',
            'reflection, critique, improvement',
            int(avg_score)
        ))

        conn.commit()


# 示例使用
def example_usage():
    """示例：使用 Reflection 架构"""
    print("="*60)
    print("Erbing Reflection Architecture - Example")
    print("="*60)

    reflection = ErbingReflection()

    # 测试查询
    query = "如何设计一个高效的记忆检索系统？"

    print(f"\n[Query] {query}")
    print("\n[Generating with reflection...]")

    result = reflection.generate_with_reflection(
        query,
        reflection_mode="balanced"
    )

    print(f"\n[Draft]\n{result['draft'][:200]}...")
    print(f"\n[Critiques] {len(result['critiques'])} rounds")
    print(f"[Final]\n{result['final'][:200]}...")
    print(f"\n[Iterations] {result['iterations']}")


if __name__ == "__main__":
    example_usage()
