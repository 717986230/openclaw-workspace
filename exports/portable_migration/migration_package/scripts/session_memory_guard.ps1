# session_memory_guard.ps1
# Session Memory Guard - Auto cleanup, force database query
# Author: Erbing | Created: 2026-03-30

param(
    [switch]$Check,
    [switch]$ForceCleanup,
    [int]$KeepRecent = 50,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

# Paths
$WorkspaceRoot = "$env:USERPROFILE\.openclaw\workspace"
$MemoryDbPath = "$WorkspaceRoot\memory\database\xiaozhi_memory.db"
$SessionLogPath = "$WorkspaceRoot\memory\sessions"
$LancedbPath = "$WorkspaceRoot\memory\database\lancedb"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-MemoryDatabase {
    if (-not (Test-Path $MemoryDbPath)) {
        Write-Log "SQLite DB not found: $MemoryDbPath" -Level ERROR
        return $false
    }
    
    $dbInfo = Get-Item $MemoryDbPath
    Write-Log "SQLite DB size: $([math]::Round($dbInfo.Length/1KB, 2)) KB"
    
    if (Test-Path $LancedbPath) {
        $lanceInfo = Get-ChildItem $LancedbPath -Recurse | Measure-Object -Property Length -Sum
        Write-Log "LanceDB size: $([math]::Round($lanceInfo.Sum/1KB, 2)) KB"
    }
    
    return $true
}

function Get-SessionMetrics {
    $metrics = @{
        SessionLogFiles = 0
        TotalSessionSize = 0
        OldestSession = $null
        NewestSession = $null
    }
    
    if (Test-Path $SessionLogPath) {
        $files = Get-ChildItem $SessionLogPath -Filter "*.md" -ErrorAction SilentlyContinue
        $metrics.SessionLogFiles = $files.Count
        
        if ($files.Count -gt 0) {
            $metrics.TotalSessionSize = ($files | Measure-Object -Property Length -Sum).Sum
            $metrics.OldestSession = ($files | Sort-Object LastWriteTime | Select-Object -First 1).LastWriteTime
            $metrics.NewestSession = ($files | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        }
    }
    
    return $metrics
}

function Invoke-SessionCleanup {
    param([int]$KeepRecent)
    
    Write-Log "Starting cleanup, keeping $KeepRecent recent sessions..."
    
    if (-not (Test-Path $SessionLogPath)) {
        Write-Log "Session log dir not found, nothing to clean" -Level WARN
        return @{ Cleaned = 0; FreedKB = 0 }
    }
    
    $files = Get-ChildItem $SessionLogPath -Filter "*.md" | Sort-Object LastWriteTime -Descending
    $totalFiles = $files.Count
    
    if ($totalFiles -le $KeepRecent) {
        Write-Log "Session file count ($totalFiles) below threshold ($KeepRecent), no cleanup needed"
        return @{ Cleaned = 0; FreedKB = 0 }
    }
    
    $toDelete = $files | Select-Object -Skip $KeepRecent
    $cleaned = 0
    $freedBytes = 0
    
    foreach ($file in $toDelete) {
        try {
            $archivePath = "$SessionLogPath\archive"
            if (-not (Test-Path $archivePath)) {
                New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
            }
            
            Move-Item -Path $file.FullName -Destination "$archivePath\$($file.Name)" -Force
            $freedBytes += $file.Length
            $cleaned++
        }
        catch {
            Write-Log "Failed to archive: $($file.Name) - $_" -Level WARN
        }
    }
    
    Write-Log "Archived $cleaned old session files, freed $([math]::Round($freedBytes/1KB, 2)) KB" -Level SUCCESS
    
    return @{ Cleaned = $cleaned; FreedKB = [math]::Round($freedBytes/1KB, 2) }
}

function Export-MemoryGuidelines {
    $guidelinesPath = "$WorkspaceRoot\memory\FORCE_DATABASE_QUERY.md"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $sb = [System.Text.StringBuilder]::new()
    $sb.AppendLine("# FORCE DATABASE QUERY RULES") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## Effective: $timestamp") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## Core Rules") | Out-Null
    $sb.AppendLine("1. NO session memory dependency - context only for current conversation") | Out-Null
    $sb.AppendLine("2. FORCE database query - all history via SQLite or LanceDB") | Out-Null
    $sb.AppendLine("3. AUTO cleanup trigger - archive when threshold exceeded") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## Database Locations") | Out-Null
    $sb.AppendLine("- SQLite: $MemoryDbPath") | Out-Null
    $sb.AppendLine("- LanceDB: $LancedbPath") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## Query Priority") | Out-Null
    $sb.AppendLine("1. LanceDB vector search - semantic similarity") | Out-Null
    $sb.AppendLine("2. SQLite structured query - exact match") | Out-Null
    $sb.AppendLine("3. Memory cache - current session hot data only") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## Cleanup Strategy") | Out-Null
    $sb.AppendLine("- Keep recent: $KeepRecent session files") | Out-Null
    $sb.AppendLine("- Old files archived to archive/ dir") | Out-Null
    $sb.AppendLine("- Archived files still queryable via database") | Out-Null
    
    Set-Content -Path $guidelinesPath -Value $sb.ToString() -Encoding UTF8
    Write-Log "Generated force query rules file: $guidelinesPath" -Level SUCCESS
}

function Show-Status {
    Write-Host ""
    Write-Host "=== Session Memory System Status ===" -ForegroundColor Cyan
    
    if (Test-MemoryDatabase) {
        Write-Log "Memory database OK" -Level SUCCESS
    }
    
    $metrics = Get-SessionMetrics
    Write-Host ""
    Write-Host "Session File Stats:" -ForegroundColor Cyan
    Write-Host "  File count: $($metrics.SessionLogFiles)"
    Write-Host "  Total size: $([math]::Round($metrics.TotalSessionSize/1KB, 2)) KB"
    Write-Host "  Oldest: $($metrics.OldestSession)"
    Write-Host "  Newest: $($metrics.NewestSession)"
    
    Write-Host ""
    Write-Host "Cleanup Policy:" -ForegroundColor Cyan
    Write-Host "  Keep recent: $KeepRecent files"
    Write-Host "  Archive dir: $SessionLogPath\archive"
}

function Show-Help {
    Write-Host "Session Memory Guard Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\session_memory_guard.ps1 -Status          # Show status"
    Write-Host "  .\session_memory_guard.ps1 -Check           # Check if cleanup needed"
    Write-Host "  .\session_memory_guard.ps1 -ForceCleanup    # Force cleanup old sessions"
    Write-Host "  .\session_memory_guard.ps1 -KeepRecent 30   # Keep only 30 recent sessions"
}

# Main logic
if ($Status) {
    Show-Status
    exit 0
}

if ($Check) {
    Write-Log "Checking session status..."
    
    $metrics = Get-SessionMetrics
    
    if ($metrics.SessionLogFiles -gt 100) {
        Write-Log "Too many session files ($($metrics.SessionLogFiles)), cleanup recommended" -Level WARN
        Write-Host "Run: .\session_memory_guard.ps1 -ForceCleanup" -ForegroundColor Yellow
    } else {
        Write-Log "Session file count OK ($($metrics.SessionLogFiles))" -Level SUCCESS
    }
    
    Test-MemoryDatabase | Out-Null
    exit 0
}

if ($ForceCleanup) {
    Test-MemoryDatabase | Out-Null
    $result = Invoke-SessionCleanup -KeepRecent $KeepRecent
    Export-MemoryGuidelines
    
    Write-Host ""
    Write-Host "Cleanup done:" -ForegroundColor Green
    Write-Host "  Archived: $($result.Cleaned) files"
    Write-Host "  Freed: $($result.FreedKB) KB"
    exit 0
}

# Default show help
Show-Help
