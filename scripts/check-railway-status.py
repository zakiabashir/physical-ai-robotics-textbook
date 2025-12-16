#!/usr/bin/env python3
"""Check Railway deployment status"""

import requests
import json

RAILWAY_URL = "https://physical-ai-robotics-textbook-production.up.railway.app"

def check_endpoints():
    print("Checking Railway deployment status...")
    print("=" * 60)

    # Check root
    try:
        response = requests.get(f"{RAILWAY_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Root endpoint: {data.get('message')}")
    except:
        print("[FAIL] Root endpoint failed")

    # Check health
    try:
        response = requests.get(f"{RAILWAY_URL}/health")
        if response.status_code == 200:
            print("[OK] Health endpoint: OK")
        else:
            print(f"[FAIL] Health endpoint: {response.status_code}")
    except:
        print("[FAIL] Health endpoint failed")

    # Check auth test
    try:
        response = requests.get(f"{RAILWAY_URL}/api/v1/auth/test")
        if response.status_code == 200:
            print("[OK] Auth test endpoint: Working")
        else:
            print(f"[FAIL] Auth test endpoint: {response.status_code}")
    except:
        print("[FAIL] Auth test endpoint failed")

    # Check available endpoints
    endpoints_to_check = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/docs",
        "/openapi.json"
    ]

    print("\nChecking other endpoints:")
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}")
            if response.status_code != 404:
                print(f"[OK] {endpoint}: {response.status_code}")
            else:
                print(f"[FAIL] {endpoint}: Not Found (404)")
        except Exception as e:
            print(f"[ERROR] {endpoint}: Error - {e}")

if __name__ == "__main__":
    check_endpoints()