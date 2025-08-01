# ChromaDB Clear Tool - PowerShell Script
# Quick way to clear ChromaDB for focused testing

param(
    [switch]$Local,
    [switch]$Railway, 
    [switch]$Both,
    [switch]$Confirm,
    [switch]$Help
)

function Show-Help {
    Write-Host "🔧 ChromaDB Clear Tool - PowerShell Version" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Green
    Write-Host "  .\clear_chroma.ps1 [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -Local      Clear local ChromaDB only (default)" -ForegroundColor White
    Write-Host "  -Railway    Clear Railway ChromaDB only" -ForegroundColor White
    Write-Host "  -Both       Clear both local and Railway" -ForegroundColor White
    Write-Host "  -Confirm    Skip confirmation prompt" -ForegroundColor White
    Write-Host "  -Help       Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\clear_chroma.ps1              # Clear local only" -ForegroundColor Gray
    Write-Host "  .\clear_chroma.ps1 -Railway     # Clear Railway only" -ForegroundColor Gray
    Write-Host "  .\clear_chroma.ps1 -Both        # Clear both" -ForegroundColor Gray
    Write-Host "  .\clear_chroma.ps1 -Both -Confirm  # Clear both without asking" -ForegroundColor Gray
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host "🔧 ChromaDB Clear Tool" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and in your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Build arguments for Python script
$args = @()

if ($Local) { $args += "--local" }
if ($Railway) { $args += "--railway" }
if ($Both) { $args += "--both" }
if ($Confirm) { $args += "--confirm" }

# Default to local if no specific option
if (-not ($Local -or $Railway -or $Both)) {
    $args += "--local"
}

Write-Host ""
Write-Host "🚀 Running ChromaDB clear tool..." -ForegroundColor Yellow

# Run the Python script
try {
    python clear_chroma_tool.py @args
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ ChromaDB clear completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️ ChromaDB clear completed with errors" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error running clear tool: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
