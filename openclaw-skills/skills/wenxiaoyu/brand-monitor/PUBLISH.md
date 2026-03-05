# 发布到 ClawHub

## 什么是 ClawHub？

ClawHub 是 OpenClaw 的公共 skill 注册中心，类似于 npm 之于 Node.js。用户可以通过 ClawHub 轻松搜索、安装和更新 skills。

网站：https://clawhub.ai

## 为什么要发布到 ClawHub？

- ✅ 用户可以一键安装：`npx clawhub install brand-monitor`
- ✅ 自动版本管理和更新
- ✅ 更好的可发现性（搜索、排名）
- ✅ 社区反馈和星标
- ✅ 使用统计和下载量

## 前置要求

1. **GitHub 账号**（至少 1 周以上）
2. **安装 ClawHub CLI**
   ```bash
   npm i -g clawhub
   ```

3. **获取 ClawHub API Token**
   
   ⚠️ **重要：不是 GitHub Token，是 ClawHub 的 API Token！**
   
   - 访问：https://clawhub.ai
   - 使用 GitHub 登录
   - 进入 Settings → API Tokens（https://clawhub.ai/settings/tokens）
   - 创建新 token
   - 复制 token

4. **登录 ClawHub**
   ```bash
   clawhub login --token YOUR_CLAWHUB_API_TOKEN
   ```

## 发布步骤

### 第一步：准备 Skill

确保你的 skill 符合规范：

```bash
# 检查必需文件
ls -la
# 应该有：
# SKILL.md
# config.example.json
# prompts/
#   monitor.md
#   alert.md
#   analyze-trend.md
```

### 第二步：验证 SKILL.md

确保 YAML frontmatter 完整：

```yaml
---
name: brand-monitor
version: 1.1.0
description: 新能源汽车品牌舆情监控
author: OpenClaw Community
license: MIT
keywords:
  - brand
  - monitoring
  - sentiment
  - automotive
allowed-tools:
  - web_search
  - web_fetch
  - message
---
```

### 第三步：获取 ClawHub API Token

⚠️ **重要：使用 ClawHub API Token，不是 GitHub Token！**

1. 访问：https://clawhub.ai
2. 使用 GitHub 登录
3. 进入 Settings → API Tokens
4. 创建新 token（权限选择 `publish`）
5. 复制 token

### 第四步：登录 ClawHub

```bash
clawhub login --token YOUR_CLAWHUB_API_TOKEN
```

验证登录：

```bash
clawhub whoami
```

### 第五步：发布到 ClawHub

```bash
# 在 skill 目录下执行
cd brand-monitor-skill

# 发布
clawhub publish . \
  --slug brand-monitor \
  --name "Brand Monitor for New Energy Vehicles" \
  --version 1.1.0 \
  --tags latest,automotive,monitoring
```

**参数说明：**
- `--slug`: Skill 的唯一标识符（用于安装命令）
- `--name`: 显示名称
- `--version`: 版本号（语义化版本）
- `--tags`: 标签（用于搜索和分类）

### 第六步：验证发布

```bash
# 搜索你的 skill
clawhub search "brand monitor"

# 查看详情
clawhub inspect brand-monitor

# 测试安装
npx clawhub install brand-monitor
```

## 更新 Skill

### 发布新版本

```bash
# 1. 更新 SKILL.md 中的版本号
# version: 1.1.0 -> 1.2.0

# 2. 发布新版本
clawhub publish . \
  --slug brand-monitor \
  --name "Brand Monitor for New Energy Vehicles" \
  --version 1.2.0 \
  --tags latest,automotive,monitoring

# 3. 用户可以更新
clawhub update brand-monitor
```

### 批量同步

如果你有多个 skills：

```bash
# 扫描并发布所有本地 skills
clawhub sync --all
```

## 版本管理

### 语义化版本

