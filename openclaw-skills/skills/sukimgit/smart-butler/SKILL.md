---
name: smart-butler
description: AI 智能管家 - 会议管理、文档生成、任务提醒、智能推荐一站式解决方案。
metadata:
  {"openclaw": {"emoji": "🤖", "requires": {"bins": ["python"]}, "primaryEnv": "FEISHU_APP_ID"}}
---

# Smart Butler - AI 智能管家

**一站式会议管理和文档生成解决方案**

整合任务管理、文档生成、智能推荐、模板引擎等功能，帮助你从会议准备到会后跟进全流程自动化。

---

## 🎯 使用场景 Use Cases

### 会议管理
- 会前：自动生成准备清单、推荐历史文档
- 会中：实时记录、模板套用
- 会后：自动生成纪要、归档文档、跟进待办

### 文档生成
- 技术方案、销售方案、投标方案
- 周会报告、项目汇报
- 会议纪要、决策记录

### 任务提醒
- 会议提醒、任务截止提醒
- 定时检查、飞书通知

---

## 🛠️ 功能模块 Features

### 1. 任务管理 Task Manager
```python
# 创建任务
create_task(content="明天 9 点开会", time="2026-03-06 09:00", remind_before_minutes=15)

# 查询任务
list_tasks(date="today")

# 完成任务
complete_task(task_id="001")

# 删除任务
delete_task(task_id="001")
```

### 2. 文档生成 Document Generator
```python
# 根据会议主题生成文档
generate_doc(topic="人员密集度检测方案", time="15:00", attendees=["老高", "Monet"])

# 支持格式：Markdown / Word / PDF
```

### 3. 文档修改 Document Modifier
```python
# 自然语言修改文档
modify_doc(file_path="方案.md", instruction="强调一下成本优势")

# 自动版本管理（v1 → v2）
```

### 4. 文档搜索 Document Search
```python
# 关键词搜索历史文档
search_docs(keyword="成本优势", category="技术方案")
```

### 5. 智能推荐 Smart Recommend
```python
# 根据会议主题推荐历史文档
recommend_docs(topic="人员密集度检测")

# 返回相似度匹配的历史文档
```

### 6. 模板引擎 Template Engine
```python
# 可用模板
- technical.md - 技术方案模板
- sales.md - 销售方案模板
- weekly.md - 周会报告模板
- bid.md - 投标方案模板
```

### 7. 文档归档 Document Archive
```python
# 自动归档到指定目录
archive_doc(file_path="方案.md", category="projects")

# 支持分类：temp/ / projects/ / meetings/
```

### 8. PDF 导出 PDF Export
```python
# Markdown/Word → PDF
export_pdf(file_path="方案.docx")
```

### 9. 准备清单 Prep Generator
```python
# 根据会议主题生成准备清单
generate_prep(topic="人员密集度检测讨论会")

# 返回：待准备材料、待邀请人员、参考文档
```

### 10. 统计数据 Stats
```python
# 生成使用统计
get_stats()

# 返回：任务完成率、文档数量、时间节省估算
```

---

## 📁 目录结构 Directory Structure

```
smart-butler/
├── SKILL.md              # 技能说明
├── src/                  # 核心代码
│   ├── task_manager.py   # 任务管理
│   ├── doc_generator.py  # 文档生成
│   ├── doc_modifier.py   # 文档修改
│   ├── doc_search.py     # 文档搜索
│   ├── doc_archive.py    # 文档归档
│   ├── smart_recommend.py# 智能推荐
│   ├── template_engine.py# 模板引擎
│   ├── pdf_export.py     # PDF 导出
│   ├── prep_generator.py # 准备清单
│   └── stats.py          # 统计数据
└── templates/            # 文档模板
    ├── technical.md      # 技术方案
    ├── sales.md          # 销售方案
    ├── weekly.md         # 周会报告
    └── bid.md            # 投标方案
```

---

## 🚀 快速开始 Quick Start

### 1. 安装技能
```bash
clawhub install smart-butler
```

### 2. 配置（可选）
```json5
{
  skills: {
    entries: {
      "smart-butler": {
        enabled: true,
        env: {
          FEISHU_APP_ID: "your_app_id",
          FEISHU_APP_SECRET: "your_app_secret"
        }
      }
    }
  }
}
```

### 3. 使用示例

**创建会议提醒：**
```
"提醒我明天 9 点开会"
```

**生成会议文档：**
```
"下午 3 点有个人员密集度检测讨论会，生成方案"
```

**修改文档：**
```
"把方案的成本部分再强调一下"
```

**搜索历史文档：**
```
"找一下之前关于成本优化的方案"
```

---

## 💰 定价 Pricing

| 版本 | 价格 | 功能 |
|------|------|------|
| **标准版 Standard** | 免费 Free | 任务管理 + 文档生成 |
| **专业版 Pro** | $30/month (¥199/月) | 全部功能 + 模板库 |
| **企业版 Enterprise** | $100/month (¥699/月) | 多用户 + 定制模板 + 优先支持 |
| **定制开发 Custom** | $1000-5000 (¥7000-35000) | 私有化部署 + 功能定制 |

---

## 📧 联系 Contact

**定制开发/企业版：**
- 📧 邮箱 Email：1776480440@qq.com
- 💬 微信 WeChat：私信获取 DM for details

**支持支付 Payment：**
- 国内 Domestic：微信/支付宝/银行转账
- 国际 International：
  - PayPal: https://paypal.me/monet888
  - Wise: Account 242009405
  - USDT: 私信获取

---

## 📊 案例展示 Cases

### 案例 1：AI 视觉监控系统方案生成
**需求：** 小区物业火灾监控方案
**时间：** 30 分钟（传统需要 4 小时）
**产出：** 完整技术方案 + 报价单
**结果：** 客户当场签约（3.98W）

### 案例 2：周会报告自动化
**需求：** 每周自动生成团队周报
**时间：** 5 分钟（传统需要 1 小时）
**产出：** GitHub 动态 + 会议记录 + 行业新闻
**结果：** 团队效率提升 90%

### 案例 3：投标方案快速生成
**需求：** 紧急投标方案（2 天截止）
**时间：** 1 小时（传统需要 2 天）
**产出：** 完整投标方案 + 技术文档
**结果：** 成功中标（50W 项目）

---

## 🎯 核心价值 Value Proposition

**节省时间：**
- 会议准备：1 小时 → 5 分钟
- 文档生成：4 小时 → 30 分钟
- 会后跟进：30 分钟 → 自动完成

**提升质量：**
- 智能推荐历史文档
- 模板化标准化输出
- 版本管理避免出错

**降低成本：**
- 减少重复劳动
- 提高成交率
- 规模化复制

---

## 🔧 技术栈 Tech Stack

- Python 3.8+
- Markdown/Word/PDF 处理
- 飞书 API（通知）
- 语义相似度匹配
- 版本控制系统

---

## 📝 更新日志 Changelog

### v1.0.0 (2026-03-05)
- 初始发布
- 整合 10 个核心功能模块
- 支持中英双语
- 完整支付配置

---

**技能来源 Source：** https://clawhub.ai/sukimgit/smart-butler
**作者 Author：** Monet + 老高
**许可 License：** MIT
