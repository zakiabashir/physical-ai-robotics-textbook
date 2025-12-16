#!/usr/bin/env python3
"""
Monitor Railway minimal deployment
This checks if the minimal server deploys successfully
"""

import requests
import time
from datetime import datetime

RAILWAY_URL = "https://physical-ai-robotics-textbook-production.up.railway.app"
EXPECTED_MESSAGE = "Minimal API is running"

def check_minimal_deployment():
    """Check if minimal server is deployed"""
    print(f"\n{'='*60}")
    print(f"Checking minimal server deployment at {datetime.now()}")
    print(f"URL: {RAILWAY_URL}")
    print(f"{'='*60}\n")

    try:
        # Check root endpoint
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            current_message = data.get("message", "Unknown")

            print(f"✅ Server is responding!")
            print(f"Message: {current_message}")

            if EXPECTED_MESSAGE in current_message:
                print("\n🎉 SUCCESS: Minimal server is deployed!")
                print("\nTesting endpoints:")

                # Test health endpoint
                health_response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
                print(f"  Health (/health): {health_response.status_code} - {health_response.json()}")

                # Test auth test endpoint
                auth_response = requests.get(f"{RAILWAY_URL}/api/v1/auth/test", timeout=10)
                print(f"  Auth Test (/api/v1/auth/test): {auth_response.status_code} - {auth_response.json()}")

                return True
            else:
                print(f"\n⚠️ Different version deployed. Expected: {EXPECTED_MESSAGE}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - Service might be starting up...")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - Service not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Monitor deployment"""
    print("Railway Minimal Server Deployment Monitor")
    print("========================================")

    max_checks = 20
    check_interval = 30

    for i in range(max_checks):
        print(f"\nCheck #{i+1}/{max_checks}")

        if check_minimal_deployment():
            print("\n✅ Minimal server deployed successfully!")
            print("\nNext steps:")
            print("1. The minimal server is working - Railway can deploy successfully")
            print("2. Now we can switch back to the auth server")
            print("3. The issue was likely with the auth server startup")
            break

        if i < max_checks - 1:
            print(f"\n⏳ Waiting {check_interval} seconds...")
            time.sleep(check_interval)

    if i == max_checks - 1:
        print(f"\n❌ Deployment failed after {max_checks} checks")
        print("\nTroubleshooting:")
        print("1. Check Railway dashboard for build logs")
        print("2. Verify Dockerfile is correct")
        print("3. Check if all dependencies are installed")

if __name__ == "__main__":
    main()