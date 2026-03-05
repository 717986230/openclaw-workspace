---
name: ai-clone
description: 通用 AI 机器人克隆技能。任何 AI 机器人都可以使用此技能：(1) 导出自己的配置打包给别人，(2) 导入别人的包复制到自己身上。用于 A→B 能力复制、团队共享机器人配置、备份恢复。
---

# AI 机器人克隆技能（通用版）

**任何 AI 机器人都可以使用的克隆工具**

---

## 🎯 核心流程

```
┌─────────────┐                    ┌─────────────┐
│  机器人 A   │                    │  机器人 B   │
│  (源)       │                    │  (目标)     │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │ 1. 使用技能导出配置               │
       │    → clone-package.zip          │
       │                                  │
       ├─────────────────────────────────>│
       │         传输文件                  │
       │                                  │
       │                                  │ 2. 使用技能导入配置
       │                                  │    ← clone-package.zip
       │                                  │
       ▼                                  ▼
```

---

## 📦 机器人 A：导出配置

**任何机器人执行以下命令导出自己：**

```bash
# 方法 1：使用当前工作目录（推荐）
python scripts/clone_robot.py export

# 方法 2：指定源目录
python scripts/clone_robot.py export --source /path/to/my/workspace

# 方法 3：自定义输出文件名
python scripts/clone_robot.py export --output my-clone-package.zip
```

**输出：**
```
✅ 导出完成！
   文件：clone-package.zip
   大小：9.1KB
   包含：7 个核心配置文件
```

**然后：** 把 `clone-package.zip` 发给机器人 B（邮件/网盘/聊天工具）

---

## 📥 机器人 B：导入配置

**收到克隆包后执行：**

```bash
# 方法 1：使用当前工作目录（推荐）
python scripts/clone_robot.py import /path/to/clone-package.zip

# 方法 2：指定目标目录
python scripts/clone_robot.py import clone-package.zip --target /path/to/my/workspace

# 方法 3：预览包内容（不执行复制）
python scripts/clone_robot.py import clone-package.zip --preview
```

**输出：**
```
📋 即将导入以下文件：
  ✅ SOUL.md
  ✅ IDENTITY.md
  ✅ USER.md
  ✅ MEMORY.md
  ✅ HEARTBEAT.md
  ✅ TOOLS.md
  ✅ AGENTS.md

⚠️  注意：这将覆盖现有文件！

✅ 导入完成！机器人 B 已复制机器人 A 的配置
```

---

## 📋 核心配置文件

克隆脚本会自动识别和复制以下文件：

### 必选文件（核心身份）
| 文件 | 说明 |
|------|------|
| `SOUL.md` | 人格和价值观 |
| `IDENTITY.md` | 机器人身份定义 |
| `USER.md` | 用户信息 |
| `MEMORY.md` | 长期记忆 |
| `HEARTBEAT.md` | 任务机制 |
| `TOOLS.md` | 本地工具配置 |
| `AGENTS.md` | Agent 配置 |

### 可选目录（能力和资产）
| 目录 | 说明 |
|------|------|
| `memory/` | 每日记忆文件 |
| `skills/` | 技能包 |
| `scripts/` | 自动化脚本 |
| `projects/` | 项目文档 |
| `docs/` | 文档资料 |
| `marketing/` | 营销素材 |

---

## 🔧 命令参考

### 扫描分析
```bash
python scripts/clone_robot.py --scan <源路径>
```
**输出：** 显示可克隆的文件和目录清单

### 创建克隆包
```bash
python scripts/clone_robot.py \
  --source <源路径> \
  --output <输出文件.zip> \
  [--no-optional]  # 可选：不包含可选目录
```

### 解包部署
```bash
python scripts/clone_robot.py \
  --unpack <克隆包.zip> \
  --target <目标路径>
```

---

## 📦 克隆包结构

```
robot-clone.zip
├── SOUL.md              # 人格
├── IDENTITY.md          # 身份
├── USER.md              # 用户
├── MEMORY.md            # 记忆
├── HEARTBEAT.md         # 任务
├── TOOLS.md             # 工具
├── AGENTS.md            # Agent 配置
├── clone_metadata.json  # 元数据
├── memory/              # 每日记忆（可选）
├── skills/              # 技能包（可选）
├── scripts/             # 脚本（可选）
└── ...
```

---

## ⚠️ 注意事项

### 环境特定内容（不克隆）
- `.git/` 目录
- `__pycache__/` 缓存
- `.openclaw/workspace-state.json` 运行状态
- `*.log` 日志文件
- `.DS_Store` 系统文件

### 需要手动配置
1. **API Keys** - 克隆后需要重新配置
2. **环境变量** - 根据新环境调整
3. **服务地址** - 如 MCP 服务器地址
4. **文件路径** - 绝对路径需要更新

### 权限和安全
- 克隆包包含敏感配置，妥善保管
- 传输时使用加密通道
- 部署后检查文件权限

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

## 📊 克隆报告示例

```
📋 检查核心配置文件...
  ✅ SOUL.md (2.1KB)
  ✅ IDENTITY.md (1.5KB)
  ✅ USER.md (892B)
  ✅ MEMORY.md (3.2KB)
  ✅ HEARTBEAT.md (1.8KB)

📁 检查可选目录...
  ✅ memory/ (15 文件，45.3KB)
  ✅ skills/ (8 技能，1.2MB)
  ✅ scripts/ (23 文件，156.7KB)

📊 扫描完成:
   机器人：machine-cat
   核心文件：7 个
   可选目录：3 个
   总大小：1.4MB

📦 创建克隆包...
   源：/home/admin/.openclaw/workspace
   目标：machine-cat-clone.zip

✅ 克隆包创建成功！
   文件：machine-cat-clone.zip
   大小：456.2KB
```

---

## 🔄 迭代更新

克隆后如有改进，可重新打包：
```bash
# 在新环境修改后
python scripts/clone_robot.py \
  --source /new/environment \
  --output machine-cat-v2.zip
```

---

*技能版本：1.0*  
*创建时间：2026-03-04*  
*机器猫 🐱 开发*
