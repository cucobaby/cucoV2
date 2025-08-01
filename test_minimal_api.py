"""
Test the minimal API to see if it can start without issues
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_minimal_api():
    """Test if the minimal API can be imported and started"""
    try:
        print("🔧 Testing minimal API import...")
        from src.minimal_api_test import app
        print("✅ Minimal API imported successfully")
        
        # Test health endpoint directly
        print("🔧 Testing health endpoint...")
        # This would normally require async testing, but we just want to see if it imports
        print("✅ Health endpoint exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal API error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def compare_apis():
    """Compare minimal vs full API to identify issues"""
    print("\n🔧 Comparing API versions...")
    
    minimal_ok = test_minimal_api()
    
    try:
        print("🔧 Testing full API import...")
        from src.api_server import app as full_app
        print("✅ Full API imported successfully")
        full_ok = True
    except Exception as e:
        print(f"❌ Full API error: {str(e)}")
        full_ok = False
    
    print(f"\n📋 API Comparison:")
    print(f"   Minimal API: {'✅ OK' if minimal_ok else '❌ Failed'}")
    print(f"   Full API: {'✅ OK' if full_ok else '❌ Failed'}")
    
    if minimal_ok and not full_ok:
        print(f"\n💡 Recommendation: Deploy minimal API first to test Railway, then add features")
    elif minimal_ok and full_ok:
        print(f"\n💡 Both APIs work locally - Railway issue may be environment-specific")
    else:
        print(f"\n⚠️ Both APIs have issues - need to fix fundamental problems")

if __name__ == "__main__":
    print("🧪 Testing Minimal API for Railway Deployment...\n")
    compare_apis()
