# ask.ps1 - 用户交互脚本
param(
    [Parameter(Mandatory=$true)]
    [string]$Question,
    
    [ValidateSet("confirm","select","multiselect","input")]
    [string]$Type = "confirm",
    
    [string[]]$Options = @(),
    
    [int]$Timeout = 300
)

# 读取配置
$configPath = "$PSScriptRoot\..\memory\preferences\ask-config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    $Timeout = $config.timeout / 1000
}

# 显示问题
Write-Host "`n$Question`n" -ForegroundColor Cyan

switch ($Type) {
    "confirm" {
        Write-Host "[y/n] > " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        return ($response -eq "y" -or $response -eq "yes")
    }
    
    "select" {
        for ($i = 0; $i -lt $Options.Count; $i++) {
            Write-Host "  [$i] $($Options[$i])" -ForegroundColor White
        }
        Write-Host "`n[选择编号] > " -NoNewline -ForegroundColor Yellow
        $response = [int](Read-Host)
        return $Options[$response]
    }
    
    "multiselect" {
        for ($i = 0; $i -lt $Options.Count; $i++) {
            Write-Host "  [$i] $($Options[$i])" -ForegroundColor White
        }
        Write-Host "`n[多选编号，逗号分隔] > " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        $indices = $response -split ',' | ForEach-Object { [int]$_.Trim() }
        return $Options[$indices]
    }
    
    "input" {
        Write-Host "> " -NoNewline -ForegroundColor Yellow
        return Read-Host
    }
}
