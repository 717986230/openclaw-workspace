# Karpathy-Inspired Claude Code Guidelines 学整合报告

## 概述

GitHub 仓库：`forrestchang/andrej-karpathy-skills`

这是一个关于 Karpathy-Inspired Claude Code Guidelines 的项目，提供了4个原则来减少 LLM 编码错误。

## 仓库内容

### 核心文件

#### CLAUDE.md
- **文件路径**: `main/CLAUDE.md`
- **内容**: Claude Code 行为指南
- **目的**: 减少 LLM 编码错误
- **原则**: 4 个核心原则

### 项目结构

```
forrestchang/andrej-karpathy-skills/
├── main/
│   ├── CLAUDE.md
│   ├── README.md
│   └── ...
└── ...
```

## 4 个核心原则

### 原则 1: Think Before Coding（编码前思考）

**核心思想**: 不要假设，不要隐藏困惑，明确权衡

#### 具体要求

- **明确假设**: 如果不确定，先问，不要猜测
- **多种解释**: 如果存在多种解释，都列出来，不要默默选择
- **权衡取舍**: 如果存在更简单的方法，说出来
- **停止困惑**: 如果不清楚，停止并说明困惑

#### 示例

**❌ 错误做法**:
```python
# 默假设用户想要一个列表，直接返回列表
def get_user_data():
    return [1, 2, 3]  # 假设用户想要列表
```

**✅ 正确做法**:
```python
# 明确假设，询问用户
def get_user_data():
    data_type = input("你想要什么类型的数据？(list/dict/string): ")
    if data_type == "list":
        return [1, 2, 3]
    elif data_type == "dict":
        return {"key": "value"}
    else:
        return "string"
```

### 原则 2: Simplicity First（简单第一）

**核心思想**: 最小化代码，只解决问题，不要过度设计

#### 具体要求

- **只实现需求**: 不要添加未请求的功能
- **不要过度抽象**: 不要为单次使用创建抽象
- **不要错误处理**: 不要为不可能的情况添加错误处理
- **简洁优先**: 如果 200 行代码可以是 50 行，重写它

#### 示例

**❌ 错误做法**:
```python
# 过度设计
class DataProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        self.validator = DataValidator()
        self.optimizer = DataOptimizer()
        # ... 更多抽象层

    def process(self, data: Dict) -> Dict:
        # 复杂的抽象
        validated = self.validator.validate(data)
        optimized = self.optimizer.optimize(validated)
        return optimized
```

**✅ 正确做法**:
```python
# 简单直接实现
def process_data(data: Dict) -> Dict:
    return data  # 直接返回，不需要验证和优化
```

### 原则 3: Surgical Changes（手术式修改）

**核心思想**: 只修改必要的代码，不要修改无关代码

#### 具体要求

- **不要改进相邻代码**: 不要修改相邻的代码、注释、格式
- **不要重构**: 不要重构未损坏的代码
- **不要删除死代码**: 除非你创建的，否则不要删除
- **匹配现有风格**: 即使你会用不同方式，也要匹配现有风格

#### 示例

**❌ 错误做法**:
```python
# 修改相邻代码
def process_data(data: Dict) -> Dict:
    # 修改了相邻的格式
    return data  # 修改了缩进
```

**✅ 正确做法**:
```python
def process_data(data: Dict) -> Dict:
    return data  # 保持原有缩进
```

### 原则 4: Goal-Driven Execution（目标驱动执行）

**核心思想**: 定义成功标准，循环验证

#### 具体要求

- **定义成功标准**: 明确成功的定义
- **循环验证**: 循环直到验证成功
- **多步骤任务**: 简要时先列出计划
- **强成功标准**: "让它工作"不够，需要验证标准

#### 示例

**❌ 错误做法**:
```python
# 添加功能验证
def add_validation(data: str) -> bool:
    # 添加验证
    try:
        validate(data)
        return True
    except:
        return False
```

