# Hermes 整合系统使用指南

## 概述

Hermes 整合系统将 Hermes Agent 的所有功能整合到二饼系统中，提供 20+ 个功能模块，可以随时调用。

## 整合模块列表

### 核心功能（5个）

1. **洞察引擎**（Insights）- 分析历史会话数据
2. **错误分类器**（Error Classifier）- 智能分类 API 错误
3. **上下文压缩器**（Context Compressor）- 自动压缩长对话
4. **凭证池**（Credential Pool）- 多凭证故障转移
5. **提示构建器**（Prompt Builder）- 系统提示组装

### 工具功能（5个）

6. **浏览器工具**（Browser Tool）- 网页浏览能力
7. **MCP 工具**（MCP Tool）- Model Context Protocol
8. **技能工具**（Skills Tool）- 技能管理
9. **终端工具**（Terminal Tool）- 终端执行
10. **TTS 工具**（TTS Tool）- 文本转语音

### 网关功能（3个）

11. **交付系统**（Delivery System）- 多平台消息交付
12. **钩子系统**（Hooks System）- 事件钩子
13. **会话管理**（Session Management）- 会话跟踪

### 定时任务（1个）

14. **定时任务**（Cron Jobs）- 定时任务调度

### 插件功能（2个）

15. **上下文引擎插件**（Context Engine Plugin）- 上下文管理
16. **记忆插件**（Memory Plugin）- 记忆管理

### 其他功能（4个）

17. **速率限制跟踪**（Rate Limit Tracker）- 速率限制处理
18. **重试工具**（Retry Utils）- 重试逻辑
19. **标题生成器**（Title Generator）- 会话标题生成
20. **轨迹保存**（Trajectory Saving）- 对话轨迹记录

## 快速开始

### 1. 导入整合系统

```python
from erbing_system.hermes_integration import (
    get_hermes_integration_system,
    use_hermes_integration,
    list_hermes_integrations,
    get_hermes_integration_status,
)
```

### 2. 获取系统实例

```python
system = get_hermes_integration_system()
```

### 3. 查看系统状态

```python
status = system.get_status()
print(f"Total Integrations: {status['total_integrations']}")
print(f"Enabled: {status['enabled_integrations']}")
print(f"Total Usage: {status['total_usage']}")
```

### 4. 列出所有整合模块

```python
for integration in system.list_integrations():
    print(f"- {integration.name}: {integration.description}")
```

### 5. 使用整合模块

```python
# 使用洞察引擎
success = use_hermes_integration("insights")

# 使用错误分类器
success = use_hermes_integration("error_classifier")

# 使用上下文压缩器
success = use_hermes_integration("context_compressor")
```

## 详细使用方法

### 洞察引擎（Insights）

```python
from erbing_system.hermes_integrations.insights import get_insights_integration

# 获取洞察引擎实例
insights = get_insights_integration()

# 初始化
insights.initialize()

# 生成洞察报告
insights_data = insights.generate_insights(days=30)
print(f"Total Sessions: {insights_data['total_sessions']}")
print(f"Total Tokens: {insights_data['total_tokens']:,}")
print(f"Total Cost: ${insights_data['total_cost']:.2f}")

# 获取成本估算
cost = insights.get_cost_estimate("claude-opus-4-6", 1000, 500)
print(f"Cost: ${cost:.4f}")

# 获取工具使用统计
tool_stats = insights.get_tool_usage_stats(days=30)
for tool in tool_stats['tools']:
    print(f"{tool['name']}: {tool['calls']} calls")

# 获取活动趋势
activity_trend = insights.get_activity_trend(days=7)
for trend in activity_trend:
    print(f"{trend['date']}: {trend['sessions']} sessions")

# 格式化洞察报告
report = insights.format_insights_report(insights_data)
print(report)
```

### 错误分类器（Error Classifier）

