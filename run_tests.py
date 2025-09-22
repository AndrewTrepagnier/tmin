#!/usr/bin/env python3
"""
Simple test runner for the TMIN package.
Runs pytest with coverage and produces both terminal and HTML reports.
"""

import subprocess
import sys
from pathlib import Path


def run_tests() -> bool:
    root = Path(__file__).resolve().parent
    print("\nRunning tests for TMIN...\n" + "-" * 50)

    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=tmin",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v"
    ]

    try:
        subprocess.run(cmd, check=True, cwd=root)
    except FileNotFoundError:
        print("pytest is not installed. Try:\n    pip install pytest pytest-cov")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Some tests failed (exit code {e.returncode}).")
        return False

    print("\nAll tests passed.")
    print("Coverage report written to: htmlcov/index.html")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
