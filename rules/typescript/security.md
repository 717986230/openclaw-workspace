# TypeScript 安全规则

## 最佳实践

### 安全原则
1. **类型安全**: 利用 TypeScript 类型系统防止常见错误
2. **输入验证**: 运行时验证所有外部输入
3. **最小权限**: 只授予必要的权限
4. **安全默认**: 默认配置应该是最安全的

### 常见威胁防护
- XSS（跨站脚本攻击）
- CSRF（跨站请求伪造）
- 注入攻击
- 敏感数据泄露
- 依赖漏洞

## 具体规则

### 类型安全
```typescript
// ✅ 严格模式 tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true
  }
}

// ✅ 使用类型守卫
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' 
    && obj !== null
    && 'id' in obj 
    && 'name' in obj;
}

function processUser(data: unknown) {
  if (isUser(data)) {
    console.log(data.name); // 类型安全
  }
}

// ❌ 使用 any
function process(data: any) {
  console.log(data.name); // 不安全
}

// ✅ 使用 unknown
function safeProcess(data: unknown) {
  if (typeof data === 'object' && data !== null && 'name' in data) {
    console.log((data as { name: string }).name);
  }
}
```

### XSS 防护
```typescript
// ✅ 使用安全的框架自动转义
// React 自动转义
const Component = ({ name }: { name: string }) => (
  <div>{name}</div>  // 安全
);

// ✅ 明确使用 textContent
element.textContent = userInput;  // 安全

// ✅ 使用 DOMPurify 清理 HTML
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
element.innerHTML = clean;

// ❌ 直接使用 innerHTML
element.innerHTML = userInput;  // XSS 风险！

// ❌ 使用 dangerouslySetInnerHTML 未清理
const Component = ({ html }: { html: string }) => (
  <div dangerouslySetInnerHTML={{ __html: html }} />  // 危险！
);

// ✅ 使用 URL 验证
function safeRedirect(url: string) {
  const allowedOrigins = ['https://example.com', 'https://app.example.com'];
  try {
    const parsed = new URL(url, window.location.origin);
    if (allowedOrigins.includes(parsed.origin)) {
      window.location.href = parsed.href;
    }
  } catch {
    console.error('Invalid URL');
  }
}

// ❌ 直接重定向
window.location.href = userInput;  // 开放重定向！
```

### SQL 注入防护
```typescript
// ✅ 使用参数化查询（使用 ORM）
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

const user = await prisma.user.findUnique({
  where: { id: userId }
});

// ✅ 使用 TypeORM
const user = await userRepository.findOne({ 
  where: { id: userId } 
});

// ✅ 使用参数化查询
const result = await db.query(
  'SELECT * FROM users WHERE id = $1',
  [userId]
);

// ❌ 字符串拼接
const query = `SELECT * FROM users WHERE id = ${userId}`;  // 危险！
await db.query(query);
```

### 输入验证
```typescript
import { z } from 'zod';

// ✅ 使用 Zod 运行时验证
const UserSchema = z.object({
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username too long')
    .regex(/^[a-zA-Z0-9_]+$/, 'Invalid username format'),
  email: z.string()
    .email('Invalid email')
    .max(100),
  age: z.number()
    .int()
    .min(0)
    .max(150),
  role: z.enum(['user', 'admin']).default('user')
});

type User = z.infer<typeof UserSchema>;

function createUser(data: unknown): User {
  return UserSchema.parse(data);  // 验证失败会抛出错误
}

// ✅ 使用 class-validator
import { IsEmail, IsString, MinLength, MaxLength, Matches } from 'class-validator';

class CreateUserDto {
  @IsString()
  @MinLength(3)
  @MaxLength(50)
  @Matches(/^[a-zA-Z0-9_]+$/)
  username: string;

  @IsEmail()
  email: string;
}

// ❌ 未验证直接使用
function processUser(body: any) {
  saveToDatabase(body);  // 不安全！
}
```

### 敏感数据处理
```typescript
// ✅ 使用环境变量
import { config } from 'dotenv';
config();

const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  throw new Error('API_KEY not set');
}

// ✅ 类型安全的环境变量
interface EnvConfig {
  API_KEY: string;
  DATABASE_URL: string;
  JWT_SECRET: string;
}

function getEnv(): EnvConfig {
  const API_KEY = process.env.API_KEY;
  const DATABASE_URL = process.env.DATABASE_URL;
  const JWT_SECRET = process.env.JWT_SECRET;

  if (!API_KEY || !DATABASE_URL || !JWT_SECRET) {
    throw new Error('Missing required environment variables');
  }

  return { API_KEY, DATABASE_URL, JWT_SECRET };
}

// ❌ 硬编码敏感信息
const API_KEY = 'sk-1234567890';  // 绝对禁止！

// ✅ 日志脱敏
const sensitiveFields = ['password', 'token', 'secret', 'apiKey'];

function sanitizeLog(data: Record<string, unknown>): Record<string, unknown> {
  const sanitized = { ...data };
  for (const field of sensitiveFields) {
    if (field in sanitized) {
      sanitized[field] = '[REDACTED]';
    }
  }
  return sanitized;
}

logger.info('User data', sanitizeLog(user));

// ❌ 记录敏感信息
logger.info('User password', { password });  // 危险！
```

