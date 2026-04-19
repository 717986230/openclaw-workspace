"""
MT5 顶配盯盘系统 - Web 界面
"""

import sys
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import MetaTrader5 as mt5

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mt5_system.mt5_top_tier_engine import MT5DataCollector, TechnicalIndicators
from mt5_system.config import (
    WEB_CONFIG,
    SYMBOLS_CONFIG,
    MONITORING_CONFIG
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mt5-top-tier-system-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
data_collector = MT5DataCollector()
indicators = TechnicalIndicators()
system_status = {
    'running': False,
    'connected': False,
    'last_update': None,
    'positions': [],
    'signals': [],
}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'running': system_status['running'],
        'connected': system_status['connected'],
        'last_update': system_status['last_update'],
        'positions_count': len(system_status['positions']),
        'signals_count': len(system_status['signals']),
    })


@app.route('/api/account')
def get_account():
    """获取账户信息"""
    if not system_status['connected']:
        return jsonify({'error': '未连接到 MT5'})

    try:
        account_info = data_collector.get_account_info()
        if account_info:
            return jsonify({
                'login': account_info['login'],
                'balance': account_info['balance'],
                'equity': account_info['equity'],
                'margin': account_info['margin'],
                'free_margin': account_info['free_margin'],
                'margin_level': account_info['margin_level'],
                'profit': account_info['profit'],
            })
        else:
            return jsonify({'error': '无法获取账户信息'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/positions')
def get_positions():
    """获取持仓信息"""
    if not system_status['connected']:
        return jsonify({'error': '未连接到 MT5'})

    try:
        positions = data_collector.get_positions()
        system_status['positions'] = positions
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/symbols')
def get_symbols():
    """获取交易品种"""
    if not system_status['connected']:
        return jsonify({'error': '未连接到 MT5'})

    try:
        symbols = data_collector.get_symbols()
        return jsonify(symbols)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/tick/<symbol>')
def get_tick(symbol):
    """获取实时报价"""
    if not system_status['connected']:
        return jsonify({'error': '未连接到 MT5'})

    try:
        tick = data_collector.get_tick(symbol)
        if tick:
            return jsonify(tick)
        else:
            return jsonify({'error': '无法获取报价'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/rates/<symbol>')
def get_rates(symbol):
    """获取历史价格"""
    if not system_status['connected']:
        return jsonify({'error': '未连接到 MT5'})

    try:
        timeframe = request.args.get('timeframe', 'H1')
        count = int(request.args.get('count', 100))

        tf_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
        }

        tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
        df = data_collector.get_rates(symbol, tf, count)

        if not df.empty:
            # 转换为 JSON 格式
            data = []
            for index, row in df.iterrows():
                data.append({
                    'time': index.strftime('%Y-%m-%d %H:%M:%S'),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['tick_volume']),
                })
            return jsonify(data)
        else:
            return jsonify({'error': '无法获取价格数据'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/indicators/<symbol>')
def get_indicators(symbol):
    """获取技术指标"""
    if not system_status['connected']:
        return jsonify({'error': '未连接到 MT5'})

    try:
        timeframe = request.args.get('timeframe', 'H1')
        count = int(request.args.get('count', 100))

        tf_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
        }

        tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
        df = data_collector.get_rates(symbol, tf, count)

        if df.empty:
            return jsonify({'error': '无法获取价格数据'})

        # 计算技术指标
        close = df['close']
        high = df['high']
        low = df['low']

        sma_20 = indicators.sma(close, 20)
        sma_50 = indicators.sma(close, 50)
        ema_12 = indicators.ema(close, 12)
        ema_26 = indicators.ema(close, 26)
        rsi = indicators.rsi(close, 14)
        macd, signal, histogram = indicators.macd(close)
        upper_bb, middle_bb, lower_bb = indicators.bollinger_bands(close)
        atr = indicators.atr(high, low, close)

        # 转换为 JSON 格式
        data = []
        for i in range(len(df)):
            data.append({
                'time': df.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                'close': float(close.iloc[i]),
                'sma_20': float(sma_20.iloc[i]) if not pd.isna(sma_20.iloc[i]) else None,
                'sma_50': float(sma_50.iloc[i]) if not pd.isna(sma_50.iloc[i]) else None,
                'ema_12': float(ema_12.iloc[i]) if not pd.isna(ema_12.iloc[i]) else None,
                'ema_26': float(ema_26.iloc[i]) if not pd.isna(ema_26.iloc[i]) else None,
                'rsi': float(rsi.iloc[i]) if not pd.isna(rsi.iloc[i]) else None,
                'macd': float(macd.iloc[i]) if not pd.isna(macd.iloc[i]) else None,
                'signal': float(signal.iloc[i]) if not pd.isna(signal.iloc[i]) else None,
                'histogram': float(histogram.iloc[i]) if not pd.isna(histogram.iloc[i]) else None,
                'upper_bb': float(upper_bb.iloc[i]) if not pd.isna(upper_bb.iloc[i]) else None,
                'middle_bb': float(middle_bb.iloc[i]) if not pd.isna(middle_bb.iloc[i]) else None,
                'lower_bb': float(lower_bb.iloc[i]) if not pd.isna(lower_bb.iloc[i]) else None,
                'atr': float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else None,
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/connect', methods=['POST'])
def connect_mt5():
    """连接到 MT5"""
    try:
        if data_collector.connect():
            system_status['connected'] = True
            system_status['last_update'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': '连接成功'})
        else:
            return jsonify({'success': False, 'message': '连接失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/disconnect', methods=['POST'])
def disconnect_mt5():
    """断开 MT5 连接"""
    try:
        data_collector.disconnect()
        system_status['connected'] = False
        return jsonify({'success': True, 'message': '已断开连接'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@socketio.on('connect')
def handle_connect():
    """WebSocket 连接"""
    logger.info(f"客户端连接: {request.sid}")
    emit('status', system_status)


@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket 断开"""
    logger.info(f"客户端断开: {request.sid}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """订阅数据"""
    symbol = data.get('symbol')
    logger.info(f"客户端 {request.sid} 订阅 {symbol}")
    emit('subscribed', {'symbol': symbol})


def broadcast_updates():
    """广播更新"""
    while True:
        if system_status['connected']:
            try:
                # 获取账户信息
                account_info = data_collector.get_account_info()
                if account_info:
                    socketio.emit('account', account_info)

                # 获取持仓信息
                positions = data_collector.get_positions()
                if positions:
                    socketio.emit('positions', positions)

                # 获取实时报价
                for symbol in SYMBOLS_CONFIG['enabled']:
                    tick = data_collector.get_tick(symbol)
                    if tick:
                        socketio.emit('tick', tick)

                system_status['last_update'] = datetime.now().isoformat()

            except Exception as e:
                logger.error(f"广播更新失败: {e}")

        socketio.sleep(MONITORING_CONFIG['check_interval'])


if __name__ == '__main__':
    logger.info("启动 MT5 顶配盯盘系统 Web 界面...")
    logger.info(f"访问地址: http://{WEB_CONFIG['host']}:{WEB_CONFIG['port']}")

    # 启动广播线程
    socketio.start_background_task(broadcast_updates)

    # 运行应用
    socketio.run(
        app,
        host=WEB_CONFIG['host'],
        port=WEB_CONFIG['port'],
        debug=WEB_CONFIG['debug']
    )