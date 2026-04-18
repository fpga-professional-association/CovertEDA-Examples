#!/usr/bin/env python3
"""Run all cocotb simulation tests across vendors/projects."""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

TB_ROOT = Path(__file__).parent / "tb"

def find_test_dirs():
    """Find all directories containing a Makefile under tb/."""
    tests = []
    for makefile in sorted(TB_ROOT.rglob("Makefile")):
        test_dir = makefile.parent
        parts = test_dir.relative_to(TB_ROOT).parts
        if len(parts) == 2:
            vendor, project = parts
            tests.append((vendor, project, test_dir))
    return tests


def run_test(vendor, project, test_dir):
    """Run a single cocotb test. Returns (vendor, project, success, output)."""
    env = os.environ.copy()
    env["SIM"] = "icarus"
    try:
        result = subprocess.run(
            ["make"],
            cwd=str(test_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        success = False
        output = "TIMEOUT after 300s"
    except Exception as e:
        success = False
        output = str(e)
    return vendor, project, success, output


def main():
    parser = argparse.ArgumentParser(description="Run cocotb simulation tests")
    parser.add_argument("--vendor", help="Only run tests for this vendor")
    parser.add_argument("--project", help="Only run this project")
    parser.add_argument("--parallel", type=int, default=1, help="Parallel jobs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output")
    args = parser.parse_args()

    tests = find_test_dirs()
    if args.vendor:
        tests = [(v, p, d) for v, p, d in tests if v == args.vendor]
    if args.project:
        tests = [(v, p, d) for v, p, d in tests if p == args.project]

    if not tests:
        print("No tests found.")
        sys.exit(1)

    print(f"Found {len(tests)} test(s) to run (parallel={args.parallel})\n")

    results = []
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {
            pool.submit(run_test, v, p, d): (v, p) for v, p, d in tests
        }
        for future in as_completed(futures):
            vendor, project, success, output = future.result()
            status = "PASS" if success else "FAIL"
            print(f"  [{status}] {vendor}/{project}")
            if args.verbose or not success:
                for line in output.strip().splitlines()[-20:]:
                    print(f"        {line}")
            results.append((vendor, project, success))

    # Summary
    passed = sum(1 for *_, s in results if s)
    failed = sum(1 for *_, s in results if not s)
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(results)} total")

    if failed:
        print("\nFailed tests:")
        for v, p, s in results:
            if not s:
                print(f"  - {v}/{p}")
        sys.exit(1)


if __name__ == "__main__":
    main()
