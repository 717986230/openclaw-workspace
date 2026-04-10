"""
API 中转服务
功能：接收前端请求，转发到目标API，返回响应
"""
from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# 配置
DEFAULT_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRY = 2         # 重试次数

@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy():
    """通用代理接口"""
    # 获取目标URL
    target_url = request.args.get('url') or request.headers.get('X-Target-URL')
    
    if not target_url:
        return jsonify({
            'error': 'Missing target URL',
            'hint': 'Add ?url= or X-Target-URL header'
        }), 400
    
    # 获取请求头和body
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    headers.pop('X-Target-URL', None)
    
    data = request.get_data()
    
    # 转发请求
    for attempt in range(MAX_RETRY + 1):
        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=data,
                params=request.args,
                timeout=DEFAULT_TIMEOUT,
                allow_redirects=False
            )
            
            # 返回响应
            return resp.content, resp.status_code, dict(resp.headers)
            
        except requests.exceptions.Timeout:
            if attempt == MAX_RETRY:
                return jsonify({'error': 'Request timeout'}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 502
    
    return jsonify({'error': 'Max retries exceeded'}), 502


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        'name': 'API Proxy Service',
        'endpoints': {
            '/proxy': '转发请求 (?url=)',
            '/health': '健康检查'
        }
    })


if __name__ == '__main__':
    print("🚀 API 中转服务启动: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)