#!/usr/bin/env python3
"""
RBAC Test Runner for AI Adventure API

This script runs the comprehensive RBAC (Role-Based Access Control) tests
to verify that user permissions are working correctly.
"""

import subprocess
import sys
import os

def run_tests():
    """Run the RBAC tests"""
    print("🧪 Running RBAC Tests for AI Adventure API")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("tests/test_rbac_adventure_access.py"):
        print("❌ Error: test_rbac_adventure_access.py not found!")
        print("   Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Run the RBAC tests
    print("📋 Running Role-Based Access Control Tests...")
    print()
    
    try:
        # Run pytest with the RBAC test file
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_rbac_adventure_access.py",
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--color=yes"  # Colored output
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print()
            print("✅ All RBAC tests passed!")
            print("🎉 Role-based access control is working correctly.")
        else:
            print()
            print("❌ Some RBAC tests failed!")
            print("🔍 Check the output above for details.")
            sys.exit(result.returncode)
            
    except FileNotFoundError:
        print("❌ Error: pytest not found!")
        print("   Please install pytest: pip install pytest pytest-asyncio")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

def run_specific_test_category(category):
    """Run tests for a specific category"""
    categories = {
        "adventure": "TestRBACAdventureAccess",
        "ownership": "TestAdventureOwnershipValidation", 
        "user_management": "TestUserManagementRBAC"
    }
    
    if category not in categories:
        print(f"❌ Unknown test category: {category}")
        print(f"   Available categories: {', '.join(categories.keys())}")
        sys.exit(1)
    
    test_class = categories[category]
    print(f"🧪 Running {test_class} tests...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            f"tests/test_rbac_adventure_access.py::{test_class}",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_class} tests passed!")
        else:
            print(f"❌ {test_class} tests failed!")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"❌ Error running {category} tests: {e}")
        sys.exit(1)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        run_specific_test_category(category)
    else:
        run_tests()

if __name__ == "__main__":
    main()
