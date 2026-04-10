# uuoo.site DNS 配置教程（DNSPod/腾讯云版）

## 🎯 你的域名信息
- **域名**: uuoo.site
- **DNS 服务商**: DNSPod（腾讯云）
- **需要配置**: 3 条 CNAME 记录

---

## 📋 配置步骤

### 第一步：登录 DNSPod 控制台

1. 打开浏览器，访问：**https://console.dnspod.cn**
2. 使用你的腾讯云账号登录
3. 找到域名 `uuoo.site`，点击进入

---

### 第二步：添加 DNS 记录

在 DNSPod 控制台，点击「添加记录」，按以下配置添加 3 条记录：

#### 记录 1：主域名
```
主机记录: @
记录类型: CNAME
记录值:   cname.vercel-dns.com
TTL:      600（或默认）
```

**操作步骤**：
1. 点击「添加记录」
2. 在「主机记录」输入框输入：`@`（或者选择「@」）
3. 在「记录类型」下拉框选择：`CNAME`
4. 在「记录值」输入框输入：`cname.vercel-dns.com`
5. TTL 保持默认或选择 `600`
6. 点击「保存」

---

#### 记录 2：www 子域名
```
主机记录: www
记录类型: CNAME
记录值:   cname.vercel-dns.com
TTL:      600（或默认）
```

**操作步骤**：
1. 再次点击「添加记录」
2. 在「主机记录」输入：`www`
3. 在「记录类型」选择：`CNAME`
4. 在「记录值」输入：`cname.vercel-dns.com`
5. 点击「保存」

---

#### 记录 3：api 子域名
```
主机记录: api
记录类型: CNAME
记录值:   cname.vercel-dns.com
TTL:      600（或默认）
```

**操作步骤**：
1. 再次点击「添加记录」
2. 在「主机记录」输入：`api`
3. 在「记录类型」选择：`CNAME`
4. 在「记录值」输入：`cname.vercel-dns.com`
5. 点击「保存」

---

## 🖼️ 配置示意图

配置完成后，你的 DNS 记录列表应该像这样：

```
┌────────┬────────┬────────┬──────────────────────┬─────┐
│ 主机记录│ 记录类型│ 记录值  │ 备注                 │ TTL │
├────────┼────────┼────────┼──────────────────────┼─────┤
│ @      │ CNAME  │ cname.vercel-dns.com │ 主站    │ 600 │
│ www    │ CNAME  │ cname.vercel-dns.com │ www站   │ 600 │
│ api    │ CNAME  │ cname.vercel-dns.com │ API接口 │ 600 │
└────────┴────────┴────────┴──────────────────────┴─────┘
```

---

## ⏰ DNS 生效时间

- **DNSPod**: 通常 10 分钟内生效
- **最长等待**: 2 小时
- **全球生效**: 可能需要 24-48 小时

---

## ✅ 验证 DNS 是否生效

### 方法 1：在线验证
访问：https://tool.chinaz.com/dns/?type=1&host=uuoo.site

检查是否有 `cname.vercel-dns.com` 的记录

### 方法 2：命令行验证
打开 PowerShell，运行：
```powershell
nslookup uuoo.site
nslookup www.uuoo.site
nslookup api.uuoo.site
```

如果看到 `cname.vercel-dns.com`，说明配置成功！

---

## 🚨 常见问题

### Q1: 主机记录不知道填什么？
**A**: 主机记录就是子域名的名称：
- `@` = 主域名（uuoo.site）
- `www` = www 子域名（www.uuoo.site）
- `api` = api 子域名（api.uuoo.site）

### Q2: 记录类型选什么？
**A**: 必须选择 `CNAME`（别名记录），不要选 A 记录！

### Q3: TTL 填多少？
**A**: 默认即可，或填 `600`（10分钟）

### Q4: 有冲突记录怎么办？
**A**: 如果已经有 `@` 的 A 记录，需要先删除，再添加 CNAME 记录

---

## 📸 DNSPod 界面说明

DNSPod 控制台界面大致如下：

```
┌─────────────────────────────────────────────┐
│  添加记录                                    │
├─────────────────────────────────────────────┤
│  主机记录: [     ]  (输入 @ 或 www 或 api)  │
│  记录类型: [CNAME ▼]                        │
│  记录值:   [                     ]          │
│  TTL:     [600 ▼]                           │
│                                             │
│            [保存]  [取消]                   │
└─────────────────────────────────────────────┘
```

---

## 🎯 配置完成后的下一步

DNS 配置生效后（10分钟），你需要：

1. **访问 Vercel**: https://vercel.com
2. **导入项目**: 选择 `717986230/my-nav-admin`
3. **部署**: 点击 Deploy 按钮
4. **绑定域名**: 在 Settings → Domains 添加 `uuoo.site`

---

## 💡 快速配置总结

在 DNSPod 添加 3 条记录：
1. `@` → CNAME → `cname.vercel-dns.com`
2. `www` → CNAME → `cname.vercel-dns.com`
3. `api` → CNAME → `cname.vercel-dns.com`

保存后等待 10 分钟即可！

---

*教程生成时间: 2026-04-05*
*域名: uuoo.site*
*DNS 服务商: DNSPod（腾讯云）*
