# AI 安全工具整合

整合自：CyberMind、HexMind v14

## 一、项目精华提炼

### 1. CyberMind - AI 驱动渗透测试
**核心设计**: AI Agent 驱动的自动化安全测试
- 自动化侦察流程
- 漏洞扫描自动化
- 级联攻击链

### 2. HexMind v14 - 自主黑客集体
**核心设计**: 多 Agent 自主安全框架
- 视觉黑客（Playwright + Gemini）
- 24/7 漏洞赏金猎人
- AST 利用变异器
- 分布式蜂群架构
- Omni-API OSINT 集成

---

## 二、安全工具表设计

```sql
-- 安全扫描记录
CREATE TABLE security_scans (
    id INTEGER PRIMARY KEY,
    target TEXT NOT NULL,
    scan_type TEXT,  -- recon, vuln_scan, exploit, osint
    status TEXT,  -- running, completed, failed
    findings TEXT,
    severity TEXT,  -- critical, high, medium, low, info
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 漏洞发现记录
CREATE TABLE vulnerability_findings (
    id INTEGER PRIMARY KEY,
    scan_id INTEGER,
    vulnerability_type TEXT,
    target TEXT,
    endpoint TEXT,
    payload TEXT,
    evidence TEXT,
    severity TEXT,
    remediation TEXT,
    verified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- OSINT 情报收集
CREATE TABLE osint_intel (
    id INTEGER PRIMARY KEY,
    target TEXT,
    intel_type TEXT,  -- domain, ip, email, phone, social
    source TEXT,
    data TEXT,
    confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 攻击链记录
CREATE TABLE attack_chains (
    id INTEGER PRIMARY KEY,
    chain_name TEXT,
    target TEXT,
    steps TEXT,
    current_step INTEGER,
    status TEXT,
    success BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 三、可用命令

整合后的安全命令：

```
# 侦察
agent-reach github <repo>     # GitHub 侦察
agent-reach web <url>         # 网页分析

# 未来扩展（需安装 HexMind/CyberMind）
hex <goal>                    # Meta-Agent 攻击编排
bounty <target>               # 24/7 漏洞赏金
vision <url>                  # 视觉沙盒攻击
research <topic>              # 深度安全研究
```

---

## 四、安全警示

⚠️ **重要提醒**:
1. 仅用于授权目标
2. 遵守当地法律法规
3. 获取书面授权后再测试
4. 不对未授权使用负责

---

整合时间: 2026-04-08
