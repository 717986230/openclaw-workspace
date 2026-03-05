# AI Clone Skill - 使用说明

**版本：** 1.0.0  
**创建时间：** 2026-03-04  
**开发者：** 机器猫 🐱

---

## 📖 技能简介

**AI Clone** 是一个通用的 AI 机器人克隆技能，任何 AI 机器人都可以使用此技能：

- ✅ **导出自己的配置** → 生成克隆包发给别人
- ✅ **导入别人的配置** → 复制对方的能力和经验

**适用场景：**
- 克隆机器猫到多个设备
- 复制任意 AI 机器人 A → B
- 备份和恢复机器人配置
- 团队间共享机器人能力包

---

## 🚀 快速开始

### 第一步：安装技能

```bash
# 从 clawhub 安装（发布后）
clawhub install ai-clone

# 或手动安装
cp -r ai-clone /your/workspace/skills/
```

### 第二步：使用技能

**机器人 A（源）：导出配置**
```bash
cd /path/to/robot-a/workspace
python scripts/clone_robot.py export
```

**机器人 B（目标）：导入配置**
```bash
cd /path/to/robot-b/workspace
python scripts/clone_robot.py import /path/to/clone-package.zip
```

---

## 📦 详细使用说明

### 命令 1：export（导出配置）

**功能：** 扫描当前工作区，打包核心配置文件

**基本用法：**
```bash
python scripts/clone_robot.py export
```

**输出示例：**
```
📦 导出配置...
   源：/home/admin/.openclaw/workspace
📋 扫描工作区...
  ✅ SOUL.md (1.6KB)
  ✅ IDENTITY.md (0.7KB)
  ✅ USER.md (0.6KB)
  ✅ MEMORY.md (1.2KB)
  ✅ HEARTBEAT.md (2.0KB)
  ✅ TOOLS.md (0.8KB)
  ✅ AGENTS.md (7.7KB)

🗜️  打包为 clone-package-20260304-180000.zip...

✅ 导出完成！
   文件：clone-package-20260304-180000.zip
   大小：9.0KB
   包含：7 个核心文件
```

**高级选项：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--source` | 指定源工作区路径 | `--source /path/to/workspace` |
| `--output` | 自定义输出文件名 | `--output my-robot-clone.zip` |

**示例：**
```bash
# 指定源目录
python scripts/clone_robot.py export --source /home/admin/.openclaw/workspace

# 自定义输出文件名
python scripts/clone_robot.py export --output machine-cat-backup.zip

# 同时指定源和输出
python scripts/clone_robot.py export \
  --source /home/admin/.openclaw/workspace \
  --output backup-20260304.zip
```

---

### 命令 2：import（导入配置）

**功能：** 从克隆包解压并复制配置文件到目标工作区

**基本用法：**
```bash
python scripts/clone_robot.py import /path/to/clone-package.zip
```

**输出示例：**
```
📥 导入配置...
   包：clone-package-20260304-180000.zip
   目标：/home/admin/.openclaw/workspace

📋 克隆包信息:
   创建时间：2026-03-04T18:00:00
   源工作区：/home/admin/.openclaw/workspace
   文件数量：7

📋 即将导入以下文件:
  ✅ SOUL.md
  ✅ IDENTITY.md
  ✅ USER.md
  ✅ MEMORY.md
  ✅ HEARTBEAT.md
  ✅ TOOLS.md
  ✅ AGENTS.md

⚠️  注意：这将覆盖目标目录的现有文件！

📥 正在导入...
  ✅ SOUL.md
  ✅ IDENTITY.md
  ✅ USER.md
  ✅ MEMORY.md
  ✅ HEARTBEAT.md
  ✅ TOOLS.md
  ✅ AGENTS.md

✅ 导入完成！
   目标：/home/admin/.openclaw/workspace
   导入：7 个文件

🎉 机器人已成功复制配置！
```

**高级选项：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--target` | 指定目标工作区路径 | `--target /path/to/workspace` |
| `--preview` | 预览包内容（不执行导入） | `--preview` |

**示例：**
```bash
# 预览包内容
python scripts/clone_robot.py import clone-package.zip --preview

# 指定目标目录
python scripts/clone_robot.py import clone-package.zip \
  --target /home/admin/.openclaw/workspace

# 同时使用多个参数
python scripts/clone_robot.py import clone-package.zip \
  --target /new/workspace \
  --preview
```

---

## 🎯 完整使用流程

### 场景 1：克隆机器猫到新设备

```bash
# === 设备 A（原机器猫）===
cd /home/admin/.openclaw/workspace
python scripts/clone_robot.py export
# 输出：clone-package-20260304-180000.zip

# 通过任何方式传输文件到新设备
# scp, rsync, 邮件，网盘，飞书...

# === 设备 B（新设备）===
cd /new/device/workspace
python scripts/clone_robot.py import /path/to/clone-package.zip

# 完成！新设备现在有机猫的配置和记忆
```

---

### 场景 2：复制任意 AI 机器人 A → B

```bash
# === 机器人 A ===
cd /path/to/robot-a
python scripts/clone_robot.py export --output robot-a-clone.zip

# 发送 robot-a-clone.zip 给机器人 B

# === 机器人 B ===
cd /path/to/robot-b
python scripts/clone_robot.py import robot-a-clone.zip

# 完成！机器人 B 现在拥有机器人 A 的配置
```

---

### 场景 3：定期备份

