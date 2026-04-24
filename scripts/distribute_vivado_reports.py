"""Move real Vivado reports from vivado_reports/ into each vivado/<project>/reports/.
Overwrites the stub files. Removes the unrealistic power/drc/io stub reports.
"""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent
src_dir = root / "vivado_reports"
proj_root = root / "vivado"

projects = sorted(p.name for p in proj_root.iterdir() if p.is_dir())
print(f"Found {len(projects)} vivado projects")

moved = 0
for proj in projects:
    src_timing = src_dir / f"{proj}_timing.rpt"
    src_util = src_dir / f"{proj}_utilization.rpt"
    dst_dir = proj_root / proj / "reports"
    dst_dir.mkdir(exist_ok=True)

    if src_timing.exists():
        shutil.copy2(src_timing, dst_dir / "timing_summary.rpt")
        moved += 1
    else:
        print(f"  MISSING timing: {proj}")
    if src_util.exists():
        shutil.copy2(src_util, dst_dir / "utilization.rpt")
        moved += 1
    else:
        print(f"  MISSING util: {proj}")

    # Remove the stub files that weren't actually produced by Vivado run
    for stub in ("power.rpt", "drc.rpt", "io.rpt"):
        f = dst_dir / stub
        if f.exists():
            f.unlink()

print(f"Copied {moved} real reports.")
