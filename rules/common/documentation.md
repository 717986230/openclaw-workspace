# 通用文档规则

## 最佳实践

### 文档层次结构
1. **项目级**: README.md, CHANGELOG.md, CONTRIBUTING.md
2. **模块级**: 各模块的 README, 架构说明
3. **代码级**: 内联注释, JSDoc/Docstring
4. **API 级**: OpenAPI/Swagger, GraphQL Schema

### 文档原则
- **及时更新**: 代码变更时同步更新文档
- **简洁明了**: 避免冗余，直达要点
- **示例驱动**: 提供可运行的代码示例
- **版本控制**: 文档与代码同仓库管理

## 具体规则

### README 结构
```markdown
✅ 标准项目 README 结构

# 项目名称

简短描述，一句话说明项目用途。

## 功能特性

- 功能 1
- 功能 2

## 快速开始

### 安装
```bash
npm install project-name
```

### 基本使用
```javascript
const project = require('project-name');
project.doSomething();
```

## 文档

详细文档链接。

## 贡献

贡献指南链接。

## 许可证

MIT
```

### 代码注释规范
```javascript
// ✅ 解释为什么，而不是做什么
// 使用二分查找优化性能，因为数据已排序
function findUser(sortedUsers, id) { ... }

// ❌ 仅重复代码内容
// 遍历数组
for (const user of users) { ... }

// ✅ TODO 注释格式
// TODO(username): 简短描述 - 关联的 issue/PR
// FIXME(username): 描述问题和解决方案
// HACK(username): 临时解决方案，需要后续改进
```

### JSDoc/Docstring 格式
```javascript
/**
 * 计算两个日期之间的天数差
 * 
 * @param {Date} startDate - 开始日期
 * @param {Date} endDate - 结束日期
 * @returns {number} 天数差（正数表示 endDate 在 startDate 之后）
 * @throws {Error} 当参数不是有效日期时抛出
 * 
 * @example
 * const diff = daysBetween(new Date('2024-01-01'), new Date('2024-01-10'));
 * // 返回 9
 */
function daysBetween(startDate, endDate) {
  // 实现
}
```

```python
def calculate_discount(price: float, membership_level: str) -> float:
    """
    根据会员等级计算折扣价格。

    Args:
        price: 原始价格，必须大于 0
        membership_level: 会员等级，可选值: 'bronze', 'silver', 'gold'

    Returns:
        折扣后的价格

    Raises:
        ValueError: 当价格小于等于 0 或会员等级无效时

    Example:
        >>> calculate_discount(100, 'gold')
        80.0
    """
    # 实现
```

### API 文档规范
```yaml
# ✅ OpenAPI 规范示例
openapi: 3.0.0
paths:
  /users/{id}:
    get:
      summary: 获取用户信息
      description: 根据用户 ID 获取详细用户信息
      operationId: getUserById
      parameters:
        - name: id
          in: path
          required: true
          description: 用户唯一标识
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 成功返回用户信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: 用户不存在
```

## 示例

### 变更日志格式
```markdown
# Changelog

## [2.1.0] - 2024-01-15

### Added
- 新增批量导出功能
- 支持 PostgreSQL 数据库

### Changed
- 重构用户认证模块，性能提升 50%

### Fixed
- 修复登录页面样式错乱问题 (#123)

### Deprecated
- 旧版 API v1 将在 3.0 版本移除

### Security
- 升级依赖库修复 CVE-2024-XXXX
```

### 架构文档
```markdown
# 系统架构

## 概述

本系统采用微服务架构，主要包含以下组件：

## 组件图

\`\`\`
┌─────────────┐     ┌─────────────┐
│   Gateway   │────▶│  Auth Svc   │
└─────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│   Web App   │     │  User Svc   │
└─────────────┘     └─────────────┘
\`\`\`

## 数据流

1. 用户请求经过 Gateway 认证
2. 认证通过后路由到对应服务
3. 服务处理后返回响应
```

### 内联注释示例
```javascript
// ✅ 好的注释
// 限制并发请求以避免触发 API 速率限制
// 参考: https://api.example.com/docs/rate-limits
const MAX_CONCURRENT = 5;

// ❌ 多余的注释
// 定义变量 i
let i = 0;

// ✅ 解释复杂逻辑
// 使用幂等键确保重试不会创建重复订单
// 幂等键格式: order_{userId}_{timestamp}_{checksum}
const idempotencyKey = generateIdempotencyKey(userId);

// ✅ 警告注释
// WARNING: 此方法直接操作数据库，跳过缓存
// 仅在批量导入场景使用
async function directInsert(records) { ... }
```

## 反例

### 文档反模式
```markdown
❌ 过时文档

# 安装
运行 setup.exe（注：已废弃，请使用 Docker）

❌ 无示例文档

## 使用方法
调用 process() 方法处理数据。

（没有具体示例）

❌ 过度注释

/**
 * 获取用户
 * 
 * @returns 用户
 */
function getUser() {
  return user; // 返回用户
}
```

### README 反模式
```markdown
❌ 缺失关键信息

# 我的项目

这是我写的项目。

❌ 安装说明不完整

## 安装
npm install

（缺少前置依赖、环境要求）

❌ 没有使用示例

## 功能
- 处理文件
- 生成报告

（没有展示如何使用）
```

## 工具和资源

### 文档生成工具
- **JSDoc**: JavaScript 文档生成
- **Sphinx**: Python 文档生成
- **TypeDoc**: TypeScript 文档生成
- **Swagger UI**: API 文档可视化

### 文档风格指南
- **Google Developer Documentation Style Guide**
- **Microsoft Writing Style Guide**
- **Write the Docs** 社区指南

### Markdown 工具
- **Markdownlint**: Markdown 格式检查
- **mdBook**: 生成文档网站
- **Docsify**: 动态文档网站

### 图表工具
- **Mermaid**: Markdown 内嵌图表
- **PlantUML**: UML 图生成
- **Draw.io**: 可视化图表编辑

### 检查清单
- [ ] README 完整（安装、使用、贡献）
- [ ] API 文档覆盖所有公开接口
- [ ] 代码注释解释复杂逻辑
- [ ] 变更日志记录重要变更
- [ ] 示例代码可运行
- [ ] 文档与代码版本一致

### 学习资源
- [Write the Docs](https://www.writethedocs.org/)
- [Documentation Guide](https://www.docslikecode.com/)
- [Google Technical Writing](https://developers.google.com/tech-writing)
