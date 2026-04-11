"""
Erbing Continuous Learning System - 基于ECC架构
================================================

自动从会话中提取可复用模式，保存为Skills。
基于Everything Claude Code的continuous-learning设计。
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import re


# ============= Pattern Types =============

class PatternType:
    """模式类型 - 基于ECC分类"""
    ERROR_RESOLUTION = "error_resolution"      # 错误解决方案
    USER_CORRECTIONS = "user_corrections"      # 用户纠正模式
    WORKAROUNDS = "workarounds"                # 变通方案
    DEBUGGING_TECHNIQUES = "debugging_techniques"  # 调试技术
    PROJECT_SPECIFIC = "project_specific"      # 项目特定约定
    CODE_PATTERNS = "code_patterns"            # 代码模式
    ARCHITECTURE_DECISIONS = "architecture_decisions"  # 架构决策


@dataclass
class Pattern:
    """提取的模式"""
    pattern_type: str
    title: str
    description: str
    context: str  # 原始上下文
    solution: str  # 解决方案
    confidence: float
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "pattern_type": self.pattern_type,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "solution": self.solution,
            "confidence": self.confidence,
            "tags": self.tags,
            "created_at": self.created_at.isoformat()
        }


# ============= Session Evaluator =============

class SessionEvaluator:
    """会话评估器"""
    
    def __init__(self, min_session_length: int = 10):
        self.min_session_length = min_session_length
    
    def should_evaluate(self, session_messages: List[Dict]) -> bool:
        """是否应该评估会话"""
        return len(session_messages) >= self.min_session_length
    
    def count_messages(self, session: Dict) -> int:
        """计算消息数量"""
        if "messages" in session:
            return len(session["messages"])
        return 0


# ============= Pattern Detector =============

class PatternDetector:
    """模式检测器"""
    
    def __init__(self):
        self.patterns_detected: List[Pattern] = []
        
        # 错误模式关键词
        self.error_keywords = [
            "error", "exception", "failed", "traceback",
            "bug", "issue", "fix", "solve"
        ]
        
        # 纠正模式关键词
        self.correction_keywords = [
            "actually", "sorry", "correction", "instead",
            "wrong", "right", "should be", "meant to"
        ]
        
        # 变通模式关键词
        self.workaround_keywords = [
            "workaround", "alternative", "hack", "temporary",
            "bypass", "绕过", "变通"
        ]
    
    def detect_error_resolution(self, messages: List[Dict]) -> List[Pattern]:
        """检测错误解决方案模式"""
        patterns = []
        
        for i, msg in enumerate(messages):
            content = msg.get("content", "").lower()
            
            # 检测错误
            if any(keyword in content for keyword in self.error_keywords):
                # 查找后续的解决方案
                if i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    solution = next_msg.get("content", "")
                    
                    if len(solution) > 50:  # 有意义的解决方案
                        pattern = Pattern(
                            pattern_type=PatternType.ERROR_RESOLUTION,
                            title=f"Error Resolution: {msg.get('content', '')[:50]}",
                            description="Automatically detected error resolution pattern",
                            context=msg.get("content", ""),
                            solution=solution,
                            confidence=0.75,
                            tags=["error", "auto-detected"]
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def detect_user_corrections(self, messages: List[Dict]) -> List[Pattern]:
        """检测用户纠正模式"""
        patterns = []
        
        for i, msg in enumerate(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                
                if any(keyword in content for keyword in self.correction_keywords):
                    # 查找之前的AI回复
                    if i > 0:
                        prev_msg = messages[i - 1]
                        wrong_approach = prev_msg.get("content", "")
                        correction = msg.get("content", "")
                        
                        pattern = Pattern(
                            pattern_type=PatternType.USER_CORRECTIONS,
                            title=f"User Correction: {correction[:50]}",
                            description="User corrected AI's approach",
                            context=wrong_approach,
                            solution=correction,
                            confidence=0.85,  # 用户纠正置信度高
                            tags=["correction", "user-feedback"]
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def detect_workarounds(self, messages: List[Dict]) -> List[Pattern]:
        """检测变通方案"""
        patterns = []
        
        for i, msg in enumerate(messages):
            content = msg.get("content", "").lower()
            
            if any(keyword in content for keyword in self.workaround_keywords):
                pattern = Pattern(
                    pattern_type=PatternType.WORKAROUNDS,
                    title=f"Workaround: {msg.get('content', '')[:50]}",
                    description="Workaround or alternative approach detected",
                    context=msg.get("content", ""),
                    solution="",
                    confidence=0.70,
                    tags=["workaround", "alternative"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def detect_code_patterns(self, messages: List[Dict]) -> List[Pattern]:
        """检测代码模式"""
        patterns = []
        
        # 检测代码块
        code_pattern = re.compile(r'```[\s\S]*?```')
        
        for msg in messages:
            content = msg.get("content", "")
            matches = code_pattern.findall(content)
            
            if matches:
                for match in matches:
                    # 提取代码
                    code = match.strip('`').strip()
                    if len(code) > 100:  # 有意义的代码
                        pattern = Pattern(
                            pattern_type=PatternType.CODE_PATTERNS,
                            title=f"Code Pattern: {code[:50]}",
                            description="Reusable code pattern detected",
                            context="",
                            solution=code,
                            confidence=0.65,
                            tags=["code", "pattern", "reusable"]
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def detect_all_patterns(self, messages: List[Dict]) -> List[Pattern]:
        """检测所有模式"""
        all_patterns = []
        
        all_patterns.extend(self.detect_error_resolution(messages))
        all_patterns.extend(self.detect_user_corrections(messages))
        all_patterns.extend(self.detect_workarounds(messages))
        all_patterns.extend(self.detect_code_patterns(messages))
        
        return all_patterns


# ============= Skill Extractor =============

class SkillExtractor:
    """Skill提取器"""
    
    def __init__(self, skills_path: str = None):
        if skills_path is None:
            skills_path = r"C:\Users\Administrator\.openclaw\workspace\skills\learned"
        self.skills_path = Path(skills_path)
        self.skills_path.mkdir(parents=True, exist_ok=True)
    
    def pattern_to_skill(self, pattern: Pattern) -> str:
        """将Pattern转换为Skill文件"""
        skill_name = self._generate_skill_name(pattern)
        skill_file = self.skills_path / f"{skill_name}.md"
        
        # 生成Skill内容
        skill_content = f"""---
