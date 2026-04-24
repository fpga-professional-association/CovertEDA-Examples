"""Add VIRTUAL_PIN + IO_STANDARD assignments to every Quartus example.

Rationale: these example projects are IP/reference designs, not full FPGA
board designs. They have no real pin-out, so Quartus's fitter fails at
"automatic periphery placement" when it tries to place 30+ I/O pins on a
real device. Marking every top-level port as a VIRTUAL_PIN tells Quartus
to treat the port as an internal signal during fitting — no pin mapping,
no board required. The result is a full synthesis + fit + STA + assembler
flow that successfully builds against any device in the family.

This runs once and rewrites each project's QSF file in place:
  - Drops any previous VIRTUAL_PIN assignments (idempotent re-runs)
  - Appends a new "Virtual pin assignments" section at the end of the QSF
  - Adds 3.3-V LVCMOS I/O standard to each virtual port (Pro requires one)

It also patches the SDC to fix a Quartus Prime Pro 25.3 syntax issue with
set_clock_uncertainty (Pro rejects `-setup 0.100 [get_clocks ...]` as
"More than 1 positional argument"; the fix is to use `-to` explicitly).
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUARTUS_DIR = ROOT / "quartus"

PORT_DECL = re.compile(
    r"^\s*(?:input|output|inout)\s+"
    r"(?:wire|reg|logic)?\s*"
    r"(?:\[[^\]]*\])?\s*"
    r"([A-Za-z_]\w*)",
    re.MULTILINE,
)


def extract_top_ports(src_files: list[Path], top_module: str) -> list[str]:
    """Pull port names from the top-level Verilog module."""
    # Find the source file containing `module <top>`
    module_re = re.compile(r"\bmodule\s+" + re.escape(top_module) + r"\b", re.MULTILINE)
    top_src = None
    for f in src_files:
        text = f.read_text(errors="ignore")
        if module_re.search(text):
            top_src = (f, text)
            break
    if top_src is None:
        return []
    f, text = top_src

    # Extract the module body up to the next `module` or `endmodule`
    start = module_re.search(text).end()
    end_match = re.search(r"\);", text[start:])
    if not end_match:
        return []
    header = text[start : start + end_match.end()]

    ports = []
    seen = set()
    for m in PORT_DECL.finditer(header):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            ports.append(name)
    return ports


def strip_existing_virtual_block(qsf: str) -> str:
    """Remove any prior '# === Virtual pin assignments ===' block."""
    pattern = re.compile(
        r"\n?#\s*=+\s*Virtual pin assignments\s*=+.*?(?=\n# =|\Z)",
        re.DOTALL,
    )
    return pattern.sub("", qsf).rstrip() + "\n"


def patch_qsf(proj: Path) -> tuple[bool, str]:
    name = proj.name
    qsf_path = proj / f"{name}.qsf"
    if not qsf_path.exists():
        return False, "no qsf at project root"

    # Top module from QSF
    qsf_text = qsf_path.read_text(errors="ignore")
    m = re.search(r"TOP_LEVEL_ENTITY\s+(\S+)", qsf_text)
    top = m.group(1).strip('"') if m else name

    src_files = sorted((proj / "src").rglob("*.v")) + sorted((proj / "src").rglob("*.sv"))
    if not src_files:
        return False, "no source files"

    ports = extract_top_ports(src_files, top)
    if not ports:
        return False, f"no ports found for top module {top}"

    qsf_text = strip_existing_virtual_block(qsf_text).rstrip() + "\n"

    block = ["", "# ========== Virtual pin assignments ==========",
             "# These examples are IP/reference designs — not full FPGA board",
             "# designs. Every top-level port is marked as a virtual pin so the",
             "# fitter doesn't attempt physical pin placement, which would require",
             "# a specific board-level pinout we don't want to pick for the user.",
             "set_global_assignment -name AUTO_SHIFT_REGISTER_RECOGNITION ALWAYS"]
    for p in ports:
        block.append(f'set_instance_assignment -name VIRTUAL_PIN ON -to {p}')
        block.append(f'set_instance_assignment -name IO_STANDARD "3.3-V LVCMOS" -to {p}')
    qsf_text += "\n".join(block) + "\n"

    qsf_path.write_text(qsf_text)
    return True, f"added virtual-pin for {len(ports)} ports"


def patch_sdc(proj: Path) -> tuple[bool, str]:
    """Fix set_clock_uncertainty syntax for Quartus Pro 25.3."""
    sdc_dir = proj / "constraints"
    if not sdc_dir.exists():
        return False, "no constraints dir"
    patched = 0
    for sdc in sdc_dir.glob("*.sdc"):
        text = sdc.read_text(errors="ignore")
        new_text = text

        # Rewrite  set_clock_uncertainty -setup 0.100 [get_clocks {clk}]
        #      ->  set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
        new_text = re.sub(
            r"set_clock_uncertainty\s+(-setup|-hold)\s+([-+]?\d*\.?\d+)\s+(\[get_clocks\s+[^\]]+\])",
            r"set_clock_uncertainty \1 -to \3 \2",
            new_text,
        )

        if new_text != text:
            sdc.write_text(new_text)
            patched += 1
    return True, f"patched {patched} sdc file(s)"


def main():
    projects = sorted(p for p in QUARTUS_DIR.iterdir() if p.is_dir() and (p / "src").is_dir())
    print(f"Patching {len(projects)} Quartus projects")
    for proj in projects:
        ok, msg = patch_qsf(proj)
        sdc_ok, sdc_msg = patch_sdc(proj)
        tag = "OK  " if ok else "SKIP"
        print(f"  [{tag}] {proj.name:<22s}  {msg}  |  {sdc_msg}")


if __name__ == "__main__":
    main()
