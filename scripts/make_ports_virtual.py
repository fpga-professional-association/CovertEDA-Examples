"""Strip physical pin-location assignments from every vendor constraint file.

Goal: the examples are IP/reference designs, not board designs. Full vendor
flows fail at place-and-route when they try to map top-level ports onto a
specific board pinout that doesn't exist. Each vendor has its own way of
expressing "don't place this port":

  Quartus  — handled separately by add_virtual_pins.py (VIRTUAL_PIN + I/O std)
  Vivado   — strip PACKAGE_PIN / LOC; keep IOSTANDARD; add IO_BUFFER_TYPE NONE
             for every top-level port (Vivado's closest analog to a virtual pin)
  Radiant  — strip ldc_set_location; keep ldc_set_port -iobuf so I/O std sticks
  Diamond  — strip LOCATE COMP; keep IOBUF PORT so I/O standard info survives
  Libero   — drop "-pinname <pin> -fixed yes" from set_io; keep iostandard
  ACE      — drop "-loc <site>" from set_pin; keep iostandard / drive / slew
  OSS      — already place-agnostic (yosys + nextpnr --pcf-allow-unconstrained)

Idempotent: safe to re-run; any lines already removed stay removed.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PORT_DECL = re.compile(
    r"^\s*(?:input|output|inout)\s+"
    r"(?:wire|reg|logic)?\s*"
    r"(?:\[[^\]]*\])?\s*"
    r"([A-Za-z_]\w*)",
    re.MULTILINE,
)


def detect_top_ports(proj_dir: Path, top_module: str | None = None) -> list[str]:
    src_files = sorted((proj_dir / "src").rglob("*.v")) + sorted((proj_dir / "src").rglob("*.sv"))
    if not src_files:
        return []
    if top_module:
        module_re = re.compile(r"\bmodule\s+" + re.escape(top_module) + r"\b")
        for f in src_files:
            text = f.read_text(errors="ignore")
            if module_re.search(text):
                m = module_re.search(text)
                end_match = re.search(r"\);", text[m.end():])
                if end_match:
                    header = text[m.end(): m.end() + end_match.end()]
                    return list(dict.fromkeys(m.group(1) for m in PORT_DECL.finditer(header)))
    # Fallback: first module in first source file
    text = src_files[0].read_text(errors="ignore")
    mm = re.search(r"\bmodule\s+\w+\b", text)
    if not mm:
        return []
    end_match = re.search(r"\);", text[mm.end():])
    if not end_match:
        return []
    header = text[mm.end(): mm.end() + end_match.end()]
    return list(dict.fromkeys(m.group(1) for m in PORT_DECL.finditer(header)))


# ---------------- Vivado XDC ----------------
def patch_vivado(proj: Path) -> str:
    """Drop PACKAGE_PIN/LOC; add `IO_BUFFER_TYPE NONE` for every top-level port."""
    xdc_dir = proj / "constraints"
    xdc_files = list(xdc_dir.glob("*.xdc"))
    if not xdc_files:
        return "no xdc"
    ports = detect_top_ports(proj)
    total_removed = 0
    for xdc in xdc_files:
        text = xdc.read_text(errors="ignore")
        new_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            # Drop any set_property PACKAGE_PIN or LOC line
            if re.match(r"set_property\s+(PACKAGE_PIN|LOC)\s+", stripped):
                total_removed += 1
                continue
            new_lines.append(line)
        new_text = "\n".join(new_lines).rstrip()

        # Remove any previous virtual-port block we wrote
        new_text = re.sub(
            r"\n?#\s*=+\s*Virtual-port assignments\s*=+.*?(?=\n# =|\Z)",
            "", new_text, flags=re.DOTALL,
        ).rstrip()

        # Append IO_BUFFER_TYPE NONE for every top-level port so PnR treats
        # them as internal nets.
        if ports:
            block = ["", "# ========== Virtual-port assignments =========="]
            block.append(
                "# Suppresses IOB inference — matches VIRTUAL_PIN semantics in Quartus."
            )
            for p in ports:
                block.append(f"set_property IO_BUFFER_TYPE NONE [get_ports {{{p}}}]")
            new_text += "\n" + "\n".join(block) + "\n"
        else:
            new_text += "\n"

        xdc.write_text(new_text)
    return f"xdc locations -{total_removed}, +{len(ports)} virtual ports"


# ---------------- Radiant PDC ----------------
def patch_radiant(proj: Path) -> str:
    pdc_dir = proj / "constraints"
    pdc_files = list(pdc_dir.glob("*.pdc"))
    if not pdc_files:
        return "no pdc"
    total_removed = 0
    for pdc in pdc_files:
        text = pdc.read_text(errors="ignore")
        new_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if re.match(r"ldc_set_location\s+", stripped):
                total_removed += 1
                continue
            new_lines.append(line)
        pdc.write_text("\n".join(new_lines).rstrip() + "\n")
    return f"pdc locations -{total_removed}"


# ---------------- Diamond LPF ----------------
def patch_diamond(proj: Path) -> str:
    lpf_dir = proj / "constraints"
    lpf_files = list(lpf_dir.glob("*.lpf"))
    if not lpf_files:
        return "no lpf"
    total_removed = 0
    for lpf in lpf_files:
        text = lpf.read_text(errors="ignore")
        new_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if re.match(r"LOCATE\s+COMP\b", stripped, re.IGNORECASE):
                total_removed += 1
                continue
            new_lines.append(line)
        lpf.write_text("\n".join(new_lines).rstrip() + "\n")
    return f"lpf locations -{total_removed}"


# ---------------- Libero PDC ----------------
def patch_libero(proj: Path) -> str:
    pdc_dir = proj / "constraints"
    pdc_files = list(pdc_dir.glob("*.pdc"))
    if not pdc_files:
        return "no pdc"
    total_rewrites = 0
    for pdc in pdc_files:
        text = pdc.read_text(errors="ignore")
        new_lines = []
        for line in text.splitlines():
            # Remove -pinname <PIN> and -fixed yes from set_io so the tool
            # can auto-place; keep everything else (iostandard, bank).
            new_line = re.sub(r"\s+-pinname\s+\S+", "", line)
            new_line = re.sub(r"\s+-fixed\s+(yes|no)", "", new_line)
            if new_line != line:
                total_rewrites += 1
            new_lines.append(new_line)
        pdc.write_text("\n".join(new_lines).rstrip() + "\n")
    return f"pdc rewrites {total_rewrites}"


# ---------------- ACE PDC ----------------
def patch_ace(proj: Path) -> str:
    pdc_dir = proj / "constraints"
    pdc_files = list(pdc_dir.glob("*.pdc"))
    if not pdc_files:
        return "no pdc"
    total_rewrites = 0
    for pdc in pdc_files:
        text = pdc.read_text(errors="ignore")
        new_lines = []
        for line in text.splitlines():
            # Strip -loc <site> from set_pin; keep -iostandard / -drive / -slew.
            new_line = re.sub(r"\s+-loc\s+\S+", "", line)
            if new_line != line:
                total_rewrites += 1
            new_lines.append(new_line)
        pdc.write_text("\n".join(new_lines).rstrip() + "\n")
    return f"pdc rewrites {total_rewrites}"


VENDORS = {
    "vivado":  patch_vivado,
    "radiant": patch_radiant,
    "diamond": patch_diamond,
    "libero":  patch_libero,
    "ace":     patch_ace,
}


def main():
    for vendor, fn in VENDORS.items():
        vendor_dir = ROOT / vendor
        if not vendor_dir.is_dir():
            continue
        projects = sorted(p for p in vendor_dir.iterdir() if p.is_dir() and (p / "src").is_dir())
        print(f"\n=== {vendor} ({len(projects)} projects) ===")
        for proj in projects:
            msg = fn(proj)
            print(f"  [OK]   {proj.name:<22s}  {msg}")


if __name__ == "__main__":
    main()
