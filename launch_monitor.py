"""
Launch the Canvas AI Assistant Pipeline Monitor Dashboard
This script opens the monitoring dashboard in your default browser
"""

import webbrowser
import os
import sys
from pathlib import Path

def launch_monitor():
    """Launch the monitoring dashboard"""
    
    # Get the path to the HTML file
    current_dir = Path(__file__).parent
    html_file = current_dir / "monitor_dashboard.html"
    
    if not html_file.exists():
        print("❌ Monitor dashboard file not found!")
        print(f"Expected location: {html_file}")
        return False
    
    # Convert to file URL
    file_url = f"file:///{html_file.resolve().as_posix()}"
    
    print("🚀 Launching Canvas AI Assistant Pipeline Monitor...")
    print(f"📊 Dashboard URL: {file_url}")
    print("🌐 Opening in your default browser...")
    
    try:
        # Open in default browser
        webbrowser.open(file_url)
        print("✅ Monitor dashboard launched successfully!")
        print("\n📋 Dashboard Features:")
        print("   • Real-time API status monitoring")
        print("   • Document count and statistics")
        print("   • Live search testing")
        print("   • Activity logging")
        print("   • Knowledge base management")
        print("\n🔄 The dashboard will auto-refresh data every 30 seconds when enabled")
        print("💡 Tip: Bookmark this page for quick access!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch browser: {str(e)}")
        print(f"🔗 Manual URL: {file_url}")
        return False

if __name__ == "__main__":
    print("🔧 Canvas AI Assistant - Pipeline Monitor Launcher")
    print("=" * 60)
    
    success = launch_monitor()
    
    if success:
        print("\n✨ Monitor is now running!")
        print("📝 Keep this terminal open to see any launcher messages")
        
        # Keep the script running so user can see the output
        try:
            input("\nPress Enter to close this launcher...")
        except KeyboardInterrupt:
            print("\n👋 Launcher closed")
    else:
        print("\n❌ Failed to launch monitor dashboard")
        input("Press Enter to exit...")
        sys.exit(1)