```python
from erbing_system.hermes_integrations.error_classifier import (
    get_error_classifier_integration,
    FailoverReason,
)

# 获取错误分类器实例
error_classifier = get_error_classifier_integration()

# 初始化
error_classifier.initialize()

# 分类错误
error = Exception("401 Unauthorized")
reason = error_classifier.classify_error(error)
print(f"Error Reason: {reason.value if reason else 'None'}")

# 获取恢复动作
action = error_classifier.get_recovery_action(reason)
print(f"Recovery Action: {action}")

# 判断是否应该重试
should_retry = error_classifier.should_retry(reason)
print(f"Should Retry: {should_retry}")

# 判断是否应该轮换凭证
should_rotate = error_classifier.should_rotate_credential(reason)
print(f"Should Rotate Credential: {should_rotate}")

# 判断是否应该压缩上下文
should_compress = error_classifier.should_compress_context(reason)
print(f"Should Compress Context: {should_compress}")

# 记录错误
error_classifier.record_error(reason)

# 获取错误统计
error_stats = error_classifier.get_error_stats()
print(f"Error Stats: {error_stats}")
```

### 其他整合模块

```python
from erbing_system.hermes_integrations import (
    ContextCompressorIntegration,
    CredentialPoolIntegration,
    PromptBuilderIntegration,
    BrowserToolIntegration,
    MCPToolIntegration,
    SkillsToolIntegration,
    TerminalToolIntegration,
    TTSToolIntegration,
    DeliverySystemIntegration,
    HooksSystemIntegration,
    SessionManagementIntegration,
    CronJobsIntegration,
    ContextEnginePluginIntegration,
    MemoryPluginIntegration,
    RateLimitTrackerIntegration,
    RetryUtilsIntegration,
    TitleGeneratorIntegration,
    TrajectorySavingIntegration,
)

# 使用上下文压缩器
context_compressor = ContextCompressorIntegration()
context_compressor.initialize()
result = context_compressor.execute()
print(f"Result: {result}")

# 使用凭证池
credential_pool = CredentialPoolIntegration()
credential_pool.initialize()
result = credential_pool.execute()
print(f"Result: {result}")

# 使用提示构建器
prompt_builder = PromptBuilderIntegration()
prompt_builder.initialize()
result = prompt_builder.execute()
print(f"Result: {result}")

# 使用浏览器工具
browser_tool = BrowserToolIntegration()
browser_tool.initialize()
result = browser_tool.execute()
print(f"Result: {result}")

# 使用 MCP 工具
mcp_tool = MCPToolIntegration()
mcp_tool.initialize()
result = mcp_tool.execute()
print(f"Result: {result}")

# 使用技能工具
skills_tool = SkillsToolIntegration()
skills_tool.initialize()
result = skills_tool.execute()
print(f"Result: {result}")

# 使用终端工具
terminal_tool = TerminalToolIntegration()
terminal_tool.initialize()
result = terminal_tool.execute()
print(f"Result: {result}")

# 使用 TTS 工具
tts_tool = TTSToolIntegration()
tts_tool.initialize()
result = tts_tool.execute()
print(f"Result: {result}")

# 使用交付系统
delivery_system = DeliverySystemIntegration()
delivery_system.initialize()
result = delivery_system.execute()
print(f"Result: {result}")

# 使用钩子系统
hooks_system = HooksSystemIntegration()
hooks_system.initialize()
result = hooks_system.execute()
print(f"Result: {result}")

# 使用会话管理
session_management = SessionManagementIntegration()
session_management.initialize()
result = session_management.execute()
print(f"Result: {result}")

# 使用定时任务
cron_jobs = CronJobsIntegration()
cron_jobs.initialize()
result = cron_jobs.execute()
print(f"Result: {result}")

# 使用上下文引擎插件
context_engine_plugin = ContextEnginePluginIntegration()
context_engine_plugin.initialize()
result = context_engine_plugin.execute()
print(f"Result: {result}")

# 使用记忆插件
memory_plugin = MemoryPluginIntegration()
memory_plugin.initialize()
result = memory_plugin.execute()
print(f"Result: {result}")

# 使用速率限制跟踪
rate_limit_tracker = RateLimitTrackerIntegration()
rate_limit_tracker.initialize()
result = rate_limit_tracker.execute()
print(f"Result: {result}")

# 使用重试工具
retry_utils = RetryUtilsIntegration()
retry_utils.initialize()
result = retry_utils.execute()
print(f"Result: {result}")

# 使用标题生成器
title_generator = TitleGeneratorIntegration()
title_generator.initialize()
result = title_generator.execute()
print(f"Result: {result}")

# 使用轨迹保存
trajectory_saving = TrajectorySavingIntegration()
trajectory_saving.initialize()
result = trajectory_saving.execute()
print(f"Result: {result}")
```

