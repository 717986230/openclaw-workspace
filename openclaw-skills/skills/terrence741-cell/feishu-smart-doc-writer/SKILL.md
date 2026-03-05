---
name: feishu-smart-doc-writer
description: |
  Feishu/Lark Smart Document Writer - 飞书智能文档写入器.
  
  Core Features / 核心功能：
  1. Smart Chunk Writing / 智能分块写入 - Solve API limit blank doc issues / 解决长文档API限制导致的空白问题
  2. Auto Ownership Transfer / 自动转移所有权 - Transfer to user after creation / 创建文档后自动转移给用户
  3. Auto Index Management / 自动索引管理 - Update local index with search support / 自动更新本地文档索引，支持搜索
  4. First-time Guide / 首次使用引导 - Auto guide for OpenID config / 自动引导配置OpenID
---

# Feishu Smart Doc Writer v1.4.1

## 🚀 Core Features / 核心功能

### 1. Smart Document Creation / 智能文档创建
- **Auto-chunk Writing / 自动分块**: Split long content into chunks to avoid API limit blank docs / 长内容自动分割成小块，避免API限制导致的空白文档
- **Auto Ownership Transfer / 自动转移所有权**: Transfer to user using OpenID after creation / 创建后自动使用 OpenID 转移给用户
- **Auto Index Update / 自动索引更新**: Add doc info to local index `memory/feishu-docs-index.md` / 文档信息自动添加到本地索引
- **Smart Categorization / 智能分类**: Auto-tag based on content (AI Tech, E-commerce, Health, etc.) / 根据内容自动打标签（AI技术、电商、健康运动等）

### 2. Document Management / 文档管理
- **Search Documents / 搜索文档**: Search local index by keywords / 按关键词搜索本地索引
- **List Documents / 列出文档**: Filter by tags and status / 按标签、状态筛选文档列表
- **Append Content / 追加内容**: Append to existing docs (auto-chunk) / 向现有文档追加内容（自动分块）

---

## 📋 Tools / 工具列表

### write_smart - Smart Document Creation / 智能创建文档
Create document with auto-chunk writing, ownership transfer, and index update.
创建文档，自动完成分块写入、所有权转移、索引更新。

```json
{
  "title": "Document Title / 文档标题",
  "content": "Content (long content supported) / 文档内容（支持长内容）",
  "folder_token": "Optional folder token / 可选的文件夹token"
}
```

**Returns / 返回：**
```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "doc_token": "xxx",
  "chunks_count": 3,
  "owner_transferred": true,
  "index_updated": true
}
```

### append_smart - Append Content / 追加内容
Append content to existing document with auto-chunk.
向现有文档追加内容（自动分块）。

```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "content": "Content to append / 要追加的内容"
}
```

### search_docs - Search Documents / 搜索文档
Search documents in local index.
搜索本地索引中的文档。

```json
{
  "keyword": "Search keyword / 搜索关键词"
}
```

**Returns / 返回：**
```json
{
  "results": [
    {
      "name": "Document Name / 文档名",
      "link": "https://...",
      "summary": "Summary / 摘要",
      "tags": "AI Tech, OpenClaw / AI技术, OpenClaw"
    }
  ],
  "count": 1
}
```

### list_docs - List Documents / 列出文档
List all documents with optional filters.
列出所有文档，支持筛选。

```json
{
  "tag": "AI Tech / AI技术",
  "status": "Completed / 已完成"
}
```

### transfer_ownership - Transfer Ownership / 转移所有权
Manually transfer document ownership (usually auto-handled by write_smart).
手动转移文档所有权（通常不需要，write_smart 已自动处理）。

```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "owner_openid": "ou_xxxxxxxx"
}
```

**Note / 注意:** Only provide OpenID, tenant_access_token is auto-obtained by Skill.
只需要提供 OpenID，tenant_access_token 由 Skill 自动获取。

### configure - Configure OpenID / 配置 OpenID
Configure OpenID for first-time use.
首次使用时配置 OpenID。

```json
{
  "openid": "ou_xxxxxxxx",
  "permission_checked": true
}
```

### get_config_status - Get Config Status / 查看配置状态
View current configuration status.
查看当前配置状态。

---

## 🚀 Quick Start / 快速开始

### First-time Setup (3 Steps) / 首次使用（3步配置）

**Step 1 / 第1步: Call write_smart / 调用 write_smart**
```
/feishu-smart-doc-writer write_smart
title: Test Document / 测试文档
content: This is a test document. / 这是一个测试文档内容
```

**Step 2 / 第2步: Get OpenID / 获取 OpenID**
If not configured, follow the guide:
如果未配置，会显示引导：
1. Login / 登录 https://open.feishu.cn
2. Go to / 进入 Application → Permission Management / 应用 → 权限管理 → Search / 搜索 `im:message`
3. Click / 点击【API】Send Message / 发送消息 → Go to API Debug Console / 前往API调试台
4. Click / 点击"Quick Copy open_id" / 快速复制 open_id", select your account / 选择你的账号, copy / 复制

**Step 3 / 第3步: Configure and Enable Permissions / 配置并开通权限**
```
/feishu-smart-doc-writer configure
openid: ou_your_openid / ou_你的OpenID
permission_checked: true
```

Then go to Permission Management / 然后到权限管理：
1. Search / 搜索 `docs:permission.member:transfer`
2. Click / 点击"Enable / 开通"
3. **Important / 重要**: Click / 点击"Publish / 发布" button to publish new version / 按钮发布新版本

