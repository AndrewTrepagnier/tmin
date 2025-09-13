#!/usr/bin/env python3
"""
Simple test runner for TMIN package
"""
import subprocess
import sys
import os

def run_tests():
    """Run the test suite"""
    print("🧪 Running TMIN Test Suite")
    print("=" * 50)
    
    # Change to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run pytest with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "--cov=tmin", 
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v"
        ], check=True)
        
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-cov")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
