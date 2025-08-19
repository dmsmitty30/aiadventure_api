#!/usr/bin/env python3
"""
Test runner script for the AI Adventure API.
Run this script to execute all tests or specific test categories.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for AI Adventure API")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "coverage", "lint", "format"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--pattern", 
        default="",
        help="Pattern to match test files (e.g., 'test_admin')"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("Error: Please run this script from the project root directory")
        print("Expected to find 'app' directory")
        sys.exit(1)
    
    # Check if tests directory exists
    if not Path("tests").exists():
        print("Error: Tests directory not found")
        print("Please ensure you have a 'tests' directory with test files")
        sys.exit(1)
    
    success = True
    
    if args.type == "all" or args.type == "unit":
        # Run unit tests
        test_command = ["python", "-m", "pytest"]
        if args.pattern:
            test_command.extend(["-k", args.pattern])
        if args.verbose:
            test_command.append("-v")
        
        success &= run_command(test_command, "Unit Tests")
    
    if args.type == "all" or args.type == "coverage":
        # Run tests with coverage
        coverage_command = [
            "python", "-m", "pytest", 
            "--cov=app", 
            "--cov-report=term-missing",
            "--cov-report=html"
        ]
        if args.pattern:
            coverage_command.extend(["-k", args.pattern])
        
        success &= run_command(coverage_command, "Tests with Coverage")
    
    if args.type == "all" or args.type == "lint":
        # Run linting
        lint_commands = [
            (["python", "-m", "flake8", "app", "tests"], "Flake8 Linting"),
            (["python", "-m", "black", "--check", "app", "tests"], "Black Format Check"),
            (["python", "-m", "isort", "--check-only", "app", "tests"], "Import Sort Check")
        ]
        
        for command, description in lint_commands:
            success &= run_command(command, description)
    
    if args.type == "all" or args.type == "format":
        # Run code formatting
        format_commands = [
            (["python", "-m", "black", "app", "tests"], "Black Code Formatting"),
            (["python", "-m", "isort", "app", "tests"], "Import Sorting")
        ]
        
        for command, description in format_commands:
            success &= run_command(command, description)
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests and checks completed successfully!")
    else:
        print("❌ Some tests or checks failed. Please review the output above.")
    print('='*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 