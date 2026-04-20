"""
Erbing-1B 模型配置
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MambaConfig:
    """Mamba 层配置"""
    d_state: int = 16
    d_conv: int = 4
    expand: int = 2


@dataclass
class TransformerConfig:
    """Transformer 层配置"""
    attention_type: str = "grouped_query"
    num_kv_heads: int = 4
    use_flash_attn: bool = True
    rope_theta: float = 10000.0


@dataclass
class Erbing1BConfig:
    """Erbing-1B 完整配置"""
    
    # 基础信息
    name: str = "Erbing-1B"
    architecture: str = "HybridMambaTransformer"
    
    # 基础参数
    hidden_size: int = 2048
    num_layers: int = 24
    num_attention_heads: int = 16
    head_dim: int = 128
    intermediate_size: int = 5504
    vocab_size: int = 32000
    
    # 混合架构配置
    mamba_layers: int = 12
    transformer_layers: int = 12
    
    # Mamba 配置
    mamba: MambaConfig = field(default_factory=MambaConfig)
    
    # Transformer 配置
    transformer: TransformerConfig = field(default_factory=TransformerConfig)
    
    # 位置编码
    position_embedding: str = "rope"
    max_position_embeddings: int = 8192
    rope_scaling: Optional[dict] = field(default_factory=lambda: {
        "type": "dynamic",
        "factor": 4.0
    })
    
    # 激活与正则化
    hidden_act: str = "swiglu"
    initializer_range: float = 0.02
    rms_norm_eps: float = 1e-5
    
    # 训练优化
    use_cache: bool = True
    tie_word_embeddings: bool = False
    
    # 左右脑配置
    dual_brain: bool = True
    left_brain_weight: float = 0.6  # 结构化记忆权重
    right_brain_weight: float = 0.4  # 语义记忆权重
    
    def __post_init__(self):
        """验证配置"""
        assert self.num_layers == self.mamba_layers + self.transformer_layers, \
            "总层数必须等于 Mamba 层数 + Transformer 层数"
        assert self.hidden_size % self.num_attention_heads == 0, \
            "hidden_size 必须能被 num_attention_heads 整除"
        assert self.num_attention_heads % self.transformer.num_kv_heads == 0, \
            "num_attention_heads 必须能被 num_kv_heads 整除"
    
    @property
    def num_params(self) -> int:
        """估算参数量"""
        # Embedding
        embedding_params = self.vocab_size * self.hidden_size
        
        # Mamba 层
        mamba_params = 12 * (3 * self.hidden_size * self.hidden_size * self.mamba.expand)
        
        # Transformer 层
        qkv_params = 3 * self.hidden_size * self.hidden_size
        o_params = self.hidden_size * self.hidden_size
        ffn_params = 3 * self.hidden_size * self.intermediate_size
        transformer_params = 12 * (qkv_params + o_params + ffn_params)
        
        total = embedding_params + mamba_params + transformer_params
        return total
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "architecture": self.architecture,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "num_attention_heads": self.num_attention_heads,
            "vocab_size": self.vocab_size,
            "mamba_layers": self.mamba_layers,
            "transformer_layers": self.transformer_layers,
            "max_position_embeddings": self.max_position_embeddings,
            "num_params": self.num_params,
        }
