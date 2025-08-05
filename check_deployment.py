#!/usr/bin/env python3
import requests
import json
import subprocess
import time

def check_deployment_status():
    print("🔍 Checking Railway deployment status...")
    
    try:
        # Check current git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='.')
        if result.stdout.strip():
            print("⚠️ Uncommitted changes detected")
            print(result.stdout)
        
        # Check if we're ahead of origin
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD', '^origin/main'], 
                              capture_output=True, text=True, cwd='.')
        commits_ahead = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        
        if commits_ahead > 0:
            print(f"⚠️ Local branch is {commits_ahead} commits ahead of origin")
            print("🚀 Attempting to push to Railway...")
            
            push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                       capture_output=True, text=True, cwd='.')
            if push_result.returncode == 0:
                print("✅ Successfully pushed to Railway")
                print("⏳ Waiting 30 seconds for Railway to deploy...")
                time.sleep(30)
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                return False
        else:
            print("✅ Local and remote are in sync")
        
        # Test the API
        print("\n📡 Testing Railway API...")
        response = requests.get('https://cucov2-production.up.railway.app/health', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {response.status_code}")
            print(f"📦 API Version: {data.get('version', 'unknown')}")
            print(f"⏰ Timestamp: {data.get('timestamp', 'unknown')}")
            
            # Quick test of question endpoint
            test_response = requests.post(
                'https://cucov2-production.up.railway.app/ask-question',
                json={'question': 'test question', 'source': 'test'},
                timeout=15
            )
            
            print(f"❓ Question endpoint: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("🎉 All improvements should now be live!")
                return True
            else:
                print("⚠️ Question endpoint issue")
                return False
        else:
            print(f"❌ API not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_deployment_status()
    if success:
        print("\n✨ Railway deployment verified successfully!")
        print("🧪 Try asking 'what is glycolysis' again - you should see improvements!")
    else:
        print("\n⚠️ Deployment may not be complete. Please wait a few more minutes.")
