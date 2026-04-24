"""Create a .qpf + co-located .qsf at the top level of every Quartus example.

CovertEDA's Quartus backend opens <project_dir>/<name>.qpf — so every project
needs both:
  <project>/<name>.qpf     (Quartus Project File, tiny, references revision)
  <project>/<name>.qsf     (Quartus Settings File, moved up from constraints/)

The existing QSF lives in constraints/*.qsf and references sources via paths
like `src/*.v` and `constraints/*.sdc` that are already correct *relative to
the project root*, so moving the QSF up one level keeps every reference
valid. We rename it to match the project name so Quartus can pair it with
the new QPF.

Idempotent: skips any project that already has <name>.qpf at the root.
"""
from __future__ import annotations
import re, shutil, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUARTUS_DIR = ROOT / "quartus"


def create_qpf(proj_dir: Path) -> tuple[bool, str]:
    name = proj_dir.name
    qpf = proj_dir / f"{name}.qpf"
    target_qsf = proj_dir / f"{name}.qsf"

    if qpf.exists() and target_qsf.exists():
        return False, "already present"

    # Locate the existing QSF in constraints/
    constr_dir = proj_dir / "constraints"
    qsf_candidates = list(constr_dir.glob("*.qsf")) if constr_dir.exists() else []
    if not qsf_candidates:
        # Fall back: any *.qsf in proj_dir tree
        qsf_candidates = list(proj_dir.rglob("*.qsf"))
        qsf_candidates = [q for q in qsf_candidates if q != target_qsf]
    if not qsf_candidates:
        return False, "no source qsf found"

    src_qsf = qsf_candidates[0]

    # Copy + rename qsf to project root
    if not target_qsf.exists():
        shutil.copy2(src_qsf, target_qsf)
        # Remove stale qsf in constraints/ so we don't have two copies in sync
        src_qsf.unlink()

    # Write a minimal Quartus Project File
    qpf.write_text(
        f'QUARTUS_VERSION = "25.3"\n'
        f'DATE = "{time.strftime("%H:%M:%S  %B %d, %Y")}"\n'
        f'\n'
        f'# Revisions\n'
        f'\n'
        f'PROJECT_REVISION = "{name}"\n'
    )
    return True, f"created qpf + moved qsf from {src_qsf.name}"


def main():
    created = 0
    skipped = 0
    failed  = []
    for proj_dir in sorted(QUARTUS_DIR.iterdir()):
        if not proj_dir.is_dir():
            continue
        if not (proj_dir / "src").is_dir():
            continue
        ok, msg = create_qpf(proj_dir)
        if ok:
            created += 1
            print(f"  [OK]   {proj_dir.name:<20s}  {msg}")
        else:
            if msg == "already present":
                skipped += 1
            else:
                failed.append((proj_dir.name, msg))
                print(f"  [SKIP] {proj_dir.name:<20s}  {msg}")

    print(f"\nCreated: {created}   Already present: {skipped}   Issues: {len(failed)}")
    for n, m in failed:
        print(f"  {n}: {m}")


if __name__ == "__main__":
    main()
