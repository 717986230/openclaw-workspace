# todo-track.ps1 - Task tracking script
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(init,add,complete,list,archive)]
    [string]$Action,
    
    [string]$Task,
    
    [int]$Index
)

$todoFile = $PSScriptRoot\..\memory\todos\current.json
$archiveDir = $PSScriptRoot\..\memory\todos\archive

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
    if (Test-Path $todoFile) {
        return Get-Content $todoFile | ConvertFrom-Json
    }
    return @()
}

# Save todos
function Save-Todos($todos) {
    $todos | ConvertTo-Json -Depth 10 | Set-Content $todoFile
}

# Execute action
switch ($Action) {
    init {
        @() | Save-Todos
        Write-Host Task list initialized -ForegroundColor Green
    }
    
    add {
        $todos = Get-Todos
        $newTask = @{
            id = $todos.Count + 1
            task = $Task
            status = pending
            createdAt = Get-Date -Format o
        }
        $todos += $newTask
        Save-Todos $todos
        Write-Host Added: $Task -ForegroundColor Green
    }
    
    complete {
        $todos = Get-Todos
        if ($Index -ge 1 -and $Index -le $todos.Count) {
            $todos[$Index - 1].status = completed
            $todos[$Index - 1].completedAt = Get-Date -Format o
            Save-Todos $todos
            Write-Host Completed: $($todos[$Index - 1].task) -ForegroundColor Green
        } else {
            Write-Host Invalid index: $Index -ForegroundColor Red
        }
    }
    
    list {
        $todos = Get-Todos
        if ($todos.Count -eq 0) {
            Write-Host No tasks -ForegroundColor Yellow
        } else {
            Write-Host 
## Todos
 -ForegroundColor Cyan
            foreach ($t in $todos) {
                $status = if ($t.status -eq completed) { [x] } else { [ ] }
                $color = if ($t.status -eq completed) { Green } else { White }
                Write-Host - $status $($t.task) -ForegroundColor $color
            }
            Write-Host "
 }
 }
 
 archive {
 $todos = Get-Todos
 if ($todos.Count -gt 0) {
 $timestamp = Get-Date -Format yyyyMMdd-HHmmss
 $archiveFile = Join-Path $archiveDir todos-$timestamp.json
 $todos | ConvertTo-Json -Depth 10 | Set-Content $archiveFile
 @() | Save-Todos
 Write-Host Archived $($todos.Count) tasks -ForegroundColor Green
 } else {
 Write-Host No tasks to archive -ForegroundColor Yellow
 }
 }
}