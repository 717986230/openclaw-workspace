# ClawHub 发布指南

## 发布步骤

### 1. 准备技能包
```
agency-agents-caller/
├── SKILL.md                    # 技能主文档
├── scripts/
│   └── agent_caller.py        # 核心脚本
├── examples/
│   └── usage_demo.py          # 使用示例
└── README.md                   # 说明文档
```

### 2. 使用ClawHub CLI发布

```bash
# 安装ClawHub CLI
npm install -g clawhub-cli

# 登录
clawhub login

# 发布技能
clawhub publish agency-agents-caller
```

### 3. 或使用API发布
```bash
curl -X POST https://clawhub.com/api/skills \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "skill=@agency-agents-caller.tar.gz"
```

---

## 当前状态
技能包已准备好，位于：
`C:\Users\Administrator\.openclaw\workspace\skills\agent-calling-system\`

需要发布的文件：
- ✅ SKILL.md
- ✅ scripts/agent_caller.py (需复制)
- ✅ examples/usage_demo.py (需创建)
- ⏳ README.md (需创建)

---

*创建时间: 2026-04-11*
