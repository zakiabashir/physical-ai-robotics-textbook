#!/usr/bin/env python3
"""
Complete Authentication System Test
Tests all authentication endpoints and functionality
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"  # Change to Railway URL when testing live

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_test(name, status, details=""):
    """Print test result"""
    status_symbol = "[PASS]" if status else "[FAIL]"
    print(f"\n{status_symbol} {name}")
    if details:
        print(f"   {details}")

def test_health_endpoint():
    """Test health endpoint"""
    print_header("Testing Health Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", True, f"Status: {data.get('status')}")
            return True
        else:
            print_test("Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_user_registration():
    """Test user registration"""
    print_header("Testing User Registration")

    # Test unique username
    username = f"testuser_{int(time.time())}"
    email = f"{username}@example.com"
    password = "testpass123"

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            params={
                "username": username,
                "password": password,
                "email": email
            }
        )

        if response.status_code == 201:
            print_test("User Registration", True, f"User {username} created")
            return username, password
        else:
            print_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print_test("User Registration", False, str(e))
        return None, None

def test_duplicate_registration(username, password):
    """Test duplicate registration fails"""
    print_header("Testing Duplicate Registration Prevention")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            params={
                "username": username,
                "password": password,
                "email": "different@example.com"
            }
        )

        if response.status_code == 400:
            print_test("Duplicate Prevention", True, "Correctly rejected duplicate username")
            return True
        else:
            print_test("Duplicate Prevention", False, f"Should have returned 400, got {response.status_code}")
            return False
    except Exception as e:
        print_test("Duplicate Prevention", False, str(e))
        return False

def test_user_login(username, password):
    """Test user login"""
    print_header("Testing User Login")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_test("User Login", True, "JWT token received")
                return token
            else:
                print_test("User Login", False, "No token in response")
                return None
        else:
            print_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_test("User Login", False, str(e))
        return None

def test_invalid_credentials():
    """Test login with invalid credentials"""
    print_header("Testing Invalid Credentials")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={
                "username": "nonexistent_user",
                "password": "wrongpassword"
            }
        )

        if response.status_code == 401:
            print_test("Invalid Credentials", True, "Correctly rejected invalid login")
            return True
        else:
            print_test("Invalid Credentials", False, f"Should have returned 401, got {response.status_code}")
            return False
    except Exception as e:
        print_test("Invalid Credentials", False, str(e))
        return False

def test_protected_endpoint(token):
    """Test access to protected endpoint with token"""
    print_header("Testing Protected Endpoint Access")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test /me endpoint
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_test("Protected Endpoint", True, f"User data retrieved: {data.get('username')}")
            return True
        else:
            print_test("Protected Endpoint", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("Protected Endpoint", False, str(e))
        return False

def test_unauthorized_access():
    """Test access without token"""
    print_header("Testing Unauthorized Access Prevention")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me")

        if response.status_code == 401:
            print_test("Unauthorized Prevention", True, "Correctly required authentication")
            return True
        else:
            print_test("Unauthorized Prevention", False, f"Should have returned 401, got {response.status_code}")
            return False
    except Exception as e:
        print_test("Unauthorized Prevention", False, str(e))
        return False

def test_logout(token):
    """Test user logout"""
    print_header("Testing User Logout")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers)

        if response.status_code == 200:
            print_test("User Logout", True, "Logout successful")
            return True
        else:
            print_test("User Logout", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("User Logout", False, str(e))
        return False

def main():
    """Run all tests"""
    print("Complete Authentication System Test")
    print("==================================")

    # Track test results
    test_results = []

    # Test health
    test_results.append(("Health Check", test_health_endpoint()))

    # Test registration
    username, password = test_user_registration()
    test_results.append(("User Registration", username is not None))

    if username and password:
        # Test duplicate registration
        test_results.append(("Duplicate Prevention", test_duplicate_registration(username, password)))

        # Test login
        token = test_user_login(username, password)
        test_results.append(("User Login", token is not None))

        # Test invalid credentials
        test_results.append(("Invalid Credentials", test_invalid_credentials()))

        if token:
            # Test protected endpoint
            test_results.append(("Protected Endpoint", test_protected_endpoint(token)))

            # Test logout
            test_results.append(("User Logout", test_logout(token)))

        # Test unauthorized access
        test_results.append(("Unauthorized Prevention", test_unauthorized_access()))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status_symbol = "[PASS]" if result else "[FAIL]"
        print(f"{status_symbol} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Authentication system is working correctly.")
        return 0
    else:
        print(f"\n[ERROR] {total - passed} test(s) failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    # Check if Railway URL is provided as argument
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Testing Railway deployment at: {BASE_URL}")

    exit_code = main()
    sys.exit(exit_code)