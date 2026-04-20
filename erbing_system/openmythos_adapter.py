# -*- coding: utf-8 -*-
"""
OpenMythos 适配器 - OpenMythos Adapter for Erbing
将OpenMythos循环深度变换器集成到Erbing系统中
"""

import os
import sys
import torch
import torch.nn as nn
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

# 添加OpenMythos路径
openmythos_path = os.path.join(os.path.dirname(__file__), "..", "OpenMythos")
if openmythos_path not in sys.path:
    sys.path.insert(0, openmythos_path)

try:
    from open_mythos.main import OpenMythos, MythosConfig
    from open_mythos.variants import (
        mythos_1b,
        mythos_3b,
        mythos_10b,
        mythos_50b,
        mythos_100b,
        mythos_500b,
        mythos_1t,
    )
    OPENMYTHOS_AVAILABLE = True
except ImportError:
    OPENMYTHOS_AVAILABLE = False
    logging.warning("OpenMythos not available. Install with: pip install open-mythos")

logger = logging.getLogger(__name__)


@dataclass
class OpenMythosConfig:
    """OpenMythos配置"""
    model_size: str = "3b"  # 1b, 3b, 10b, 50b, 100b, 500b, 1t
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    max_loop_iters: int = 16  # 默认循环次数
    adaptive_loops: bool = True  # 是否使用自适应循环
    min_loops: int = 4  # 最小循环次数
    max_loops: int = 32  # 最大循环次数
    temperature: float = 1.0
    top_k: int = 50
    use_cache: bool = True


class OpenMythosAdapter:
    """OpenMythos适配器"""

    def __init__(self, config: OpenMythosConfig):
        """
        初始化OpenMythos适配器

        Args:
            config: OpenMythos配置
        """
        self.config = config
        self.model = None
        self.model_cfg = None
        self.device = torch.device(config.device)

        if not OPENMYTHOS_AVAILABLE:
            raise ImportError("OpenMythos not available. Install with: pip install open-mythos")

        self._load_model()

    def _load_model(self):
        """加载OpenMythos模型"""
        logger.info(f"Loading OpenMythos {self.config.model_size} model...")

        # 获取模型配置
        model_config_map = {
            "1b": mythos_1b,
            "3b": mythos_3b,
            "10b": mythos_10b,
            "50b": mythos_50b,
            "100b": mythos_100b,
            "500b": mythos_500b,
            "1t": mythos_1t,
        }

        if self.config.model_size not in model_config_map:
            raise ValueError(f"Unknown model size: {self.config.model_size}")

        self.model_cfg = model_config_map[self.config.model_size]()
        self.model = OpenMythos(self.model_cfg).to(self.device)
        self.model.eval()

        # 计算参数数量
        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Loaded OpenMythos {self.config.model_size} model with {total_params:,} parameters")

    def forward(
        self,
        input_ids: torch.Tensor,
        n_loops: Optional[int] = None,
        kv_cache: Optional[Dict] = None,
        start_pos: int = 0,
    ) -> torch.Tensor:
        """
        前向传播

        Args:
            input_ids: 输入token IDs (B, T)
            n_loops: 循环次数（如果为None，使用配置的默认值）
            kv_cache: KV缓存
            start_pos: 起始位置

        Returns:
            输出logits (B, T, vocab_size)
        """
        if n_loops is None:
            n_loops = self.config.max_loop_iters

        with torch.no_grad():
            logits = self.model(
                input_ids=input_ids,
                n_loops=n_loops,
                kv_cache=kv_cache,
                start_pos=start_pos,
            )

        return logits

    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 64,
        n_loops: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> torch.Tensor:
        """
        生成文本

        Args:
            input_ids: 输入token IDs (B, T)
            max_new_tokens: 最大生成token数
            n_loops: 循环次数
            temperature: 温度
            top_k: Top-K采样

        Returns:
            生成的token IDs (B, T + max_new_tokens)
        """
        if n_loops is None:
            n_loops = self.config.max_loop_iters

        if temperature is None:
            temperature = self.config.temperature

        if top_k is None:
            top_k = self.config.top_k

        with torch.no_grad():
            output = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                n_loops=n_loops,
                temperature=temperature,
                top_k=top_k,
            )

        return output

    def adaptive_generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 64,
        task_difficulty: str = "medium",  # easy, medium, hard
    ) -> torch.Tensor:
        """
        自适应生成（根据任务难度调整循环次数）

        Args:
            input_ids: 输入token IDs (B, T)
            max_new_tokens: 最大生成token数
            task_difficulty: 任务难度

        Returns:
            生成的token IDs (B, T + max_new_tokens)
        """
        if not self.config.adaptive_loops:
            return self.generate(input_ids, max_new_tokens)

        # 根据任务难度调整循环次数
        difficulty_to_loops = {
            "easy": self.config.min_loops,
            "medium": self.config.max_loop_iters,
            "hard": self.config.max_loops,
        }

        n_loops = difficulty_to_loops.get(task_difficulty, self.config.max_loop_iters)

        logger.info(f"Adaptive generation: task_difficulty={task_difficulty}, n_loops={n_loops}")

        return self.generate(input_ids, max_new_tokens, n_loops=n_loops)

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        total_params = sum(p.numel() for p in self.model.parameters())

        return {
            "model_size": self.config.model_size,
            "total_params": total_params,
            "dim": self.model_cfg.dim,
            "n_heads": self.model_cfg.n_heads,
            "n_kv_heads": self.model_cfg.n_kv_heads,
            "max_seq_len": self.model_cfg.max_seq_len,
            "max_loop_iters": self.model_cfg.max_loop_iters,
            "prelude_layers": self.model_cfg.prelude_layers,
            "coda_layers": self.model_cfg.coda_layers,
            "attn_type": self.model_cfg.attn_type,
            "n_experts": self.model_cfg.n_experts,
            "n_shared_experts": self.model_cfg.n_shared_experts,
            "n_experts_per_tok": self.model_cfg.n_experts_per_tok,
            "expert_dim": self.model_cfg.expert_dim,
            "device": str(self.device),
        }

    def get_spectral_radius(self) -> float:
        """
        获取注入参数A的谱半径

        Returns:
            谱半径（必须 < 1 才能保证稳定性）
        """
        A = self.model.recurrent.injection.get_A()
        return A.max().item()


