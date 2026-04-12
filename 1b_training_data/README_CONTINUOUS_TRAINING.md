# Erbing 24小时持续训练系统

让Erbing在虚拟世界中24小时不停训练，自主进化！

---

## 🚀 快速开始

### 1. 启动训练

双击运行 `start_continuous_training.bat`

或者手动运行：

```bash
cd C:\Users\Administrator\.openclaw\workspace\1b_training_data
python erbing_continuous_trainer.py
```

### 2. 监控训练进度

运行监控脚本：

```bash
python monitor_training.py
```

### 3. 停止训练

双击运行 `stop_continuous_training.bat`

或者在训练窗口按 `Ctrl+C`

---

## 📊 训练系统

### 核心功能

- **24/7持续训练**: 不间断运行，自动保存checkpoint
- **智能决策**: 根据能量、技能、知识自动选择最佳行动
- **自动保存**: 每10个episode自动保存checkpoint
- **日志记录**: 完整的训练日志，记录所有活动
- **进度监控**: 实时查看训练进度和状态

### 训练参数

- **保存间隔**: 每10个episode
- **每个episode步数**: 100步
- **行动类型**: 探索、学习、练习、休息
- **技能领域**: 8个（编程、AI技术、安全、部署、工具使用、问题解决、沟通、协作）
- **知识主题**: 15个（Python、JavaScript、机器学习、深度学习、NLP、计算机视觉等）

---

## 📁 文件结构

```
1b_training_data/
├── erbing_virtual_world.db              # 虚拟世界数据库
├── erbing_continuous_trainer.py          # 持续训练系统
├── start_continuous_training.bat         # 启动脚本
├── stop_continuous_training.bat          # 停止脚本
├── monitor_training.py                   # 监控脚本
├── logs/                                 # 日志目录
│   ├── training_YYYYMMDD_HHMMSS.log      # 训练日志
│   └── checkpoint_N.json                 # Checkpoint文件
└── README_CONTINUOUS_TRAINING.md         # 本文件
```

---

## 🎯 训练目标

### 短期目标（1天）
- 完成100个episode
- 探索50个知识点
- 积累500个经验
- 所有技能达到Level 2

### 中期目标（1周）
- 完成700个episode
- 探索200个知识点
- 积累3000个经验
- 所有技能达到Level 5

### 长期目标（1月）
- 完成3000个episode
- 探索500个知识点
- 积累10000个经验
- 所有技能达到Level 10

---

## 📈 监控指标

### 训练进度
- **总Episodes**: 已完成的episode数量
- **总步数**: 已完成的总步数
- **总奖励**: 累计奖励
- **平均奖励**: 每个episode的平均奖励
- **最佳奖励**: 单个episode的最高奖励
- **最差奖励**: 单个episode的最低奖励

### 当前状态
- **能量**: 当前能量/最大能量
- **知识点**: 已探索的知识点数量
- **经验**: 已积累的经验数量

### 技能状态
- **等级**: 技能等级
- **经验**: 技能经验值

---

## 🔧 高级配置

### 修改训练参数

编辑 `erbing_continuous_trainer.py`:

```python
# 修改保存间隔
trainer.run_continuous(save_interval=10, max_steps=100)

# 修改为每5个episode保存一次
trainer.run_continuous(save_interval=5, max_steps=100)

# 修改每个episode的步数
trainer.run_continuous(save_interval=10, max_steps=200)
```

### 修改决策逻辑

编辑 `erbing_auto_evolution.py` 中的 `decide_action()` 方法:

```python
def decide_action(self):
    stats = self.world.get_stats()
    energy = stats['energy']
    
    # 自定义决策逻辑
    if energy < 30:
        return 'rest', None, None
    
    # 更多自定义逻辑...
```

---

## 🛡️ 安全措施

### 自动保存
- 每10个episode自动保存checkpoint
- 按Ctrl+C时自动保存checkpoint
- Checkpoint包含完整的训练状态

### 日志记录
- 所有训练活动都记录在日志文件
- 日志文件按时间戳命名
- 日志文件保存在logs目录

### 数据备份
- 数据库文件: `erbing_virtual_world.db`
- Checkpoint文件: `logs/checkpoint_N.json`
- 日志文件: `logs/training_YYYYMMDD_HHMMSS.log`

---

## 🐛 故障排除

### 训练无法启动

检查Python环境：
```bash
python --version
```

检查依赖：
```bash
pip install sqlite3
```

### 训练中断

查看最新checkpoint：
```bash
python monitor_training.py
```

从checkpoint恢复：
```python
# 手动加载checkpoint
with open('logs/checkpoint_N.json', 'r') as f:
    checkpoint = json.load(f)
```

### 数据库损坏

备份数据库：
```bash
copy erbing_virtual_world.db erbing_virtual_world.db.backup
```

重新初始化：
```bash
python init_world.py
```

---

## 📊 性能优化

### 减少日志输出

编辑 `erbing_continuous_trainer.py`:

```python
# 修改日志间隔
if step % 20 == 19:  # 从每10步改为每20步
    self.log(f"  Step {step + 1}: ...")
```

### 增加训练速度

编辑 `erbing_continuous_trainer.py`:

```python
# 移除sleep
# time.sleep(1)  # 注释掉这行
```

### 减少checkpoint大小

编辑 `erbing_continuous_trainer.py`:

```python
# 减少保存间隔
trainer.run_continuous(save_interval=20, max_steps=100)
```

---

## 🎉 预期效果

### 24小时训练后

- **Episodes**: ~864个（假设每个episode100秒）
- **知识点**: ~200个
- **经验**: ~2000个
- **技能等级**: Level 3-5

### 1周训练后

- **Episodes**: ~6000个
- **知识点**: ~500个
- **经验**: ~10000个
- **技能等级**: Level 8-10

### 1月训练后

- **Episodes**: ~25000个
- **知识点**: ~1000个
- **经验**: ~40000个
- **技能等级**: Level 15-20

---

## 📞 支持

如有问题，查看日志文件：
```bash
type logs\training_*.log
```

或查看checkpoint：
```bash
python monitor_training.py
```

---

**让Erbing自主进化，成为更强的AI助手！** 🚀