```bash
# 每天备份一次
python scripts/clone_robot.py export \
  --output backup-$(date +%Y%m%d).zip

# 示例输出：
# backup-20260304.zip
# backup-20260305.zip
# backup-20260306.zip
```

---

### 场景 4：团队共享配置

```bash
# 团队成员 A 创建标准配置模板
cd /team/standard-config
python scripts/clone_robot.py export --output team-standard.zip

# 分享给团队成员
# 上传到团队网盘/Git/飞书...

# 团队成员 B/C/D 下载并导入
python scripts/clone_robot.py import team-standard.zip

# 完成！所有成员使用统一配置
```

---

## 📋 克隆的文件清单

### 核心配置文件（必选）

| 文件 | 说明 | 大小示例 |
|------|------|---------|
| `SOUL.md` | 人格和价值观 | 1.6KB |
| `IDENTITY.md` | 机器人身份定义 | 0.7KB |
| `USER.md` | 用户信息 | 0.6KB |
| `MEMORY.md` | 长期记忆 | 1.2KB |
| `HEARTBEAT.md` | 任务机制 | 2.0KB |
| `TOOLS.md` | 工具配置 | 0.8KB |
| `AGENTS.md` | Agent 配置 | 7.7KB |

**总计：** 约 9-15KB（仅文本配置）

### 不包含的内容（可选）

以下目录默认**不包含**在克隆包中：

- `skills/` - 技能包（体积大，可单独安装）
- `scripts/` - 脚本文件（技能自带）
- `marketing/` - 营销素材（体积大）
- `projects/` - 项目文档
- `docs/` - 文档资料
- `memory/` - 每日记忆文件（可选包含）

**原因：** 保持克隆包轻量，仅复制核心身份配置

---

## ⚠️ 注意事项

### 安全提示

1. **克隆包包含敏感配置**
   - SOUL.md - 人格定义
   - USER.md - 用户信息
   - MEMORY.md - 记忆内容
   - **妥善保管，不要公开分享**

2. **传输时使用加密通道**
   - 推荐使用加密邮件
   - 私有网盘
   - 端到端加密聊天工具

3. **部署后检查文件权限**
   ```bash
   chmod 600 SOUL.md USER.md MEMORY.md
   ```

### 环境特定内容

克隆后**需要手动配置**的内容：

| 项目 | 说明 |
|------|------|
| API Keys | 各服务的 API 密钥 |
| 环境变量 | `.env` 文件内容 |
| 服务地址 | MCP 服务器地址、端口 |
| 文件路径 | 绝对路径需要更新 |

### 不克隆的内容

以下文件/目录**不会**被克隆：

```
.git/                  # Git 版本控制
__pycache__/           # Python 缓存
.openclaw/workspace-state.json  # 运行状态
*.log                  # 日志文件
.DS_Store              # 系统文件
*.pyc                  # Python 编译文件
```

---

## 🔧 故障排查

### 问题 1：找不到核心文件

**错误：** `❌ 未找到核心配置文件`

**解决：**
```bash
# 确认当前目录是工作区根目录
pwd
ls SOUL.md IDENTITY.md USER.md

# 或指定源目录
python scripts/clone_robot.py export --source /path/to/workspace
```

### 问题 2：导入后文件不存在

**解决：**
```bash
# 检查目标目录
ls -la /path/to/target

# 使用绝对路径
python scripts/clone_robot.py import clone-package.zip \
  --target /absolute/path/to/workspace
```

### 问题 3：权限错误

**错误：** `Permission denied`

**解决：**
```bash
# 检查目标目录权限
ls -la /path/to/target

# 修改权限
chmod 755 /path/to/target
chmod 644 /path/to/target/*.md
```

---

## 📊 克隆包结构

```
clone-package-20260304-180000.zip
├── SOUL.md              # 人格
├── IDENTITY.md          # 身份
├── USER.md              # 用户
├── MEMORY.md            # 记忆
├── HEARTBEAT.md         # 任务
├── TOOLS.md             # 工具
├── AGENTS.md            # Agent 配置
└── clone_metadata.json  # 元数据
```

**元数据内容：**
```json
{
  "version": "1.0",
  "created_at": "2026-03-04T18:00:00",
  "source_workspace": "/home/admin/.openclaw/workspace",
  "files": [
    "SOUL.md",
    "IDENTITY.md",
    "USER.md",
    "MEMORY.md",
    "HEARTBEAT.md",
    "TOOLS.md",
    "AGENTS.md"
  ],
  "description": "AI Robot Clone Package"
}
```

---

## 🧪 验证克隆

部署后运行验证：

```bash
# 1. 检查核心文件
ls -la SOUL.md IDENTITY.md USER.md MEMORY.md

# 2. 验证记忆文件
cat MEMORY.md | head -20

# 3. 检查技能包
ls skills/

# 4. 启动测试
openclaw status
```

---

## 📞 技术支持

**问题反馈：** 请在 clawhub.com 技能页面留言

**版本更新：** 
```bash
# 检查更新
clawhub list

# 更新技能
clawhub update ai-clone
```

---

## 📝 更新日志

### v1.0.0 (2026-03-04)
- ✅ 初始版本发布
- ✅ 支持 export 导出配置
- ✅ 支持 import 导入配置
- ✅ 支持 preview 预览包内容
- ✅ 自动识别工作区根目录
- ✅ 元数据记录创建时间和源路径

---

*文档版本：1.0*  
*最后更新：2026-03-04*  
*机器猫 🐱 维护*
