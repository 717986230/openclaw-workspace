#!/usr/bin/env python3
"""
API侦察兵 - API Scout
自动发现AI模型API，比较价格，测试可用性
"""
import json
import time
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

@dataclass
class APIEndpoint:
    name: str
    provider: str
    base_url: str
    auth_type: str  # api_key, oauth, none
    models: List[str]
    pricing: Dict[str, float]  # model -> price per 1k tokens
    rate_limit: Optional[Dict]  # requests per minute/hour
    documentation_url: str
    signup_url: str
    available: bool = False
    tested_at: Optional[str] = None

class APIProvider(Enum):
    NVIDIA = "nvidia"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"
    TOGETHER = "together"
    GROQ = "groq"
    MISTRAL = "mistral"

class APIScout:
    """API侦察兵 - 负责发现和测试AI API"""
    
    def __init__(self):
        self.known_apis = self._load_known_apis()
        self.tested_apis = []  # 已测试的API列表
        
    def _load_known_apis(self) -> List[APIEndpoint]:
        """加载已知的API列表"""
        return [
            # NVIDIA API
            APIEndpoint(
                name="NVIDIA NIM API",
                provider="nvidia",
                base_url="https://integrate.api.nvidia.com/v1",
                auth_type="api_key",
                models=["nemotron-3-super", "llama-3", "mixtral"],
                pricing={},  # 需要查询
                rate_limit=None,
                documentation_url="https://docs.nvidia.com/nim/",
                signup_url="https://build.nvidia.com/",
            ),
            # OpenAI
            APIEndpoint(
                name="OpenAI API",
                provider="openai",
                base_url="https://api.openai.com/v1",
                auth_type="api_key",
                models=["gpt-4", "gpt-3.5-turbo"],
                pricing={"gpt-4": 0.03, "gpt-3.5-turbo": 0.002},
                rate_limit={"requests_per_minute": 3500},
                documentation_url="https://platform.openai.com/docs/",
                signup_url="https://platform.openai.com/signup",
            ),
            # Anthropic
            APIEndpoint(
                name="Anthropic API",
                provider="anthropic",
                base_url="https://api.anthropic.com/v1/",
                auth_type="api_key",
                models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                pricing={"claude-3-opus": 0.015, "claude-3-sonnet": 0.003, "claude-3-haiku": 0.00025},
                rate_limit=None,
                documentation_url="https://docs.anthropic.com/claude/",
                signup_url="https://console.anthropic.com/",
            ),
            # Google Gemini
            APIEndpoint(
                name="Google Gemini API",
                provider="google",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                auth_type="api_key",
                models=["gemini-pro", "gemini-1.5-pro"],
                pricing={"gemini-pro": 0.0005, "gemini-1.5-pro": 0.007},
                rate_limit=None,
                documentation_url="https://ai.google.dev/",
                signup_url="https://makersuite.google.com/",
            ),
            # Hugging Face Inference API
            APIEndpoint(
                name="Hugging Face Inference API",
                provider="huggingface",
                base_url="https://api-inference.huggingface.co/models/",
                auth_type="api_key",
                models=[],  # 动态获取
                pricing={"free_tier": 0},  # 有免费额度
                rate_limit={"requests_per_minute": 30},
                documentation_url="https://huggingface.co/docs/api-inference/",
                signup_url="https://huggingface.co/join",
            ),
            # Together AI
            APIEndpoint(
                name="Together AI",
                provider="together",
                base_url="https://api.together.xyz/v1",
                auth_type="api_key",
                models=["llama-2-70b", "mixtral-8x7b"],
                pricing={"llama-2-70b": 0.0009, "mixtral-8x7b": 0.0006},
                rate_limit=None,
                documentation_url="https://docs.together.ai/",
                signup_url="https://api.together.xyz/signup",
            ),
            # Groq
            APIEndpoint(
                name="Groq API",
                provider="groq",
                base_url="https://api.groq.com/openai/v1",
                auth_type="api_key",
                models=["mixtral-8x7b-32768", "llama2-70b-4096"],
                pricing={"mixtral-8x7b-32768": 0.0006, "llama2-70b-4096": 0.0008},
                rate_limit=None,
                documentation_url="https://groq.com/",
                signup_url="https://console.groq.com/",
            ),
        ]
    
    # ========== API发现 ==========
    def discover_new_apis(self) -> List[Dict]:
        """发现新的AI API"""
        # 这里可以实现：
        # 1. 爬取知名AI目录网站
        # 2. 搜索GitHub上的awesome-ai-api列表
        # 3. 检索Product Hunt等平台
        # 4. 监控Twitter/Reddit上的AI API讨论
        
        discovery_sources = [
            "https://www.producthunt.com/topics/ai-api",
            "https://github.com/forethought-ai/awesome-ai-apis",
            "https://www.productboard.com/ai-api-list/",
        ]
        
        # 实际实现中会使用web_agent爬取这些页面
        return [
            {
                "source": "producthunt_ai_api",
                "found_apis": ["新发现的API1", "新发现的API2"],
                "timestamp": time.time()
            }
        ]
    
    # ========== API测试 ==========
    def test_api_availability(self, api: APIEndpoint) -> Dict:
        """测试API是否可用"""
        # 实际测试步骤：
        # 1. 检查是否有API key（从环境变量或安全存储）
        # 2. 发送一个最小的测试请求
        # 3. 检查响应状态和延迟
        # 4. 记录结果
        
        test_result = {
            "api_name": api.name,
            "provider": api.provider,
            "tested_at": time.time(),
            "available": False,
            "latency_ms": None,
            "error": None,
            "models_working": []
        }
        
        # 模拟测试（实际实现需要真正的API key和网络请求）
        if api.provider == "nvidia":
            # 模拟NVIDIA API测试
            test_result["available"] = True  # 假设可用
            test_result["latency_ms"] = 150
            test_result["models_working"] = ["nemotron-3-super"]
        elif api.provider == "openai":
            # 模拟OpenAPI测试
            test_result["available"] = False  # 假设没有key
            test_result["error"] = "API key not configured"
        
        return test_result
    
    def batch_test_apis(self, apis: List[APIEndpoint] = None) -> List[Dict]:
        """批量测试多个API"""
        if apis is None:
            apis = self.known_apis
            
        results = []
        for api in apis:
            result = self.test_api_availability(api)
            results.append(result)
            # 更新API状态
            api.available = result["available"]
            api.tested_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(result["tested_at"]))
            
        return results
    
    # ========== 价格比较 ==========
    def compare_pricing(self, model_pattern: str = None) -> Dict:
        """比较不同API的价格"""
        comparisons = {}
        
        for api in self.known_apis:
            if not api.pricing:
                continue
                
            for model, price in api.pricing.items():
                if model_pattern and model_pattern not in model:
                    continue
                    
                key = f"{api.provider}:{model}"
                if key not in comparisons or price < comparisons[key]["price"]:
                    comparisons[key] = {
                        "provider": api.provider,
                        "model": model,
                        "price_per_1k_tokens": price,
                        "api_name": api.name,
                        "url": api.base_url
                    }
        
        # 按价格排序
        sorted_comparisons = dict(sorted(
            comparisons.items(), 
            key=lambda x: x[1]["price_per_1k_tokens"]
        ))
        
        return {
            "comparison": sorted_comparisons,
            "cheapest": list(sorted_comparisons.values())[0] if sorted_comparisons else None,
            "timestamp": time.time()
        }
    
    # ========== 自动注册建议 ==========
    def suggest_registration(self, api: APIEndpoint) -> Dict:
        """为API生成注册建议"""
        return {
            "api": api.name,
            "provider": api.provider,
            "signup_url": api.signup_url,
            "documentation_url": api.documentation_url,
            "steps": [
                f"访问 {api.signup_url}",
                "创建账号并验证邮箱",
                "完成实名认证（如果需要）",
                "获取API Key",
                "将API Key安全存储到环境变量或密钥管理器",
                f"测试连接: curl {api.base_url}/models -H \"Authorization: Bearer YOUR_KEY\""
            ],
            "estimated_time_minutes": 5,
            "difficulty": "easy" if api.auth_type == "api_key" else "medium"
        }

