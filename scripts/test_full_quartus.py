"""Run a FULL Quartus compile (syn + fit + sta + asm) on one project to
verify the virtual-pin setup actually makes the fitter succeed.
"""
from run_quartus_project import QUARTUS_SH, read_qsf
import os, shutil, subprocess, sys, time
from pathlib import Path

def main(project: str = "blinky_led"):
    root = Path.cwd()
    proj_dir = root / "quartus" / project
    qsf_path = proj_dir / f"{project}.qsf"
    family, device, top, _ = read_qsf(qsf_path)

    build_dir = proj_dir / ".build_full"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    # Copy all sources
    for f in (proj_dir / "src").rglob("*"):
        if f.is_file():
            shutil.copy2(f, build_dir / f.name)
    for f in (proj_dir / "constraints").glob("*.sdc"):
        shutil.copy2(f, build_dir / f.name)
    # Copy QSF and rename it so the flow finds it
    shutil.copy2(qsf_path, build_dir / f"{project}.qsf")
    # Minimal QPF
    (build_dir / f"{project}.qpf").write_text(f'PROJECT_REVISION = "{project}"\n')

    tcl = build_dir / "run.tcl"
    tcl.write_text(
        f'load_package flow\n'
        f'project_open {project}\n'
        f'execute_flow -compile\n'
        f'project_close\n'
    )

    env = os.environ.copy()
    # Prepend Quartus bin to PATH if QUARTUS_BIN is set, so the subprocess can
    # find quartus_sh without requiring a system-wide PATH change.
    quartus_bin = os.environ.get("QUARTUS_BIN")
    if quartus_bin and Path(quartus_bin).is_dir():
        env["PATH"] = quartus_bin + os.pathsep + env.get("PATH", "")

    t0 = time.time()
    result = subprocess.run(
        [str(QUARTUS_SH), "-t", "run.tcl"],
        cwd=str(build_dir),
        env=env,
        capture_output=True, text=True, timeout=1200,
    )
    dt = time.time() - t0
    (build_dir / "run.log").write_text(result.stdout + "\n--- STDERR ---\n" + result.stderr)

    print(f"[{'PASS' if result.returncode == 0 else 'FAIL'}] {project}  ({dt:.1f}s)")
    if result.returncode != 0:
        # Print last 60 lines of stdout
        for line in result.stdout.splitlines()[-60:]:
            print(" ", line)
    else:
        # Show summary
        summary = build_dir / "output_files" / f"{project}.fit.summary"
        if summary.exists():
            print("--- FIT SUMMARY ---")
            print(summary.read_text())

    shutil.rmtree(build_dir, ignore_errors=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "blinky_led")
