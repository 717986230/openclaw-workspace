# Erbing 统一进化系统

## 🌍 概述

统一进化系统整合了三个独立的进化/训练系统，提供一个完整的AI进化环境。

## 📦 整合的组件

### 1. erbing-evolution - 进化框架
- **定位**: 宏观进化框架
- **核心功能**:
  - 进化引擎 (EvolutionEngine)
  - 自我评估器 (SelfEvaluator)
  - 自我调节器 (SelfRegulator)
  - 进化配置 (evolution_config.yaml)
- **作用**: 定义进化目标、评估指标、进化机制

### 2. erbing-gbrain-evolution - GBrain架构
- **定位**: GBrain架构概念整合
- **核心功能**:
  - 编译真相页面 (Compiled Truth Pages)
  - 时间线追踪 (Timeline Tracking)
  - 实体关系管理
- **作用**: 提供特定的知识组织方式

### 3. virtual_world_advanced - 虚拟世界
- **定位**: 具体训练环境
- **核心功能**:
  - 虚拟沙盒 (Virtual Sandbox)
  - 时间压缩器 (Time Accelerator)
  - 并行多宇宙 (Parallel Universe)
  - 任务模拟器 (Mission Simulator)
  - 对抗训练场 (Adversarial Arena)
  - 边界案例生成 (Edge Case Generator)
  - 压力测试池 (Stress Test Pool)
  - 现实接口 (Reality Interface)
  - 能力输出 (Capability Exporter)
  - 安全守护 (Safety Guardian)
- **作用**: 提供具体的训练工具和环境

## 🚀 快速开始

### 方法1: 使用批处理文件
```bash
start_unified_evolution.bat
```

### 方法2: 直接运行Python
```bash
cd C:\Users\Administrator\.openclaw\workspace
python unified_evolution_system.py
```

## 🎮 使用流程

### 1. 启动统一进化
```
选择 [1] 启动统一进化
```
这将：
- 初始化所有子系统
- 执行进化框架评估
- 创建GBrain真相页面
- 启动虚拟世界训练环境

### 2. 运行训练周期
```
选择 [2] 运行训练周期
```
这将：
- 在虚拟世界中执行任务训练
- 在对抗训练场进行对战
- 执行进化框架调节
- 更新GBrain知识库

### 3. 查看状态
```
选择 [3] 查看统一状态
```
显示：
- 当前等级和XP
- 训练周期数
- 各子系统状态

### 4. 保存/加载状态
```
选择 [5] 保存状态
选择 [6] 加载状态
```
状态保存在 `unified_evolution_state.json`

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│   Unified Evolution System (统一系统)    │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  Evolution   │ │  GBrain  │ │  Virtual     │
│  Framework   │ │  Arch    │ │  World       │
│              │ │          │ │              │
│ - Engine     │ │ - Truth  │ │ - Sandbox    │
│ - Evaluator  │ │ - Timeline│ │ - Training   │
│ - Regulator  │ │ - Entity  │ │ - Bridge     │
└──────────────┘ └──────────┘ └──────────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
        ┌──────────────────────┐
        │  Unified State       │
        │  - XP & Level        │
        │  - Training Cycles   │
        │  - System Status     │
        └──────────────────────┘
```

## 🎯 进化机制

### XP系统
- 完成任务获得XP
- 对战胜利获得XP
- 每1000XP升一级

### 训练周期
每个训练周期包括：
1. 虚拟世界任务训练
2. 对抗训练场对战
3. 进化框架自动调节
4. GBrain知识更新

### 等级系统
- 等级1: 基础能力
- 等级2-5: 进阶能力
- 等级6-10: 高级能力
- 等级10+: 专家能力

## 📈 状态文件

`unified_evolution_state.json` 存储统一状态：

```json
{
  "agent_id": "erbing",
  "version": "3.0.0-unified",
  "start_time": "2026-04-14T05:30:00",
  "active_systems": [
    "evolution_framework",
    "gbrain_architecture",
    "virtual_world"
  ],
  "evolution_phase": "PHASE_1",
  "training_cycles": 10,
  "total_xp": 2500,
  "current_level": 3,
  "capsule_id": "77467f0153d21cd0",
  "sandbox_id": "SBX-20260414050655-6085"
}
```

## 🔧 配置

### 进化配置
编辑 `erbing-evolution/evolution_config.yaml` 修改进化参数

### 虚拟世界配置
编辑 `virtual_world_advanced/environment/graduation_criteria.yaml` 修改毕业标准

## 📝 日志

各子系统有自己的日志文件：
- `erbing-evolution/evolution_state.json`
- `virtual_world_advanced/*.db` (SQLite数据库)

## 🛡️ 安全机制

- 所有数据加密存储
- 会话令牌验证
- 速率限制保护
- 权限分级管理

## 🔄 持续进化

系统设计为24/7持续运行：
- 自动保存检查点
- 持续训练和进化
- 自动调节和优化

## 📞 支持

如有问题，检查：
1. 各子系统是否正确初始化
2. 状态文件是否可访问
3. 数据库文件是否正常

---
**Created: 2026-04-14**
**Version: 3.0.0-unified**
**Status: Active**
