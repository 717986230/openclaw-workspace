"""
Erbing Agent System - 基于Everything Claude Code架构
===========================================

集成140K stars的ECC项目精华，实现专业Agent系统。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# ============= Confidence-Based Filtering =============

class ConfidenceLevel(Enum):
    """置信度级别"""
    CRITICAL = 0.95  # 必须报告
    HIGH = 0.85      # 高置信度
    MEDIUM = 0.80    # 中等置信度
    LOW = 0.70       # 低置信度（可选）


class Finding:
    """发现的问题"""
    def __init__(self, category: str, message: str, confidence: float, location: str = ""):
        self.category = category
        self.message = message
        self.confidence = confidence
        self.location = location
        self.timestamp = datetime.now()
    
    def should_report(self, threshold: float = 0.80) -> bool:
        """是否应该报告（基于置信度过滤）"""
        return self.confidence >= threshold
    
    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "message": self.message,
            "confidence": self.confidence,
            "location": self.location,
            "timestamp": self.timestamp.isoformat()
        }


# ============= Agent Base Class =============

@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    description: str
    tools: List[str] = field(default_factory=list)
    model: str = "sonnet"  # sonnet, opus, haiku
    confidence_threshold: float = 0.80
    priority_levels: Dict[str, float] = field(default_factory=lambda: {
        "CRITICAL": 0.95,
        "HIGH": 0.85,
        "MEDIUM": 0.80,
        "LOW": 0.70
    })


class ErbingAgent:
    """Erbing Agent基类 - 基于ECC架构"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.findings: List[Finding] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_finding(self, category: str, message: str, confidence: float, location: str = ""):
        """添加发现的问题"""
        finding = Finding(category, message, confidence, location)
        if finding.should_report(self.config.confidence_threshold):
            self.findings.append(finding)
    
    def consolidate_similar(self) -> List[Finding]:
        """合并相似发现（避免噪音）"""
        grouped = {}
        for finding in self.findings:
            key = (finding.category, finding.message[:50])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(finding)
        
        consolidated = []
        for key, group in grouped.items():
            if len(group) > 1:
                consolidated.append(Finding(
                    category=group[0].category,
                    message=f"{group[0].message} (x{len(group)}次)",
                    confidence=max(f.confidence for f in group),
                    location=group[0].location
                ))
            else:
                consolidated.append(group[0])
        
        return consolidated
    
    def prioritize(self) -> List[Finding]:
        """按优先级排序"""
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(
            self.findings,
            key=lambda f: priority_order.get(f.category, 99)
        )
    
    def generate_report(self) -> str:
        """生成报告"""
        consolidated = self.consolidate_similar()
        prioritized = sorted(
            consolidated,
            key=lambda f: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(f.category, 99)
        )
        
        report = f"# {self.config.name} Report\n\n"
        report += f"**Session**: {self.session_id}\n"
        report += f"**Confidence Threshold**: {self.config.confidence_threshold}\n"
        report += f"**Total Findings**: {len(prioritized)}\n\n"
        
        current_category = None
        for finding in prioritized:
            if finding.category != current_category:
                current_category = finding.category
                report += f"\n## {current_category}\n\n"
            
            confidence_emoji = "!" if finding.confidence >= 0.95 else "?" if finding.confidence >= 0.85 else "-"
            report += f"{confidence_emoji} **[{finding.confidence:.0%}]** {finding.message}\n"
            if finding.location:
                report += f"   - Location: `{finding.location}`\n"
        
        return report
    
    def save_to_database(self, db_path: str = None):
        """保存到数据库"""
        if db_path is None:
            db_path = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for finding in self.findings:
            cursor.execute('''
                INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'agent_finding',
                f"[{self.config.name}] {finding.category}",
                finding.message,
                finding.category.lower(),
                json.dumps(["agent", self.config.name, finding.category]),
                int(finding.confidence * 10),
                finding.timestamp.isoformat(),
                finding.timestamp.isoformat()
            ))
        
        conn.commit()
        conn.close()


# ============= Code Reviewer Agent =============

class CodeReviewerAgent(ErbingAgent):
    """代码审查Agent - 基于ECC code-reviewer"""
    
    def __init__(self):
        config = AgentConfig(
            name="Code Reviewer",
            description="Expert code review specialist",
            tools=["Read", "Grep", "Glob", "Bash"],
            model="sonnet",
            confidence_threshold=0.80
        )
        super().__init__(config)
        
        self.checklist = {
            "CRITICAL": [
                "hardcoded_credentials",
                "sql_injection",
                "xss_vulnerabilities",
                "path_traversal",
                "csrf_vulnerabilities",
                "authentication_bypasses",
                "insecure_dependencies",
                "exposed_secrets_in_logs"
            ],
            "HIGH": [
                "large_functions",
                "large_files",
                "deep_nesting",
                "missing_error_handling",
                "mutation_patterns",
                "console_log_statements",
                "missing_tests",
                "dead_code"
            ],
            "MEDIUM": [
                "naming_conventions",
                "code_duplication",
                "magic_numbers",
                "todo_comments"
            ],
            "LOW": [
                "formatting",
                "whitespace",
                "comment_style"
            ]
        }
    
    def check_security(self, code: str, file_path: str = ""):
        """安全检查（CRITICAL）"""
        if any(keyword in code.lower() for keyword in ["password =", "api_key =", "secret =", "token ="]):
            self.add_finding("CRITICAL", "Potential hardcoded credential detected", 0.90, file_path)
        
        if 'f"' in code and "SELECT" in code.upper():
            self.add_finding("CRITICAL", "Potential SQL injection via f-string", 0.85, file_path)
        
        if "innerHTML" in code or "dangerouslySetInnerHTML" in code:
            self.add_finding("CRITICAL", "Potential XSS vulnerability", 0.88, file_path)
    
    def check_quality(self, code: str, file_path: str = ""):
        """代码质量检查（HIGH）"""
        lines = code.split('\n')
        
        if len(lines) > 800:
            self.add_finding("HIGH", f"Large file ({len(lines)} lines). Consider extracting modules", 0.85, file_path)
        
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        
        if max_indent > 16:
            self.add_finding("HIGH", f"Deep nesting detected (level {max_indent // 4}). Use early returns", 0.82, file_path)
        
        if "console.log" in code:
            self.add_finding("HIGH", "Remove console.log statements before merge", 0.90, file_path)
    
    def review_file(self, file_path: str):
        """审查文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            self.check_security(code, file_path)
            self.check_quality(code, file_path)
        except Exception as e:
            self.add_finding("LOW", f"Could not review file: {str(e)}", 0.60, file_path)


# ============= Security Reviewer Agent =============

class SecurityReviewerAgent(ErbingAgent):
    """安全审查Agent"""
    
    def __init__(self):
        config = AgentConfig(
            name="Security Reviewer",
            description="Security vulnerability scanner",
            tools=["Read", "Grep", "Bash"],
            model="sonnet",
            confidence_threshold=0.85
        )
        super().__init__(config)
    
    def scan_for_vulnerabilities(self, code: str, file_path: str):
        """扫描漏洞"""
        owasp_checks = {
            "A01:2021 - Broken Access Control": self._check_access_control,
            "A02:2021 - Cryptographic Failures": self._check_crypto,
            "A03:2021 - Injection": self._check_injection,
            "A04:2021 - Insecure Design": self._check_design,
            "A05:2021 - Security Misconfiguration": self._check_config,
            "A06:2021 - Vulnerable Components": self._check_dependencies,
            "A07:2021 - Auth Failures": self._check_auth,
            "A08:2021 - Software Integrity": self._check_integrity,
            "A09:2021 - Logging Failures": self._check_logging,
            "A10:2021 - SSRF": self._check_ssrf
        }
        
        for owasp_category, check_func in owasp_checks.items():
            check_func(code, file_path, owasp_category)
    
    def _check_access_control(self, code: str, file_path: str, category: str):
        if "public" in code and any(auth in code for auth in ["delete", "update", "admin"]):
            self.add_finding("CRITICAL", f"{category}: Potential broken access control", 0.85, file_path)
    
    def _check_crypto(self, code: str, file_path: str, category: str):
        if any(weak in code for weak in ["md5", "sha1", "DES", "ECB"]):
            self.add_finding("CRITICAL", f"{category}: Weak cryptographic algorithm", 0.92, file_path)
    
    def _check_injection(self, code: str, file_path: str, category: str):
        if any(pattern in code for pattern in ["eval(", "exec(", "system(", "subprocess.call("]):
            self.add_finding("CRITICAL", f"{category}: Potential code injection", 0.90, file_path)
    
    def _check_design(self, code: str, file_path: str, category: str):
        pass
    
    def _check_config(self, code: str, file_path: str, category: str):
        if any(config in code for config in ["DEBUG = True", "debug=True", "development"]):
            self.add_finding("HIGH", f"{category}: Debug mode potentially enabled in production", 0.82, file_path)
    
    def _check_dependencies(self, code: str, file_path: str, category: str):
        pass
    
    def _check_auth(self, code: str, file_path: str, category: str):
        if "password" in code.lower() and "hash" not in code.lower():
            self.add_finding("CRITICAL", f"{category}: Password potentially stored without hashing", 0.88, file_path)
    
    def _check_integrity(self, code: str, file_path: str, category: str):
        pass
    
    def _check_logging(self, code: str, file_path: str, category: str):
        if any(sensitive in code for sensitive in ["password", "token", "secret", "api_key"]):
            if "log" in code.lower() or "print" in code:
                self.add_finding("CRITICAL", f"{category}: Sensitive data potentially logged", 0.87, file_path)
    
    def _check_ssrf(self, code: str, file_path: str, category: str):
        if "requests.get" in code or "urllib.request" in code:
            if "user" in code.lower() or "input" in code.lower():
                self.add_finding("HIGH", f"{category}: Potential SSRF vulnerability", 0.83, file_path)


# ============= Architect Agent =============

class ArchitectAgent(ErbingAgent):
    """架构设计Agent"""
    
    def __init__(self):
        config = AgentConfig(
            name="Architect",
            description="System architecture designer",
            tools=["Read", "Glob", "Bash"],
            model="opus",
            confidence_threshold=0.75
        )
        super().__init__(config)
    
    def analyze_structure(self, project_path: str):
        """分析项目结构"""
        project = Path(project_path)
        if not project.exists():
            self.add_finding("HIGH", f"Project path does not exist: {project_path}", 0.95, project_path)
            return
        
        dirs = [d for d in project.iterdir() if d.is_dir()]
        files = [f for f in project.iterdir() if f.is_file()]
        
        if not any(d.name in ["tests", "test", "__tests__"] for d in dirs):
            self.add_finding("HIGH", "Missing tests directory", 0.85, project_path)
        
        if not any(d.name in ["docs", "documentation"] for d in dirs):
            self.add_finding("MEDIUM", "Missing docs directory", 0.80, project_path)
        
        if not any(f.name.lower() == "readme.md" for f in files):
            self.add_finding("MEDIUM", "Missing README.md", 0.82, project_path)


# ============= Performance Optimizer Agent =============

class PerformanceOptimizerAgent(ErbingAgent):
    """性能优化Agent"""
    
    def __init__(self):
        config = AgentConfig(
            name="Performance Optimizer",
            description="Performance analysis and optimization",
            tools=["Read", "Bash"],
            model="sonnet",
            confidence_threshold=0.80
        )
        super().__init__(config)
    
    def check_performance(self, code: str, file_path: str):
        """检查性能问题"""
        if "for " in code and ".query(" in code:
            self.add_finding("HIGH", "Potential N+1 query pattern detected", 0.85, file_path)
        
        if "for " in code and any(io in code for io in ["open(", "read(", "write("]):
            self.add_finding("MEDIUM", "Synchronous I/O in loop, consider async", 0.80, file_path)
        
        if code.count("+=") > 3 and "str" in code:
            self.add_finding("MEDIUM", "Inefficient string concatenation, use join()", 0.78, file_path)


# ============= Agent Factory =============

class AgentFactory:
    """Agent工厂"""
    
    _agents = {
        "code-reviewer": CodeReviewerAgent,
        "security-reviewer": SecurityReviewerAgent,
        "architect": ArchitectAgent,
        "performance-optimizer": PerformanceOptimizerAgent
    }
    
    @classmethod
    def create(cls, agent_type: str) -> ErbingAgent:
        """创建Agent"""
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return cls._agents[agent_type]()
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """列出所有可用Agent"""
        return list(cls._agents.keys())


# ============= Testing =============

if __name__ == "__main__":
    print("=" * 60)
    print("Erbing Agent System - Based on Everything Claude Code")
    print("=" * 60)
    
    print("\nAvailable Agents:")
    for agent_name in AgentFactory.list_agents():
        print(f"  - {agent_name}")
    
    print("\n" + "=" * 60)
    print("Testing Code Reviewer Agent")
    print("=" * 60)
    
    reviewer = AgentFactory.create("code-reviewer")
    print(f"\n[{reviewer.config.name}]")
    print(f"  Tools: {reviewer.config.tools}")
    print(f"  Model: {reviewer.config.model}")
    print(f"  Confidence Threshold: {reviewer.config.confidence_threshold}")
    
    test_code = '''
password = "hardcoded_secret123"
api_key = "sk-xxxxx"

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
'''
    
    print("\nAnalyzing test code...")
    reviewer.check_security(test_code, "test.py")
    reviewer.check_quality(test_code, "test.py")
    
    print("\n" + reviewer.generate_report())
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
