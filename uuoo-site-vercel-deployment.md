# uuoo.site Vercel 部署指南

## 🎯 部署目标
将导航网站部署到 Vercel，并绑定域名 uuoo.site

---

## 📋 前提条件
✅ DNS 已配置（CNAME → cname.vercel-dns.com）
✅ GitHub 仓库已准备好：https://github.com/717986230/my-nav-admin
✅ 代码已上传完成

---

## 🚀 Vercel 部署步骤

### Step 1: 访问 Vercel
1. 打开浏览器，访问：**https://vercel.com**
2. 点击右上角「Sign Up」或「Log In」
3. 选择「Continue with GitHub」
4. 授权 Vercel 访问你的 GitHub 账号

---

### Step 2: 导入项目
1. 登录后，点击右上角「**Add New...**」
2. 选择「**Project**」
3. 在「Import Git Repository」页面：
   - 找到 `717986230/my-nav-admin`
   - 点击「**Import**」按钮

---

### Step 3: 配置项目
在「Configure Project」页面：

**Framework Preset**:
- 选择：`Node.js`（或 Vercel 自动检测）

**Root Directory**:
- 保持默认：`./`

**Build Command**:
- 自动检测：`npm install`（或保持默认）

**Output Directory**:
- 填写：`public`

**Install Command**:
- 自动检测：`npm install`（或保持默认）

**Environment Variables**:
- 暂时不需要添加

---

### Step 4: 开始部署
1. 确认配置无误
2. 点击底部的「**Deploy**」按钮
3. 等待部署完成（通常 1-2 分钟）

你会看到：
- 构建日志滚动输出
- 最后显示「🎉 Congratulations!」

---

### Step 5: 绑定域名
部署成功后：

1. 在项目页面，点击「**Settings**」
2. 点击左侧「**Domains**」
3. 在输入框输入：`uuoo.site`
4. 点击「**Add**」
5. 同样添加：
   - `www.uuoo.site`
   - `api.uuoo.site`

---

### Step 6: 验证部署
绑定域名后，等待 DNS 生效（几分钟），然后访问：

- **主站**: https://uuoo.site
- **API**: https://api.uuoo.site

---

## 🎨 Vercel 界面示意

### 导入项目页面
```
┌─────────────────────────────────────────┐
│ Import Git Repository                   │
├─────────────────────────────────────────┤
│                                         │
│ 🔍 Search repositories...               │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 717986230/my-nav-admin    [Import]  │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 配置项目页面
```
┌─────────────────────────────────────────┐
│ Configure Project                       │
├─────────────────────────────────────────┤
│                                         │
│ Project Name: my-nav-admin              │
│                                         │
│ Framework Preset: [Node.js    ▼]        │
│                                         │
│ Root Directory:  [./           ]        │
│                                         │
│ Build Command:   [npm install ]        │
│                                         │
│ Output Directory:[public       ]        │
│                                         │
│           [Deploy]                      │
│                                         │
└─────────────────────────────────────────┘
```

### 绑定域名页面
```
┌─────────────────────────────────────────┐
│ Domains                                 │
├─────────────────────────────────────────┤
│                                         │
│ Add Domain: [uuoo.site        ] [Add]   │
│                                         │
│ ─────────────────────────────────────── │
│                                         │
│ ✅ uuoo.site                            │
│    Status: Valid Configuration          │
│                                         │
│ ✅ www.uuoo.site                        │
│    Status: Valid Configuration          │
│                                         │
│ ✅ api.uuoo.site                        │
│    Status: Valid Configuration          │
│                                         │
└─────────────────────────────────────────┘
```

---

## ⏰ 时间预估

- **导入项目**: 1 分钟
- **配置项目**: 1 分钟
- **部署**: 1-2 分钟
- **绑定域名**: 1 分钟
- **DNS 生效**: 几分钟

**总计**: 约 5-10 分钟

---

## ✅ 部署成功标志

部署成功后，你会看到：

1. ✅ 构建日志显示「Build Complete」
2. ✅ 项目首页显示预览链接
3. ✅ Domains 设置显示「Valid Configuration」
4. ✅ 访问 https://uuoo.site 能看到网站

---

## 🚨 常见问题

### Q1: 部署失败怎么办？
A: 查看构建日志，通常是依赖安装问题。确保 `package.json` 正确。

### Q2: 域名显示 Invalid Configuration？
A: 等待几分钟，DNS 需要时间生效。

### Q3: 网站打不开？
A: 
1. 检查 DNS 配置是否正确
2. 检查 Vercel 项目状态
3. 等待 DNS 完全生效（最长 2 小时）

---

## 📦 部署完成后的配置

### 1. 微信小程序
修改 API 地址为：`https://api.uuoo.site`

### 2. 添加链接
访问 https://uuoo.site，使用管理后台添加链接

### 3. 上传图标
使用管理后台上传网站图标

---

## 🌐 最终访问地址

- **主站**: https://uuoo.site
- **API**: https://api.uuoo.site
- **管理后台**: https://uuoo.site（首页即后台）

---

## 🎯 下一步

部署完成后：
1. ✅ 测试网站功能
2. ✅ 添加链接和分类
3. ✅ 上传微信小程序

---

*教程生成时间: 2026-04-05*
*项目: uuoo.site 导航网站*
*平台: Vercel*
