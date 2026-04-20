# 通用测试规则

## 最佳实践

### 测试金字塔
- **单元测试 (70%)**: 测试独立函数和组件，快速反馈
- **集成测试 (20%)**: 测试模块间交互，验证协作
- **端到端测试 (10%)**: 测试完整用户流程，模拟真实场景

### 测试原则
1. **FIRST 原则**
   - Fast (快速): 测试应快速执行
   - Independent (独立): 测试之间不应有依赖
   - Repeatable (可重复): 任何环境下结果一致
   - Self-validating (自验证): 明确的通过/失败
   - Timely (及时): 与代码同步编写

2. **AAA 模式**
   - Arrange (准备): 设置测试数据和条件
   - Act (执行): 调用被测代码
   - Assert (断言): 验证结果

### 测试覆盖
- 核心业务逻辑: 100%
- 工具函数: 100%
- UI 组件: 关键路径覆盖
- 错误处理: 所有可能的失败路径

## 具体规则

### 命名规范
```
✅ test_<功能>_<场景>_<预期结果>
   test_login_invalidPassword_throwsException
   test_calculateDiscount_vipMember_returns20Percent

❌ test1(), testFunction(), testStuff()
```

### 测试结构
```markdown
✅ 每个测试文件对应一个源文件
   src/utils/calculator.ts → tests/utils/calculator.test.ts

✅ 测试描述使用自然语言
   describe('Calculator', () => {
     describe('add()', () => {
       it('should return sum of two numbers', () => {})
     })
   })

❌ 混乱的测试组织，测试之间有依赖
```

### 断言规范
```javascript
// ✅ 明确的断言消息
expect(result).toBe(42, 'Sum should equal 42')
expect(user).toBeDefined('User should exist after creation')

// ❌ 模糊的断言
expect(result).toBeTruthy()
```

## 示例

### 单元测试示例
```javascript
describe('PasswordValidator', () => {
  let validator;

  beforeEach(() => {
    validator = new PasswordValidator();
  });

  describe('validate()', () => {
    it('should return valid for strong password', () => {
      // Arrange
      const password = 'StrongP@ss123';

      // Act
      const result = validator.validate(password);

      // Assert
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should return errors for weak password', () => {
      // Arrange
      const password = 'weak';

      // Act
      const result = validator.validate(password);

      // Assert
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters');
    });
  });
});
```

### Mock 示例
```javascript
// ✅ 正确使用 Mock
jest.mock('../api/userService');
const userService = require('../api/userService');

it('should fetch user data', async () => {
  userService.getUser.mockResolvedValue({ id: 1, name: 'Test' });
  
  const result = await fetchUser(1);
  
  expect(userService.getUser).toHaveBeenCalledWith(1);
  expect(result.name).toBe('Test');
});

// ❌ 调用真实服务
it('should work with real API', async () => {
  const result = await fetchUser(1); // 实际调用 API
});
```

### 边界测试示例
```javascript
describe('divide()', () => {
  it('should handle normal division', () => {
    expect(divide(10, 2)).toBe(5);
  });

  it('should handle division by zero', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('should handle negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  it('should handle floating point', () => {
    expect(divide(10, 3)).toBeCloseTo(3.333, 2);
  });
});
```

## 反例

### 测试反模式
```javascript
// ❌ 测试之间有依赖
let sharedState;

it('test1', () => {
  sharedState = { value: 1 };
});

it('test2', () => {
  expect(sharedState.value).toBe(1); // 依赖 test1
});

// ❌ 测试实现细节
it('should call internal method', () => {
  const obj = new MyClass();
  obj.process();
  expect(obj._internalCounter).toBe(1); // 测试私有变量
});

// ❌ 不稳定的测试
it('should work sometimes', () => {
  if (Math.random() > 0.5) {
    expect(true).toBe(true);
  }
});
```

### 异步测试反模式
```javascript
// ❌ 忘记 await
it('should fetch data', () => {
  fetchData().then(data => {
    expect(data).toBeDefined(); // 不会执行
  });
});

// ✅ 正确处理
it('should fetch data', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});
```

## 工具和资源

### 测试框架
- **JavaScript/TypeScript**: Jest, Vitest, Mocha
- **Python**: pytest, unittest, nose2
- **通用**: assertion libraries, test runners

### 覆盖率工具
- **Istanbul/nyc**: JavaScript 覆盖率
- **Coverage.py**: Python 覆盖率
- **JaCoCo**: Java 覆盖率

### Mock 工具
- **Jest Mocks**: 内置 mock 功能
- **Sinon**: 独立 mock 库
- **unittest.mock**: Python mock 库

### CI/CD 集成
```yaml
# GitHub Actions 示例
- name: Run tests
  run: npm test

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/coverage-final.json
```

### 测试报告
- **Jest HTML Reporter**: 可视化测试报告
- **Allure**: 多框架测试报告
- **Mochawesome**: Mocha 报告生成器

### 学习资源
- [Testing JavaScript](https://testingjavascript.com/)
- [Python Testing](https://docs.pytest.org/)
- [Google Testing Blog](https://testing.googleblog.com/)
