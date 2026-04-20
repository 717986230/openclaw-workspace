# -*- coding: utf-8 -*-
"""
OpenMythos 集成模块 - OpenMythos Integration for Erbing
将OpenMythos循环深度变换器集成到Erbing的推理引擎中
"""

import os
import sys
import torch
import logging
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# 添加OpenMythos适配器路径
sys.path.insert(0, os.path.dirname(__file__))

from openmythos_adapter import (
    OpenMythosAdapter,
    OpenMythosConfig,
    OpenMythosPool,
    get_openmythos_pool,
    OPENMYTHOS_AVAILABLE,
)

logger = logging.getLogger(__name__)


class TaskDifficulty(Enum):
    """任务难度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class TaskType(Enum):
    """任务类型"""
    REASONING = "reasoning"  # 推理任务
    KNOWLEDGE = "knowledge"  # 知识任务
    CODE = "code"  # 代码任务
    MATH = "math"  # 数学任务
    GENERAL = "general"  # 通用任务


@dataclass
class TaskAnalysis:
    """任务分析结果"""
    task_type: TaskType
    difficulty: TaskDifficulty
    requires_deep_reasoning: bool
    requires_cross_domain: bool
    estimated_loops: int
    confidence: float


class OpenMythosIntegrator:
    """OpenMythos集成器"""

    def __init__(self, default_model: str = "3b"):
        """
        初始化OpenMythos集成器

        Args:
            default_model: 默认模型大小
        """
        self.pool = get_openmythos_pool()
        self.default_model = default_model

        # 添加默认模型
        if OPENMYTHOS_AVAILABLE:
            config = OpenMythosConfig(
                model_size=default_model,
                device="cuda" if torch.cuda.is_available() else "cpu",
                max_loop_iters=16,
                adaptive_loops=True,
            )
            self.pool.add_model("default", config)
            self.pool.set_default_model("default")

        logger.info(f"OpenMythos Integrator initialized with default model: {default_model}")

    def analyze_task(self, prompt: str) -> TaskAnalysis:
        """
        分析任务

        Args:
            prompt: 任务提示

        Returns:
            任务分析结果
        """
        # 简单的任务分析（实际应用中可以使用更复杂的分析）
        prompt_lower = prompt.lower()

        # 任务类型分析
        if any(keyword in prompt_lower for keyword in ["reason", "think", "solve", "prove"]):
            task_type = TaskType.REASONING
        elif any(keyword in prompt_lower for keyword in ["code", "program", "function", "class"]):
            task_type = TaskType.CODE
        elif any(keyword in prompt_lower for keyword in ["math", "calculate", "equation", "solve"]):
            task_type = TaskType.MATH
        elif any(keyword in prompt_lower for keyword in ["what", "who", "when", "where", "why", "how"]):
            task_type = TaskType.KNOWLEDGE
        else:
            task_type = TaskType.GENERAL

        # 难度分析
        if any(keyword in prompt_lower for keyword in ["complex", "difficult", "challenging"]):
            difficulty = TaskDifficulty.HARD
        elif any(keyword in prompt_lower for keyword in ["simple", "easy", "basic"]):
            difficulty = TaskDifficulty.EASY
        else:
            difficulty = TaskDifficulty.MEDIUM

        # 是否需要深度推理
        requires_deep_reasoning = task_type in [TaskType.REASONING, TaskType.CODE, TaskType.MATH]

        # 是否需要跨领域能力
        requires_cross_domain = task_type in [TaskType.REASONING, TaskType.CODE]

        # 估计循环次数
        difficulty_to_loops = {
            TaskDifficulty.EASY: 4,
            TaskDifficulty.MEDIUM: 16,
            TaskDifficulty.HARD: 32,
            TaskDifficulty.VERY_HARD: 48,
        }
        estimated_loops = difficulty_to_loops.get(difficulty, 16)

        # 置信度
        confidence = 0.8

        return TaskAnalysis(
            task_type=task_type,
            difficulty=difficulty,
            requires_deep_reasoning=requires_deep_reasoning,
            requires_cross_domain=requires_cross_domain,
            estimated_loops=estimated_loops,
            confidence=confidence,
        )

    def select_model(self, task_analysis: TaskAnalysis) -> str:
        """
        选择模型

        Args:
            task_analysis: 任务分析结果

        Returns:
            模型名称
        """
        # 根据任务类型和难度选择模型
        if task_analysis.difficulty == TaskDifficulty.EASY:
            return "1b"
        elif task_analysis.difficulty == TaskDifficulty.MEDIUM:
            return "3b"
        elif task_analysis.difficulty == TaskDifficulty.HARD:
            return "10b"
        else:
            return "50b"

    def ensure_model_loaded(self, model_name: str) -> OpenMythosAdapter:
        """
        确保模型已加载

        Args:
            model_name: 模型名称

        Returns:
            OpenMythos适配器
        """
        if model_name not in self.pool.list_models():
            config = OpenMythosConfig(
                model_size=model_name,
                device="cuda" if torch.cuda.is_available() else "cpu",
                max_loop_iters=32,
                adaptive_loops=True,
            )
            self.pool.add_model(model_name, config)

        return self.pool.get_model(model_name)

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 64,
        model_name: Optional[str] = None,
        n_loops: Optional[int] = None,
        temperature: float = 1.0,
        top_k: int = 50,
    ) -> str:
        """
        生成文本

        Args:
            prompt: 输入提示
            max_new_tokens: 最大生成token数
            model_name: 模型名称（如果为None，自动选择）
            n_loops: 循环次数（如果为None，自动确定）
            temperature: 温度
            top_k: Top-K采样

        Returns:
            生成的文本
        """
        if not OPENMYTHOS_AVAILABLE:
            raise RuntimeError("OpenMythos not available")

        # 分析任务
        task_analysis = self.analyze_task(prompt)

        # 选择模型
        if model_name is None:
            model_name = self.select_model(task_analysis)

        # 确定循环次数
        if n_loops is None:
            n_loops = task_analysis.estimated_loops

        # 确保模型已加载
        adapter = self.ensure_model_loaded(model_name)

        # 将prompt转换为token IDs（这里需要实际的tokenizer）
        # 简化版本：使用随机token IDs
        input_ids = torch.randint(0, 32000, (1, len(prompt.split()))).to(adapter.device)

        # 生成
        output_ids = adapter.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            n_loops=n_loops,
            temperature=temperature,
            top_k=top_k,
        )

        # 将token IDs转换回文本（这里需要实际的tokenizer）
        # 简化版本：返回占位符
        return f"[Generated text with {output_ids.shape[1]} tokens]"

    def adaptive_generate(
        self,
        prompt: str,
        max_new_tokens: int = 64,
        model_name: Optional[str] = None,
    ) -> str:
        """
        自适应生成（根据任务分析自动调整参数）

        Args:
            prompt: 输入提示
            max_new_tokens: 最大生成token数
            model_name: 模型名称（如果为None，自动选择）

        Returns:
            生成的文本
        """
        if not OPENMYTHOS_AVAILABLE:
            raise RuntimeError("OpenMythos not available")

        # 分析任务
        task_analysis = self.analyze_task(prompt)

        # 选择模型
        if model_name is None:
            model_name = self.select_model(task_analysis)

        # 确保模型已加载
        adapter = self.ensure_model_loaded(model_name)

        # 将prompt转换为token IDs
        input_ids = torch.randint(0, 32000, (1, len(prompt.split()))).to(adapter.device)

        # 根据难度自适应生成
        difficulty_to_task = {
            TaskDifficulty.EASY: "easy",
            TaskDifficulty.MEDIUM: "medium",
            TaskDifficulty.HARD: "hard",
            TaskDifficulty.VERY_HARD: "hard",
        }
        task_difficulty = difficulty_to_task.get(task_analysis.difficulty, "medium")

        output_ids = adapter.adaptive_generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            task_difficulty=task_difficulty,
        )

        return f"[Adaptive generated text with {output_ids.shape[1]} tokens]"

    def get_status(self) -> Dict[str, Any]:
        """
        获取状态

        Returns:
            状态字典
        """
        status = {
            "available": OPENMYTHOS_AVAILABLE,
            "default_model": self.default_model,
            "loaded_models": self.pool.list_models(),
        }

        if OPENMYTHOS_AVAILABLE:
            for model_name in self.pool.list_models():
                adapter = self.pool.get_model(model_name)
                info = adapter.get_model_info()
                spectral_radius = adapter.get_spectral_radius()
                status[model_name] = {
                    "info": info,
                    "spectral_radius": spectral_radius,
                    "stable": spectral_radius < 1.0,
                }

        return status


# 全局OpenMythos集成器
_openmythos_integrator = None


def get_openmythos_integrator(default_model: str = "3b") -> OpenMythosIntegrator:
    """
    获取全局OpenMythos集成器

    Args:
        default_model: 默认模型大小

    Returns:
        OpenMythos集成器
    """
    global _openmythos_integrator
    if _openmythos_integrator is None:
        _openmythos_integrator = OpenMythosIntegrator(default_model)
    return _openmythos_integrator


if __name__ == "__main__":
    # 测试OpenMythos集成器
    print("Testing OpenMythos Integrator...")

    if not OPENMYTHOS_AVAILABLE:
        print("OpenMythos not available. Install with: pip install open-mythos")
        sys.exit(1)

    # 创建集成器
    integrator = get_openmythos_integrator()

    # 获取状态
    status = integrator.get_status()
    print("\nStatus:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    # 测试任务分析
    print("\nTesting task analysis...")
    prompts = [
        "Solve this complex math problem",
        "Write a simple function",
        "What is the capital of France?",
    ]

    for prompt in prompts:
        analysis = integrator.analyze_task(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"  Type: {analysis.task_type.value}")
        print(f"  Difficulty: {analysis.difficulty.value}")
        print(f"  Requires Deep Reasoning: {analysis.requires_deep_reasoning}")
        print(f"  Estimated Loops: {analysis.estimated_loops}")

    # 测试生成
    print("\nTesting generation...")
    try:
        output = integrator.generate("Test prompt", max_new_tokens=4)
        print(f"Output: {output}")
    except Exception as e:
        print(f"Error: {e}")

    # 测试自适应生成
    print("\nTesting adaptive generation...")
    try:
        output = integrator.adaptive_generate("Test prompt", max_new_tokens=4)
        print(f"Output: {output}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nOpenMythos Integrator tested successfully!")
