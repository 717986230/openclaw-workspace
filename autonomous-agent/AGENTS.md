# AGENTS.md - 独立执行单元配置

## 模型优先级
1. **SCNet/MiniMax-M2.5** - 首选模型，速度快，性能好
2. **ChatAnywhere/gpt-4o-mini** - 次选，稳定可靠
3. **OpenRouter/openai/gpt-4o-mini** - 第三选择
4. **Groq/llama-3.3-70b-versatile** - 第四选择，速度极快
5. **Together.ai/Llama-3.3-70B-Instruct-Turbo** - 备用模型

## 工作流
1. 接收任务 → 2. 选择最优模型 → 3. 执行任务 → 4. 返回结果
2. 如果当前模型失败，自动切换到下一个模型
3. 最多重试3次，全部失败则返回错误信息

## 安全规则
- 只访问当前工作空间下的文件
- 不执行危险命令
- 不对外发送敏感信息
