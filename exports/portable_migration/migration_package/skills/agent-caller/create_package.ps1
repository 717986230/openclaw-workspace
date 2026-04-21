cd C:\Users\Administrator\.openclaw\workspace

# 创建技能包目录结构
Write-Host "Creating skill package structure..." -ForegroundColor Yellow

$skillDir = "skills\agency-agents-caller"
$packageDir = "skills\packages"

# 创建输出目录
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null

# 显示文件结构
Write-Host "`nSkill Package Contents:" -ForegroundColor Green
Get-ChildItem -Path $skillDir -Recurse -File | Select-Object FullName

# 创建压缩包
Write-Host "`nCreating package..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packageName = "agency-agents-caller_$timestamp.tar.gz"
$packagePath = Join-Path $packageDir $packageName

# 压缩文件
$filesToZip = @(
    "SKILL.md",
    "README.md",
    "package.json",
    "scripts\agent_caller.py",
    "examples\usage_demo.py"
)

Compress-Archive -Path (Resolve-Path "$skillDir\*") -DestinationPath $packagePath -Force

Write-Host "`nPackage created: $packagePath" -ForegroundColor Green
Write-Host "Package size: $((Get-Item $packagePath).Length) bytes" -ForegroundColor Cyan

Write-Host @"

======================================================================
Publish Instructions
======================================================================

Option 1: ClawHub CLI (Recommended)

  npm install -g clawhub-cli
  clawhub login
  cd $skillDir
  clawhub publish


Option 2: Web UI

  Visit: https://clawhub.com/publish
  Upload: $packagePath


Option 3: Manual

  Copy to: ~/.clawhub/skills/agency-agents-caller
  Register: clawhub register agency-agents-caller


After Publishing:

  Your skill will be at: https://clawhub.com/skills/agency-agents-caller
  Install command: clawhub install agency-agents-caller

"@ -ForegroundColor Yellow
