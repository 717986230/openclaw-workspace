# 发布到 ClawHub 步骤指南

## 正确的登录方式

ClawHub 使用自己的 API Token 系统，**不是** GitHub Personal Access Token。

## 完整步骤

### 第一步：获取 ClawHub API Token

1. **访问 ClawHub 网站**
   
   打开：https://clawhub.ai

2. **使用 GitHub 登录**
   
   - 点击 "Sign in with GitHub"
   - 授权 ClawHub 访问你的 GitHub 账号
   - 完成登录

3. **获取 API Token**
   
   登录后，访问：https://clawhub.ai/settings/tokens
   
   或者：
   - 点击右上角头像
   - 选择 "Settings"
   - 选择 "API Tokens"

4. **创建新 Token**
   
   - 点击 "Create Token" 或 "New Token"
   - 名称：`CLI Token`
   - 权限：选择需要的权限（通常选择 `publish`）
   - 点击 "Create"
   - **立即复制 token**（只显示一次！保存到安全的地方）

### 第二步：使用 Token 登录 CLI

```bash
clawhub login --token YOUR_CLAWHUB_API_TOKEN
```

**重要：** 使用的是 ClawHub 的 API Token，不是 GitHub Token！

验证登录：

```bash
clawhub whoami
```

应该显示你的 GitHub 用户名和登录状态。

### 第三步：发布 Skill

```bash
# 进入 skill 目录
cd brand-monitor-skill

# 发布
clawhub publish . \
  --slug brand-monitor \
  --name "Brand Monitor for New Energy Vehicles" \
  --version 1.1.0 \
  --description "新能源汽车品牌舆情监控 - 自动搜索、分析国内平台的品牌提及情况" \
  --tags latest,automotive,monitoring,chinese-platforms,new-energy-vehicle
```

### 第四步：验证发布

```bash
# 搜索你的 skill
clawhub search "brand monitor"

# 查看详情
clawhub inspect brand-monitor

# 测试安装
cd /tmp
clawhub install brand-monitor
ls ~/.openclaw/skills/brand-monitor/
```

## 常见问题

### Q: "Unauthorized" 错误

**原因：** 使用了错误的 token 类型。

**解决：**
- ❌ 不要使用 GitHub Personal Access Token
- ✅ 必须使用 ClawHub API Token（从 https://clawhub.ai/settings/tokens 获取）

### Q: 如何获取 ClawHub API Token？

**步骤：**
1. 访问 https://clawhub.ai
2. 使用 GitHub 登录
3. 进入 Settings → API Tokens
4. 创建新 token
5. 复制 token

### Q: Token 在哪里使用？

```bash
# 登录
clawhub login --token YOUR_CLAWHUB_API_TOKEN

# 或设置环境变量
export CLAWHUB_TOKEN=YOUR_CLAWHUB_API_TOKEN
```

### Q: "Missing state" 错误

**原因：** 浏览器登录流程中断。

**解决：** 使用 token 登录方式（推荐），不要使用浏览器登录。

### Q: GitHub 账号太新

**错误：** "Account must be at least 1 week old"

**解决：** ClawHub 要求 GitHub 账号至少 1 周以上才能发布。等待账号满足要求。

### Q: Skill 已存在

**错误：** "Skill already exists"

**解决：**
- 如果是你的 skill，更新版本号重新发布
- 如果不是你的，使用不同的 slug

## 发布后

### 分享给用户

用户可以通过以下命令安装：

```bash
npx clawhub install brand-monitor
```

### 更新 skill

```bash
# 1. 修改代码
# 2. 更新 SKILL.md 中的版本号
# 3. 重新发布
clawhub publish . \
  --slug brand-monitor \
  --version 1.2.0
```

### 查看统计

```bash
clawhub inspect brand-monitor
```

会显示：
- 下载量
- 星标数
- 版本历史

## 替代方案：网站上传

如果 CLI 有问题，可以直接在网站上传：

1. 访问 https://clawhub.ai
2. 登录
3. 点击 "Publish" 或 "Upload Skill"
4. 上传 `brand-monitor-skill` 文件夹或 ZIP
5. 填写信息：
   - Slug: `brand-monitor`
   - Name: `Brand Monitor for New Energy Vehicles`
   - Version: `1.1.0`
   - Description: `新能源汽车品牌舆情监控`
   - Tags: `automotive`, `monitoring`, `chinese-platforms`
6. 提交

## 需要帮助？

- ClawHub 网站：https://clawhub.ai
- ClawHub 文档：https://molty.finna.ai/docs/tools/clawhub
- OpenClaw Discord：https://discord.gg/openclaw

---

## 快速参考

```bash
# 1. 获取 ClawHub API Token
# 访问：https://clawhub.ai/settings/tokens

# 2. 登录
clawhub login --token YOUR_CLAWHUB_API_TOKEN

# 3. 验证
clawhub whoami

# 4. 发布
cd brand-monitor-skill
clawhub publish . --slug brand-monitor --version 1.1.0

# 5. 验证
clawhub inspect brand-monitor
```

---

**重要提示：**
- ✅ 使用 ClawHub API Token（从网站获取）
- ❌ 不要使用 GitHub Personal Access Token
- 🔒 不要分享你的 token
- 💾 保存 token 到安全的地方
