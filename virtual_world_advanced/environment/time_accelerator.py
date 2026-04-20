"""
Time Accelerator
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class TimeConfig:
    dilation_factor: float
    virtual_time: datetime
    real_time: datetime
    status: str


class TimeAccelerator:
    """
    Time Compression Accelerator
    Simulate months of training in hours
    """
    
    def __init__(self):
        self.dilation_factors = {
            'normal': 1.0,
            'fast': 10.0,
            'ultra': 100.0,
            'extreme': 1000.0
        }
        self.current_dilation = 1.0
        self.virtual_start: Optional[datetime] = None
        self.real_start: Optional[datetime] = None
    
    def start_time_dilation(self, mode: str = 'fast') -> TimeConfig:
        if mode not in self.dilation_factors:
            mode = 'fast'
        
        self.current_dilation = self.dilation_factors[mode]
        self.real_start = datetime.now()
        self.virtual_start = datetime.now()
        
        return TimeConfig(
            dilation_factor=self.current_dilation,
            virtual_time=self.virtual_start,
            real_time=self.real_start,
            status='active'
        )
    
    def get_virtual_time(self) -> datetime:
        if not self.real_start or not self.virtual_start:
            return datetime.now()
        
        elapsed_real = (datetime.now() - self.real_start).total_seconds()
        elapsed_virtual = elapsed_real * self.current_dilation
        
        return self.virtual_start + timedelta(seconds=elapsed_virtual)
    
    def convert_real_to_virtual(self, real_seconds: float) -> float:
        return real_seconds * self.current_dilation
    
    def convert_virtual_to_real(self, virtual_seconds: float) -> float:
        return virtual_seconds / self.current_dilation
    
    def get_stats(self) -> Dict:
        if not self.real_start:
            return {'status': 'inactive'}
        
        real_elapsed = (datetime.now() - self.real_start).total_seconds()
        virtual_elapsed = self.convert_real_to_virtual(real_elapsed)
        
        return {
            'dilation_factor': self.current_dilation,
            'real_elapsed_seconds': real_elapsed,
            'virtual_elapsed_seconds': virtual_elapsed,
            'virtual_days': virtual_elapsed / 86400,
            'virtual_months': virtual_elapsed / 2592000,
            'efficiency': f'{self.current_dilation}x'
        }
    
    def stop_time_dilation(self):
        self.current_dilation = 1.0
        self.real_start = None
        self.virtual_start = None
