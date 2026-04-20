# Python 安全规则

## 最佳实践

### 安全原则
1. **最小权限原则**: 只授予必要的权限
2. **纵深防御**: 多层安全措施
3. **输入验证**: 永远不信任外部输入
4. **安全默认**: 默认配置应该是最安全的

### OWASP Top 10 防护
- 注入攻击防护
- 身份认证安全
- 敏感数据保护
- 访问控制
- 安全配置

## 具体规则

### SQL 注入防护
```python
# ✅ 使用参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ✅ 使用 ORM
user = User.query.filter_by(id=user_id).first()

# ❌ 字符串拼接 SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ❌ 格式化字符串
cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)
```

### 命令注入防护
```python
import subprocess
import shlex

# ✅ 使用列表参数
subprocess.run(["ls", "-l", user_input], check=True)

# ✅ 使用 shlex.quote 转义
subprocess.run(f"ls -l {shlex.quote(user_input)}", shell=True, check=True)

# ❌ 直接拼接命令
subprocess.run(f"ls -l {user_input}", shell=True)  # 危险！
```

### 路径遍历防护
```python
import os
from pathlib import Path

# ✅ 安全的路径处理
def safe_path(base_dir, filename):
    base = Path(base_dir).resolve()
    target = (base / filename).resolve()
    
    if not str(target).startswith(str(base)):
        raise ValueError("Invalid path")
    return target

# ✅ 验证文件扩展名
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.png'}
if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
    raise ValueError("Invalid file type")

# ❌ 直接使用用户输入
with open(f"/uploads/{filename}", 'r') as f:  # 可能路径遍历
    content = f.read()
```

### 输入验证
```python
from pydantic import BaseModel, validator, constr

# ✅ 使用 Pydantic 验证
class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: constr(max_length=100)
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()

# ✅ 使用正则验证
import re
if not re.match(r'^[a-zA-Z0-9_]+$', username):
    raise ValueError("Invalid username")

# ❌ 未验证直接使用
user_input = request.form['data']
process(user_input)  # 危险！
```

### 敏感数据处理
```python
import os
from dotenv import load_dotenv

# ✅ 使用环境变量
load_dotenv()
API_KEY = os.environ.get('API_KEY')

# ✅ 使用 secrets 模块
import secrets
token = secrets.token_urlsafe(32)

# ❌ 硬编码敏感信息
API_KEY = "sk-1234567890abcdef"  # 绝对禁止！

# ✅ 日志脱敏
import logging
logging.basicConfig(level=logging.INFO)

def log_user(user):
    safe_user = {**user, 'password': '***REDACTED***'}
    logging.info(f"User data: {safe_user}")

# ❌ 记录敏感信息
logging.info(f"User password: {password}")
```

### 密码安全
```python
from passlib.context import CryptContext

# ✅ 使用安全的哈希算法
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto"
)

# 哈希密码
hashed = pwd_context.hash(password)

# 验证密码
if pwd_context.verify(plain_password, hashed):
    print("Password correct")

# ❌ 使用弱哈希
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()  # 危险！
```

### HTTPS 和 SSL
```python
import ssl
import urllib.request

# ✅ 强制 SSL 验证
context = ssl.create_default_context()
with urllib.request.urlopen(url, context=context) as response:
    data = response.read()

# ❌ 禁用 SSL 验证
context = ssl._create_unverified_context()  # 危险！

# ✅ 使用 requests 的 verify
import requests
response = requests.get(url, verify=True)  # 默认为 True

# ❌ 禁用验证
response = requests.get(url, verify=False)  # 危险！
```

## 示例

### 完整的用户认证示例
```python
from passlib.context import CryptContext
from pydantic import BaseModel, validator, constr
import secrets
import time

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: constr(max_length=100)
    password: constr(min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

def create_user(user_data: UserCreate):
    """安全创建用户"""
    # 哈希密码
    hashed_password = pwd_context.hash(user_data.password)
    
    # 存储到数据库（伪代码）
    user = {
        'username': user_data.username,
        'email': user_data.email.lower(),
        'password': hashed_password,
        'created_at': time.time()
    }
    db.insert(user)
    return user

def authenticate_user(username: str, password: str) -> dict | None:
    """验证用户登录"""
    user = db.find_by_username(username)
    if not user:
        return None
    
    if pwd_context.verify(password, user['password']):
        # 生成会话令牌
        token = secrets.token_urlsafe(32)
        return {'user': user, 'token': token}
    return None
```

### 安全的文件上传示例
```python
import os
from pathlib import Path
import magic
import hashlib

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = Path('/uploads')

def secure_upload(file_data: bytes, filename: str) -> str:
    """安全文件上传"""
    # 检查文件大小
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError('File too large')
    
    # 验证 MIME 类型
    mime = magic.from_buffer(file_data, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f'File type {mime} not allowed')
    
    # 生成安全文件名
    file_hash = hashlib.sha256(file_data).hexdigest()[:16]
    ext = Path(filename).suffix.lower()
    safe_filename = f"{file_hash}{ext}"
    
    # 确保路径安全
    file_path = (UPLOAD_DIR / safe_filename).resolve()
    if not str(file_path).startswith(str(UPLOAD_DIR.resolve())):
        raise ValueError('Invalid path')
    
    # 写入文件
    file_path.write_bytes(file_data)
    return str(file_path)
```

## 反例

### 常见安全漏洞
```python
# ❌ 硬编码凭证
DB_PASSWORD = "admin123"

# ❌ 使用不安全的随机数
import random
token = str(random.random())  # 不安全！

# ❌ eval 用户输入
data = eval(user_input)  # 代码注入！

# ❌ pickle 不信任数据
import pickle
data = pickle.loads(untrusted_data)  # 反序列化攻击！

# ❌ 不处理异常泄露信息
try:
    process()
except Exception as e:
    print(f"Error: {e}")  # 可能泄露敏感信息
```

### SSRF 防护
```python
import requests
from urllib.parse import urlparse

# ✅ 验证 URL
BLOCKED_DOMAINS = {'localhost', '127.0.0.1', '169.254.169.254'}

def safe_request(url: str):
    parsed = urlparse(url)
    if parsed.hostname in BLOCKED_DOMAINS:
        raise ValueError('Blocked domain')
    if parsed.scheme not in {'http', 'https'}:
        raise ValueError('Invalid scheme')
    return requests.get(url, timeout=5)

# ❌ 无验证请求
response = requests.get(user_provided_url)  # SSRF 风险！
```

## 工具和资源

### 安全检查工具
- **Bandit**: Python 安全代码检查
- **Safety**: 检查依赖漏洞
- **pip-audit**: 依赖安全审计
- **Semgrep**: 代码安全扫描

### 密码学库
- **cryptography**: 标准加密库
- **passlib**: 密码哈希
- **PyJWT**: JWT 处理
- **python-secrets**: 安全随机数

### 框架安全
- **Flask-Login**: 用户会话管理
- **Flask-Talisman**: HTTPS 和安全头
- **django-axes**: 登录失败保护
- **FastAPI Security**: 内置安全工具

### 安全头配置
```python
# Flask 示例
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", 'https://cdn.example.com']
    }
)
```

### 学习资源
- [OWASP Python Security](https://github.com/OWASP/owasp-python-security)
- [Python Security Best Practices](https://python.org/doc/security/)
- [CWE/SANS Top 25](https://www.sans.org/top25-software-errors/)
- [Bandit Documentation](https://bandit.readics.com/)