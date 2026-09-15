#!/usr/bin/env python3
"""Lab loader for the AI-Augmented Engineering course repo.

    python lab.py start 2            # reset the workspace to the start of Lab 2
    python lab.py solution 2         # load the finished state of Lab 2
    python lab.py status             # which lab state the workspace matches
    python lab.py list               # what each lab state contains

Run it from this folder (lab-workspace/), which is the folder you open in
the editor. A lab state is a zip archive one level up, in ../lab-starters/:
lab1.zip ... lab4.zip and solution.zip. Each holds both editors' configuration
(.cursor/ for Cursor, .github/ for Copilot), so the same command serves both. "start N"
removes every file any lab produces, then extracts labN.zip into this folder.
"solution N" loads lab(N+1).zip; the finished state of the last lab is
solution.zip. Nothing outside those files is touched.

Instructors editing a starter:

    python lab.py unpack 2           # extract ../lab-starters/lab2.zip -> ../lab-starters/lab2/
    python lab.py pack 2             # rebuild lab2.zip from that folder and delete the folder

The script refuses to run if git shows uncommitted changes, so nobody loses
work by accident. Commit or stash first, or pass --force.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent   # lab-workspace/: the folder students open
REPO = ROOT.parent                        # repository root: starters, lab text, notes
LAST_LAB = 4
STATE_ORDER = ["lab1", "lab2", "lab3", "lab4", "solution"]


def starters_dir(copilot: bool = False) -> Path:
    return REPO / "lab-starters"


class State:
    """One lab state, read from <name>.zip (preferred) or a <name>/ folder."""

    def __init__(self, name: str, base: Path):
        self.name = name
        self.zip = base / f"{name}.zip"
        self.dir = base / name
        if not self.zip.is_file() and not self.dir.is_dir():
            sys.exit(f"No such lab state: {self.zip.relative_to(REPO)}")

    def files(self) -> list[PurePosixPath]:
        if self.zip.is_file():
            with zipfile.ZipFile(self.zip) as zf:
                return sorted(PurePosixPath(i.filename) for i in zf.infolist()
                              if not i.is_dir() and not i.filename.startswith("__MACOSX"))
        return sorted(PurePosixPath(p.relative_to(self.dir).as_posix())
                      for p in self.dir.rglob("*") if p.is_file())

    def read(self, rel: PurePosixPath) -> bytes:
        if self.zip.is_file():
            with zipfile.ZipFile(self.zip) as zf:
                return zf.read(str(rel))
        return (self.dir / rel).read_bytes()


def states(copilot: bool) -> list[State]:
    base = starters_dir(copilot)
    found = []
    for name in STATE_ORDER:
        if (base / f"{name}.zip").is_file() or (base / name).is_dir():
            found.append(State(name, base))
    return found


def owned_paths(copilot: bool) -> set[PurePosixPath]:
    """Every file that any lab state ships. These are the files labs create
    or edit, so they are the only files start/solution may delete."""
    owned: set[PurePosixPath] = set()
    for st in states(copilot):
        owned.update(st.files())
    return owned


def git_dirty() -> bool:
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return bool(out.strip())


def load(name: str, copilot: bool, force: bool) -> None:
    src = State(name, starters_dir(copilot))
    if git_dirty() and not force:
        sys.exit("You have uncommitted changes. Commit or stash them first "
                 "(git add -A && git commit -m 'checkpoint'), or re-run with --force.")
    removed = 0
    for rel in owned_paths(copilot):
        target = ROOT / rel
        if target.exists():
            target.unlink()
            removed += 1
    # drop directories a lab may have emptied (keeps .gitkeep-only folders tidy)
    for d in ("src", "tests", "docs", "audit", ".cursor/skills", ".cursor/rules", ".github"):
        p = ROOT / d
        if p.is_dir():
            for sub in sorted(p.rglob("*"), reverse=True):
                if sub.is_dir() and not any(sub.iterdir()):
                    sub.rmdir()
    copied = 0
    for rel in src.files():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read(rel))
        copied += 1
    for cache in ROOT.rglob("__pycache__"):
        if "venv" not in cache.parts and ".venv" not in cache.parts:
            shutil.rmtree(cache, ignore_errors=True)
    print(f"Loaded {src.name} into {ROOT.name}/: removed {removed} file(s), copied {copied}.")
    print("Check with:  python lab.py status")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def status(copilot: bool) -> None:
    owned = owned_paths(copilot)
    present = {rel for rel in owned if (ROOT / rel).exists()}
    print(f"Workspace: {ROOT}")
    for st in states(copilot):
        files = st.files()
        same = sum(1 for rel in files
                   if (ROOT / rel).exists() and digest((ROOT / rel).read_bytes()) == digest(st.read(rel)))
        extra = len(present - set(files))
        mark = "  <- matches" if same == len(files) and extra == 0 else ""
        print(f"  {st.name:10s} {same}/{len(files)} files identical, {extra} extra lab file(s) present{mark}")
    if git_dirty():
        print("git: uncommitted changes present")


def list_states(copilot: bool) -> None:
    for st in states(copilot):
        print(f"{st.name}/")
        for rel in st.files():
            print(f"    {rel.as_posix()}")


def unpack(name: str, copilot: bool) -> None:
    base = starters_dir(copilot)
    z, d = base / f"{name}.zip", base / name
    if not z.is_file():
        sys.exit(f"No archive {z.relative_to(REPO)}")
    if d.exists():
        sys.exit(f"{d.relative_to(REPO)} already exists; pack or remove it first")
    with zipfile.ZipFile(z) as zf:
        zf.extractall(d)
    print(f"Extracted {z.relative_to(REPO)} -> {d.relative_to(REPO)}/  (edit, then: python lab.py pack {name[-1] if name != 'solution' else 'solution'})")


def pack(name: str, copilot: bool) -> None:
    base = starters_dir(copilot)
    z, d = base / f"{name}.zip", base / name
    if not d.is_dir():
        sys.exit(f"No folder {d.relative_to(REPO)} to pack")
    files = sorted(p for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(d).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, p.read_bytes())
    shutil.rmtree(d)
    print(f"Packed {len(files)} file(s) into {z.relative_to(REPO)} and removed {d.relative_to(REPO)}/")


def state_name(lab: str) -> str:
    if lab == "solution":
        return "solution"
    if lab.isdigit() and 1 <= int(lab) <= LAST_LAB:
        return f"lab{lab}"
    sys.exit(f"Give a lab number 1-{LAST_LAB} or 'solution'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["start", "solution", "status", "list", "pack", "unpack"])
    ap.add_argument("lab", nargs="?", help="lab number 1-4 (pack/unpack also accept 'solution')")
    ap.add_argument("--force", action="store_true", help="proceed even with uncommitted git changes")
    a = ap.parse_args()

    if a.command in ("start", "solution"):
        if a.lab is None or not (a.lab.isdigit() and 1 <= int(a.lab) <= LAST_LAB):
            sys.exit(f"Give a lab number 1-{LAST_LAB}, e.g.  python lab.py {a.command} 2")
        n = int(a.lab)
        if a.command == "start":
            load(f"lab{n}", False, a.force)
        else:
            load("solution" if n == LAST_LAB else f"lab{n + 1}", False, a.force)
    elif a.command == "status":
        status(False)
    elif a.command == "list":
        list_states(False)
    elif a.command == "unpack":
        unpack(state_name(a.lab or ""), False)
    else:
        pack(state_name(a.lab or ""), False)


if __name__ == "__main__":
    main()
