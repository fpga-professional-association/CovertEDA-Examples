"""Batch-build all projects for a single vendor (quartus or oss).

Runs sequentially (Quartus synthesis and yosys+nextpnr are CPU-bound and don't
benefit from parallelism on a laptop). Writes a summary file at
reports/summary_<vendor>.txt in repo root.
"""
from __future__ import annotations
import argparse, subprocess, sys, time
from pathlib import Path

def list_projects(root: Path, vendor: str) -> list[str]:
    d = root / vendor
    return sorted(p.name for p in d.iterdir() if p.is_dir())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vendor", choices=["quartus", "oss"])
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--only", nargs="*", help="only build these projects")
    args = ap.parse_args()

    root = Path.cwd()
    script = root / "scripts" / f"run_{args.vendor}_project.py"
    if not script.exists():
        print(f"missing {script}")
        sys.exit(1)

    projects = list_projects(root, args.vendor)
    if args.only:
        projects = [p for p in projects if p in args.only]
    projects = [p for p in projects if p != "README.txt"]

    print(f"=== Batch {args.vendor.upper()} — {len(projects)} projects ===\n")
    t0 = time.time()
    results = []
    for i, proj in enumerate(projects, 1):
        t_start = time.time()
        try:
            r = subprocess.run(
                [sys.executable, str(script), proj, "--timeout", str(args.timeout)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=args.timeout + 60,
            )
            line = (r.stdout or "").strip().splitlines()[-1] if r.stdout else "no-output"
            ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            line = f"[FAIL] {proj}  timeout"
            ok = False
        dt = time.time() - t_start
        print(f"  [{i:2d}/{len(projects)}]  {line}")
        results.append((proj, ok, dt))

    total = time.time() - t0
    pass_count = sum(1 for _, ok, _ in results if ok)
    fail_count = len(results) - pass_count

    summary = [
        f"{args.vendor.upper()} build summary",
        f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        f"Total:   {len(results)}",
        f"PASS:    {pass_count}",
        f"FAIL:    {fail_count}",
        f"Runtime: {total:.1f}s",
        "=" * 50,
        "",
    ]
    for proj, ok, dt in results:
        summary.append(f"  {'PASS' if ok else 'FAIL'}  {proj:30s}  {dt:6.1f}s")

    out = root / f"{args.vendor}_reports_summary.txt"
    out.write_text("\n".join(summary) + "\n")
    print(f"\n=== Wrote {out.name} ===")
    print(f"PASS: {pass_count}/{len(results)}  in {total:.1f}s")


if __name__ == "__main__":
    main()
