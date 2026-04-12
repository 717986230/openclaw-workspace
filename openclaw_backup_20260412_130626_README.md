# OpenClaw 完整备份清单

> 备份时间: 2026-04-12 13:06:26
> 备份文件: openclaw_backup_20260412_130626.zip
> 文件大小: 6.7 MB

---

## 📦 备份内容

### 1. 数据库文件

#### SQLite 数据库
- `xiaozhi_memory.db` - 主数据库（包含所有记忆、账户、事件等）
- `xiaozhi_secure.db` - 安全数据库（包含加密的敏感信息）
- `xiaozhi_memory.db.backup_*` - 数据库备份文件（多个版本）

#### LanceDB 向量数据库
- `lancedb/memories.lance/` - 向量记忆数据库
- `lancedb/memories.lance/_transactions/` - 事务日志
- `lancedb/memories.lance/_versions/` - 版本信息

#### 数据库脚本
- `init_db.py` - 数据库初始化脚本
- `design_patterns_schema.sql` - 设计模式数据库结构
- `optimize_database.py` - 数据库优化脚本
- `verify_database.py` - 数据库验证脚本
- 其他数据库相关脚本（60+ 个文件）

### 2. 配置文件

#### OpenClaw 配置
- `config.json` - OpenClaw 主配置文件（包含所有设置）
- `exec-approvals.json` - 执行批准配置（包含权限设置）
- `openclaw.json` - OpenClaw 运行时配置

#### 备份配置
- `openclaw-gemini-backup.json` - Gemini 模型备份配置

### 3. 遗传神经网络系统
- `genetic_neural_system/` - 完整的遗传神经网络系统
  - `api.py` - API 接口
  - `database.py` - 数据库模块
  - `config.yaml` - 配置文件
  - `requirements.txt` - 依赖列表
  - 其他相关文件

---

## 🔐 敏感信息说明

### 包含的敏感信息

#### 1. API 密钥
- OpenAI API 密钥（在 config.json 中）
- Gemini API 密钥（在 config.json 中）
- 其他第三方服务密钥

#### 2. 账户信息
- 账户密码（存储在 xiaozhi_secure.db 中）
- 登录凭证
- 认证令牌

#### 3. 个人数据
- 记忆数据（在 xiaozhi_memory.db 中）
- 事件日志
- 用户偏好设置

#### 4. 系统配置
- 执行权限设置
- 模型配置
- 渠道配置

---

## 📋 数据库表结构

### xiaozhi_memory.db 表列表

#### 核心表
- `memories` - 记忆表
- `accounts` - 账户表
- `events` - 事件表
- `preferences` - 偏好表
- `skills` - 技能表

#### 设计模式表
- `design_systems` - 设计系统表
- `color_palettes` - 色彩系统表
- `typography_systems` - 排版系统表
- `component_styles` - 组件样式表
- `layout_systems` - 布局系统表
- `design_tags` - 设计标签表
- `design_similarities` - 设计相似度表

#### 其他表
- `knowledge_relations` - 知识关系表
- `causal_relations` - 因果关系表
- `emotional_state` - 情绪状态表
- `meta_cognition` - 元认知表
- `user_beliefs` - 用户信念表
- 其他 40+ 张表

### xiaozhi_secure.db 表列表

- `accounts` - 加密账户表
- `secrets` - 加密密钥表
- `tokens` - 认证令牌表

---

## 🚀 恢复步骤

### 1. 解压备份
```bash
unzip openclaw_backup_20260412_130626.zip
```

### 2. 恢复数据库
```bash
# 复制数据库文件
cp xiaozhi_memory.db ~/.openclaw/workspace/memory/database/
cp xiaozhi_secure.db ~/.openclaw/workspace/memory/database/

# 复制 LanceDB
cp -r lancedb ~/.openclaw/workspace/memory/database/
```

### 3. 恢复配置
```bash
# 复制配置文件
cp config.json ~/.openclaw/
cp exec-approvals.json ~/.openclaw/
cp openclaw.json ~/.openclaw/
```

### 4. 重启 OpenClaw
```bash
openclaw gateway restart
```

---

## ⚠️ 注意事项

### 安全警告
1. **不要分享此备份文件** - 包含所有敏感信息
2. **妥善保管** - 建议加密存储
3. **定期备份** - 建议每周备份一次
4. **验证备份** - 定期验证备份完整性

### 使用建议
1. **测试恢复** - 在测试环境中验证恢复流程
2. **版本控制** - 保留多个版本的备份
3. **异地备份** - 建议备份到云端或外部存储
4. **备份加密** - 使用加密工具保护备份文件

---

## 📊 备份统计

### 文件统计
- 总文件数: 100+ 个
- 总大小: 6.7 MB
- 数据库文件: 5 个
- 配置文件: 4 个
- 脚本文件: 60+ 个

### 数据统计
- 记忆条目: 4,000+ 条
- 账户记录: 多个
- 事件日志: 多条
- 向量数据: 多个

---

## 🎯 下一步

1. **验证备份** - 检查备份文件完整性
2. **测试恢复** - 在测试环境中验证恢复流程
3. **加密存储** - 使用加密工具保护备份文件
4. **定期备份** - 设置自动备份计划

---

## 📞 支持

如有问题，请联系：
- OpenClaw 文档: https://docs.openclaw.ai
- OpenClaw 社区: https://discord.com/invite/clawd

---

*备份生成者: Erbing (二饼)*
*备份时间: 2026-04-12 13:06:26*
*备份版本: v1.0*
