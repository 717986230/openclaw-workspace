# Erbing Agent - U 盘便携迁移系统

## 简介
使用 U 盘在不同电脑间一键迁移 Erbing Agent，无需网络，整个过程离线完成。

## 使用方法

### 第一步：在原电脑导出
1. 把整个 `Erbing_Migration` 文件夹复制到 U 盘
2. 在原电脑上双击 `migrate.bat` 或在命令行运行：
   ```
   migrate.bat export
   ```
3. 等待导出完成（大约 30MB）

### 第二步：在新电脑导入
1. 把 U 盘插到新电脑
2. 确保新电脑已安装 OpenClaw
3. 双击 `migrate.bat` 或在命令行运行：
   ```
   migrate.bat import
   ```
4. 等待导入完成

### 第三步：验证
在新电脑上运行：
```
migrate.bat check
```

## 迁移内容
- ✅ 记忆数据库（288+ 记忆，71 个表）
- ✅ LanceDB 向量数据库
- ✅ 33 个 Skills
- ✅ 317 个 Scripts
- ✅ 配置文件
- ✅ 工作区文件（身份、偏好设置等）

## 不包括（需重新配置）
- ❌ OpenClaw 本身（需新电脑先安装）
- ❌ 频道凭证（Discord、Feishu 等）
- ❌ 本地 Ollama 模型

## 文件夹结构
```
Erbing_Migration/
├── migrate.bat          # 主迁移脚本（双击运行）
├── README.md            # 本说明文件
└── migration_package/   # 迁移包（导出后生成）
    ├── xiaozhi_memory.db
    ├── lancedb/
    ├── skills/
    ├── scripts/
    ├── config/
    └── *.md (工作区文件)
```

## 命令行选项
```cmd
migrate.bat export    # 导出到 U 盘
migrate.bat import    # 从 U 盘导入
migrate.bat check     # 验证迁移包
```

## 系统要求
- Windows 7/10/11
- Python 3.7+（可选，用于高级验证）
- OpenClaw 已安装

## 故障排除

### "未找到迁移包" 错误
确保在原电脑已运行 `migrate.bat export`，并且 migration_package 文件夹存在。

### "未找到 OpenClaw 工作区" 错误
先在新电脑安装 OpenClaw。

### 导入后技能不可用
尝试重启 OpenClaw 服务：
```cmd
openclaw gateway restart
```

## 版本
v1.0.0 - 2026-04-21

---
由 Erbing Agent 生成