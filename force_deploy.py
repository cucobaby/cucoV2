#!/usr/bin/env python3
"""
Force push improvements to Railway
"""
import subprocess
import sys
import requests
import time

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=r'e:\VSCODE\cucoV2')
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        return False

def main():
    print("🔄 Checking git status and forcing deployment...")
    
    # Check current status
    print("\n1. Checking git status:")
    run_command("git status")
    
    print("\n2. Checking recent commits:")
    run_command("git log --oneline -5")
    
    print("\n3. Adding all changes:")
    run_command("git add .")
    
    print("\n4. Committing with timestamp:")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    run_command(f'git commit -m "Force deploy enhanced question answering - {timestamp}"')
    
    print("\n5. Force pushing to Railway:")
    success = run_command("git push --force origin main")
    
    if success:
        print("\n✅ Push successful! Waiting for Railway to deploy...")
        
        # Wait and test
        print("Waiting 30 seconds for deployment...")
        time.sleep(30)
        
        print("\n6. Testing live API:")
        try:
            response = requests.get('https://cucov2-production.up.railway.app/health', timeout=10)
            print(f"Health check: {response.status_code}")
            
            # Test the question endpoint
            test_response = requests.post(
                'https://cucov2-production.up.railway.app/ask-question',
                json={'question': 'what is glycolysis', 'source': 'test'},
                timeout=15
            )
            print(f"Question test: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("✅ Enhanced question answering is now live!")
            else:
                print("⚠️  API responding but may still be using old version")
                
        except Exception as e:
            print(f"❌ Error testing API: {e}")
    else:
        print("❌ Push failed!")

if __name__ == "__main__":
    main()
