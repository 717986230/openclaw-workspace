# 自动化代码审查修复流水线 - 完整文档

## 📋 概述

这是一个自动化代码审查修复流水线，可以自动监控PR的代码审查反馈，识别需要修复的问题，自动修复，并提交PR。

## 🚀 功能

### 核心功能

1. **自动监控** - 定期检查指定PR的代码审查反馈
2. **智能识别** - 自动分析评论，提取需要修复的问题
3. **自动修复** - 根据问题类型自动修复代码
4. **自动提交** - 自动提交修复并推送到远程
5. **自动创建PR** - 自动创建或更新PR

### 支持的自动修复类型

1. **导出问题** - 自动添加 `export` 关键字
2. **冗余代码** - 自动移除冗余的代码
3. **空字符串问题** - 自动修复空字符串处理
4. **规范化问题** - 自动修复ID规范化

## 📦 文件结构

```
scripts/
├── auto-fix-code-review.js          # v1 - 基础版本
├── auto-fix-code-review-v2.js       # v2 - 增强版本
├── auto-fix-code-review-v3.js       # v3 - 完整版本（推荐）
├── start-auto-fix.bat                # v1 启动脚本
├── start-auto-fix-v3.bat             # v3 启动脚本（推荐）
└── AUTO_FIX_README.md               # 使用文档
```

## 🎯 使用方法

### 快速开始

```bash
# Windows - 使用推荐版本
scripts\start-auto-fix-v3.bat

# 或者直接运行
node scripts\auto-fix-code-review-v3.js
```

### 配置

编辑 `scripts/auto-fix-code-review-v3.js` 中的配置：

```javascript
const CONFIG = {
  owner: 'openclaw',
  repo: 'openclaw',
  prNumbers: [65669, 65675], // 要监控的PR编号
  branches: {
    65669: 'feature/cron-add-custom-id',
    65675: 'docs/avatar-size-limit',
  },
  checkInterval: 5 * 60 * 1000, // 5分钟检查一次
  logFile: path.join(process.cwd(), 'auto-fix-log.txt'),
  autoCreatePR: true, // 自动创建PR
};
```

## 🔧 工作流程

1. **启动** - 运行启动脚本
2. **监控** - 每5分钟检查一次PR的代码审查反馈
3. **识别** - 分析评论，提取需要修复的问题
4. **修复** - 根据问题类型自动修复代码
5. **提交** - 自动提交修复并推送到远程
6. **创建PR** - 自动创建或更新PR
7. **循环** - 继续监控，直到手动停止

## 📊 日志

所有操作都会记录到 `auto-fix-log.txt` 文件中，包括：

- 检查时间
- 发现的问题
- 修复的操作
- 提交的信息
- 推送的结果

## 🛑 停止

按 `Ctrl+C` 停止自动化流水线。

## ⚙️ 系统要求

1. **Node.js** - 版本 14 或更高
2. **GitHub CLI** - 已安装并配置 (`gh`)
3. **Git** - 已安装并配置
4. **网络连接** - 稳定的网络连接
5. **代理设置** - 脚本会自动禁用代理

## 🔍 扩展

### 添加新的自动修复类型

在 `autoFix()` 函数中添加新的条件分支：

```javascript
function autoFix(issue) {
  const title = issue.title.toLowerCase();

  if (title.includes('export')) {
    return fixExportIssue(issue);
  } else if (title.includes('your-new-issue')) {
    return fixYourNewIssue(issue); // 添加新的修复函数
  } else {
    log(`无法自动修复: ${issue.title}`, colors.yellow);
    return false;
  }
}
```

### 实现新的修复函数

```javascript
function fixYourNewIssue(issue) {
  try {
    const filePath = issue.path;
    const content = fs.readFileSync(filePath, 'utf-8');

    // 实现你的修复逻辑
    const newContent = content.replace(
      /old-pattern/,
      'new-pattern'
    );

    if (newContent !== content) {
      fs.writeFileSync(filePath, newContent, 'utf-8');
      log('修复成功', colors.green);
      return true;
    }

    log('没有找到需要修复的问题', colors.yellow);
    return false;
  } catch (error) {
    log(`修复失败: ${error.message}`, colors.red);
    return false;
  }
}
```

## 📝 注意事项

1. **测试** - 在使用前，先在测试分支上测试
2. **备份** - 确保代码已提交或备份
3. **监控** - 定期检查日志文件
4. **网络** - 确保网络连接稳定
5. **权限** - 确保有足够的权限推送代码

## 🎉 优势

1. **自动化** - 无需手动干预
2. **高效** - 快速修复问题
3. **准确** - 基于代码审查反馈
4. **可扩展** - 易于添加新的修复类型
5. **可追踪** - 完整的日志记录

## 📞 支持

如有问题，请查看日志文件 `auto-fix-log.txt`。

## 🔄 版本历史

- **v1** - 基础版本
- **v2** - 增强版本，添加更多自动修复类型
- **v3** - 完整版本，添加自动创建PR功能

## 📄 许可

MIT License
