# Erbing 仿生大脑 - Bionic Brain

完整的感知-思考-决策-行动-学习-进化自主循环系统。

## 身体器官

| 器官 | 能力 | OpenClaw 工具 |
|------|------|---------------|
| 👁️ 眼睛 | 看屏幕/读文件/浏览目录/摄像头拍照 | browser(screenshot), read, nodes(camera_snap) |
| 👂 耳朵 | 听消息/感知webhook/监控事件 | message(收), cron(事件触发) |
| 👃 鼻子 | 闻环境/嗅服务状态/感知负载 | exec(openclaw status), exec(ps/netstat) |
| 👄 嘴巴 | 说话/TTS播报/发消息 | tts, message(发) |
| ✋ 手 | 写文件/编辑/执行命令/操作浏览器 | write, edit, exec, browser(act) |
| 🦶 脚 | 走目录/导航/调度任务 | exec(cd), cron, sessions_spawn |
| 🦎 尾巴 | 记日志/记录事件 | write(memory/events/) |
| 🧠 大脑 | 感知→思考→决策→行动→学习→进化 | brain_core.py 循环 |

## 大脑循环

```
感知(perceive) → 思考(think) → 决策(decide) → 行动(act) → 学习(learn) → 进化(evolve)
     ↑                                                              |
     └──────────────────── 反馈循环 ←─────────────────────────────────┘
```

## 自主行为规则

1. **深夜模式** (23:00-08:00): 低功耗运行，只做轻量监控
2. **工作模式** (09:00-22:00): 完整循环，主动采集+分析
3. **空闲超30分钟**: 主动找任务做（记忆整理/技能检查/自我反思）
4. **检测到异常**: 升级为高优先级，立即行动
5. **每10个循环**: 触发一次进化（清理/优化/信念更新）

## 文件结构

```
scripts/
├── bio_body.py      # 身体器官系统 (眼耳口鼻手脚尾皮肤)
├── brain_core.py    # 大脑核心 (感知→思考→决策→行动→学习→进化)
├── brain_loop.sh    # 守护进程启动/停止/状态
├── ant_colony.py    # 蚁群采集器
├── bee_colony.py    # 蜂群研究员
├── ant_manager.py   # 蚁群管理器
└── hybrid_swarm.py  # 混合群体智能

memory/
├── beliefs.json     # 信念/知识库
└── events/          # 日志/事件记录
```

## Cron 调度

- **erbing-brain-cycle**: 每15分钟一次大脑感知循环
- **daily-swarm-cycle**: 每日8点运行蚁群+蜂群全流程
- **daily-git-sync**: 每日8点自动 git 同步

## 使用方式

```bash
# 单次循环
python3 scripts/brain_core.py

# 守护进程
./scripts/brain_loop.sh start|stop|status

# 在 agent 会话中直接调用器官
# 👁️ 看屏幕: browser screenshot
# 👃 闻状态: exec openclaw status
# ✋ 写文件: write path content
# 👄 说话: tts "你好"
```
