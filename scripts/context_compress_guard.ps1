# context_compress_guard.ps1
# Context Compression Guard - Auto compress when session full, force DB query
# Author: Erbing | Created: 2026-03-30

<#
.SYNOPSIS
    Monitors context usage and triggers compression when threshold reached.

.DESCRIPTION
    This script checks OpenClaw session context usage and:
    1. Estimates current context token usage
    2. Triggers compression when approaching limit
    3. Forces database queries for historical information retrieval
    
    Context compression happens automatically in OpenClaw when:
    - Token count approaches model limit
    - Summary compaction is triggered
    
    This script helps monitor and enforce the compression behavior.

.PARAMETER Threshold
    Percentage threshold to trigger compression warning (default: 80%)

.PARAMETER ForceCompress
    Request immediate context compression

.PARAMETER Status
    Show current context status

.EXAMPLE
    .\context_compress_guard.ps1 -Status
    Show current context usage status

.EXAMPLE
    .\context_compress_guard.ps1 -ForceCompress
    Request immediate compression
#>

param(
    [switch]$Status,
    [switch]$ForceCompress,
    [int]$Threshold = 80
)

$ErrorActionPreference = "Stop"

# Paths
$WorkspaceRoot = "$env:USERPROFILE\.openclaw\workspace"
$MemoryDbPath = "$WorkspaceRoot\memory\database\xiaozhi_memory.db"
$LancedbPath = "$WorkspaceRoot\memory\database\lancedb"
$TranscriptsPath = "$env:USERPROFILE\.openclaw\transcripts"

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