class OpenMythosPool:
    """OpenMythos模型池"""

    def __init__(self):
        """初始化OpenMythos模型池"""
        self.models: Dict[str, OpenMythosAdapter] = {}
        self.default_model: Optional[str] = None

    def add_model(self, name: str, config: OpenMythosConfig) -> OpenMythosAdapter:
        """
        添加模型到池中

        Args:
            name: 模型名称
            config: 模型配置

        Returns:
            OpenMythos适配器
        """
        logger.info(f"Adding OpenMythos model: {name}")
        adapter = OpenMythosAdapter(config)
        self.models[name] = adapter

        if self.default_model is None:
            self.default_model = name

        return adapter

    def get_model(self, name: Optional[str] = None) -> OpenMythosAdapter:
        """
        获取模型

        Args:
            name: 模型名称（如果为None，使用默认模型）

        Returns:
            OpenMythos适配器
        """
        if name is None:
            name = self.default_model

        if name not in self.models:
            raise ValueError(f"Model not found: {name}")

        return self.models[name]

    def list_models(self) -> List[str]:
        """
        列出所有模型

        Returns:
            模型名称列表
        """
        return list(self.models.keys())

    def set_default_model(self, name: str):
        """
        设置默认模型

        Args:
            name: 模型名称
        """
        if name not in self.models:
            raise ValueError(f"Model not found: {name}")

        self.default_model = name
        logger.info(f"Set default model: {name}")


# 全局OpenMythos池
_openmythos_pool = None


def get_openmythos_pool() -> OpenMythosPool:
    """
    获取全局OpenMythos池

    Returns:
        OpenMythos池
    """
    global _openmythos_pool
    if _openmythos_pool is None:
        _openmythos_pool = OpenMythosPool()
    return _openmythos_pool


if __name__ == "__main__":
    # 测试OpenMythos适配器
    print("Testing OpenMythos Adapter...")

    if not OPENMYTHOS_AVAILABLE:
        print("OpenMythos not available. Install with: pip install open-mythos")
        sys.exit(1)

    # 创建配置
    config = OpenMythosConfig(
        model_size="3b",
        device="cuda" if torch.cuda.is_available() else "cpu",
        max_loop_iters=16,
        adaptive_loops=True,
    )

    # 创建适配器
    adapter = OpenMythosAdapter(config)

    # 获取模型信息
    info = adapter.get_model_info()
    print("\nModel Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # 获取谱半径
    spectral_radius = adapter.get_spectral_radius()
    print(f"\nSpectral Radius ρ(A): {spectral_radius:.4f} (must be < 1)")

    # 测试生成
    print("\nTesting generation...")
    input_ids = torch.randint(0, 32000, (1, 8)).to(adapter.device)
    output = adapter.generate(input_ids, max_new_tokens=4, n_loops=4)
    print(f"Input shape: {input_ids.shape}")
    print(f"Output shape: {output.shape}")

    # 测试自适应生成
    print("\nTesting adaptive generation...")
    output_easy = adapter.adaptive_generate(input_ids, max_new_tokens=4, task_difficulty="easy")
    output_hard = adapter.adaptive_generate(input_ids, max_new_tokens=4, task_difficulty="hard")
    print(f"Easy task output shape: {output_easy.shape}")
    print(f"Hard task output shape: {output_hard.shape}")

    print("\nOpenMythos Adapter tested successfully!")
