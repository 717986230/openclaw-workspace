# uuoo.site DNS 配置教程（腾讯云版）

## 🎯 域名信息
- **域名**: uuoo.site
- **服务商**: 腾讯云
- **DNS**: DNSPod（腾讯云的 DNS 服务）

---

## 📋 详细配置步骤

### 第一步：登录腾讯云控制台

1. 打开浏览器，访问：**https://console.cloud.tencent.com**
2. 使用你的腾讯云账号登录
3. 在顶部搜索框输入「域名注册」或「DNS 解析」
4. 点击进入「DNS 解析 DNSPod」

或者直接访问：**https://console.dnspod.cn**

---

### 第二步：找到你的域名

在 DNSPod 控制台，你会看到域名列表：
- 找到 `uuoo.site`
- 点击域名，进入解析设置页面

---

### 第三步：添加 DNS 记录

在解析设置页面，点击「**添加记录**」按钮。

你需要添加 **3 条记录**：

---

#### 📌 记录 1：主域名（uuoo.site）

**填写内容**：
```
主机记录: @
记录类型: CNAME
线路类型: 默认
记录值:   cname.vercel-dns.com
TTL:      默认（或选择 600）
```

**操作步骤**：
1. 在「主机记录」输入框输入：`@`（或点击下拉选择「@」）
2. 在「记录类型」下拉框选择：`CNAME`
3. 「线路类型」保持：`默认`
4. 在「记录值」输入框输入：`cname.vercel-dns.com`
5. 「TTL」保持默认
6. 点击「**保存**」按钮

---

#### 📌 记录 2：www 子域名（www.uuoo.site）

**填写内容**：
```
主机记录: www
记录类型: CNAME
线路类型: 默认
记录值:   cname.vercel-dns.com
TTL:      默认（或选择 600）
```

**操作步骤**：
1. 再次点击「添加记录」
2. 在「主机记录」输入：`www`
3. 在「记录类型」选择：`CNAME`
4. 在「记录值」输入：`cname.vercel-dns.com`
5. 点击「保存」

---

#### 📌 记录 3：API 子域名（api.uuoo.site）

**填写内容**：
```
主机记录: api
记录类型: CNAME
线路类型: 默认
记录值:   cname.vercel-dns.com
TTL:      默认（或选择 600）
```

**操作步骤**：
1. 再次点击「添加记录」
2. 在「主机记录」输入：`api`
3. 在「记录类型」选择：`CNAME`
4. 在「记录值」输入：`cname.vercel-dns.com`
5. 点击「保存」

---

## 🖼️ 配置完成示例

配置完成后，你的记录列表应该是这样的：

```
┌────────┬────────┬────────┬──────────────────────┬────────┐
│ 主机记录│ 记录类型│ 线路类型│ 记录值               │ 操作   │
├────────┼────────┼────────┼──────────────────────┼────────┤
│ @      │ CNAME  │ 默认   │ cname.vercel-dns.com │ 修改 删除│
│ www    │ CNAME  │ 默认   │ cname.vercel-dns.com │ 修改 删除│
│ api    │ CNAME  │ 默认   │ cname.vercel-dns.com │ 修改 删除│
└────────┴────────┴────────┴──────────────────────┴────────┘
```

---

## 🚨 重要提示

### 如果已有冲突记录

如果你的域名已经有 `@` 的 **A 记录**（指向 IP 地址），需要：
1. 先**删除**这条 A 记录
2. 再添加 CNAME 记录

**如何检查**：
- 看记录类型是否为 `A`
- 如果是，点击「删除」按钮删除它
- 然后添加我们的 CNAME 记录

---

## ⏰ DNS 生效时间

- **腾讯云 DNSPod**: 通常 5-10 分钟生效
- **最长等待**: 2 小时
- **全球生效**: 可能需要 24 小时

**建议**：配置完成后等待 10 分钟再进行下一步

---

## ✅ 验证 DNS 是否生效

### 方法 1：命令行验证（推荐）

打开 PowerShell，运行：

```powershell
# 检查主域名
nslookup uuoo.site

# 检查 www 子域名
nslookup www.uuoo.site

# 检查 api 子域名
nslookup api.uuoo.site
```

**成功示例**：
```
服务器:  dns.google
Address:  8.8.8.8

非权威应答:
uuoo.site canonical name = cname.vercel-dns.com
```

如果看到 `canonical name = cname.vercel-dns.com`，说明配置成功！

---

### 方法 2：在线验证

访问以下网站检查：

1. **站长工具**: https://tool.chinaz.com/dns/?type=1&host=uuoo.site
2. **DNSChecker**: https://dnschecker.org/#CNAME/uuoo.site

---

## 📸 腾讯云界面示意

DNSPod 控制台的「添加记录」界面：

```
┌──────────────────────────────────────────────┐
│  添加记录                                     │
├──────────────────────────────────────────────┤
│  主机记录 *   [        ]                      │
│              ↑ 输入 @ 或 www 或 api          │
│                                              │
│  记录类型 *   [ CNAME        ▼ ]             │
│              ↑ 选择 CNAME                    │
│                                              │
│  线路类型     [ 默认         ▼ ]             │
│              ↑ 保持默认                       │
│                                              │
│  记录值 *     [                        ]     │
│              ↑ 输入 cname.vercel-dns.com     │
│                                              │
│  TTL          [ 默认         ▼ ]             │
│              ↑ 保持默认                       │
│                                              │
│            [ 保存 ]    [ 取消 ]               │
└──────────────────────────────────────────────┘
```

---

## 🎯 配置完成后

DNS 配置生效后（等待 10 分钟），你需要：

### 1. 部署到 Vercel

1. 访问：**https://vercel.com**
2. 使用 GitHub 登录
3. 点击「New Project」
4. 选择仓库：`717986230/my-nav-admin`
5. 点击「Import」
6. 点击「Deploy」

### 2. 绑定域名

1. 在 Vercel 项目页面，点击「Settings」
2. 点击「Domains」
3. 输入：`uuoo.site`
4. 点击「Add」
5. 同样添加：`www.uuoo.site` 和 `api.uuoo.site`

### 3. 访问你的网站

- **主站**: https://uuoo.site
- **API**: https://api.uuoo.site

---

## 💡 快速配置总结

在腾讯云 DNSPod 控制台，添加 3 条 CNAME 记录：

| 主机记录 | 记录类型 | 记录值 |
|---------|---------|--------|
| @ | CNAME | cname.vercel-dns.com |
| www | CNAME | cname.vercel-dns.com |
| api | CNAME | cname.vercel-dns.com |

保存后等待 10 分钟！

---

## 🆘 遇到问题？

### 常见问题

**Q1: 找不到「添加记录」按钮？**
A: 确保你已经点击进入 `uuoo.site` 的解析设置页面

**Q2: 提示记录冲突？**
A: 删除已有的相同主机记录，再重新添加

**Q3: 不知道填什么？**
A: 
- 主机记录：`@` `www` `api`
- 记录类型：选 `CNAME`
- 记录值：`cname.vercel-dns.com`

**Q4: 还是不懂？**
A: 告诉我你的腾讯云账号截图，我可以帮你标注

---

## 📞 腾讯云官方帮助

- **DNS 解析文档**: https://cloud.tencent.com/document/product/302
- **DNSPod 帮助**: https://docs.dnspod.cn
- **客服电话**: 95716

---

*教程生成时间: 2026-04-05*
*域名服务商: 腾讯云*
*DNS 服务: DNSPod*
