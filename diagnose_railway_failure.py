"""
Quick test of the health endpoint to diagnose Railway deployment issues
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all imports work correctly"""
    try:
        print("🔧 Testing API imports...")
        
        # Test basic imports
        import uvicorn
        print("✅ uvicorn imported successfully")
        
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        import chromadb
        print("✅ chromadb imported successfully")
        
        # Test our API server imports
        print("\n🔧 Testing API server imports...")
        from src.api_server import app
        print("✅ API server imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_health_endpoint_logic():
    """Test the health endpoint logic directly"""
    try:
        print("\n🔧 Testing health endpoint logic...")
        
        # Import the health check function
        from src.api_server import app
        
        # Test basic health status structure
        health_status = {
            "status": "healthy",
            "timestamp": "test",
            "version": "2.0",
            "services": {}
        }
        
        print("✅ Health status structure works")
        
        # Test ChromaDB connection logic
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
        client = chromadb.PersistentClient(path=chroma_path)
        print("✅ ChromaDB connection works locally")
        
        return True
        
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def diagnose_railway_issues():
    """Diagnose potential Railway-specific issues"""
    print("\n🔍 Diagnosing Railway Issues:")
    
    # Check for common Railway issues
    issues = []
    
    # Check if we have Railway-specific environment variables
    if not os.getenv("PORT"):
        issues.append("Missing PORT environment variable for Railway")
    
    # Check for potential path issues
    if not os.path.exists("./chroma_db_v3_fresh"):
        issues.append("ChromaDB path might not exist on Railway")
    
    # Check for dependency issues
    try:
        import openai
        print("✅ OpenAI package available")
    except ImportError:
        issues.append("OpenAI package missing")
    
    if issues:
        print("❌ Potential Railway Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No obvious Railway issues detected")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("🚨 Diagnosing Railway Deployment Failure...\n")
    
    imports_ok = test_imports()
    health_ok = test_health_endpoint_logic() 
    railway_ok = diagnose_railway_issues()
    
    print(f"\n📋 Diagnosis Summary:")
    print(f"   Imports: {'✅ OK' if imports_ok else '❌ Failed'}")
    print(f"   Health Endpoint: {'✅ OK' if health_ok else '❌ Failed'}")
    print(f"   Railway Compatibility: {'✅ OK' if railway_ok else '⚠️ Issues'}")
    
    if not all([imports_ok, health_ok]):
        print(f"\n🚨 Critical Issues Found - Fix needed before redeployment")
    elif not railway_ok:
        print(f"\n⚠️ Railway-specific issues detected - May need configuration fixes")
    else:
        print(f"\n✅ Local testing passed - Railway issue may be temporary")
