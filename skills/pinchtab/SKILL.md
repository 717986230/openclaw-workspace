---
name: pinchtab
description: Use Pinchtab to control a browser through the unified pinchtab tool for navigation, snapshots, clicks, typing, readable text extraction, screenshots, JavaScript evaluation, PDF export, and tab management.
---

# Pinchtab 技能

**用 Pinchtab 控制浏览器，Token 效率提升 5-13 倍！**

---

## 前置条件

1. Pinchtab 服务器正在运行（默认端口 9867）
2. 如果有认证 token，设置环境变量 `PINCHTAB_TOKEN`

---

## 快速开始

### 1. 启动 Pinchtab 服务器

```bash
# 方式1：直接运行
pinchtab

# 方式2：带认证
PINCHTAB_TOKEN=my-secret pinchtab

# 方式3：Docker
docker run -d -p 9867:9867 pinchtab/pinchtab
```

### 2. 使用技能

这个技能提供以下工具：

- `pinchtab` - 统一的浏览器控制工具

---

## 工具使用

### pinchtab - 统一浏览器控制

**支持的 actions：**

| Action | 描述 |
|--------|------|
| `navigate` | 导航到 URL |
| `snapshot` | 获取页面结构（可交互元素） |
| `click` | 点击元素 |
| `type` | 输入文本 |
| `press` | 按键（如 Enter） |
| `fill` | 填写表单 |
| `hover` | 悬停 |
| `scroll` | 滚动 |
| `select` | 选择下拉框 |
| `focus` | 聚焦元素 |
| `text` | 提取可读文本（最便宜） |
| `tabs` | 标签页管理 |
| `screenshot` | 截图 |
| `evaluate` | 运行 JavaScript |
| `pdf` | 导出 PDF |
| `health` | 健康检查 |

---

## 使用示例

### 示例1：搜索并提取结果

```python
# 1. 导航到搜索页
pinchtab(action="navigate", url="https://example.com/search")

# 2. 获取可交互元素
pinchtab(action="snapshot", filter="interactive", format="compact")

# 3. 点击搜索框（ref 从 snapshot 获取）
pinchtab(action="click", ref="e5")

# 4. 输入搜索词
pinchtab(action="type", ref="e5", text="pinchtab")

# 5. 按回车搜索
pinchtab(action="press", key="Enter")

# 6. 只获取变化（节省 Token）
pinchtab(action="snapshot", diff=True, format="compact")

# 7. 提取文本结果（约 800 tokens）
pinchtab(action="text")
```

### 示例2：Token 策略

**最省 Token 的组合：**
- 阅读内容：用 `text` action
- 交互操作：用 `snapshot` + `filter=interactive&format=compact`
- 后续快照：用 `diff=True`
- 视觉验证：最后才用 `screenshot`

---

## 配置

**环境变量：**

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `PINCHTAB_BASE_URL` | Pinchtab 服务器地址 | `http://localhost:9867` |
| `PINCHTAB_TOKEN` | 认证 token（可选） | - |
| `PINCHTAB_TIMEOUT` | 请求超时（毫秒） | `30000` |

---

## 安全注意事项

- `evaluate` action 可以执行任意 JavaScript，仅限信任的 agent 和域名
- 生产环境建议使用 `PINCHTAB_TOKEN` 保护 API
- 生产环境建议使用 HTTPS 反向代理（Caddy/nginx）

---

## 相关资源

- 官方文档：https://pinchtab.com/docs
- GitHub：https://github.com/pinchtab/pinchtab
