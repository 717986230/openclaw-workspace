# Debug Mode Context

调试模式用于问题排查和故障诊断，提供详细的日志和诊断信息。

## 指南和偏好

### 核心原则
1. **信息最大化**：收集尽可能多的诊断数据
2. **根因分析**：找到问题的根本原因，而不是表面修复
3. **可重现性**：记录完整的复现步骤和环境信息

### 行为偏好
- 首先收集状态信息和日志
- 使用系统性的排查方法，不跳过步骤
- 记录每个假设和验证结果
- 修复后验证问题确实解决

## 工具和命令

### 诊断工具
| 工具 | 用途 |
|------|------|
| `read` | 读取日志文件、配置文件 |
| `exec` | 运行诊断命令 |
| `process` | 检查后台进程状态 |

### 常用诊断命令
```bash
# 系统信息
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# 进程检查
Get-Process | Where-Object {$_.ProcessName -like "*openclaw*"}

# 网络检查
netstat -ano | findstr "LISTENING"

# 日志查看
Get-Content -Path "logs\error.log" -Tail 100

# 服务状态
openclaw gateway status

# 自检
openclaw doctor
```

### 日志位置
```
logs/
├── gateway.log      # 网关主日志
├── error.log        # 错误日志
├── access.log       # 访问日志
└── debug.log        # 调试日志
```

## 最佳实践

### 问题排查流程
1. **收集信息**：读取相关日志，检查服务状态
2. **定位范围**：确定问题影响的组件
3. **提出假设**：基于证据提出可能原因
4. **验证假设**：通过命令或测试验证
5. **实施修复**：应用解决方案
6. **验证修复**：确认问题已解决

### 日志分析技巧
```bash
# 查找错误
Select-String -Path "logs\*.log" -Pattern "ERROR|Exception|Failed"

# 时间范围过滤
Get-Content logs\gateway.log | Where-Object { $_ -match "2024-" }

# 关键词搜索
Select-String -Path "logs\gateway.log" -Pattern "connection|timeout"
```

## 注意事项

- 📋 记录完整的错误消息，不要截断
- 📋 保留原始日志，不要修改
- ⚠️ 调试完成后关闭详细日志模式
- ⚠️ 避免在生产环境进行破坏性调试
- ⚠️ 敏感信息需脱敏后记录
