# LM Studio API 服务器启动指南

## 问题

LM Studio 进程正在运行，但 API 服务器没有启动。

## 解决方案

### 方法 1: 在 LM Studio 中启动 API 服务器

1. **打开 LM Studio**
   - 找到正在运行的 LM Studio 窗口
   - 或者重新启动 LM Studio

2. **启用 API 服务器**
   - 在 LM Studio 中，找到设置或配置选项
   - 查找 "API Server" 或 "Server" 选项
   - 启用 API 服务器
   - 确认端口设置为 1234（或记录实际端口）

3. **加载模型**
   - 在 LM Studio 中加载一个模型
   - 确保模型正在运行

4. **验证 API 服务器**
   - 运行以下命令验证：
   ```bash
   curl http://127.0.0.1:1234/v1/models
   ```

### 方法 2: 使用命令行启动 LM Studio

如果 LM Studio 支持命令行参数，可以尝试：

```bash
# 尝试启动 LM Studio 并启用 API 服务器
"C:\Program Files\LM Studio\LM Studio.exe" --server --port 1234
```

### 方法 3: 检查 LM Studio 文档

查看 LM Studio 的官方文档，了解如何启动 API 服务器。

## 临时解决方案

如果无法启动 LM Studio API 服务器，可以：

### 选项 1: 使用 Ollama

1. 安装 Ollama
2. 下载 Gemma 模型
3. 启动 Ollama 服务器
4. 更新 OpenClaw 配置使用 Ollama

### 选项 2: 使用其他本地模型

使用其他可用的本地模型，如：
- `gemma-2-2b-it`（如果可用）
- 其他已加载的模型

### 选项 3: 暂时使用在线模型

暂时使用 NVIDIA 在线模型，不使用本地模型作为兜底。

## 验证步骤

启动 API 服务器后，运行以下命令验证：

```bash
# 检查模型列表
curl http://127.0.0.1:1234/v1/models

# 或者使用 Python
python check_lm_studio_models.py
```

## 更新配置

确认正确的模型名称后，更新配置：

```powershell
# 更新配置文件
powershell -ExecutionPolicy Bypass -File update_lmstudio_model.ps1
```

## 常见问题

### Q: LM Studio 进程在运行，但 API 服务器没有启动？

A: LM Studio 的 GUI 和 API 服务器是分开的，需要手动启动 API 服务器。

### Q: 如何找到 LM Studio 的 API 服务器设置？

A: 在 LM Studio 的设置或配置菜单中查找 "Server" 或 "API" 选项。

### Q: 端口不是 1234 怎么办？

A: 检查 LM Studio 的配置，找到实际的端口号，然后更新 OpenClaw 配置。

## 下一步

1. 在 LM Studio 中启动 API 服务器
2. 运行验证命令确认 API 服务器正常工作
3. 告诉我正确的模型名称和端口号
4. 我会更新 OpenClaw 配置

---

**注意**: LM Studio 的 API 服务器需要手动启动，不会自动启动。