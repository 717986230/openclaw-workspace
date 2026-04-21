# todo-track.ps1 - Task tracking script
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("init","add","complete","list","archive")]
    [string]$Action,
    
    [string]$Task,
    
    [int]$Index
)

$workspaceRoot = "C:\Users\Administrator\.openclaw\workspace"
$todoFile = "$workspaceRoot\memory\todos\current.json"
$archiveDir = "$workspaceRoot\memory\todos\archive"

# Ensure directories exist
$todoDir = Split-Path $todoFile -Parent
if (-not (Test-Path $todoDir)) {
    New-Item -ItemType Directory -Path $todoDir -Force | Out-Null
}
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
}

# Read existing todos
function Get-Todos {
    if (Test-Path $script:todoFile) {
        return Get-Content $script:todoFile | ConvertFrom-Json
    }
    return @()
}

# Save todos
function Save-Todos($todos) {
    $todos | ConvertTo-Json -Depth 10 | Set-Content $script:todoFile
}

# Execute action
switch ($Action) {
    "init" {
        @() | Save-Todos
        Write-Host "Task list initialized" -ForegroundColor Green
    }
    
    "add" {
        $todos = Get-Todos
        $newTask = @{
            id = $todos.Count + 1
            task = $Task
            status = "pending"
            createdAt = Get-Date -Format "o"
        }
        $todos += $newTask
        Save-Todos $todos
        Write-Host "Added: $Task" -ForegroundColor Green
    }
    
    "complete" {
        $todos = Get-Todos
        if ($Index -ge 1 -and $Index -le $todos.Count) {
            $updated = $todos | ForEach-Object -Begin {$i=0} -Process {
                if ($i -eq ($Index - 1)) {
                    @{
                        id = $_.id
                        task = $_.task
                        status = "completed"
                        createdAt = $_.createdAt
                        completedAt = Get-Date -Format "o"
                    }
                } else {
                    $_
                }
                $i++
            }
            Save-Todos $updated
            Write-Host "Completed: $($todos[$Index - 1].task)" -ForegroundColor Green
        } else {
            Write-Host "Invalid index: $Index" -ForegroundColor Red
        }
    }
    
    "list" {
        $todos = Get-Todos
        if ($todos.Count -eq 0) {
            Write-Host "No tasks" -ForegroundColor Yellow
        } else {
            Write-Host ""
            Write-Host "## Todos" -ForegroundColor Cyan
            Write-Host ""
            foreach ($t in $todos) {
                if ($t.status -eq "completed") {
                    $status = "[x]"
                    $color = "Green"
                } else {
                    $status = "[ ]"
                    $color = "White"
                }
                Write-Host "- $status $($t.task)" -ForegroundColor $color
            }
            Write-Host ""
        }
    }
    
    "archive" {
        $todos = Get-Todos
        if ($todos.Count -gt 0) {
            $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $archiveFile = Join-Path $archiveDir "todos-$timestamp.json"
            $todos | ConvertTo-Json -Depth 10 | Set-Content $archiveFile
            @() | Save-Todos
            Write-Host "Archived $($todos.Count) tasks" -ForegroundColor Green
        } else {
            Write-Host "No tasks to archive" -ForegroundColor Yellow
        }
    }
}
