#!/usr/bin/env python3
"""
Test TMIN in a fresh environment: build a wheel, install into a new venv,
run from an empty directory (no examples/) to verify bundled template + example.

Works on Windows and Mac/Linux. From repo root:

  python scripts/test_fresh_install.py

or:

  py -3 scripts/test_fresh_install.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def run(
    cmd: list,
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
) -> subprocess.CompletedProcess:
    kw = {"cwd": cwd, "check": True, "capture_output": True, "text": True}
    if env is not None:
        kw["env"] = {**os.environ, **env}
    return subprocess.run(cmd, **kw)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    work = Path(tempfile.mkdtemp(prefix="tmin_fresh_"))
    try:
        print(f"=== Fresh install test: {work} ===")
        wheels_dir = work / "wheels"
        wheels_dir.mkdir()

        # 1. Build wheel (use current Python)
        print("1. Building wheel...")
        run([sys.executable, "-m", "pip", "install", "-q", "build"], cwd=repo_root)
        run([sys.executable, "-m", "build", "--wheel", "-q", "-o", str(wheels_dir)], cwd=repo_root)
        wheels = list(wheels_dir.glob("*.whl"))
        if not wheels:
            print("FAIL: no wheel produced")
            return 1
        print(f"   Built: {wheels[0].name}")

        # 2. Fresh venv
        print("2. Creating fresh venv...")
        venv = work / "venv"
        run([sys.executable, "-m", "venv", str(venv)])
        if (venv / "Scripts" / "python.exe").exists():
            py = venv / "Scripts" / "python.exe"
            pip = venv / "Scripts" / "pip.exe"
        else:
            py = venv / "bin" / "python"
            pip = venv / "bin" / "pip"

        # 3. Install wheel into venv (no repo on sys.path)
        print("3. Installing tmin into venv...")
        run([str(pip), "install", "-q", str(wheels[0])])

        # 4. Run from empty dir (no examples/ -> must use bundled data)
        run_here = work / "run_here"
        run_here.mkdir()
        print("4. Running tmin from empty directory (bundled example)...")
        env = os.environ.copy()
        env["PATH"] = os.pathsep.join([str(py.parent), env.get("PATH", "")])
        run([str(py), "-m", "tmin.report"], cwd=run_here, env=env)

        # 5. Check output
        print("5. Checking output...")
        memo = run_here / "output" / "engineering_memorandum.txt"
        if not memo.exists():
            print("FAIL: engineering_memorandum.txt not created")
            return 1
        if memo.stat().st_size == 0:
            print("FAIL: memorandum is empty")
            return 1
        text = memo.read_text(encoding="utf-8")
        if "ENGINEERING MEMORANDUM" not in text:
            print("FAIL: memorandum content unexpected")
            return 1
        print("   OK: output/engineering_memorandum.txt exists with content")
        print("=== Fresh install test PASSED ===")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"FAIL: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return 1
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
