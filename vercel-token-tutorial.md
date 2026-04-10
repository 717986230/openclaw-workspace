# Vercel API Token 获取教程

## 🎯 目标
获取 Vercel API Token，用于自动化部署

---

## 📋 获取步骤

### 第一步：登录 Vercel

1. 打开浏览器，访问：**https://vercel.com**
2. 登录你的账号（使用 GitHub 登录的那个）

---

### 第二步：进入 Settings

1. 登录后，点击右上角的**头像**
2. 在下拉菜单中，点击「**Settings**」

或者直接访问：**https://vercel.com/account/tokens**

---

### 第三步：生成 Token

1. 在 Settings 页面，点击左侧的「**Tokens**」
2. 你会看到「**Create a Token**」或「**Generate New Token**」按钮
3. 点击该按钮

---

### 第四步：配置 Token

在弹出的对话框中：

**Token Name**:
- 输入一个名称，例如：`uuoo-site-deployment`
- 或者：`openclaw-automation`

**Scope**:
- 选择「**Full Account**」（完整权限）
- 或者选择「**Projects**」，然后选择 `my-nav-admin` 项目

**Expiration**:
- 选择「**No Expiration**」（永不过期）
- 或者选择一个时间段（例如 30 天）

---

### 第五步：生成并复制

1. 点击「**Create Token**」或「**Generate**」按钮
2. **重要**：立即复制生成的 Token（类似 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
3. **注意**：Token 只显示一次，务必保存好！

---

## 🖼️ 界面示意

### Tokens 页面
```
┌─────────────────────────────────────────────┐
│ Tokens                                      │
├─────────────────────────────────────────────┤
│                                             │
│ Authentication tokens allow you to         │
│ interact with the Vercel API.              │
│                                             │
│ [Create a Token]                            │
│                                             │
│ ─────────────────────────────────────────── │
│                                             │
│ Existing Tokens:                            │
│                                             │
│ • github-actions  (created 2024-01-01)     │
│ • vercel-cli      (created 2024-01-02)     │
│                                             │
└─────────────────────────────────────────────┘
```

### 创建 Token 对话框
```
┌─────────────────────────────────────────────┐
│ Create Token                                │
├─────────────────────────────────────────────┤
│                                             │
│ Token Name:                                 │
│ [uuoo-site-deployment            ]          │
│                                             │
│ Scope:                                      │
│ ○ Full Account                              │
│ ○ Projects (select below)                   │
│                                             │
│ Expiration:                                 │
│ [No Expiration                  ▼]          │
│                                             │
│           [Cancel]    [Create Token]        │
│                                             │
└─────────────────────────────────────────────┘
```

### Token 生成成功
```
┌─────────────────────────────────────────────┐
│ Token Created!                              │
├─────────────────────────────────────────────┤
│                                             │
│ Your token has been created:                │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx│ │
│ └─────────────────────────────────────────┘ │
│                           [📋 Copy]         │
│                                             │
│ ⚠️ Make sure to copy your token now.       │
│    You won't be able to see it again!      │
│                                             │
│                              [Done]         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## ⚠️ 重要提示

### 安全警告
- **Token 只显示一次**，必须立即保存
- **不要分享给任何人**
- **不要提交到 GitHub** 或公开仓库
- 如果泄露，立即在 Vercel 后台删除并重新生成

### Token 格式
Token 通常是一串随机字符，例如：
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 💾 保存 Token

### 方法 1：直接发给我
复制 Token 后，直接发送给我，我会帮你部署。

### 方法 2：保存到本地
创建文件保存：
```bash
# Windows
echo YOUR_TOKEN > ~/.vercel/token.txt

# Linux/Mac
echo "YOUR_TOKEN" > ~/.vercel/token
```

---

## 🎯 获取后下一步

获取到 Token 后，发给我，我会：

1. ✅ 自动创建 Vercel 项目
2. ✅ 配置项目设置
3. ✅ 触发部署
4. ✅ 绑定域名 uuoo.site
5. ✅ 验证部署成功

---

## 🔄 如果 Token 泄露

如果 Token 泄露或想重新生成：

1. 回到 Vercel Settings → Tokens
2. 找到对应的 Token
3. 点击「**Revoke**」或「**Delete**」
4. 重新生成新的 Token

---

## 📞 官方文档

- **Vercel API 文档**: https://vercel.com/docs/rest-api
- **Token 管理**: https://vercel.com/account/tokens

---

## 🆘 常见问题

### Q1: 找不到 Tokens 选项？
A: 
- 确保你已经登录 Vercel
- 直接访问：https://vercel.com/account/tokens

### Q2: Token 生成后没复制怎么办？
A: Token 只显示一次，必须删除旧的，重新生成新的

### Q3: Token 权限怎么选？
A: 建议选择「Full Account」，方便我帮你操作所有项目

---

## 📝 快速步骤总结

1. 访问 https://vercel.com
2. 点击右上角头像 → Settings
3. 点击左侧 Tokens
4. 点击 Create a Token
5. 输入名称，选择 Full Account
6. 点击 Create Token
7. **立即复制 Token**
8. 发送给我

---

*教程生成时间: 2026-04-05*
