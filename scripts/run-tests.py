#!/usr/bin/env python3
"""
Test Runner for Physical AI Textbook
"""

import sys
import subprocess
import requests
import time
from pathlib import Path
import argparse

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def run_command(cmd, description, timeout=30):
    """Run a command and return success status"""
    print(f"\n[TEST] {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"[PASS] {description} - Success")
            return True
        else:
            print(f"[FAIL] {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description} - Timeout")
        return False
    except Exception as e:
        print(f"[ERROR] {description} - Error: {e}")
        return False


def test_backend():
    """Test backend services"""
    print("\n" + "="*50)
    print("[TEST] Testing Backend Services")
    print("="*50)

    tests = [
        ("curl -s http://localhost:8000/health", "Backend Health Check"),
        ("curl -s http://localhost:8000/", "Backend Root Endpoint"),
        ("curl -s http://localhost:8000/api/v1/content/navigation", "Navigation API"),
        ("curl -s http://localhost:8000/api/v1/content/chapters", "Chapters API"),
    ]

    all_passed = True
    for cmd, desc in tests:
        if not run_command(cmd, desc):
            all_passed = False

    return all_passed


def test_frontend():
    """Test frontend services"""
    print("\n" + "="*50)
    print("[FRONTEND] Testing Frontend Services")
    print("="*50)

    # Check if frontend is running
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("[PASS] Frontend is running")
            print(f"   URL: {FRONTEND_URL}")
            return True
        else:
            print(f"[FAIL] Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Frontend is not running")
        return False
    except Exception as e:
        print(f"[FAIL] Frontend test error: {e}")
        return False


def test_files():
    """Test required files exist"""
    print("\n" + "="*50)
    print("[FILES] Checking Required Files")
    print("="*50)

    # Important files to check
    required_files = [
        "package.json",
        "docusaurus.config.js",
        "sidebars.js",
        ".env",
        "backend/requirements.txt",
        "backend/app/main.py",
        "backend/.env.example",
    ]

    # Content files
    content_files = [
        "docs/introduction.md",
        "docs/chapter-1/lesson-1.mdx",
        "docs/chapter-4/lesson-4.mdx",
    ]

    all_exist = True
    for file_path in required_files + content_files:
        if Path(file_path).exists():
            print(f"[PASS] {file_path}")
        else:
            print(f"[FAIL] {file_path} - Missing!")
            all_exist = False

    return all_exist


def test_dependencies():
    """Test dependencies are installed"""
    print("\n" + "="*50)
    print("[DEPS] Checking Dependencies")
    print("="*50)

    # Check Node.js
    if run_command("node --version", "Node.js Version"):
        # Check npm packages
        if Path("node_modules").exists():
            print("[PASS] Node.js modules installed")
        else:
            print("[WARN]  Node.js modules not installed (run: npm install)")
    else:
        print("[FAIL] Node.js not installed")

    # Check Python
    if run_command("python --version", "Python Version"):
        # Check if backend requirements installed
        backend_req = Path("backend/requirements.txt")
        if backend_req.exists():
            print("[FILE] Backend requirements.txt found")
            print("   Run: pip install -r backend/requirements.txt")
        else:
            print("[FAIL] Backend requirements.txt missing")
    else:
        print("[FAIL] Python not installed")


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Test runner for Physical AI Textbook")
    parser.add_argument("--skip-backend", action="store_true", help="Skip backend tests")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip frontend tests")
    parser.add_argument("--skip-files", action="store_true", help="Skip file checks")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency checks")
    args = parser.parse_args()

    print("\n[TEST] Physical AI & Humanoid Robotics Textbook Test Runner")
    print("="*60)

    all_tests_passed = True

    # Run tests
    if not args.skip_deps:
        test_dependencies()

    if not args.skip_files:
        if not test_files():
            all_tests_passed = False

    if not args.skip_backend:
        if not test_backend():
            all_tests_passed = False

    if not args.skip_frontend:
        if not test_frontend():
            all_tests_passed = False

    # Summary
    print("\n" + "="*60)
    if all_tests_passed:
        print("[PASS] All tests passed!")
        print("\n[SUCCESS] System is ready!")
        print("\nTo start:")
        print("  Backend: cd backend && uvicorn app.main:app --reload")
        print("  Frontend: npm start")
    else:
        print("[FAIL] Some tests failed!")
        print("\nPlease fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()