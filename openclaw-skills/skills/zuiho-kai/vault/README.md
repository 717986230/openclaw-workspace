# Vault - Secure Password Storage

🔒 **AES-256-GCM encryption** - Secure local password storage with industry-standard encryption.

Secure local password storage tool with CLI interface and AES-256-GCM encryption.

## Features

- 🔒 AES-256-GCM encryption for all stored passwords
- 📝 Simple command-line interface
- 🗂️ Key management and listing
- 💾 JSON-based local storage (encrypted)
- 🕐 Automatic timestamp tracking
- 🔑 Master key protection

## 安装

```bash
cd /path/to/openclaw-vault
npm install
openclaw plugins link $(pwd)
```

## 配置主密钥

**必需**: 设置主加密密钥

通过环境变量：

```bash
export VAULT_MASTER_KEY="your-secure-master-key-here"
```

或在 OpenClaw 配置中：

```json
{
  "plugins": {
    "vault": {
      "masterKey": "your-secure-master-key-here",
      "storageFile": ".vault/passwords.json"
    }
  }
}
```

⚠️ **重要**: 请妥善保管主密钥！没有它将无法解密已存储的密码。

## 使用方法

### 设置密码

```bash
vault gemini sk-abc123xyz
```

保存密钥 `gemini` 的密码为 `sk-abc123xyz`。

### 显示密码

```bash
vault gemini show
```

显示密钥 `gemini` 的密码。

### 删除密码

```bash
vault gemini remove
```

删除密钥 `gemini` 的密码。

### 列出所有密钥

```bash
vault list
```

显示所有已保存的密钥及其创建/更新时间。

## 配置

在 OpenClaw 配置中可以自定义：

```json
{
  "plugins": {
    "vault": {
      "masterKey": "your-secure-master-key-here",
      "storageFile": ".vault/passwords.json"
    }
  }
}
```

### 配置选项

- `masterKey`: 主加密密钥（也可使用 VAULT_MASTER_KEY 环境变量）
- `storageFile`: 密码存储文件路径（相对于用户主目录）

## 存储位置

默认存储在 `~/.vault/passwords.json`（加密格式）

## 安全特性

🔒 **加密详情**:

- **算法**: AES-256-GCM (Galois/Counter Mode)
- **密钥派生**: scrypt 使用随机盐（每个密码独立）
- **初始化向量**: 每个密码使用随机 12 字节 IV（GCM 推荐大小）
- **盐值**: 每个密码使用随机 32 字节盐，与加密数据一起存储
- **认证**: GCM 认证标签确保完整性验证

**安全最佳实践**：
1. 使用强壮且唯一的主密钥（建议至少 32 字符）
2. 安全存储主密钥（环境变量或安全配置）
3. 设置严格的文件权限：`chmod 600 ~/.vault/passwords.json`
4. 将 `.vault/` 添加到 `.gitignore`
5. 永远不要将主密钥提交到版本控制
6. 使用系统级磁盘加密提供额外保护
7. 安全备份主密钥 - 丢失密钥意味着丢失所有密码

**适用于**：
- 开发/测试凭据
- API 密钥和令牌
- 个人密码
- 团队共享凭据（需安全分发密钥）

## 示例

```bash
# 保存 API 密钥
vault openai sk-proj-abc123
vault anthropic sk-ant-xyz789

# 查看密钥
vault openai show
# 输出: Password for 'openai': sk-proj-abc123

# 列出所有密钥
vault list
# 输出:
# Stored passwords:
# • openai (created: 2026-02-17T..., updated: 2026-02-17T...)
# • anthropic (created: 2026-02-17T..., updated: 2026-02-17T...)

# 删除密钥
vault openai remove
```

## 许可证

MIT

## 作者

zuiho-kai
