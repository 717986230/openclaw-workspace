"""
MT5 顶配盯盘系统 - 配置文件
"""

# 系统配置
SYSTEM_CONFIG = {
    'name': 'MT5 顶配盯盘系统',
    'version': '1.0.0',
    'log_level': 'INFO',
    'log_file': 'mt5_system.log',
}

# MT5 连接配置
MT5_CONFIG = {
    'login': 2046664504,  # MT5 账号
    'password': '54*O^-c!',  # MT5 密码
    'server': 'Dukascopy-demo-mt5-1',  # MT5 服务器
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',  # MT5 终端路径
}

# 交易品种配置
SYMBOLS_CONFIG = {
    'enabled': [
        'EURUSD',
        'GBPUSD',
        'USDJPY',
        'XAUUSD',  # Gold
        'XAGUSD',  # Silver
    ],
    'timeframes': {
        'EURUSD': 'H1',
        'GBPUSD': 'H1',
        'USDJPY': 'H1',
        'XAUUSD': 'H4',
        'XAGUSD': 'H4',
    },
}

# 风险管理配置
RISK_CONFIG = {
    'max_position_size': 0.02,  # 最大仓位比例 (2%)
    'max_daily_loss': 0.05,  # 最大日亏损比例 (5%)
    'max_drawdown': 0.15,  # 最大回撤比例 (15%)
    'risk_reward_ratio': 1.49,  # 风险收益比
    'max_positions': 5,  # 最大持仓数
    'max_correlation': 0.7,  # 最大相关性
    'min_confidence': 0.6,  # 最小信号置信度
}

# 技术指标配置
INDICATORS_CONFIG = {
    'sma': {
        'short_period': 20,
        'long_period': 50,
    },
    'ema': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9,
    },
    'rsi': {
        'period': 14,
        'overbought': 70,
        'oversold': 30,
    },
    'bollinger_bands': {
        'period': 20,
        'std_dev': 2,
    },
    'atr': {
        'period': 14,
        'multiplier': 2,
    },
}

# 信号生成配置
SIGNAL_CONFIG = {
    'min_strength': 0.6,  # 最小信号强度
    'max_signals_per_symbol': 1,  # 每个品种最大信号数
    'signal_timeout': 300,  # 信号超时时间（秒）
}

# 订单执行配置
ORDER_CONFIG = {
    'default_type': 'MARKET',  # 默认订单类型
    'dry_run': True,  # 测试模式：只构造订单请求，不发送真实订单
    'slippage': 20,  # 滑点容忍度
    'timeout': 30,  # 订单超时时间（秒）
    'magic_number': 123456,  # 魔术数字
    'comment': 'MT5 顶配系统',
}

# 监控配置
MONITORING_CONFIG = {
    'enabled': True,
    'check_interval': 60,  # 检查间隔（秒）
    'alert_enabled': True,
    'alert_methods': ['log', 'email', 'telegram'],
}

# 告警配置
ALERT_CONFIG = {
    'email': {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender': '',
        'password': '',
        'recipients': [],
    },
    'telegram': {
        'enabled': False,
        'bot_token': '',
        'chat_id': '',
    },
}

# 数据库配置
DATABASE_CONFIG = {
    'enabled': True,
    'type': 'sqlite',  # sqlite, postgresql, mysql
    'sqlite': {
        'path': 'mt5_system.db',
    },
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'mt5_system',
        'user': 'postgres',
        'password': '',
    },
}

# 回测配置
BACKTEST_CONFIG = {
    'enabled': True,
    'start_date': '2023-01-01',
    'end_date': '2024-01-01',
    'initial_balance': 10000,
    'spread': 0.0002,
    'commission': 0.0001,
}

# 机器学习配置
ML_CONFIG = {
    'enabled': False,
    'model_type': 'xgboost',  # xgboost, lightgbm, lstm, transformer
    'features': [
        'sma_short',
        'sma_long',
        'ema_fast',
        'ema_slow',
        'rsi',
        'macd',
        'signal',
        'atr',
        'volume',
    ],
    'train_interval': 7,  # 训练间隔（天）
}

# Web 界面配置
WEB_CONFIG = {
    'enabled': True,
    'host': '0.0.0.0',
    'port': 8080,
    'debug': False,
}

# API 配置
API_CONFIG = {
    'enabled': True,
    'host': '0.0.0.0',
    'port': 8000,
    'api_key': '',
    'rate_limit': 100,  # 每分钟请求数
}

# 性能配置
PERFORMANCE_CONFIG = {
    'max_workers': 10,
    'cache_enabled': True,
    'cache_ttl': 300,
    'async_enabled': True,
}

# 安全配置
SECURITY_CONFIG = {
    'encryption_enabled': True,
    'api_key_required': True,
    'ip_whitelist': [],
    'max_requests_per_minute': 100,
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': {
        'file': {
            'enabled': True,
            'filename': 'mt5_system.log',
            'max_bytes': 10485760,  # 10MB
            'backup_count': 5,
        },
        'console': {
            'enabled': True,
        },
    },
}

# 导出配置
EXPORT_CONFIG = {
    'enabled': True,
    'formats': ['csv', 'json'],
    'interval': 3600,  # 导出间隔（秒）
    'directory': 'exports',
}

# 备份配置
BACKUP_CONFIG = {
    'enabled': True,
    'interval': 86400,  # 备份间隔（秒）
    'directory': 'backups',
    'keep_days': 30,
}
