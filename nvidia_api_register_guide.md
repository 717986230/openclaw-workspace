# NVIDIA API 账户注册指南

## 概述

NVIDIA 提供免费的 OpenAI 兼容 API，支持多种开源模型。

## ⚠️ 重要说明

**没有自动注册脚本**

- NVIDIA API 账户需要手动注册
- 自动注册脚本可能违反 NVIDIA 服务条款
- 建议使用官方注册流程

## 手动注册步骤

### 1. 访问 NVIDIA Build 平台

打开浏览器，访问：
```
https://build.nvidia.com
```

### 2. 创建账户

- 点击 "Sign Up" 或 "注册"
- 填写邮箱地址
- 设置密码
- 完成邮箱验证

### 3. 获取 API 密钥

登录后，访问：
```
https://build.nvidia.com/settings/api-keys
```

- 点击 "Create API Key"
- 复制生成的 API 密钥（格式：`nvapi-...`）

### 4. 配置 OpenClaw

#### 方法 1：环境变量

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
```

#### 方法 2：配置文件

编辑 `~/.openclaw/config.json`：

```json5
{
  "env": {
    "NVIDIA_API_KEY": "nvapi-..."
  },
  "models": {
    "providers": {
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "api": "openai-completions"
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "nvidia/nvidia/nemotron-3-super-120b-a12b"
      }
    }
  }
}
```

### 5. 设置模型

```bash
openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
```

## 可用模型

| 模型引用 | 名称 | 上下文长度 | 最大输出 |
|---------|------|-----------|---------|
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192 |
| `nvidia/moonshotai/kimi-k2.5` | Kimi K2.5 | 262,144 | 8,192 |
| `nvidia/minimaxai/minimax-m2.5` | Minimax M2.5 | 196,608 | 8,192 |
| `nvidia/z-ai/glm5` | GLM 5 | 202,752 | 8,192 |

## 费用说明

- **当前状态**: 免费
- **限制**: 可能有速率限制
- **更新**: 访问 build.nvidia.com 查看最新信息

## 注意事项

### 安全建议

- 不要在命令行中直接传递 API 密钥（会进入历史记录）
- 使用环境变量存储 API 密钥
- 不要将 API 密钥提交到 Git 仓库

### 服务条款

- 遵守 NVIDIA 服务条款
- 不要滥用 API
- 注意速率限制

## 故障排除

### API 密钥无效

- 检查 API 密钥格式（应该以 `nvapi-` 开头）
- 确认账户状态正常
- 重新生成 API 密钥

### 连接失败

- 检查网络连接
- 确认 API 端点地址正确
- 检查防火墙设置

### 速率限制

- 减少请求频率
- 使用缓存
- 考虑升级账户

## 相关资源

- NVIDIA Build: https://build.nvidia.com
- API 文档: https://build.nvidia.com/docs
- OpenClaw 文档: https://docs.openclaw.ai

## 总结

NVIDIA API 提供免费的 OpenAI 兼容接口，支持多种开源模型。

**注册方式**: 手动注册
**费用**: 免费
**模型**: 4 种可用模型
**上下文**: 最高 262,144 tokens

---

**注意**: 没有自动注册脚本，请使用官方注册流程！