name: {skill_name}
description: {pattern.description}
origin: learned
pattern_type: {pattern.pattern_type}
confidence: {pattern.confidence}
tags: {json.dumps(pattern.tags)}
created: {pattern.created_at.isoformat()}
---

# {pattern.title}

## Context

{pattern.context}

## Solution

{pattern.solution if pattern.solution else "See context above"}

## Pattern Type

{pattern.pattern_type}

## Confidence

{pattern.confidence:.0%}

## Tags

{', '.join(pattern.tags)}
"""
        
        # 保存文件
        skill_file.write_text(skill_content, encoding='utf-8')
        
        return str(skill_file)
    
    def _generate_skill_name(self, pattern: Pattern) -> str:
        """生成Skill名称"""
        # 使用类型+时间戳
        timestamp = pattern.created_at.strftime("%Y%m%d_%H%M%S")
        pattern_type_short = pattern.pattern_type.split("_")[0]
        return f"{pattern_type_short}_{timestamp}"
    
    def extract_skills(self, patterns: List[Pattern]) -> List[str]:
        """批量提取Skills"""
        skill_files = []
        
        for pattern in patterns:
            if pattern.confidence >= 0.70:  # 只保存高置信度模式
                skill_file = self.pattern_to_skill(pattern)
                skill_files.append(skill_file)
        
        return skill_files


# ============= Continuous Learning System =============

class ContinuousLearningSystem:
    """持续学习系统 - 主控制器"""
    
    def __init__(
        self,
        db_path: str = None,
        min_session_length: int = 10,
        extraction_threshold: str = "medium",
        auto_approve: bool = False
    ):
        if db_path is None:
            db_path = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"
        
        self.db_path = db_path
        self.min_session_length = min_session_length
        self.extraction_threshold = extraction_threshold
        self.auto_approve = auto_approve
        
        # 组件
        self.evaluator = SessionEvaluator(min_session_length)
        self.detector = PatternDetector()
        self.extractor = SkillExtractor()
        
        # 阈值映射
        self.threshold_map = {
            "low": 0.60,
            "medium": 0.70,
            "high": 0.80
        }
    
    def process_session(self, session: Dict) -> List[Pattern]:
        """处理会话"""
        messages = session.get("messages", [])
        
        # 1. 评估会话
        if not self.evaluator.should_evaluate(messages):
            print(f"Session too short ({len(messages)} messages), skipping")
            return []
        
        print(f"Evaluating session with {len(messages)} messages...")
        
        # 2. 检测模式
        patterns = self.detector.detect_all_patterns(messages)
        print(f"Detected {len(patterns)} patterns")
        
        # 3. 过滤低置信度
        threshold = self.threshold_map.get(self.extraction_threshold, 0.70)
        patterns = [p for p in patterns if p.confidence >= threshold]
        print(f"After filtering: {len(patterns)} patterns")
        
        # 4. 提取Skills
        if self.auto_approve:
            skill_files = self.extractor.extract_skills(patterns)
            print(f"Extracted {len(skill_files)} skills")
        
        # 5. 保存到数据库
        self._save_patterns_to_db(patterns)
        
        return patterns
    
    def _save_patterns_to_db(self, patterns: List[Pattern]):
        """保存模式到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern in patterns:
            cursor.execute('''
                INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'learned_pattern',
                pattern.title,
                json.dumps(pattern.to_dict()),
                pattern.pattern_type,
                json.dumps(pattern.tags + ["learned", pattern.pattern_type]),
                int(pattern.confidence * 10),
                pattern.created_at.isoformat(),
                pattern.created_at.isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Saved {len(patterns)} patterns to database")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询所有learned_pattern类型的记忆
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(importance) as avg_importance
            FROM memories
            WHERE type = 'learned_pattern'
            GROUP BY category
        ''')
        
        stats = {
            "total_patterns": 0,
            "by_type": {}
        }
        
        for row in cursor.fetchall():
            category, count, avg_importance = row
            stats["by_type"][category] = {
                "count": count,
                "avg_importance": avg_importance
            }
            stats["total_patterns"] += count
        
        conn.close()
        
        return stats


