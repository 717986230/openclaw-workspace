"""
Skill 工厂（整合 Hermes Skill Factory）
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Skill:
    """技能"""
    id: str
    name: str
    description: str
    code: str
    metadata: Dict[str, Any]
    created_at: datetime
    version: str


@dataclass
class MetaSkill:
    """元技能"""
    id: str
    name: str
    description: str
    skill_generator: str
    parameters: Dict[str, Any]
    created_at: datetime


class SkillFactory:
    """技能工厂"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.meta_skills: Dict[str, MetaSkill] = {}

    def create_skill(
        self,
        name: str,
        description: str,
        code: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Skill:
        """创建技能"""
        skill = Skill(
            id=self._generate_skill_id(),
            name=name,
            description=description,
            code=code,
            metadata=metadata or {},
            created_at=datetime.now(),
            version="1.0.0",
        )

        self.skills[skill.id] = skill
        return skill

    def create_meta_skill(
        self,
        name: str,
        description: str,
        skill_generator: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> MetaSkill:
        """创建元技能"""
        meta_skill = MetaSkill(
            id=self._generate_meta_skill_id(),
            name=name,
            description=description,
            skill_generator=skill_generator,
            parameters=parameters or {},
            created_at=datetime.now(),
        )

        self.meta_skills[meta_skill.id] = meta_skill
        return meta_skill

    def generate_skill_from_meta(
        self,
        meta_skill_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Skill]:
        """从元技能生成技能"""
        if meta_skill_id not in self.meta_skills:
            return None

        meta_skill = self.meta_skills[meta_skill_id]

        skill = self.create_skill(
            name=f"Generated from {meta_skill.name}",
            description=f"Auto-generated skill from meta-skill",
            code=meta_skill.skill_generator,
            metadata={
                "meta_skill_id": meta_skill_id,
                "context": context,
            },
        )

        return skill

    def auto_generate_skills(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Skill]:
        """自动生成技能"""
        task_analysis = self._analyze_task(task)

        skills = []
        for analysis in task_analysis:
            skill = self.create_skill(
                name=analysis["name"],
                description=analysis["description"],
                code=analysis["code"],
                metadata={
                    "auto_generated": True,
                    "task": task,
                    "context": context,
                },
            )
            skills.append(skill)

        return skills

    def _analyze_task(self, task: str) -> List[Dict[str, Any]]:
        """分析任务"""
        return [
            {
                "name": f"Skill for {task}",
                "description": f"Auto-generated skill for task: {task}",
                "code": f"# Auto-generated code for: {task}\ndef execute():\n    pass",
            }
        ]

    def _generate_skill_id(self) -> str:
        """生成技能 ID"""
        return f"skill_{uuid.uuid4()}"

    def _generate_meta_skill_id(self) -> str:
        """生成元技能 ID"""
        return f"meta_skill_{uuid.uuid4()}"

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_id)

    def get_all_skills(self) -> List[Skill]:
        """获取所有技能"""
        return list(self.skills.values())

    def get_meta_skill(self, meta_skill_id: str) -> Optional[MetaSkill]:
        """获取元技能"""
        return self.meta_skills.get(meta_skill_id)

    def get_all_meta_skills(self) -> List[MetaSkill]:
        """获取所有元技能"""
        return list(self.meta_skills.values())

    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "total_skills": len(self.skills),
            "total_meta_skills": len(self.meta_skills),
            "auto_generated_count": len([
                s for s in self.skills.values()
                if s.metadata.get("auto_generated")
            ]),
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "code": s.code,
                    "metadata": s.metadata,
                    "created_at": s.created_at.isoformat(),
                    "version": s.version,
                }
                for s in self.skills.values()
            ],
            "meta_skills": [
                {
                    "id": ms.id,
                    "name": ms.name,
                    "description": ms.description,
                    "skill_generator": ms.skill_generator,
                    "parameters": ms.parameters,
                    "created_at": ms.created_at.isoformat(),
                }
                for ms in self.meta_skills.values()
            ],
            "summary": self.get_summary(),
        }
