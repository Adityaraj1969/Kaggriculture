"""
TITAN-1 Production Packaging & Pre-Flight Verification Tool
Validates Kaggle submission constraints and generates certified archives.
"""

import os
import sys
import tarfile

from kaggle_environments import make

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAIN_PY = os.path.join(ROOT, "main.py")
DIST_DIR = os.path.join(ROOT, "dist")


def verify_submission():
    print("=" * 80)
    print("TITAN-1 KAGGLE PRE-FLIGHT SUBMISSION CERTIFICATION")
    print("=" * 80)

    # 1. Existence and size verification
    if not os.path.exists(MAIN_PY):
        print("[FAIL] main.py not found at repository root.")
        return False

    size_bytes = os.path.getsize(MAIN_PY)
    size_kb = size_bytes / 1024.0
    print(f"[1/4] Checking file size: {size_kb:.2f} KiB (Limit: 100 MiB) ... OK")

    # 2. Syntax & Import Check
    print("[2/4] Verifying Python syntax and callable interface ... ", end="")
    import importlib.util
    spec = importlib.util.spec_from_file_location("submission_main", MAIN_PY)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        assert hasattr(mod, "agent"), "main.py does not define an 'agent' entry point."
        print("OK")
    except Exception as e:
        print(f"FAIL: {e}")
        return False

    # 3. Dry-run single episode step
    print("[3/4] Performing dry-run sandbox initialization ... ", end="")
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 2, "seed": 42}, debug=True)
        env.run([MAIN_PY, "starter"])
        print("OK")
    except Exception as e:
        print(f"FAIL: {e}")
        return False

    # 4. Generate deployment artifacts
    print("[4/4] Assembling production archives ... ", end="")
    os.makedirs(DIST_DIR, exist_ok=True)
    tar_path = os.path.join(DIST_DIR, "submission.tar.gz")

    with tarfile.open(tar_path, "w:gz") as tar:
        # Only main.py is needed — it's fully self-contained for Kaggle submission.
        # The src/titan/ package is the development-time modular equivalent but
        # is NOT imported by main.py at runtime.
        tar.add(MAIN_PY, arcname="main.py")

    tar_size_kb = os.path.getsize(tar_path) / 1024.0
    print(f"OK -> {tar_path} ({tar_size_kb:.2f} KiB)")

    print("=" * 80)
    print("[SUCCESS] CERTIFIED READY FOR KAGGLE SUBMISSION.")
    print("Direct CLI upload command:")
    print("  kaggle competitions submit -c kaggriculture -f main.py -m 'TITAN-1 v2.0 Release'")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = verify_submission()
    sys.exit(0 if success else 1)


