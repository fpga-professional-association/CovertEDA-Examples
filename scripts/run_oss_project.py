"""Run yosys + nextpnr on a single OSS CAD Suite project.

Usage:
  python scripts/run_oss_project.py <project_name>

Writes these reports into oss/<name>/reports/:
  yosys.log        - full yosys stdout
  yosys_stat.rpt   - post-synth `stat` output (cell counts, area estimate)
  nextpnr.log      - full nextpnr stdout (timing summary at the end)
  timing.json      - nextpnr detailed timing report (--report)
  build_summary.txt
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

OSS_ROOT = Path(r"C:\oss-cad-suite\oss-cad-suite")
OSS_BIN  = OSS_ROOT / "bin"
OSS_LIB  = OSS_ROOT / "lib"
YOSYS   = OSS_BIN / "yosys.exe"
NEXTPNR_ICE40 = OSS_BIN / "nextpnr-ice40.exe"
NEXTPNR_ECP5  = OSS_BIN / "nextpnr-ecp5.exe"


def oss_env():
    """Replicate environment.bat so yosys/nextpnr can find their libs."""
    e = os.environ.copy()
    e["YOSYSHQ_ROOT"] = str(OSS_ROOT) + os.sep
    e["PATH"] = f"{OSS_BIN}{os.pathsep}{OSS_LIB}{os.pathsep}" + e.get("PATH", "")
    e["SSL_CERT_FILE"]     = str(OSS_ROOT / "etc" / "cacert.pem")
    e["PYTHON_EXECUTABLE"] = str(OSS_LIB / "python3.exe")
    e["QT_PLUGIN_PATH"]    = str(OSS_LIB / "qt5" / "plugins")
    e["QT_LOGGING_RULES"]  = "*=false"
    return e

def read_config(proj_dir: Path):
    cfg = proj_dir / ".coverteda"
    device = top = None
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text())
            device = data.get("device")
            top    = data.get("topModule")
        except Exception:
            pass
    return device, top


def detect_top(src_files: list[Path], hint: str | None) -> str | None:
    """Heuristic: prefer module named *_top, then the hint-ish file, else first module."""
    modules = []
    for f in src_files:
        for line in f.read_text(errors="ignore").splitlines():
            m = re.match(r"\s*module\s+(\w+)", line)
            if m:
                modules.append(m.group(1))
    if not modules:
        return None
    # Priority: *_top, hint exact, hint match, any
    tops = [m for m in modules if m.endswith("_top")]
    if tops:
        return tops[0]
    if hint and hint in modules:
        return hint
    return modules[0]


def select_device(device_str: str | None):
    """Return (family, nextpnr_exe, nextpnr_args, yosys_synth_cmd) based on device string."""
    s = (device_str or "iCE40UP5K").lower()
    if "ecp5" in s or "lfe5" in s:
        # ECP5 family
        part = "25k" if "25" in s else ("45k" if "45" in s else "85k")
        return ("ecp5", NEXTPNR_ECP5, ["--" + part, "--package", "CABGA381"], "synth_ecp5 -json design.json")
    # default iCE40
    if "up5k" in s:
        pkg = "sg48"
        return ("ice40", NEXTPNR_ICE40, ["--up5k", "--package", pkg], "synth_ice40 -json design.json")
    if "hx8k" in s:
        return ("ice40", NEXTPNR_ICE40, ["--hx8k", "--package", "ct256"], "synth_ice40 -json design.json")
    # fallback
    return ("ice40", NEXTPNR_ICE40, ["--up5k", "--package", "sg48"], "synth_ice40 -json design.json")


def build(project: str, root: Path, timeout: int = 300) -> tuple[bool, str]:
    proj_dir = root / "oss" / project
    if not proj_dir.exists():
        return False, f"project dir missing: {proj_dir}"

    device, hint_top = read_config(proj_dir)
    src_files = sorted((proj_dir / "src").glob("*.v")) + sorted((proj_dir / "src").glob("*.sv"))
    if not src_files:
        return False, "no src/*.v"
    hex_files = sorted((proj_dir / "src").glob("*.hex"))

    top = detect_top(src_files, hint_top)
    if not top:
        return False, "could not detect top module"

    family, nextpnr_exe, nextpnr_dev_args, synth_cmd = select_device(device)

    # Scratch build dir
    build_dir = proj_dir / ".build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()

    # Copy sources + hex readmemh files
    for f in src_files + hex_files:
        shutil.copy2(f, build_dir / f.name)

    # Find PCF/LPF constraints
    constr_dir = proj_dir / "constraints"
    pcf_files = list(constr_dir.glob("*.pcf"))
    lpf_files = list(constr_dir.glob("*.lpf"))
    for f in pcf_files + lpf_files:
        shutil.copy2(f, build_dir / f.name)

    # Build yosys script
    read_cmds = []
    for s in src_files:
        read_cmds.append(f"read_verilog {s.name}")
    ys = build_dir / "build.ys"
    ys.write_text(
        "\n".join(read_cmds) +
        f"\nhierarchy -check -top {top}\n"
        f"{synth_cmd}\n"
        f"stat\n"
    )

    env = oss_env()

    reports_out = proj_dir / "reports"
    reports_out.mkdir(exist_ok=True)
    for f in list(reports_out.iterdir()):
        f.unlink()

    # --- Run yosys ---
    yosys_log = reports_out / "yosys.log"
    try:
        proc = subprocess.run(
            [str(YOSYS), "-s", "build.ys"],
            cwd=str(build_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        yosys_output = (proc.stdout or "") + "\n--- STDERR ---\n" + (proc.stderr or "")
        yosys_log.write_text(yosys_output)
        if proc.returncode != 0:
            (reports_out / "build_summary.txt").write_text(
                f"Project: {project}\nStage: yosys\nStatus: FAIL\nDevice: {device}\nTop: {top}\n"
            )
            shutil.rmtree(build_dir, ignore_errors=True)
            return False, "yosys failed"
    except subprocess.TimeoutExpired:
        yosys_log.write_text("TIMEOUT")
        return False, "yosys TIMEOUT"

    # Extract post-synth stat block
    stat_block = []
    in_stat = False
    for line in yosys_output.splitlines():
        if "Printing statistics." in line:
            in_stat = True
            continue
        if in_stat:
            if line.startswith("2.") or line.startswith("End of script"):
                break
            stat_block.append(line)
    (reports_out / "yosys_stat.rpt").write_text("\n".join(stat_block).strip() or yosys_output[-4000:])

    # --- Run nextpnr ---
    npnr_log = reports_out / "nextpnr.log"
    timing_json = reports_out / "timing.json"
    npnr_args = [str(nextpnr_exe)] + nextpnr_dev_args + [
        "--json", "design.json",
        "--report", "timing.json",
    ]
    # Add constraint file if present
    if family == "ice40" and pcf_files:
        npnr_args += ["--pcf", pcf_files[0].name]
    if family == "ecp5" and lpf_files:
        npnr_args += ["--lpf", lpf_files[0].name]
    # Low-effort defaults to keep runs short. Allow unconstrained I/O because
    # most example PCFs only pin-assign the headline ports (clk, rst_n, primary
    # outputs), not every signal — nextpnr refuses to pick free pins by default.
    npnr_args += ["--seed", "1", "--timing-allow-fail"]
    if family == "ice40":
        npnr_args += ["--pcf-allow-unconstrained"]
    if family == "ecp5":
        npnr_args += ["--lpf-allow-unconstrained"]

    def run_npnr(args):
        p = subprocess.run(args, cwd=str(build_dir), env=env,
                           capture_output=True, text=True, timeout=timeout)
        return (p.returncode == 0,
                (p.stdout or "") + "\n--- STDERR ---\n" + (p.stderr or ""))

    try:
        npnr_ok, text = run_npnr(npnr_args)
        # Some example PCFs reference pins that don't exist in the target
        # package. Strip them and retry without any PCF (nextpnr will
        # auto-place all I/O). We keep the retry output instead of the failed
        # first run so reports reflect an actually-completed PnR.
        bad_pin = ("package does not have a pin" in text
                   or "does not exist for package" in text)
        if not npnr_ok and bad_pin:
            cleaned = []
            skip = False
            for a in npnr_args:
                if skip: skip = False; continue
                if a in ("--pcf", "--lpf"): skip = True; continue
                cleaned.append(a)
            npnr_ok, text = run_npnr(cleaned)
        npnr_log.write_text(text)
    except subprocess.TimeoutExpired:
        npnr_log.write_text("TIMEOUT")
        shutil.rmtree(build_dir, ignore_errors=True)
        return False, "nextpnr TIMEOUT"

    # Copy timing json if produced
    produced_timing = build_dir / "timing.json"
    if produced_timing.exists():
        shutil.copy2(produced_timing, timing_json)

    summary = (
        f"Project:  {project}\n"
        f"Device:   {device}\n"
        f"Family:   {family}\n"
        f"Top:      {top}\n"
        f"yosys:    PASS\n"
        f"nextpnr:  {'PASS' if npnr_ok else 'FAIL (timing/routing)'}\n"
    )
    (reports_out / "build_summary.txt").write_text(summary)

    shutil.rmtree(build_dir, ignore_errors=True)
    return npnr_ok, f"yosys ok, nextpnr {'ok' if npnr_ok else 'fail'}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    root = Path.cwd()
    t0 = time.time()
    ok, msg = build(args.project, root, timeout=args.timeout)
    dt = time.time() - t0
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {args.project:25s}  {dt:6.1f}s  {msg}")
    sys.exit(0 if ok else 1)
