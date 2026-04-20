# Erbing 统一进化系统 - 快速参考

## 🚀 快速启动

### Windows用户
```bash
start_unified_evolution.bat
```

### 直接运行
```bash
cd C:\Users\Administrator\.openclaw\workspace
python unified_evolution_system.py
```

### 自动化测试
```bash
python test_unified_system.py
```

## 📋 菜单选项

```
[1] 启动统一进化
[2] 运行训练周期
[3] 查看统一状态
[4] 查看系统状态
[5] 保存状态
[6] 加载状态
[0] 退出
```

## 🎯 典型工作流

### 首次使用
1. 选择 [1] 启动统一进化
2. 等待所有系统初始化完成
3. 选择 [5] 保存初始状态

### 日常训练
1. 选择 [6] 加载之前的状态
2. 选择 [2] 运行训练周期（可重复）
3. 选择 [3] 查看进度
4. 选择 [5] 保存状态

### 查看进度
1. 选择 [3] 查看统一状态
2. 选择 [4] 查看系统状态

## 📊 状态说明

### 统一状态
- **agent_id**: 代理标识符
- **version**: 系统版本
- **current_level**: 当前等级
- **total_xp**: 总经验值
- **training_cycles**: 训练周期数
- **capsule_id**: 虚拟舱ID

### 系统状态
- **evolution_framework**: 进化框架状态
- **gbrain_architecture**: GBrain架构状态
- **virtual_world**: 虚拟世界状态

## 🎮 XP系统

### 获得XP
- 完成任务: +XP
- 对战胜利: +XP
- 训练完成: +XP

### 等级提升
- 每1000XP升一级
- 等级越高，能力越强

## 📁 重要文件

### 系统文件
- `unified_evolution_system.py` - 主程序
- `test_unified_system.py` - 测试脚本
- `start_unified_evolution.bat` - 启动脚本

### 状态文件
- `unified_evolution_state.json` - 统一状态

### 文档文件
- `UNIFIED_EVOLUTION_README.md` - 完整文档
- `UNIFIED_INTEGRATION_REPORT.md` - 整合报告

## 🔧 故障排除

### 系统无法启动
- 检查Python是否安装
- 检查依赖是否满足
- 查看错误信息

### 状态无法加载
- 检查 `unified_evolution_state.json` 是否存在
- 检查文件格式是否正确

### 训练失败
- 检查虚拟世界是否正常初始化
- 检查Capsule ID是否有效
- 查看详细错误信息

## 📞 获取帮助

### 查看文档
```bash
cat UNIFIED_EVOLUTION_README.md
```

### 查看整合报告
```bash
cat UNIFIED_INTEGRATION_REPORT.md
```

### 运行测试
```bash
python test_unified_system.py
```

## 💡 提示

- 定期保存状态
- 查看训练进度
- 监控系统状态
- 阅读文档了解更多

---
**Version: 3.0.0-unified**
**Last Updated: 2026-04-14**
