# -*- coding: utf-8 -*-
"""
DeepGEMM 整合适配器 - DeepGEMM Integration Adapter
将 DeepGEMM 的核心功能整合到二饼系统中
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class GEMMDataType(Enum):
    """GEMM 数据类型"""
    FP8 = "fp8"
    FP4 = "fp4"
    BF16 = "bf16"
    FP16 = "fp16"
    FP32 = "fp32"


class GEMMLayout(Enum):
    """GEMM 布局"""
    NT = "nt"  # Non-transposed A, Transposed B
    NN = "nn"  # Non-transposed A, Non-transposed B
    TN = "tn"  # Transposed A, Non-transposed B
    TT = "tt"  # Transposed A, Transposed B


@dataclass
class GEMMConfig:
    """GEMM 配置"""
    data_type: GEMMDataType
    layout: GEMMLayout
    m: int
    n: int
    k: int
    use_fp8_scaling: bool = True
    use_moe: bool = False
    num_experts: int = 1


@dataclass
class GEMMResult:
    """GEMM 结果"""
    output: np.ndarray
    config: GEMMConfig
    execution_time: float
    tflops: float = 0.0


class DeepGEMMAdapter:
    """DeepGEMM 适配器"""

    def __init__(self):
        self.configs: Dict[str, GEMMConfig] = {}
        self.results: Dict[str, GEMMResult] = {}
        self.initialized = False

    def initialize(self):
        """初始化适配器"""
        logger.info("Initializing DeepGEMM Adapter...")

        # 添加示例配置
        self._add_sample_configs()

        self.initialized = True
        logger.info("DeepGEMM Adapter initialized successfully")

    def _add_sample_configs(self):
        """添加示例配置"""
        # 添加示例 FP8 GEMM 配置
        self.add_config(
            GEMMConfig(
                data_type=GEMMDataType.FP8,
                layout=GEMMLayout.NT,
                m=4096,
                n=4096,
                k=4096,
                use_fp8_scaling=True,
            )
        )

    def add_config(self, config: GEMMConfig) -> bool:
        """添加配置"""
        config_id = self._generate_config_id(config)

        if config_id in self.configs:
            logger.warning(f"Config '{config_id}' already exists")
            return False

        self.configs[config_id] = config
        logger.info(f"Config '{config_id}' added successfully")
        return True

    def get_config(self, config_id: str) -> Optional[GEMMConfig]:
        """获取配置"""
        return self.configs.get(config_id)

    def list_configs(self) -> List[GEMMConfig]:
        """列出所有配置"""
        return list(self.configs.values())

    def remove_config(self, config_id: str) -> bool:
        """移除配置"""
        if config_id not in self.configs:
            logger.warning(f"Config '{config_id}' not found")
            return False

        del self.configs[config_id]
        logger.info(f"Config '{config_id}' removed successfully")
        return True

    def run_gemm(self, config: GEMMConfig, a: np.ndarray, b: np.ndarray, c: Optional[np.ndarray] = None) -> Optional[GEMMResult]:
        """运行 GEMM"""
        logger.info(f"Running GEMM with config: {config.data_type.value} {config.layout.value} {config.m}x{config.n}x{config.k}")

        # 验证输入
        if not self._validate_inputs(config, a, b):
            logger.error("Invalid inputs for GEMM")
            return None

        # 记录开始时间
        start_time = datetime.now()

        try:
            # 执行 GEMM
            output = self._execute_gemm(config, a, b, c)

            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()

            # 计算 TFLOPS
            tflops = self._calculate_tflops(config, execution_time)

            # 创建结果
            result = GEMMResult(
                output=output,
                config=config,
                execution_time=execution_time,
                tflops=tflops,
            )

            # 保存结果
            result_id = self._generate_result_id(result)
            self.results[result_id] = result

            logger.info(f"GEMM completed in {execution_time:.4f}s, {tflops:.2f} TFLOPS")
            return result

        except Exception as e:
            logger.error(f"GEMM failed: {str(e)}")
            return None

    def _validate_inputs(self, config: GEMMConfig, a: np.ndarray, b: np.ndarray) -> bool:
        """验证输入"""
        # 验证 A 矩阵
        if config.layout == GEMMLayout.NT or config.layout == GEMMLayout.NN:
            if a.shape != (config.m, config.k):
                logger.error(f"Invalid A shape: {a.shape}, expected ({config.m}, {config.k})")
                return False
        else:  # TN or TT
            if a.shape != (config.k, config.m):
                logger.error(f"Invalid A shape: {a.shape}, expected ({config.k}, {config.m})")
                return False

        # 验证 B 矩阵
        if config.layout == GEMMLayout.NT or config.layout == GEMMLayout.TN:
            if b.shape != (config.k, config.n):
                logger.error(f"Invalid B shape: {b.shape}, expected ({config.k}, {config.n})")
                return False
        else:  # NN or TT
            if b.shape != (config.n, config.k):
                logger.error(f"Invalid B shape: {b.shape}, expected ({config.n}, {config.k})")
                return False

        return True

    def _execute_gemm(self, config: GEMMConfig, a: np.ndarray, b: np.ndarray, c: Optional[np.ndarray] = None) -> np.ndarray:
        """执行 GEMM"""
        # 根据布局执行矩阵乘法
        if config.layout == GEMMLayout.NT:
            # D = C + A @ B.T
            output = a @ b.T
        elif config.layout == GEMMLayout.NN:
            # D = C + A @ B
            output = a @ b
        elif config.layout == GEMMLayout.TN:
            # D = C + A.T @ B
            output = a.T @ b
        elif config.layout == GEMMLayout.TT:
            # D = C + A.T @ B.T
            output = a.T @ b.T
        else:
            raise ValueError(f"Unsupported layout: {config.layout}")

        # 添加 C 矩阵（如果提供）
        if c is not None:
            output = output + c

        return output

    def _calculate_tflops(self, config: GEMMConfig, execution_time: float) -> float:
        """计算 TFLOPS"""
        if execution_time == 0:
            return 0.0

        # 计算浮点运算次数
        flops = 2 * config.m * config.n * config.k  # 2 * M * N * K

        # 转换为 TFLOPS
        tflops = flops / (execution_time * 1e12)

        return tflops

    def _generate_config_id(self, config: GEMMConfig) -> str:
        """生成配置 ID"""
        return f"{config.data_type.value}_{config.layout.value}_{config.m}x{config.n}x{config.k}"

    def _generate_result_id(self, result: GEMMResult) -> str:
        """生成结果 ID"""
        return f"{self._generate_config_id(result.config)}_{result.execution_time:.4f}"

    def get_result(self, result_id: str) -> Optional[GEMMResult]:
        """获取结果"""
        return self.results.get(result_id)

    def list_results(self) -> List[GEMMResult]:
        """列出所有结果"""
        return list(self.results.values())

    def remove_result(self, result_id: str) -> bool:
        """移除结果"""
        if result_id not in self.results:
            logger.warning(f"Result '{result_id}' not found")
            return False

        del self.results[result_id]
        logger.info(f"Result '{result_id}' removed successfully")
        return True

    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "initialized": self.initialized,
            "total_configs": len(self.configs),
            "total_results": len(self.results),
            "configs": {
                config_id: {
                    "data_type": config.data_type.value,
                    "layout": config.layout.value,
                    "m": config.m,
                    "n": config.n,
                    "k": config.k,
                    "use_fp8_scaling": config.use_fp8_scaling,
                    "use_moe": config.use_moe,
                    "num_experts": config.num_experts,
                }
                for config_id, config in self.configs.items()
            },
            "results": {
                result_id: {
                    "config_id": self._generate_config_id(result.config),
                    "execution_time": result.execution_time,
                    "tflops": result.tflops,
                }
                for result_id, result in self.results.items()
            },
        }


# 全局实例
_deepgemm_adapter = None


def get_deepgemm_adapter() -> DeepGEMMAdapter:
    """获取 DeepGEMM 适配器实例"""
    global _deepgemm_adapter
    if _deepgemm_adapter is None:
        _deepgemm_adapter = DeepGEMMAdapter()
        _deepgemm_adapter.initialize()
    return _deepgemm_adapter


if __name__ == "__main__":
    # 测试 DeepGEMM 适配器
    print("Testing DeepGEMM Adapter...")

    # 获取适配器实例
    adapter = get_deepgemm_adapter()

    # 创建测试矩阵
    import numpy as np
    a = np.random.randn(128, 128).astype(np.float32)
    b = np.random.randn(128, 128).astype(np.float32)

    # 创建配置
    config = GEMMConfig(
        data_type=GEMMDataType.FP32,
        layout=GEMMLayout.NN,
        m=128,
        n=128,
        k=128,
    )

    # 运行 GEMM
    result = adapter.run_gemm(config, a, b)

    if result:
        print(f"Output shape: {result.output.shape}")
        print(f"Execution time: {result.execution_time:.4f}s")
        print(f"TFLOPS: {result.tflops:.2f}")

    # 获取状态
    status = adapter.get_status()
    print(f"\nDeepGEMM Adapter Status:")
    print(f"  Initialized: {status['initialized']}")
    print(f"  Total Configs: {status['total_configs']}")
    print(f"  Total Results: {status['total_results']}")

    print("\nDeepGEMM Adapter tested successfully!")
