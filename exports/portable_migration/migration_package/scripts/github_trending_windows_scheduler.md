# GitHub Trending 每日自动化 - Windows 任务计划配置

## 方法 1: 使用任务计划程序 (Task Scheduler)

### 创建每日任务

1. 打开任务计划程序
   - 按 `Win + R`，输入 `taskschd.msc`，回车

2. 创建基本任务
   - 点击右侧 "创建基本任务"
   - 名称: `GitHub Trending Daily Scan`
   - 描述: `每日扫描 GitHub Trending 项目并寻找贡献机会`

3. 触发器
   - 选择 "每天"
   - 开始时间: `09:00:00`
   - 重复: 每天

4. 操作
   - 程序或脚本: `python`
   - 添加参数: `C:\Users\Administrator\.openclaw\workspace\scripts\github_trending_daily.py`
   - 起始于: `C:\Users\Administrator\.openclaw\workspace`

5. 完成
   - 点击 "完成"

### 创建每周任务（包含自动贡献）

1. 创建基本任务
   - 名称: `GitHub Trending Weekly Auto-Contribute`
   - 描述: `每周自动为热门项目创建 PR`

2. 触发器
   - 选择 "每周"
   - 开始时间: `08:00:00`
   - 重复: 每周一

3. 操作
   - 程序或脚本: `python`
   - 添加参数: `C:\Users\Administrator\.openclaw\workspace\scripts\github_trending_daily.py`
   - 起始于: `C:\Users\Administrator\.openclaw\workspace`

4. 完成
   - 点击 "完成"

## 方法 2: 使用 PowerShell 脚本创建任务

```powershell
# 创建每日扫描任务
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "C:\Users\Administrator\.openclaw\workspace\scripts\github_trending_daily.py" `
    -WorkingDirectory "C:\Users\Administrator\.openclaw\workspace"

$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "09:00"

Register-ScheduledTask `
    -TaskName "GitHub Trending Daily Scan" `
    -Action $action `
    -Trigger $trigger `
    -Description "每日扫描 GitHub Trending 项目并寻找贡献机会"

# 创建每周自动贡献任务
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "C:\Users\Administrator\.openclaw\workspace\scripts\github_trending_daily.py" `
    -WorkingDirectory "C:\Users\Administrator\.openclaw\workspace"

$trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday `
    -At "08:00"

Register-ScheduledTask `
    -TaskName "GitHub Trending Weekly Auto-Contribute" `
    -Action $action `
    -Trigger $trigger `
    -Description "每周自动为热门项目创建 PR"
```

## 方法 3: 使用 Python 脚本创建任务

```python
import subprocess
import sys

def create_windows_task():
    """创建 Windows 任务计划"""
    # 创建每日扫描任务
    daily_cmd = f"""
    schtasks /create /tn "GitHub Trending Daily Scan" /tr "python C:\\Users\\Administrator\\.openclaw\\workspace\\scripts\\github_trending_daily.py" /sc daily /st 09:00
    """
    subprocess.run(daily_cmd, shell=True)

    # 创建每周自动贡献任务
    weekly_cmd = f"""
    schtasks /create /tn "GitHub Trending Weekly Auto-Contribute" /tr "python C:\\Users\\Administrator\\.openclaw\\workspace\\scripts\\github_trending_daily.py" /sc weekly /d MON /st 08:00
    """
    subprocess.run(weekly_cmd, shell=True)

    print("Windows 任务计划创建完成！")

if __name__ == "__main__":
    create_windows_task()
```

## 验证任务

### 查看所有任务
```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "*GitHub*" }
```

### 查看任务详情
```powershell
Get-ScheduledTaskInfo "GitHub Trending Daily Scan"
```

### 手动运行任务
```powershell
Start-ScheduledTask "GitHub Trending Daily Scan"
```

### 删除任务
```powershell
Unregister-ScheduledTask "GitHub Trending Daily Scan" -Confirm:$false
```

## 日志配置

### 创建日志目录
```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\Administrator\.openclaw\workspace\logs"
```

### 查看日志
```powershell
Get-Content "C:\Users\Administrator\.openclaw\workspace\logs\github_trending.log" -Tail 50
```

## 注意事项

1. **Python 路径**: 确保 `python` 命令在 PATH 中，或使用完整路径
2. **权限**: 确保任务有足够的权限访问文件系统和网络
3. **日志**: 建议配置日志输出到文件，便于排查问题
4. **测试**: 创建任务后，先手动运行一次测试是否正常
5. **GitHub API**: 如果使用 GitHub API，需要配置认证 token

## 故障排除

### 任务不运行
1. 检查任务是否启用: `Get-ScheduledTask "GitHub Trending Daily Scan"`
2. 检查触发器是否正确: `Get-ScheduledTaskInfo "GitHub Trending Daily Scan"`
3. 检查日志文件是否有错误信息

### Python 脚本错误
1. 手动运行脚本测试: `python scripts/github_trending_daily.py`
2. 检查 Python 版本: `python --version`
3. 检查依赖包是否安装: `pip list`

### 网络问题
1. 检查网络连接
2. 检查防火墙设置
3. 检查代理配置
