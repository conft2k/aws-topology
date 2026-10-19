#!/usr/bin/env python3
"""Rebuild assets/icons.json from the official AWS Architecture Icons package.

Download the "Icon package" zip from https://aws.amazon.com/architecture/icons/,
unzip it, and pass the extracted folder:

    python scripts/build_bundle.py <extracted-package-dir>

Sets built from the package (64px service/category, 48px resource, 32px group):
  service   Arch_<Name>_64.svg              -> service/<Name>
  resource  Res_<Name>_48.svg               -> resource/<Name>
            Res_<Name>_48_Light.svg         -> resource/<Name>        (general icons)
            Res_<Name>_48_Dark.svg          -> resource/<Name>_Dark
  group     <Name>_32[_Dark].svg            -> group/<Name>_32[_Dark]
  category  Arch-Category_<Name>_64.svg     -> category/<Name>

Service names that disappear from a new package release are moved to the `legacy`
set so older drafts keep resolving.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icons.json"


def svg(path: Path):
    return {"type": "svg", "data": path.read_text(encoding="utf-8")}


def collect(pkg: Path, pattern: str, rename):
    entries = {}
    for p in sorted(pkg.glob(pattern)):
        if "__MACOSX" in p.parts:
            continue
        name = rename(p.stem)
        if name:
            entries.setdefault(name, svg(p))
    return entries


def resource_name(stem: str):
    m = re.fullmatch(r"Res_(.+)_48(?:_(Light|Dark))?", stem)
    if not m:
        return None
    return m.group(1) + ("_Dark" if m.group(2) == "Dark" else "")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    pkg = Path(sys.argv[1])
    old = json.loads(OUT.read_text(encoding="utf-8"))["sets"] if OUT.exists() else {}

    sets = {
        "service": collect(pkg, "Architecture-Service-Icons_*/*/64/Arch_*_64.svg",
                           lambda s: s[len("Arch_"):-len("_64")]),
        "resource": collect(pkg, "Resource-Icons_*/**/Res_*.svg", resource_name),
        "group": collect(pkg, "Architecture-Group-Icons_*/*.svg", lambda s: s),
        "category": collect(pkg, "Category-Icons_*/Arch-Category_64/Arch-Category_*_64.svg",
                            lambda s: s[len("Arch-Category_"):-len("_64")]),
    }
    if not sets["service"]:
        sys.exit(f"No service icons found under {pkg} — is it the extracted Icon package?")

    legacy = dict(old.get("legacy", {}))
    for name, entry in old.get("service", {}).items():
        if name not in sets["service"]:
            legacy[name] = entry
    sets["legacy"] = {k: v for k, v in sorted(legacy.items()) if k not in sets["service"]}

    # Write beside the bundle and rename, so a failed run never leaves a half-written one.
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"version": 2, "sets": sets}, ensure_ascii=False), encoding="utf-8")
    tmp.replace(OUT)
    for name, entries in sets.items():
        print(f"  {name}: {len(entries)}")
    total = sum(len(v) for v in sets.values())
    print(f"Wrote {OUT} — {total} icons, {OUT.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