**✅ 正确做法**:
```python
# 添加功能验证
def add_validation(data: str) -> bool:
    # 先写测试
    test_cases = [
        ("valid_input", "valid_data"),
        ("invalid_input", "invalid_data"),
        ("empty_input", ""),
    ]

    for test_name, test_data in test_cases:
        try:
            validate(test_data)
            print(f"{test_name}: PASS")
        except:
            print(f"{test_name}: FAIL")

    # 确保所有测试通过后再添加功能
    return all([validate(d) for _, d in test_cases])
```

## 与学整合

### 整合目标

将 Karpathy-Inspired Claude Code Guidelines 的 4 个原则整合到学习过程中。

### 整合方法

#### 1. 思考前检查清单

在开始编码前，先检查：

- [ ] 我理解需求了吗？
- [ ] 有多种解释吗？
- [ ] 有更简单的方法吗？
- [ ] 需要澄清吗？

#### 2. 简单性检查清单

在编码时检查：

- [ ] 这是最小实现吗？
- [ ] 有不必要的抽象吗？
- 有错误处理吗？
- 能用更少代码吗？

#### 3. 手术检查清单

在提交代码前检查：

- [ ] 只修改必要的代码
- [ ] 匹配现有风格
- 保留原有死代码
- 通过所有测试

#### 4. 成功标准检查

在完成任务后检查：

- [ ] 测试通过了吗？
- [ ] 验证成功了吗？
- 有副作用吗？
- 需要回滚吗？

### 整合示例

#### 示例 1: 思考前检查

**需求**: 添加用户数据验证功能

**❌ 错误做法**:
```python
# 直接实现验证功能
def validate_user_data(data: Dict) -> bool:
    if 'email' in data and '@' in data['email']:
        return True
    return False
```

**✅ 正确做法**:
```python
# 先思考
# 1. 需要验证什么？邮箱格式？用户名？域名？
# 2. 有多种解释吗？邮箱格式？用户名？域名？
# 3. 有更简单的方法吗？正则表达式？内置验证？
# 4. 需要澄清吗？需要支持哪些邮箱格式？

# 明确假设
email_regex = r'^[\\w\\.-]+@[\\w\\.-]+\\.[a-z]{2,}$'
phone_regex = r'^\\+?[0-9]+-\\s*[0-9]+$'

# 明确多种解释
if 'email' in data:
    # 邮箱格式验证
    if not re.match(email_regex, data['email']):
        return False
elif 'phone' in data:
    # 电话号码验证
    if not re.match(phone_regex, data['phone']):
        return False
else:
    # 其他类型验证
    return True

# 明确更简单的方法
import re
return bool(re.match(email_regex, data.get('email', '')))
```

#### 示例 2: 简单性检查

**需求**: 添加用户数据存储功能

**❌ 错误做法**:
```python
# 过度设计
class UserDataManager:
    def __init__(self):
        self.storage = {}
        self.cache = {}
        self.backup = BackupManager()
        self.validator = DataValidator()
        self.logger = logging.getLogger(__name__)

    def store(self, key: str, value: any):
        self.storage[key] = value
        self.cache[key] = value
        self.backup.backup(key, value)

    def retrieve(self, key: str) -> any:
        if key in self.storage:
            return self.storage[key]
        elif key in self.cache:
            return self.cache[key]
        else:
            return None
```

**✅ 正确做法**:
```python
# 简单直接实现
def store_data(key: str, value: any) -> bool:
    self.storage[key] = value
    return True

def retrieve_data(key: str) -> Optional[any]:
    return self.storage.get(key, None)
```

#### 示例 3: 手术检查

**需求**: 修改用户数据存储功能

**❌ 错误做法**:
```python
# 修改相邻代码
def store_data(key: str, value: any) -> bool:
    # 修改了缩进
    self.storage[key] = value  # 修改了缩进
    return True
```

**✅ 正确做法**:
```python
# 保持原有风格
def store_data(key: str, value: any) -> bool:
    self.storage[key] = value  # 保持原有缩进
    return True
```

#### 示例 4: 成功标准检查

**需求**: 添加用户数据删除功能

**❌ 错误做法**:
```python
# 添加功能验证
def delete_data(key: str) -> bool:
    try:
        del self.storage[key]
        return True
    except:
        return False
```

