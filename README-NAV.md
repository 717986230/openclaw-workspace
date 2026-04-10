# 导航网站完整解决方案

## 📦 项目结构

```
├── my-nav-admin/          # 后端管理
│   ├── server.js         # Express 服务器
│   ├── package.json      # 依赖配置
│   ├── public/           # 管理界面
│   └── uploads/          # 上传的图标
│
└── my-nav-miniprogram/   # 微信小程序
    ├── app.js
    ├── app.json
    ├── app.wxss
    └── pages/
        └── index/        # 首页
```

---

## 🚀 部署步骤

### 1. 后端部署

#### 本地测试
```bash
cd my-nav-admin
npm install
npm start
```

访问: http://localhost:3000

#### 云端部署 (Railway/Vercel)

**Railway (推荐)**:
1. 访问 https://railway.app
2. 连接 GitHub 仓库
3. 选择 `my-nav-admin` 目录
4. 自动部署

**Vercel**:
1. 访问 https://vercel.com
2. Import Project
3. 选择仓库
4. 部署

---

### 2. 微信小程序部署

#### 配置后端地址
编辑 `app.js`，修改 apiUrl:
```javascript
apiUrl: 'https://你的域名.com/api'
```

#### 上传到微信
1. 下载微信开发者工具
2. 导入 `my-nav-miniprogram` 目录
3. 点击"上传"
4. 提交审核

---

## ✨ 功能特点

### 后端管理
- ✅ SQLite 数据库（轻量级）
- ✅ 链接 CRUD（增删改查）
- ✅ 分类管理
- ✅ 图标上传（支持图片）
- ✅ 点击统计
- ✅ REST API

### 微信小程序
- ✅ 分类展示
- ✅ 搜索功能
- ✅ 下拉刷新
- ✅ 分享功能
- ✅ 点击统计
- ✅ 复制链接

---

## 🔗 API 文档

### 链接管理
- `GET /api/links` - 获取所有链接
- `POST /api/links` - 添加链接
- `PUT /api/links/:id` - 更新链接
- `DELETE /api/links/:id` - 删除链接
- `POST /api/links/:id/click` - 记录点击

### 分类管理
- `GET /api/categories` - 获取所有分类
- `POST /api/categories` - 添加分类
- `DELETE /api/categories/:id` - 删除分类

### 统计
- `GET /api/stats` - 获取统计数据

---

## 💰 成本

- 后端托管: ¥0 (Railway/Vercel 免费层)
- 数据库: ¥0 (SQLite 文件数据库)
- 微信小程序: ¥0 (免费)
- 域名: ¥20-80/年

**总计: ¥20-80/年**

---

## 🎯 下一步

1. [ ] 部署后端到 Railway
2. [ ] 配置域名
3. [ ] 修改小程序 API 地址
4. [ ] 上传小程序到微信
5. [ ] 提交审核

---

*创建时间: 2026-04-05*