After setup, future document creation will automatically:
配置完成后，以后创建文档会自动：
- ✅ Chunk write content / 分块写入内容
- ✅ Transfer ownership to you / 转移所有权给你
- ✅ Update local index / 更新本地索引

---

## 📊 Index Management / 索引管理

### Auto Index Workflow / 自动索引流程
```
write_smart creates document / 创建文档
    ↓
Write content (auto-chunk) / 写入内容（自动分块）
    ↓
Transfer ownership / 转移所有权
    ↓
Auto update index → memory/feishu-docs-index.md / 自动更新索引
    ↓
Done! / 完成！
```

### Auto-categorization Tags / 自动分类标签
Auto-identified based on content / 根据内容自动识别：
- **AI Tech / AI技术** - AI, artificial intelligence / 人工智能, model / 模型, GPT, LLM
- **OpenClaw** - OpenClaw, skill, agent
- **Feishu Docs / 飞书文档** - Feishu / 飞书, document / 文档, feishu
- **E-commerce / 电商** - e-commerce / 电商, TikTok, Alibaba / 阿里巴巴
- **Health & Sports / 健康运动** - Garmin, Strava, cycling / 骑行, health / 健康
- **Daily Archive / 每日归档** - conversation / 对话, archive / 归档, chat history / 聊天记录

### Index File Location / 索引文件位置
`memory/feishu-docs-index.md`

Format / 格式: Markdown table with / Markdown 表格，包含 index / 序号, name / 名称, type / 类型, link / 链接, summary / 摘要, status / 状态, tags / 标签, owner / 所有者

---

## 🔍 Usage Examples / 使用示例

### Example 1 / 示例1: Create Tech Document / 创建技术文档
```
/feishu-smart-doc-writer write_smart
title: AI Tech Research Report / AI技术调研报告
content: # AI Overview / AI技术概述\n\nAI is... / 人工智能（AI）是...
```

Result / 结果：
- Document created successfully / 文档创建成功
- Auto-tagged "AI Tech / AI技术" / 自动打上"AI技术"标签
- Index updated / 索引已更新

### Example 2 / 示例2: Search Documents / 搜索文档
```
/feishu-smart-doc-writer search_docs
keyword: AI Tech / AI技术
```

### Example 3 / 示例3: List All Tech Documents / 列出所有技术文档
```
/feishu-smart-doc-writer list_docs
tag: AI Tech / AI技术
```

---

## ⚙️ Configuration / 配置说明

### User Config File / 用户配置文件
Location / 位置: `skills/feishu-smart-doc-writer/user_config.json`

```json
{
  "owner_openid": "ou_5b921cba0fd6e7c885276a02d730ec19",
  "permission_noted": true,
  "first_time": false
}
```

### Required Permissions / 必需权限
- `docx:document:create` - Create document / 创建文档
- `docx:document:write` - Write content / 写入内容
- `docs:permission.member:transfer` - Transfer ownership ⚠️ Critical / 转移所有权 ⚠️ 关键权限

---

## 📝 Version History / 版本历史

### v1.4.1 (2026-02-23)
- ✅ Fixed description inconsistency between skill.json and package.json / 修复 skill.json 和 package.json 描述不一致问题
- ✅ Unified all file versions to v1.4.1 / 统一所有文件版本号为 v1.4.1
- ✅ Verified all 7 tools properly declared / 确认所有 7 个工具正确声明

### v1.4.0 (2026-02-23)
- ✅ Added auto index management (index_manager.py) / 新增自动索引管理（index_manager.py）
- ✅ Added search_docs tool (search local index) / 新增 search_docs 工具（搜索本地索引）
- ✅ Added list_docs tool (list documents) / 新增 list_docs 工具（列出文档）
- ✅ Smart auto-categorization tags / 智能自动分类标签
- ✅ Fixed ownership transfer (independent API calls, no ctx dependency) / 修复所有权转移（独立 API 调用，不依赖 ctx）

### v1.2.0
- ✅ Auto-chunk writing / 自动分块写入
- ✅ Auto ownership transfer / 自动转移所有权
- ✅ First-time user guide / 首次使用引导

### v1.1.0
- ✅ Basic document creation and append / 基础文档创建和追加

---

## 🔧 Troubleshooting / 故障排除

### "open_id is not exist" Error / 错误
**Cause / 原因**: Used user_id instead of openid / 使用了 user_id 而不是 openid
**Solution / 解决**: Use openid starting with `ou_` / 使用以 `ou_` 开头的 openid

### "Permission Denied" Error / "权限不足" 错误
**Cause / 原因**: `docs:permission.member:transfer` not enabled or app not published / 未开通权限，或未发布应用
**Solution / 解决**：
1. Permission Management → Search `docs:permission.member:transfer` → Enable / 权限管理 → 搜索 → 开通
2. Click "Publish" button to publish new version (Critical!) / 点击"发布"按钮（关键！）

### Index Not Updated / 索引未更新
**Check / 检查**：
1. Check if `memory/feishu-docs-index.md` exists / 查看文件是否存在
2. Check `index_updated` field in write_smart return / 检查返回字段
3. Check error logs / 查看错误日志

---

## 📞 Support / 支持

If issues, please check / 如有问题，请检查：
1. OpenID format correct (starts with ou_) / 格式是否正确（ou_ 开头）
2. Permissions enabled and published / 权限是否已开通并发布
3. Index file path correct / 索引文件路径是否正确