**✅ 正确做法**:
```python
# 先写测试
test_cases = [
    ("existing_key", "test_key"),
    ("non_existing_key", "test_key"),
    ("empty_key", ""),
]

for test_name, test_key in test_cases:
    try:
        delete_data(test_key)
        print(f"{test_name}: PASS")
    except:
        print(f"{test_name}: FAIL")

# 确保所有测试通过后再添加功能
return all([delete_data(k) for _, k in test_cases])
```

## 整合建议

### 1. 创建检查清单

创建 `checklist.md` 文件，包含：

```markdown
# 编码前检查清单

## 思考前检查
- [ ] 我理解需求了吗？
- [ ] 有多种解释吗？
- [ ] 有更简单的方法吗？
- [ ] 需要澄清吗？

## 简单性检查
- [ ] 这是最小实现吗？
- [ ] 有不必要的抽象吗？
- 有错误处理吗？
- 能用更少代码吗？

## 技术检查
- [ ] 只修改必要的代码
- [ ] 匹配现有风格
- 保留原有死代码
- 通过所有测试

## 成功标准
- [ ] 测试通过了吗？
- [ ] 验证成功了吗？
- 有副作用吗？
- 需要回滚吗？
```

### 2. 创建示例文件

创建 `examples/` 目录，包含：

```markdown
# 示例 1: 思考前检查

## 需求
添加用户数据验证功能

## 思考前检查
- 需要验证什么？邮箱格式？用户名？域名？
- 有多种解释吗？邮箱格式？用户名？域名？
- 有更简单的方法吗？正则表达式？内置验证？
- 需要澄清吗？需要支持哪些邮箱格式？

## 明确假设
email_regex = r'^[\\w\\.-]+@[\\w\\.-]+\\.[a-z]{2,}$'
phone_regex = r'^\\+?[0-9]+-\\s*[0-9]+$'

# 明确多种解释
if 'email' in data:
    # 邮箱格式验证
    if not re.match(email_regex, data['email']):
        return False
elif 'phone' in data:
    # 电话号码验证
    if not re.match(phone_regex, data['phone']):
        return False
else:
    # 其他类型验证
    return True

# 明确更简单的方法
import re
return bool(re.match(email_regex, data.get('email', '')))
```

### 3. 创建测试模板

创建 `tests/` 目录，包含：

```python
# 测试模板

import pytest

class TestUserData:
    def test_validate_email_valid(self):
        """测试有效邮箱"""
        data = {'email': 'test@example.com'}
        assert validate_user_data(data) == True

    def test_validate_email_invalid(self):
        """测试无效邮箱"""
        data = {'email': 'invalid-email'}
        assert validate_user_data(data) == False

    def test_validate_phone_valid(self):
        """测试有效电话"""
        data = {'phone': '+86113800138000'}
        assert validate_user_data(data) == True

    def test_validate_phone_invalid(self):
        """测试无效电话"""
        data = {'phone': '123'}
        assert validate_user_data(data) == False
```

### 4. 创建最佳实践文档

创建 `best_practices.md` 文档，包含：

```markdown
# 最佳实践

## 思考前
- 明确假设
- 多种解释
- 权衡取舍
- 停止困惑

## 简单性
- 最小实现
- 不要过度设计
- 不要错误处理
- 能用更少代码

## 手术检查
- 只修改必要的代码
- 匹配现有风格
- 保留原有死代码
- 通过所有测试

## 成功标准
- 测试通过
- 验证成功
- 无副作用
- 需要时回滚
```

### 5. 整合到学习流程

将 4 个原则整合到学习流程中：

#### 学习前
- 检查检查清单
- 理解示例
- 理解最佳实践

#### 学习中
- 遵循检查清单
- 参考示例
- 遵循最佳实践

#### 学习后
- 遵循检查清单
- 参考示例
- 遵循最佳实践

## 总结

通过整合 Karpathy-Inspired Claude Code Guidelines 的 4 个原则，可以显著提高 LLM 编码质量，减少错误，提高代码可维护性。

---

**整合时间**: 2026-04-20 19:55
**状态**: 整合指南已创建
**下一步**: 根据指南创建检查清单、示例文件、测试模板和最佳实践文档