### CSRF 防护
```typescript
// ✅ Express 中使用 CSRF 中间件
import csrf from 'csurf';
const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/process', csrfProtection, (req, res) => {
  // CSRF token 已验证
});

// ✅ 使用 SameSite Cookie
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    httpOnly: true,
    secure: true,
    sameSite: 'strict'  // 或 'lax'
  }
}));

// ✅ 前端发送 CSRF token
const response = await fetch('/api/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify(data)
});
```

### 密码安全
```typescript
import bcrypt from 'bcrypt';
import { randomBytes } from 'crypto';

const SALT_ROUNDS = 12;

// ✅ 安全哈希密码
async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

// ✅ 安全验证密码
async function verifyPassword(
  password: string, 
  hashedPassword: string
): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword);
}

// ✅ 生成安全令牌
function generateToken(): string {
  return randomBytes(32).toString('hex');
}

// ❌ 使用弱哈希
import { createHash } from 'crypto';
const hashed = createHash('md5').update(password).digest('hex');  // 危险！

// ❌ 明文存储密码
await db.users.insert({ username, password });  // 绝对禁止！
```

## 示例

### 完整的认证中间件
```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

interface JwtPayload {
  userId: string;
  role: 'user' | 'admin';
}

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

const JWT_SECRET = process.env.JWT_SECRET!;
if (!JWT_SECRET) {
  throw new Error('JWT_SECRET must be set');
}

export function authMiddleware(
  req: Request, 
  res: Response, 
  next: NextFunction
): void {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'No token provided' });
    return;
  }

  const token = authHeader.substring(7);
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as JwtPayload;
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

export function requireRole(role: 'user' | 'admin') {
  return (req: Request, res: Response, next: NextFunction): void {
    if (req.user?.role !== role) {
      res.status(403).json({ error: 'Forbidden' });
      return;
    }
    next();
  };
}

// 使用
app.get('/admin', authMiddleware, requireRole('admin'), (req, res) => {
  res.json({ message: 'Admin only content' });
});
```

### 安全的 API 路由
```typescript
import { Router } from 'express';
import { z } from 'zod';
import rateLimit from 'express-rate-limit';

const router = Router();

// 速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 分钟
  max: 100,  // 最多 100 请求
  message: 'Too many requests'
});

// 验证 schema
const UpdateUserSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  email: z.string().email().optional()
});

router.put('/users/:id', limiter, authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    // 验证 ID 格式
    if (!/^[a-zA-Z0-9-]+$/.test(id)) {
      return res.status(400).json({ error: 'Invalid ID format' });
    }

    // 授权检查
    if (req.user?.userId !== id && req.user?.role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden' });
    }

    // 验证请求体
    const updateData = UpdateUserSchema.parse(req.body);

    // 更新数据库
    const user = await db.users.update(id, updateData);
    
    // 返回脱敏数据
    const { password, ...safeUser } = user;
    res.json(safeUser);
  } catch (error) {
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: error.errors });
    } else {
      console.error('Update error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});
```

## 反例

### 常见安全漏洞
```typescript
// ❌ 硬编码凭证
const DB_PASSWORD = 'password123';

// ❌ 不安全的随机数
const token = Math.random().toString(36);  // 不安全！

// ❌ eval 用户输入
const result = eval(userInput);  // 代码注入！

// ❌ 原型污染
Object.assign(obj, userInput);  // 可能原型污染！

// ❌ SQL 注入
const query = `SELECT * FROM users WHERE name = '${name}'`;

// ❌ 不安全的正则
const regex = new RegExp(userInput);  // ReDoS 风险！

// ❌ 不处理错误导致信息泄露
try {
  process();
} catch (error) {
  res.json({ error: error.message });  // 可能泄露敏感信息
}

// ✅ 安全的错误处理
catch (error) {
  console.error('Process error:', error);
  res.status(500).json({ error: 'Internal server error' });
}
```

## 工具和资源

### 安全检查工具
- **ESLint Security Plugin**: 代码安全检查
- **npm audit**: 依赖漏洞扫描
- **Snyk**: 安全漏洞监控
- **SonarQube**: 代码质量和安全分析

### 类型验证库
- **Zod**: TypeScript 优先的 schema 验证
- **class-validator**: 装饰器验证
- **io-ts**: 运行时类型检查
- **yup**: Schema 验证

### 安全中间件
- **helmet**: 安全 HTTP 头
- **cors**: CORS 配置
- **express-rate-limit**: 速率限制
- **hpp**: HTTP 参数污染防护

### 安全头配置
```typescript
import helmet from 'helmet';

app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", 'https://cdn.example.com'],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'", 'https://api.example.com'],
    fontSrc: ["'self'", 'https://fonts.gstatic.com'],
    objectSrc: ["'none'"],
    frameSrc: ["'none'"],
    baseUri: ["'self'"],
    formAction: ["'self'"],
    frameAncestors: ["'none'"]
  }
}));
```

### 依赖安全
```bash
# 检查漏洞
npm audit

# 自动修复
npm audit fix

# 检查过期依赖
npm outdated

# 使用 lockfile
# 确保 package-lock.json 提交到版本控制
```

### 学习资源
- [OWASP Node.js Security](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [TypeScript Security Best Practices](https://typescript-security.readthedocs.io/)
- [Node.js Security Guide](https://nodejs.org/en/docs/guides/security/)
- [Snyk Learn](https://learn.snyk.io/)
