#!/usr/bin/env python3
"""
Monitor Railway deployment status
This script will check if the latest version is deployed
"""

import requests
import time
import json
from datetime import datetime

RAILWAY_URL = "https://physical-ai-robotics-textbook-production.up.railway.app"
EXPECTED_MESSAGE = "Physical AI & Humanoid Robotics Textbook API - Auth Only"
CHECK_INTERVAL = 30  # seconds
MAX_CHECKS = 20

def check_deployment():
    """Check if Railway has deployed the latest version"""
    print(f"\n{'='*60}")
    print(f"Checking Railway deployment at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {RAILWAY_URL}")
    print(f"{'='*60}\n")

    try:
        # Check root endpoint
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            current_message = data.get("message", "Unknown")

            print(f"Current API Message: {current_message}")
            print(f"Expected Message: {EXPECTED_MESSAGE}")

            if current_message == EXPECTED_MESSAGE:
                print("\n✅ SUCCESS: Latest version is deployed!")
                return True
            else:
                print("\n⏳ Waiting for deployment...")
                return False
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")
        return False

def check_auth_endpoints():
    """Check if auth endpoints are available"""
    print("\nChecking authentication endpoints...")

    endpoints = [
        ("/api/v1/auth/test", "GET"),
        ("/health", "GET")
    ]

    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=10)

            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - Working")
            else:
                print(f"❌ {method} {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")

def main():
    """Main monitoring function"""
    print("Railway Deployment Monitor")
    print("This script will monitor the Railway deployment")
    print("Press Ctrl+C to stop monitoring\n")

    check_count = 0

    while check_count < MAX_CHECKS:
        check_count += 1

        if check_deployment():
            # If deployment is successful, test auth endpoints
            check_auth_endpoints()
            print("\n🎉 Deployment complete and endpoints are working!")
            break

        if check_count < MAX_CHECKS:
            print(f"\n⏱️ Waiting {CHECK_INTERVAL} seconds before next check...")
            time.sleep(CHECK_INTERVAL)

    if check_count >= MAX_CHECKS:
        print(f"\n⚠️ Maximum checks ({MAX_CHECKS}) reached.")
        print("Please check the Railway dashboard for deployment status.")
        print("\nTo manually trigger a redeploy:")
        print("1. Go to Railway Dashboard")
        print("2. Find your project")
        print("3. Click on the service")
        print("4. Click 'Settings' tab")
        print("5. Click 'Redeploy' button")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError: {e}")