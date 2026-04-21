#!/usr/bin/env python3
"""
Markdown格式化工具 - 快速生成标准MD格式
"""
import sys
from pathlib import Path

class MDFormatter:
    """Markdown格式化器"""
    
    def __init__(self):
        self.output = []
    
    def h1(self, text):
        """一级标题"""
        self.output.append(f"# {text}\n")
        return self
    
    def h2(self, text):
        """二级标题"""
        self.output.append(f"## {text}\n")
        return self
    
    def h3(self, text):
        """三级标题"""
        self.output.append(f"### {text}\n")
        return self
    
    def table(self, headers, rows):
        """生成表格
        
        Args:
            headers: 表头列表 ['列1', '列2']
            rows: 数据行列表 [['值1', '值2'], ['值3', '值4']]
        """
        # 表头
        self.output.append("| " + " | ".join(headers) + " |")
        # 分隔线
        self.output.append("| " + " | ".join(["---"] * len(headers)) + " |")
        # 数据行
        for row in rows:
            self.output.append("| " + " | ".join(str(cell) for cell in row) + " |")
        self.output.append("")
        return self
    
    def bullet_list(self, items):
        """无序列表"""
        for item in items:
            self.output.append(f"- {item}")
        self.output.append("")
        return self
    
    def numbered_list(self, items):
        """有序列表"""
        for i, item in enumerate(items, 1):
            self.output.append(f"{i}. {item}")
        self.output.append("")
        return self
    
    def code(self, code, lang=""):
        """代码块"""
        self.output.append(f"```{lang}")
        self.output.append(code)
        self.output.append("```\n")
        return self
    
    def bold(self, text):
        """加粗"""
        self.output.append(f"**{text}**\n")
        return self
    
    def italic(self, text):
        """斜体"""
        self.output.append(f"*{text}*\n")
        return self
    
    def link(self, text, url):
        """链接"""
        self.output.append(f"[{text}]({url})\n")
        return self
    
    def hr(self):
        """分隔线"""
        self.output.append("---\n")
        return self
    
    def text(self, content):
        """普通文本"""
        self.output.append(f"{content}\n")
        return self
    
    def build(self):
        """构建最终输出"""
        return "\n".join(self.output)
    
    def save(self, filepath):
        """保存到文件"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(self.build(), encoding="utf-8")
        print(f"[保存] {filepath}")

# 快速模板
TEMPLATES = {
    "report": lambda f: (
        f.h1("报告标题")
         .h2("概述")
         .text("这里是概述内容...")
         .h2("详细内容")
         .table(["项目", "状态", "备注"], [
             ["项目A", "完成", "无"],
             ["项目B", "进行中", "待确认"]
         ])
         .h2("总结")
         .bullet_list(["总结点1", "总结点2", "总结点3"])
    ),
    
    "task": lambda f: (
        f.h1("任务清单")
         .h2("待办事项")
         .table(["任务", "优先级", "状态"], [
             ["任务1", "高", "待开始"],
             ["任务2", "中", "进行中"],
             ["任务3", "低", "已完成"]
         ])
         .h2("备注")
         .text("其他说明...")
    ),
    
    "summary": lambda f: (
        f.h1("总结")
         .h2("关键数据")
         .table(["指标", "数值", "变化"], [
             ["数据A", "100", "+10%"],
             ["数据B", "50", "-5%"]
         ])
         .h2("关键发现")
         .numbered_list(["发现1", "发现2", "发现3"])
         .h2("下一步")
         .bullet_list(["行动1", "行动2"])
    )
}

def main():
    if len(sys.argv) < 2:
        print("""
# Markdown格式化工具

用法: python scripts/md_formatter.py <模板名> [输出文件]

可用模板:
  report  - 报告模板
  task    - 任务清单模板
  summary - 总结模板

示例:
  python scripts/md_formatter.py report output.md
  python scripts/md_formatter.py task
""")
        return
    
    template_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if template_name not in TEMPLATES:
        print(f"[错误] 未知模板: {template_name}")
        print(f"可用: {', '.join(TEMPLATES.keys())}")
        return
    
    # 使用模板
    formatter = MDFormatter()
    TEMPLATES[template_name](formatter)
    
    # 输出
    result = formatter.build()
    
    if output_file:
        formatter.save(output_file)
    else:
        print(result)

if __name__ == "__main__":
    main()
