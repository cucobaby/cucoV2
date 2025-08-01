# Canvas AI Assistant - Pipeline Monitor Launcher (PowerShell)
# Quick launcher for the monitoring dashboard

param(
    [switch]$Help
)

function Show-Help {
    Write-Host "🔧 Canvas AI Assistant - Pipeline Monitor Launcher" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Green
    Write-Host "  .\launch_monitor.ps1          # Launch the monitoring dashboard" -ForegroundColor White
    Write-Host "  .\launch_monitor.ps1 -Help    # Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "What this does:" -ForegroundColor Green
    Write-Host "  • Opens the pipeline monitoring dashboard in your browser" -ForegroundColor Gray
    Write-Host "  • Shows real-time API status and data statistics" -ForegroundColor Gray
    Write-Host "  • Allows testing search functionality" -ForegroundColor Gray
    Write-Host "  • Provides knowledge base management tools" -ForegroundColor Gray
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host "🚀 Canvas AI Assistant - Pipeline Monitor Launcher" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if HTML file exists
$htmlFile = Join-Path $PSScriptRoot "monitor_dashboard.html"

if (-not (Test-Path $htmlFile)) {
    Write-Host "❌ Monitor dashboard file not found!" -ForegroundColor Red
    Write-Host "Expected location: $htmlFile" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📊 Dashboard found: $htmlFile" -ForegroundColor Green
Write-Host "🌐 Opening in your default browser..." -ForegroundColor Yellow

try {
    # Convert to file URL for proper browser opening
    $fileUrl = "file:///" + $htmlFile.Replace('\', '/')
    
    # Open in default browser
    Start-Process $fileUrl
    
    Write-Host "✅ Monitor dashboard launched successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Dashboard Features:" -ForegroundColor Cyan
    Write-Host "   • Real-time API status monitoring" -ForegroundColor Gray
    Write-Host "   • Document count and statistics" -ForegroundColor Gray
    Write-Host "   • Live search testing" -ForegroundColor Gray
    Write-Host "   • Activity logging" -ForegroundColor Gray
    Write-Host "   • Knowledge base management" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔄 The dashboard will auto-refresh data every 30 seconds when enabled" -ForegroundColor Blue
    Write-Host "💡 Tip: Bookmark this page for quick access!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔗 Dashboard URL: $fileUrl" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Failed to launch browser: $_" -ForegroundColor Red
    Write-Host "🔗 Manual URL: file:///$($htmlFile.Replace('\', '/'))" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to close this launcher"
