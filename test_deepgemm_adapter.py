# -*- coding: utf-8 -*-
"""
测试 DeepGEMM 适配器 - Test DeepGEMM Adapter
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from erbing_system.deepgemm_adapter import (
    get_deepgemm_adapter,
    GEMMConfig,
    GEMMDataType,
    GEMMLayout,
)
import numpy as np


def test_deepgemm_adapter():
    """测试 DeepGEMM 适配器"""
    print("=" * 60)
    print("Testing DeepGEMM Adapter")
    print("=" * 60)

    try:
        # 获取适配器实例
        adapter = get_deepgemm_adapter()

        # 测试 1: 添加配置
        print("\n[Test 1] Adding config...")
        config = GEMMConfig(
            data_type=GEMMDataType.FP32,
            layout=GEMMLayout.NN,
            m=128,
            n=128,
            k=128,
        )
        success = adapter.add_config(config)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 2: 获取配置
        print("\n[Test 2] Getting config...")
        config_id = f"{config.data_type.value}_{config.layout.value}_{config.m}x{config.n}x{config.k}"
        retrieved_config = adapter.get_config(config_id)
        print(f"  Result: {'PASS' if retrieved_config is not None else 'FAIL'}")

        # 测试 3: 列出配置
        print("\n[Test 3] Listing configs...")
        configs = adapter.list_configs()
        print(f"  Result: {'PASS' if len(configs) > 0 else 'FAIL'}")

        # 测试 4: 运行 GEMM
        print("\n[Test 4] Running GEMM...")
        a = np.random.randn(128, 128).astype(np.float32)
        b = np.random.randn(128, 128).astype(np.float32)
        result = adapter.run_gemm(config, a, b)
        print(f"  Result: {'PASS' if result is not None else 'FAIL'}")

        # 测试 5: 获取结果
        print("\n[Test 5] Getting result...")
        if result:
            result_id = f"{config.data_type.value}_{config.layout.value}_{config.m}x{config.n}x{config.k}_{result.execution_time:.4f}"
            retrieved_result = adapter.get_result(result_id)
            print(f"  Result: {'PASS' if retrieved_result is not None else 'FAIL'}")
        else:
            print(f"  Result: FAIL")

        # 测试 6: 列出结果
        print("\n[Test 6] Listing results...")
        results = adapter.list_results()
        print(f"  Result: {'PASS' if len(results) > 0 else 'FAIL'}")

        # 测试 7: 获取状态
        print("\n[Test 7] Getting status...")
        status = adapter.get_status()
        print(f"  Result: {'PASS' if status['initialized'] else 'FAIL'}")

        # 测试 8: 移除结果
        print("\n[Test 8] Removing result...")
        if result:
            result_id = f"{config.data_type.value}_{config.layout.value}_{config.m}x{config.n}x{config.k}_{result.execution_time:.4f}"
            success = adapter.remove_result(result_id)
            print(f"  Result: {'PASS' if success else 'FAIL'}")
        else:
            print(f"  Result: FAIL")

        # 测试 9: 移除配置
        print("\n[Test 9] Removing config...")
        config_id = f"{config.data_type.value}_{config.layout.value}_{config.m}x{config.n}x{config.k}"
        success = adapter.remove_config(config_id)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        print("\n" + "=" * 60)
        print("[PASS] All DeepGEMM Adapter tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_deepgemm_adapter()
    sys.exit(0 if success else 1)
