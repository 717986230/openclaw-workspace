# 自动化代码审查修复流水线

## 功能

这个自动化流水线可以：
1. 监控指定PR的代码审查反馈
2. 自动识别需要修复的问题
3. 自动修复问题
4. 自动提交和推送
5. 自动更新PR

## 使用方法

### 启动自动化流水线

```bash
# Windows
scripts\start-auto-fix.bat

# 或者直接运行
node scripts\auto-fix-code-review-v2.js
```

### 配置

编辑 `scripts/auto-fix-code-review-v2.js` 中的配置：

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
};
```

## 支持的自动修复

目前支持以下类型的自动修复：

1. **导出问题** - 自动添加 `export` 关键字
2. **冗余代码** - 自动移除冗余的代码
3. **空字符串问题** - 自动修复空字符串处理
4. **规范化问题** - 自动修复ID规范化

## 日志

所有操作都会记录到 `auto-fix-log.txt` 文件中。

## 停止

按 `Ctrl+C` 停止自动化流水线。

## 注意事项

1. 确保已安装 Node.js
2. 确保已配置 GitHub CLI (`gh`)
3. 确保已配置 Git 认证
4. 确保网络连接正常
5. 确保代理设置正确（脚本会自动禁用代理）

## 扩展

如需添加新的自动修复类型，在 `autoFix()` 函数中添加新的条件分支即可。