遵循 [SemVer](https://semver.org/) 规范：

- `1.0.0` - 初始版本
- `1.0.1` - Bug 修复（向后兼容）
- `1.1.0` - 新增功能（向后兼容）
- `2.0.0` - 破坏性变更（不向后兼容）

### 标签（Tags）

- `latest` - 最新稳定版本
- `beta` - 测试版本
- `alpha` - 开发版本

用户可以安装特定版本：

```bash
# 安装最新版本
clawhub install brand-monitor

# 安装特定版本
clawhub install brand-monitor@1.1.0

# 安装 beta 版本
clawhub install brand-monitor@beta
```

## 最佳实践

### 1. 完整的文档

在 SKILL.md 中提供：
- 清晰的使用说明
- 配置示例
- 故障排查指南

### 2. 配置示例

提供 `config.example.json`：
```json
{
  "brand_name": "示例品牌",
  "feishu_webhook": "https://..."
}
```

### 3. 关键词优化

添加相关关键词，方便搜索：
```yaml
keywords:
  - brand
  - monitoring
  - sentiment
  - social-media
  - automotive
  - new-energy-vehicle
  - chinese-platforms
```

### 4. 安全声明

明确声明 `allowed-tools`：
```yaml
allowed-tools:
  - web_search
  - web_fetch
  - message
```

### 5. 变更日志

在 README.md 中维护变更日志：
```markdown
## 更新日志

### v1.1.0 (2026-02-25)
- 适配国内平台
- 新能源汽车行业定制
```

## 管理你的 Skill

### 查看统计

```bash
# 查看下载量和星标
clawhub info brand-monitor
```

### 删除版本

```bash
# 删除特定版本（需要所有者权限）
clawhub delete brand-monitor@1.0.0

# 恢复删除的版本
clawhub undelete brand-monitor@1.0.0
```

### 转移所有权

在 ClawHub 网站上操作：
1. 访问 https://clawhub.ai
2. 登录你的账号
3. 找到你的 skill
4. 点击 "Settings" → "Transfer ownership"

## 社区互动

### 收集反馈

- 在 GitHub 上创建 Issues
- 在 OpenClaw Discord 讨论
- 查看 ClawHub 上的评论和星标

### 成为维护者

如果你的 skill 受欢迎，可以：
- 邀请其他贡献者
- 创建贡献指南
- 设置 CI/CD 自动发布

## 安全和审核

### ClawHub 安全措施

- GitHub 账号需要至少 1 周
- 社区举报机制
- 管理员审核

### 举报恶意 Skill

如果发现恶意 skill：
1. 在 ClawHub 上点击 "Report"
2. 在 OpenClaw Discord 联系管理员
3. 发送邮件到 security@clawhub.ai

## 常见问题

### Q: 发布需要付费吗？

A: 不需要，ClawHub 完全免费。

### Q: 可以发布私有 skill 吗？

A: 不可以，ClawHub 上的所有 skills 都是公开的。如果需要私有 skill，直接安装到本地即可。

### Q: 如何更新已发布的 skill？

A: 更新 SKILL.md 中的版本号，然后重新发布：
```bash
clawhub publish . --slug brand-monitor --version 1.2.0
```

### Q: 可以删除已发布的 skill 吗？

A: 可以删除特定版本，但不建议删除被广泛使用的版本。

### Q: 如何提高 skill 的可见性？

A: 
- 添加相关关键词
- 编写清晰的文档
- 在社区分享
- 收集用户反馈和星标

## 参考资源

- [ClawHub 官网](https://clawhub.ai)
- [ClawHub CLI 文档](https://molty.finna.ai/docs/tools/clawhub)
- [AgentSkills 规范](https://github.com/anthropics/agentskills)
- [OpenClaw Discord](https://discord.gg/openclaw)

## 示例：完整发布流程

```bash
# 1. 准备 skill
cd brand-monitor-skill
ls -la  # 检查文件

# 2. 登录 ClawHub
clawhub login

# 3. 发布
clawhub publish . \
  --slug brand-monitor \
  --name "Brand Monitor for New Energy Vehicles" \
  --version 1.1.0 \
  --tags latest,automotive,monitoring,chinese-platforms

# 4. 验证
clawhub search "brand monitor"
clawhub info brand-monitor

# 5. 测试安装
cd /tmp
npx clawhub install brand-monitor
ls ~/.openclaw/skills/brand-monitor/

# 6. 分享给用户
echo "用户可以通过以下命令安装："
echo "npx clawhub install brand-monitor"
```

---

**祝你的 skill 受欢迎！** 🎉

如有问题，欢迎在 OpenClaw Discord 或 GitHub 上讨论。