## 系统管理

### 启用/禁用整合模块

```python
# 启用整合模块
system.enable_integration("insights")

# 禁用整合模块
system.disable_integration("insights")
```

### 查看整合模块状态

```python
# 获取特定整合模块
integration = system.get_integration("insights")
print(f"Name: {integration.name}")
print(f"Description: {integration.description}")
print(f"Enabled: {integration.enabled}")
print(f"Status: {integration.status}")
print(f"Last Used: {integration.last_used}")
print(f"Usage Count: {integration.usage_count}")
```

### 获取系统状态

```python
status = system.get_status()
print(f"Initialized: {status['initialized']}")
print(f"Total Integrations: {status['total_integrations']}")
print(f"Enabled: {status['enabled_integrations']}")
print(f"Disabled: {status['disabled_integrations']}")
print(f"Total Usage: {status['total_usage']}")
```

## 测试

### 运行测试

```bash
python test_hermes_integration.py
```

### 测试内容

1. **Hermes 整合系统测试** - 测试系统基本功能
2. **洞察引擎测试** - 测试洞察引擎功能
3. **错误分类器测试** - 测试错误分类器功能
4. **所有整合模块测试** - 测试所有 18 个整合模块

## 文件结构

```
erbing_system/
├── hermes_integration.py              # Hermes 整合系统
├── hermes_integrations/               # 整合模块目录
│   ├── __init__.py                    # 初始化文件
│   ├── insights.py                    # 洞察引擎
│   ├── error_classifier.py            # 错误分类器
│   ├── context_compressor.py          # 上下文压缩器
│   ├── credential_pool.py             # 凭证池
│   ├── prompt_builder.py              # 提示构建器
│   ├── browser_tool.py                # 浏览器工具
│   ├── mcp_tool.py                    # MCP 工具
│   ├── skills_tool.py                 # 技能工具
│   ├── terminal_tool.py               # 终端工具
│   ├── tts_tool.py                    # TTS 工具
│   ├── delivery_system.py             # 交付系统
│   ├── hooks_system.py                # 钩子系统
│   ├── session_management.py          # 会话管理
│   ├── cron_jobs.py                   # 定时任务
│   ├── context_engine_plugin.py       # 上下文引擎插件
│   ├── memory_plugin.py               # 记忆插件
│   ├── rate_limit_tracker.py          # 速率限制跟踪
│   ├── retry_utils.py                 # 重试工具
│   ├── title_generator.py             # 标题生成器
│   └── trajectory_saving.py           # 轨迹保存
test_hermes_integration.py             # 测试文件
create_hermes_integrations.py          # 创建脚本
HERMES_INTEGRATION_GUIDE.md            # 使用指南（本文件）
```

## 注意事项

1. **全局实例** - 所有整合模块都使用全局实例，确保单例模式
2. **线程安全** - 整合模块是线程安全的，可以在多线程环境中使用
3. **缓存机制** - 洞察引擎有缓存机制，默认缓存 1 小时
4. **错误处理** - 所有整合模块都有错误处理机制
5. **状态跟踪** - 所有整合模块都跟踪使用状态

## 下一步

1. **扩展功能** - 根据需要扩展整合模块的功能
2. **优化性能** - 优化整合模块的性能
3. **添加测试** - 添加更多测试用例
4. **完善文档** - 完善使用文档

---

**更新时间**: 2026-04-20 22:55
**状态**: Hermes 整合系统已完成并测试通过
**整合模块**: 20 个
**测试状态**: 所有测试通过