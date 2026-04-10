# worktree-manage.ps1 - Git Worktree 管理脚本
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("create","list","remove","prune")]
    [string]$Action,
    
    [string]$Branch,
    
    [string]$Path
)

$branchPrefix = "task/"

switch ($Action) {
    "create" {
        if (-not $Branch) {
            $Branch = Read-Host "输入分支名称"
        }
        
        $fullBranch = "$branchPrefix$Branch"
        $worktreePath = ".worktrees/$Branch"
        
        # 检查是否是 git 仓库
        if (-not (Test-Path ".git")) {
            Write-Host "✗ 当前目录不是 Git 仓库" -ForegroundColor Red
            exit 1
        }
        
        # 创建 worktree
        Write-Host "创建 worktree: $worktreePath (分支: $fullBranch)" -ForegroundColor Cyan
        
        # 检查分支是否存在
        $branchExists = git branch --list $fullBranch
        if ($branchExists) {
            git worktree add $worktreePath $fullBranch 2>&1
        } else {
            git worktree add -b $fullBranch $worktreePath 2>&1
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Worktree 创建成功: $worktreePath" -ForegroundColor Green
            Write-Host "  进入: cd $worktreePath" -ForegroundColor Yellow
        } else {
            Write-Host "✗ Worktree 创建失败" -ForegroundColor Red
        }
    }
    
    "list" {
        Write-Host "`n## Worktrees`n" -ForegroundColor Cyan
        git worktree list | ForEach-Object {
            Write-Host "  $_" -ForegroundColor White
        }
        Write-Host ""
    }
    
    "remove" {
        if (-not $Path) {
            $Path = Read-Host "输入 worktree 路径"
        }
        
        Write-Host "移除 worktree: $Path" -ForegroundColor Yellow
        git worktree remove $Path --force 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Worktree 已移除" -ForegroundColor Green
            
            # 可选：删除分支
            $deleteBranch = Read-Host "是否删除对应分支? [y/n]"
            if ($deleteBranch -eq "y") {
                $branchName = Split-Path $Path -Leaf
                git branch -D "$branchPrefix$branchName" 2>&1
                Write-Host "✓ 分支已删除: $branchPrefix$branchName" -ForegroundColor Green
            }
        } else {
            Write-Host "✗ Worktree 移除失败" -ForegroundColor Red
        }
    }
    
    "prune" {
        Write-Host "清理无效 worktree..." -ForegroundColor Cyan
        git worktree prune -v
        Write-Host "✓ 清理完成" -ForegroundColor Green
    }
}