# 全局侦察兵实例
_api_scout = None

def get_api_scout() -> APIScout:
    global _api_scout
    if _api_scout is None:
        _api_scout = APIScout()
    return _api_scout

# 演示函数
def demo():
    scout = get_api_scout()
    print("=== API Scout Demo ===")
    
    print("\n1. 已知API列表:")
    for api in scout.known_apis[:3]:  # 显示前3个
        print(f"  - {api.name} ({api.provider}): {len(api.models)} models")
    
    print("\n2. 价格比较（前5名）:")
    pricing = scout.compare_pricing()
    for i, (key, info) in enumerate(list(pricing["comparison"].items())[:5]):
        print(f"  {i+1}. {info['provider']}:{info['model']} - ${info['price_per_1k_tokens']}/1K tokens")
    
    print(f"\n3. 最便宜选项:")
    if pricing["cheapest"]:
        cheapest = pricing["cheapest"]
        print(f"  {cheapest['provider']}:{cheapest['model']} - ${cheapest['price_per_1k_tokens']}/1K tokens")
    
    print("\n4. API测试示例:")
    test_results = scout.batch_test_apis(scout.known_apis[:2])
    for result in test_results:
        status = "✅ 可用" if result["available"] else f"❌ 不可用 ({result.get('error', 'unknown')})"
        print(f"  {result['api_name']}: {status}")

if __name__ == "__main__":
    demo()