# ============= Hook Integration =============

class StopHook:
    """Stop Hook - 会话结束时触发"""
    
    def __init__(self):
        self.learning_system = ContinuousLearningSystem(
            min_session_length=10,
            extraction_threshold="medium",
            auto_approve=False
        )
    
    def on_stop(self, session: Dict):
        """会话结束时调用"""
        print("\n" + "=" * 60)
        print("Stop Hook: Evaluating session...")
        print("=" * 60)
        
        patterns = self.learning_system.process_session(session)
        
        if patterns:
            print(f"\nExtracted {len(patterns)} patterns:")
            for i, pattern in enumerate(patterns, 1):
                print(f"  {i}. [{pattern.pattern_type}] {pattern.title[:50]}...")
        else:
            print("\nNo patterns extracted")
        
        print("=" * 60)


# ============= Testing =============

if __name__ == "__main__":
    print("=" * 60)
    print("Erbing Continuous Learning System")
    print("Based on Everything Claude Code Architecture")
    print("=" * 60)
    
    # 创建测试会话
    test_session = {
        "messages": [
            {"role": "user", "content": "Help me fix this SQL error"},
            {"role": "assistant", "content": "I see the error. The issue is... Let me provide a fix."},
            {"role": "user", "content": "Actually, the problem was different. You should use parameterized queries instead."},
            {"role": "assistant", "content": "You're right. Here's the corrected approach using parameterized queries..."},
            {"role": "user", "content": "How do I work around this framework limitation?"},
            {"role": "assistant", "content": "Here's a workaround for that framework limitation..."},
            {"role": "user", "content": "Debug this code please"},
            {"role": "assistant", "content": "Let me debug. I found the issue in line 42..."},
            {"role": "user", "content": "Thanks! That fixed it"},
            {"role": "assistant", "content": "Great! The debugging technique used was..."},
            {"role": "user", "content": "One more question about error handling"},
            {"role": "assistant", "content": "Here's a robust error handling pattern..."},
        ]
    }
    
    # 测试Stop Hook
    hook = StopHook()
    hook.on_stop(test_session)
    
    # 测试统计
    learning_system = ContinuousLearningSystem()
    stats = learning_system.get_stats()
    
    print("\n" + "=" * 60)
    print("Learning System Statistics")
    print("=" * 60)
    print(f"Total Patterns: {stats['total_patterns']}")
    for pattern_type, data in stats["by_type"].items():
        print(f"  {pattern_type}: {data['count']} patterns (avg importance: {data['avg_importance']:.1f})")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
