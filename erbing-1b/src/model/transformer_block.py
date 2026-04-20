"""
Transformer 块（带 Grouped Query Attention）
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class RotaryEmbedding(nn.Module):
    """旋转位置编码 (RoPE)"""
    
    def __init__(self, dim: int, max_seq_len: int = 8192, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len
        self.base = base
        
        # 预计算频率
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        
        # 预计算缓存
        self._build_cache(max_seq_len)
    
    def _build_cache(self, seq_len: int):
        """构建位置编码缓存"""
        t = torch.arange(seq_len, device=self.inv_freq.device).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos()[None, None, :, :], persistent=False)
        self.register_buffer("sin_cached", emb.sin()[None, None, :, :], persistent=False)
    
    def forward(self, seq_len: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """获取 RoPE 编码
        
        Args:
            seq_len: 序列长度
            device: 设备
        
        Returns:
            (cos, sin) 形状为 (1, 1, seq_len, dim)
        """
        if seq_len > self.max_seq_len:
            self._build_cache(seq_len)
        
        return (
            self.cos_cached[:, :, :seq_len, :].to(device),
            self.sin_cached[:, :, :seq_len, :].to(device),
        )


def apply_rotary_pos_emb(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """应用旋转位置编码
    
    Args:
        q: (batch, seq_len, num_heads, head_dim)
        k: (batch, seq_len, num_kv_heads, head_dim)
        cos: (1, 1, seq_len, head_dim)
        sin: (1, 1, seq_len, head_dim)
    
    Returns:
        (q_rot, k_rot)
    """
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """旋转一半维度"""
    x1, x2 = x[..., : x.shape[-1] // 2], x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


class TransformerBlock(nn.Module):
    """带 Grouped Query Attention 的 Transformer 块"""
    
    def __init__(
        self,
        hidden_size: int,
        num_heads: int,
        num_kv_heads: int,
        intermediate_size: int,
        rms_norm_eps: float = 1e-5,
        use_flash_attn: bool = True,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = hidden_size // num_heads
        self.use_flash_attn = use_flash_attn
        
        # Grouped Query Attention 投影
        self.q_proj = nn.Linear(hidden_size, num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(hidden_size, num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(hidden_size, num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(num_heads * self.head_dim, hidden_size, bias=False)
        
        # SwiGLU FFN
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=False)
        
        # RMSNorm
        self.input_layernorm = nn.RMSNorm(hidden_size, eps=rms_norm_eps)
        self.post_attention_layernorm = nn.RMSNorm(hidden_size, eps=rms_norm_eps)
    
    def forward(
        self,
        x: torch.Tensor,
        cos: torch.Tensor,
        sin: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, hidden_size)
            cos: RoPE cos
            sin: RoPE sin
            attention_mask: 可选的注意力掩码
        
        Returns:
            (batch, seq_len, hidden_size)
        """
        batch, seq_len, _ = x.shape
        
        # Attention
        residual = x
        x = self.input_layernorm(x)
        
        # QKV 投影
        q = self.q_proj(x).view(batch, seq_len, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim)
        v = self.v_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim)
        
        # 应用 RoPE
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        
        # GQA: 重复 K/V 头
        if self.num_kv_heads < self.num_heads:
            k = k.repeat_interleave(self.num_heads // self.num_kv_heads, dim=2)
            v = v.repeat_interleave(self.num_heads // self.num_kv_heads, dim=2)
        
        # Flash Attention 或标准 Attention
        if self.use_flash_attn:
            attn_output = self.flash_attention(q, k, v, attention_mask)
        else:
            attn_output = self.standard_attention(q, k, v, attention_mask)
        
        attn_output = self.o_proj(attn_output)
        x = residual + attn_output
        
        # FFN with SwiGLU
        residual = x
        x = self.post_attention_layernorm(x)
        gate = F.silu(self.gate_proj(x))
        up = self.up_proj(x)
        x = self.down_proj(gate * up)
        
        return x + residual
    
    def flash_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Flash Attention 2"""
        # 转换为 (batch, num_heads, seq_len, head_dim)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        
        # 使用 PyTorch 的 scaled_dot_product_attention
        attn_output = F.scaled_dot_product_attention(
            q, k, v,
            attn_mask=attention_mask,
            is_causal=True,
        )
        
        # 转回 (batch, seq_len, num_heads, head_dim)
        attn_output = attn_output.transpose(1, 2)
        
        # 合并头
        batch, seq_len, num_heads, head_dim = attn_output.shape
        attn_output = attn_output.reshape(batch, seq_len, num_heads * head_dim)
        
        return attn_output
    
    def standard_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """标准 Attention（备用）"""
        # 转换为 (batch, num_heads, seq_len, head_dim)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        
        # 应用掩码
        if attention_mask is not None:
            scores = scores + attention_mask
        
        # 因果掩码
        causal_mask = torch.triu(
            torch.ones(seq_len, seq_len, device=scores.device, dtype=torch.bool),
            diagonal=1,
        )
        scores = scores.masked_fill(causal_mask, float("-inf"))
        
        # Softmax
        attn_weights = F.softmax(scores, dim=-1)
        
        # 加权求和
        attn_output = torch.matmul(attn_weights, v)
        
        # 转回 (batch, seq_len, num_heads, head_dim)
        attn_output = attn_output.transpose(1, 2)
        
        # 合并头
        batch, seq_len, num_heads, head_dim = attn_output.shape
        attn_output = attn_output.reshape(batch, seq_len, num_heads * head_dim)
        
        return attn_output
