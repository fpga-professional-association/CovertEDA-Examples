"""Run Quartus Prime Pro on a single project and capture reports.

Usage:
  python run_quartus_project.py <project_name>
Assumes CWD is the CovertEDA-Examples root.

Each project lives at:
  quartus/<name>/constraints/*.qsf   - project file (with family/device/top-entity)
  quartus/<name>/constraints/*.sdc   - timing constraints
  quartus/<name>/src/*.v             - RTL

We create a scratch build dir under quartus/<name>/.build/ that mirrors the project,
runs quartus_sh -t flow-compile.tcl, and then copies the output reports back into
quartus/<name>/reports/.
"""
from __future__ import annotations
import argparse, os, re, shutil, subprocess, sys, time
from pathlib import Path

QUARTUS_BIN = r"C:\altera_pro\25.3\quartus\bin64"
QUARTUS_SH  = Path(QUARTUS_BIN) / "quartus_sh.exe"

def read_qsf(qsf_path: Path):
    """Pull family, device, top-level entity out of the existing QSF."""
    family = device = top = None
    sdc_files = []
    for line in qsf_path.read_text().splitlines():
        m = re.search(r'set_global_assignment\s+-name\s+FAMILY\s+"([^"]+)"', line)
        if m: family = m.group(1)
        m = re.search(r'set_global_assignment\s+-name\s+DEVICE\s+(\S+)', line)
        if m: device = m.group(1)
        m = re.search(r'set_global_assignment\s+-name\s+TOP_LEVEL_ENTITY\s+(\S+)', line)
        if m: top = m.group(1)
        m = re.search(r'set_global_assignment\s+-name\s+SDC_FILE\s+(\S+)', line)
        if m: sdc_files.append(m.group(1))
    return family, device, top, sdc_files


def build(project: str, root: Path, timeout: int = 600) -> tuple[bool, str]:
    proj_dir = root / "quartus" / project
    if not proj_dir.exists():
        return False, f"project dir missing: {proj_dir}"

    src_files = list((proj_dir / "src").glob("*.v")) + list((proj_dir / "src").glob("*.sv"))
    constr_dir = proj_dir / "constraints"
    qsf_files = list(constr_dir.glob("*.qsf"))
    if not qsf_files:
        return False, "no .qsf in constraints/"

    qsf = qsf_files[0]
    family, device, top, sdc_refs = read_qsf(qsf)
    if not (family and device and top):
        return False, f"qsf missing family/device/top: {family}/{device}/{top}"

    sdc_files = list(constr_dir.glob("*.sdc"))

    # Scratch build area
    build_dir = proj_dir / ".build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()

    # Copy sources + constraints into build_dir
    for s in src_files:
        shutil.copy2(s, build_dir / s.name)
    for s in sdc_files:
        shutil.copy2(s, build_dir / s.name)

    proj_name = project
    qpf = build_dir / f"{proj_name}.qpf"
    qsf_new = build_dir / f"{proj_name}.qsf"

    # Write minimal QPF
    qpf.write_text(f'QUARTUS_VERSION = "25.3"\nDATE = "{time.strftime("%H:%M:%S  %b %d, %Y")}"\nPROJECT_REVISION = "{proj_name}"\n')

    # Write QSF
    qsf_lines = [
        f'set_global_assignment -name FAMILY "{family}"',
        f'set_global_assignment -name DEVICE {device}',
        f'set_global_assignment -name TOP_LEVEL_ENTITY {top}',
        f'set_global_assignment -name ORIGINAL_QUARTUS_VERSION 25.3.0',
        f'set_global_assignment -name LAST_QUARTUS_VERSION "25.3.0 Pro Edition"',
        f'set_global_assignment -name PROJECT_OUTPUT_DIRECTORY output_files',
        f'set_global_assignment -name NUM_PARALLEL_PROCESSORS 4',
    ]
    for s in src_files:
        qsf_lines.append(f'set_global_assignment -name VERILOG_FILE {s.name}')
    for s in sdc_files:
        qsf_lines.append(f'set_global_assignment -name SDC_FILE {s.name}')
    qsf_new.write_text("\n".join(qsf_lines) + "\n")

    # Synthesis-only flow. Full compile (fitter + STA) fails on these
    # example designs because pin assignments are intentionally left out so
    # projects are device-agnostic. Synthesis alone gives us LUT/FF/BRAM/DSP
    # utilization at the RTL-elaboration level, which is what the existing
    # repo baselines (commit 1feff42 "Quartus 19/19") verified.
    flow_tcl = build_dir / "run_flow.tcl"
    flow_tcl.write_text(
        f'load_package flow\n'
        f'project_open {proj_name}\n'
        f'execute_module -tool syn\n'
        f'project_close\n'
    )

    log_file = build_dir / "run.log"
    env = os.environ.copy()
    env["PATH"] = QUARTUS_BIN + os.pathsep + env.get("PATH", "")

    try:
        proc = subprocess.run(
            [str(QUARTUS_SH), "-t", "run_flow.tcl"],
            cwd=str(build_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        log_file.write_text((proc.stdout or "") + "\n--- STDERR ---\n" + (proc.stderr or ""))
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        log_file.write_text("TIMEOUT")
        return False, f"TIMEOUT after {timeout}s"

    # Collect reports
    reports_out = proj_dir / "reports"
    reports_out.mkdir(exist_ok=True)
    # Clear old reports
    for f in reports_out.iterdir():
        f.unlink()

    out = build_dir / "output_files"
    mapping = {
        f"{proj_name}.syn.rpt":         "synthesis.rpt",
        f"{proj_name}.syn.summary":     "synthesis.summary",
        f"{proj_name}.map.rpt":         "synthesis.map.rpt",
        f"{proj_name}.syn.ae.rpt":      "synthesis.analysis_elab.rpt",
        f"{proj_name}.flow.rpt":        "flow.rpt",
    }
    copied = 0
    for src_name, dst_name in mapping.items():
        src = out / src_name
        if src.exists():
            shutil.copy2(src, reports_out / dst_name)
            copied += 1
    # Always save log
    shutil.copy2(log_file, reports_out / "build.log")

    # Also save a summary
    summary = reports_out / "build_summary.txt"
    summary.write_text(
        f"Project:   {project}\n"
        f"Family:    {family}\n"
        f"Device:    {device}\n"
        f"Top:       {top}\n"
        f"Quartus:   25.3 Pro\n"
        f"Status:    {'PASS' if ok else 'FAIL'}\n"
        f"Reports:   {copied}\n"
    )

    # Clean build dir to save space
    shutil.rmtree(build_dir, ignore_errors=True)

    return ok, f"copied {copied} reports"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    root = Path.cwd()
    t0 = time.time()
    ok, msg = build(args.project, root, timeout=args.timeout)
    dt = time.time() - t0
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {args.project:30s}  {dt:6.1f}s  {msg}")
    sys.exit(0 if ok else 1)
