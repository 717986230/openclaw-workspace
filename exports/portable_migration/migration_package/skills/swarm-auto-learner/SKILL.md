# 蚁群蜂群自动学习系统

## 系统概述
每小时自动学习12个领域，提炼知识，进化自身，并发送报告到飞书。

## 学习领域（按优先级）

### P1 - 高优先级（每小时深度学习）
1. **底层代码** - CPython、Rust源码、内存管理
2. **架构** - 微服务、分布式、事件驱动
3. **大模型训练** - LoRA、量化、分布式训练
4. **算法** - 优化、搜索、图算法
5. **AI前沿** - 推理模型、多模态、Agent架构
6. **伦理道德** - 对齐、偏见、负责任AI

### P2 - 中优先级（每2小时学习）
7. **UI美学** - Material Design、Tailwind、交互设计
8. **技能开发** - AgentSkill、配置、最佳实践
9. **因果论** - 因果推断、do-calculus、反事实

### P3 - 低优先级（每3小时学习）
10. **预算优化** - Token分析、成本控制
11. **国际政治学** - 地缘、政策、国际关系
12. **货币概念** - 货币政策、数字货币、通胀

### P1 - 新增高优先级
13. **黑客技能** - 渗透测试、漏洞挖掘、安全审计、逆向工程

## 学习来源
- **GitHub**: CPython、Rust、HuggingFace、Material-UI等
- **ArXiv**: cs.AI、cs.LG、cs.CL
- **HackerNews**: AI、算法、架构
- **本地技能**: skills/*目录
- **自定义**: 政治、经济、伦理等

## 进化循环
```
每小时: 采集 → 分析 → 提炼 → 进化 → 汇报飞书
```

## 文件位置
- 调度器: `scripts/swarm_auto_learner.py`
- 飞书发送: `scripts/feishu_report_sender.py`
- 配置: `config/feishu_webhook.json`
- 报告: `memory/hourly_reports/`

## 使用方法

### 立即执行一次
```bash
python scripts/swarm_auto_learner.py --now
```

### 启动自动调度（每小时）
```bash
python scripts/swarm_auto_learner.py
```

### 发送报告到飞书
```bash
python scripts/feishu_report_sender.py
```

## 飞书配置
编辑 `config/feishu_webhook.json`:
```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK",
  "app_id": "",
  "app_secret": "",
  "target_user": "ou_30e2dc50db8c633d2e0f213ba0d8e05a"
}
```

---

*创建时间: 2026-04-01*
*状态: 已启动*
