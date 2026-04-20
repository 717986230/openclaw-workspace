"""
Mamba 状态空间模型块
"""

import torch
import torch.nn as nn
from typing import Optional


class MambaBlock(nn.Module):
    """Mamba 状态空间模型块
    
    使用线性复杂度的状态空间模型处理长序列
    """
    
    def __init__(
        self,
        hidden_size: int,
        d_state: int = 16,
        d_conv: int = 4,
        expand: int = 2,
        rms_norm_eps: float = 1e-5,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.d_state = d_state
        self.d_conv = d_conv
        self.expand = expand
        
        # 内部维度
        self.d_inner = int(self.expand * self.hidden_size)
        
        # 输入投影
        self.in_proj = nn.Linear(self.hidden_size, self.d_inner * 2, bias=False)
        
        # 卷积层
        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            kernel_size=d_conv,
            padding=d_conv - 1,
            groups=self.d_inner,
            bias=False,
        )
        
        # SSM 参数投影
        self.x_proj = nn.Linear(self.d_inner, self.d_state * 2 + self.d_inner, bias=False)
        self.dt_proj = nn.Linear(self.d_state, self.d_inner, bias=True)
        
        # S4D 参数
        self.A_log = nn.Parameter(torch.log(torch.rand(self.d_inner, self.d_state)))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        
        # 输出投影
        self.out_proj = nn.Linear(self.d_inner, self.hidden_size, bias=False)
        
        # RMSNorm
        self.norm = nn.RMSNorm(hidden_size, eps=rms_norm_eps)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, hidden_size)
        
        Returns:
            (batch, seq_len, hidden_size)
        """
        batch, seq_len, _ = x.shape
        
        # Pre-norm
        residual = x
        x = self.norm(x)
        
        # 输入投影
        xz = self.in_proj(x)  # (batch, seq_len, d_inner * 2)
        x, z = xz.chunk(2, dim=-1)  # 各 (batch, seq_len, d_inner)
        
        # 卷积
        x = x.transpose(1, 2)  # (batch, d_inner, seq_len)
        x = self.conv1d(x)[..., :seq_len]  # 移除 padding
        x = x.transpose(1, 2)  # (batch, seq_len, d_inner)
        
        # SiLU 激活
        x = torch.nn.functional.silu(x)
        
        # SSM 参数
        B, C, dt = self.x_proj(x).split([self.d_state, self.d_state, self.d_inner], dim=-1)
        dt = torch.nn.functional.softplus(dt_proj(dt))
        B = torch.nn.functional.softplus(B)
        
        # S4D 核心
        A = -torch.exp(self.A_log.float())  # (d_inner, d_state)
        
        # 简化的 SSM 前向传播（实际实现需要更高效的算法）
        y = self.ssm_step(x, A, B, C, dt)
        
        # 门控
        y = y * torch.nn.functional.silu(z)
        
        # 输出投影
        output = self.out_proj(y)
        
        return output + residual
    
    def ssm_step(
        self,
        x: torch.Tensor,
        A: torch.Tensor,
        B: torch.Tensor,
        C: torch.Tensor,
        dt: torch.Tensor,
    ) -> torch.Tensor:
        """简化的 SSM 前向传播
        
        实际实现应该使用更高效的并行算法
        """
        # 这里使用简化版本，实际需要使用 mamba_ssm 库
        # 或者实现高效的并行扫描算法
        
        batch, seq_len, d_inner = x.shape
        d_state = A.shape[1]
        
        # 初始化状态
        h = torch.zeros(batch, d_inner, d_state, device=x.device, dtype=x.dtype)
        
        outputs = []
        
        for t in range(seq_len):
            # 离散化
            dA = torch.exp(dt[:, t:t+1] * A.T)  # (batch, d_state, d_inner)
            dB = dt[:, t:t+1] * B[:, t:t+1]  # (batch, d_state, 1)
            
            # 状态更新
            h = h * dA.transpose(1, 2) + (x[:, t:t+1, :] * dB.transpose(1, 2))
            
            # 输出
            y_t = torch.sum(h * C[:, t:t+1, :].transpose(1, 2), dim=-1)
            outputs.append(y_t)
        
        y = torch.cat(outputs, dim=1)
        
        # 添加跳跃连接
        y = y + x * self.D.unsqueeze(0).unsqueeze(0)
        
        return y


def dt_proj(dt: torch.Tensor) -> torch.Tensor:
    """投影 delta_t 到正数域"""
    return torch.nn.functional.softplus(dt)


# 如果有 mamba_ssm 库，使用优化版本
try:
    from mamba_ssm import Mamba as MambaSSM
    
    class OptimizedMambaBlock(nn.Module):
        """使用 mamba_ssm 库的优化版本"""
        
        def __init__(
            self,
            hidden_size: int,
            d_state: int = 16,
            d_conv: int = 4,
            expand: int = 2,
            rms_norm_eps: float = 1e-5,
        ):
            super().__init__()
            self.mamba = MambaSSM(
                d_model=hidden_size,
                d_state=d_state,
                d_conv=d_conv,
                expand=expand,
            )
            self.norm = nn.RMSNorm(hidden_size, eps=rms_norm_eps)
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            residual = x
            x = self.norm(x)
            x = self.mamba(x)
            return x + residual
    
    MambaBlock = OptimizedMambaBlock  # 使用优化版本
    
except ImportError:
    # 使用简化版本
    pass
