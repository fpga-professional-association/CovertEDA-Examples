"""Create a .coverteda project file at the root of every example that is
missing one. Walks each vendor directory, inspects src/ and constraints/ to
infer device, top module, source/constraint patterns.

Safe to re-run: only writes files that don't already exist.
"""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOW  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f000+00:00")

VENDOR_DEFAULTS = {
    "vivado":  {"device": "xc7a35ti-csg324-1L", "cfmt": ["*.xdc"],           "impl": "impl_1"},
    "quartus": {"device": "10CX085YU484E5G",     "cfmt": ["*.qsf", "*.sdc"], "impl": "output_files"},
    "radiant": {"device": "LIFCL-40-7BG400I",    "cfmt": ["*.pdc", "*.sdc"], "impl": "impl1"},
    "diamond": {"device": "LFE5U-25F-6BG381C",   "cfmt": ["*.lpf"],          "impl": "impl1"},
    "libero":  {"device": "MPF300T",             "cfmt": ["*.pdc", "*.sdc"], "impl": "designer"},
    "ace":     {"device": "AC7t1500",            "cfmt": ["*.pdc", "*.sdc"], "impl": "impl1"},
    "oss":     {"device": "iCE40UP5K",           "cfmt": ["*.pcf", "*.lpf"], "impl": "impl1"},
}

DEVICE_FROM_SRC = [
    (re.compile(r"(xc7[akz]\w+-\w+-\w+)",            re.I), None),
    (re.compile(r"(xc7[akz]\w+)",                    re.I), None),
    (re.compile(r"(EP\d\w+-\w+|10C[XM]\w+|10M\w+|5CSE\w+)", re.I), None),
    (re.compile(r"(LIFCL-\d+[^\s\"']+)",             re.I), None),
    (re.compile(r"(LFE5U\w*-\w+[^\s\"']+)",          re.I), None),
    (re.compile(r"(iCE40\w+[-_]?\w*)",               re.I), None),
    (re.compile(r"(MPF\d+T[^\s\"']*)",               re.I), None),
    (re.compile(r"(AC7t\d+)",                        re.I), None),
]

def detect_device(src_files, constr_files, vendor):
    texts = []
    for f in list(src_files) + list(constr_files):
        try:
            texts.append(f.read_text(errors="ignore"))
        except Exception:
            pass
    blob = "\n".join(texts)
    for rx, _ in DEVICE_FROM_SRC:
        m = rx.search(blob)
        if m:
            dev = m.group(1).strip()
            if re.match(r"\d+(\.\d+)*$", dev):  # version number, skip
                continue
            return dev
    return VENDOR_DEFAULTS[vendor]["device"]


def detect_top(src_files, proj_name):
    modules = []
    for f in src_files:
        for line in f.read_text(errors="ignore").splitlines():
            m = re.match(r"\s*module\s+(\w+)", line)
            if m:
                modules.append(m.group(1))
    if not modules:
        return proj_name
    tops = [m for m in modules if m.endswith("_top")]
    if tops: return tops[0]
    if proj_name in modules: return proj_name
    return modules[0]


def source_patterns(src_dir):
    exts = set(p.suffix for p in src_dir.rglob("*") if p.is_file())
    patterns = []
    if ".v" in exts:  patterns.append("src/**/*.v")
    if ".sv" in exts: patterns.append("src/**/*.sv")
    if ".vhd" in exts: patterns.append("src/**/*.vhd")
    return patterns or ["src/**/*.v"]


def constraint_patterns(constr_dir, vendor):
    if not constr_dir.exists():
        return [f"constraints/{p}" for p in VENDOR_DEFAULTS[vendor]["cfmt"]]
    pats = []
    for p in VENDOR_DEFAULTS[vendor]["cfmt"]:
        if any(constr_dir.glob(p)):
            pats.append(f"constraints/{p}")
    return pats or [f"constraints/{p}" for p in VENDOR_DEFAULTS[vendor]["cfmt"][:1]]


def short_desc(top, proj):
    base = proj.replace("_", " ")
    return f"{base} example — top module {top}"


def generate_all():
    created = 0
    for vendor, cfg in VENDOR_DEFAULTS.items():
        vendor_dir = ROOT / vendor
        if not vendor_dir.is_dir():
            continue
        for proj_dir in sorted(vendor_dir.iterdir()):
            if not proj_dir.is_dir():
                continue
            src_dir = proj_dir / "src"
            if not src_dir.is_dir():
                continue
            cv = proj_dir / ".coverteda"
            if cv.exists():
                continue

            src_files = sorted(list(src_dir.rglob("*.v")) + list(src_dir.rglob("*.sv")) + list(src_dir.rglob("*.vhd")))
            constr_dir = proj_dir / "constraints"
            constr_files = sorted(constr_dir.glob("*")) if constr_dir.exists() else []

            top = detect_top(src_files, proj_dir.name)
            device = detect_device(src_files, constr_files, vendor)

            data = {
                "name": proj_dir.name,
                "description": short_desc(top, proj_dir.name),
                "backendId": vendor,
                "device": device,
                "topModule": top,
                "sourcePatterns": source_patterns(src_dir),
                "constraintFiles": constraint_patterns(constr_dir, vendor),
                "implDir": cfg["impl"],
                "backendConfig": {},
                "buildStages": [],
                "buildOptions": {},
                "createdAt": NOW,
                "updatedAt": NOW,
            }
            cv.write_text(json.dumps(data, indent=2) + "\n")
            print(f"created {vendor}/{proj_dir.name}/.coverteda  (device={device}, top={top})")
            created += 1
    print(f"\nCreated {created} .coverteda files.")
    return created


if __name__ == "__main__":
    generate_all()
