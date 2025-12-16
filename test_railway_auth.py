#!/usr/bin/env python3
"""
Test script to verify Railway authentication endpoints
Run this after Railway has deployed the latest version
"""

import requests
import json

BASE_URL = "https://physical-ai-robotics-textbook-production.up.railway.app"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("Testing authentication endpoints...")

    # Test endpoint
    print("1. Testing /api/v1/auth/test")
    response = requests.get(f"{BASE_URL}/api/v1/auth/test")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

    # Register user
    print("2. Testing user registration")
    register_data = {
        "username": "testuser_railway",
        "password": "testpass123",
        "email": "testrailway@example.com"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        params=register_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

    # Login user
    print("3. Testing user login")
    login_data = {
        "username": "testuser_railway",
        "password": "testpass123"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        params=login_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        login_response = response.json()
        print(f"Response: {json.dumps(login_response, indent=2)}")

        # Test protected endpoint with token
        if "access_token" in login_response:
            print("\n4. Testing protected endpoint with token")
            headers = {
                "Authorization": f"Bearer {login_response['access_token']}"
            }
            response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Railway Authentication Endpoint Test")
    print("=" * 50)
    test_health()
    test_auth_endpoints()