function Get-ContextMetrics {
    # Estimate context from recent transcript files
    $metrics = @{
        TranscriptFiles = 0
        TotalSizeKB = 0
        EstimatedTokens = 0
        OldestFile = $null
        NewestFile = $null
    }
    
    if (Test-Path $TranscriptsPath) {
        $files = Get-ChildItem $TranscriptsPath -Filter "*.json" -ErrorAction SilentlyContinue | 
                 Sort-Object LastWriteTime -Descending | 
                 Select-Object -First 10
        
        $metrics.TranscriptFiles = $files.Count
        
        if ($files.Count -gt 0) {
            $totalBytes = ($files | Measure-Object -Property Length -Sum).Sum
            $metrics.TotalSizeKB = [math]::Round($totalBytes / 1KB, 2)
            
            # Rough estimate: 1 token ~ 4 chars, JSON overhead ~2x
            $metrics.EstimatedTokens = [math]::Round($totalBytes * 0.3 / 4)
            
            $metrics.OldestFile = ($files | Sort-Object LastWriteTime | Select-Object -First 1).LastWriteTime
            $metrics.NewestFile = ($files | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        }
    }
    
    return $metrics
}

function Test-DatabaseAccess {
    $dbStatus = @{
        SQLiteOK = $false
        SQLiteSize = 0
        LanceDBOK = $false
        LanceDBSize = 0
    }
    
    # Check SQLite
    if (Test-Path $MemoryDbPath) {
        $dbInfo = Get-Item $MemoryDbPath
        $dbStatus.SQLiteOK = $true
        $dbStatus.SQLiteSize = [math]::Round($dbInfo.Length / 1KB, 2)
    }
    
    # Check LanceDB
    if (Test-Path $LancedbPath) {
        $lanceInfo = Get-ChildItem $LancedbPath -Recurse -ErrorAction SilentlyContinue | 
                     Measure-Object -Property Length -Sum
        $dbStatus.LanceDBOK = $true
        $dbStatus.LanceDBSize = [math]::Round($lanceInfo.Sum / 1KB, 2)
    }
    
    return $dbStatus
}

function Write-CompressionGuidelines {
    # Write guidelines for memory retrieval after compression
    $guidelinesPath = "$WorkspaceRoot\memory\CONTEXT_COMPRESSION_RULES.md"
    
    $sb = [System.Text.StringBuilder]::new()
    $sb.AppendLine("# CONTEXT COMPRESSION RULES") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## When Context is Compressed") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("### MANDATORY BEHAVIOR") | Out-Null
    $sb.AppendLine("1. DO NOT rely on session memory for historical information") | Out-Null
    $sb.AppendLine("2. ALWAYS query database for:") | Out-Null
    $sb.AppendLine("   - User preferences (USER.md, preferences/)") | Out-Null
    $sb.AppendLine("   - Past decisions (MEMORY.md, learnings/)") | Out-Null
    $sb.AppendLine("   - Event history (events/, database/)") | Out-Null
    $sb.AppendLine("   - Skill knowledge (skills/, memory/)") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("### Database Query Priority") | Out-Null
    $sb.AppendLine("1. LanceDB vector search for semantic/similarity queries") | Out-Null
    $sb.AppendLine("2. SQLite for structured/exact queries") | Out-Null
    $sb.AppendLine("3. File read for markdown/config files") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("### After Compression") | Out-Null
    $sb.AppendLine("- Re-read SOUL.md, IDENTITY.md, USER.md") | Out-Null
    $sb.AppendLine("- Use memory_search before answering history questions") | Out-Null
    $sb.AppendLine("- Use memory_get to fetch specific snippets") | Out-Null
    $sb.AppendLine("- NEVER assume you remember previous context") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("## Database Locations") | Out-Null
    $sb.AppendLine("- SQLite: $MemoryDbPath") | Out-Null
    $sb.AppendLine("- LanceDB: $LancedbPath") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("---") | Out-Null
    $sb.AppendLine("*Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*") | Out-Null
    
    Set-Content -Path $guidelinesPath -Value $sb.ToString() -Encoding UTF8
    Write-Log "Generated compression rules: $guidelinesPath" -Level SUCCESS
}

function Show-Status {
    Write-Host ""
    Write-Host "=== Context Compression Guard Status ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Database status
    $dbStatus = Test-DatabaseAccess
    
    Write-Host "Memory Database:" -ForegroundColor Yellow
    Write-Host "  SQLite: $($dbStatus.SQLiteSize) KB - $(if($dbStatus.SQLiteOK){'OK'}else{'MISSING'})"
    Write-Host "  LanceDB: $($dbStatus.LanceDBSize) KB - $(if($dbStatus.LanceDBOK){'OK'}else{'EMPTY'})"
    Write-Host ""
    
    # Context metrics
    $metrics = Get-ContextMetrics
    
    Write-Host "Context Estimation:" -ForegroundColor Yellow
    Write-Host "  Transcript files: $($metrics.TranscriptFiles)"
    Write-Host "  Total size: $($metrics.TotalSizeKB) KB"
    Write-Host "  Est. tokens: $($metrics.EstimatedTokens)"
    Write-Host "  Time range: $($metrics.OldestFile) ~ $($metrics.NewestFile)"
    Write-Host ""
    
    # Warning if approaching threshold
    $modelLimit = 128000  # Typical context limit
    $usagePercent = [math]::Min(100, ($metrics.EstimatedTokens / $modelLimit) * 100)
    
    Write-Host "Context Usage: " -NoNewline
    if ($usagePercent -ge $Threshold) {
        Write-Host "$([math]::Round($usagePercent, 1))% - APPROACHING LIMIT!" -ForegroundColor Red
        Write-Host ""
        Write-Host "ACTION REQUIRED: Run with -ForceCompress to trigger compression" -ForegroundColor Yellow
    } elseif ($usagePercent -ge 50) {
        Write-Host "$([math]::Round($usagePercent, 1))% - Moderate" -ForegroundColor Yellow
    } else {
        Write-Host "$([math]::Round($usagePercent, 1))% - OK" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Compression Policy:" -ForegroundColor Cyan
    Write-Host "  Threshold: $Threshold%"
    Write-Host "  On compress: Force database queries for history"
    Write-Host "  After compress: Re-read SOUL.md, IDENTITY.md, USER.md"
}

function Request-Compression {
    Write-Log "Requesting context compression..."
    
    # Write compression guidelines
    Write-CompressionGuidelines
    
    # Create compression marker for OpenClaw
    $markerPath = "$WorkspaceRoot\.compress_request"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $marker = @{
        RequestedAt = $timestamp
        Reason = "User requested or threshold exceeded"
        Action = "Force database queries for all historical information"
    } | ConvertTo-Json
    
    Set-Content -Path $markerPath -Value $marker -Encoding UTF8
    
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Yellow
    Write-Host "  COMPRESSION REQUEST CREATED" -ForegroundColor Yellow
    Write-Host "======================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next actions:" -ForegroundColor Cyan
    Write-Host "1. OpenClaw will compact the session when needed"
    Write-Host "2. After compaction, MANDATORY database queries:"
    Write-Host "   - Use memory_search for history"
    Write-Host "   - Use memory_get for specific content"
    Write-Host "   - Re-read SOUL.md, IDENTITY.md, USER.md"
    Write-Host "3. NEVER assume session context is preserved"
    Write-Host ""
    Write-Host "Compression rules written to:" -ForegroundColor Green
    Write-Host "  $WorkspaceRoot\memory\CONTEXT_COMPRESSION_RULES.md"
    Write-Host ""
}

# Main
if ($ForceCompress) {
    Request-Compression
    exit 0
}

if ($Status) {
    Show-Status
    exit 0
}

# Default: show help
Write-Host "Context Compression Guard" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage:"
Write-Host "  .\context_compress_guard.ps1 -Status           # Show context status"
Write-Host "  .\context_compress_guard.ps1 -ForceCompress    # Request compression"
Write-Host "  .\context_compress_guard.ps1 -Threshold 70     # Set warning threshold"
Write-Host ""
Write-Host "This script monitors context usage and enforces database queries"
Write-Host "after compression to ensure memory continuity."
