# Claude Code Features - 任务追踪与交互增强

## 描述
将 Claude Code 的优秀特性融合到 OpenClaw 中：TodoWrite 任务追踪、Ask 用户交互、worktree 隔离模式。

## 功能

### 1. TodoWrite - 任务追踪系统

自动追踪任务进度，支持状态更新和进度可视化。

```markdown
## Todos
- [ ] 分析代码结构
- [x] 创建任务追踪模块
- [ ] 实现用户交互
```

### 2. Ask - 用户交互系统

支持多种交互模式：
- 确认问题 (confirm)
- 选择问题 (select)
- 多选问题 (multiselect)
- 输入问题 (input)

### 3. Worktree 隔离模式

支持 Git worktree 隔离，实现并行开发：
- 主工作区保持干净
- 每个任务独立 worktree
- 完成后自动清理

## 使用方式

### 任务追踪

在执行复杂任务时，系统会自动：
1. 分析任务步骤
2. 创建 todo 列表
3. 实时更新进度
4. 完成后归档

### 用户交互

当需要用户确认时：
- 简单确认：直接回复 y/n
- 选择：回复选项编号
- 多选：回复多个编号（逗号分隔）

### Worktree 模式

对于需要隔离的任务：
1. 创建新的 worktree
2. 在隔离环境中执行
3. 完成后合并或清理

## 配置

在 `memory/preferences/todo-config.md` 中配置：

```yaml
todo:
  autoTrack: true        # 自动追踪任务
  showProgress: true     # 显示进度条
  archiveOnComplete: true # 完成后归档

ask:
  timeout: 300000        # 交互超时（5分钟）
  defaultConfirm: false  # 默认确认值

worktree:
  enabled: true          # 启用 worktree 隔离
  branchPrefix: "task/"  # 分支前缀
  cleanupOnMerge: true   # 合并后清理
```

## 注意事项

1. 任务追踪不会影响正常对话
2. 用户交互有超时机制
3. Worktree 模式需要 Git 仓库
