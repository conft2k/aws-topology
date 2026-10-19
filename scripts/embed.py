#!/usr/bin/env python3
"""Inline bundled icons into an SVG, producing a portable standalone file.

In your draft SVG, reference icons from the bundle with the `bundle:` scheme:

    <image href="bundle:service/AWS-Lambda"  x="200" y="200" width="48" height="48"/>
    <image href="bundle:group/AWS-Cloud-logo_32"  x="20"  y="20"  width="32" height="32"/>

Then:  python scripts/embed.py draft.svg final.svg

Each bundle: ref is replaced with a data: URI pulled from assets/icons.json,
so the final SVG renders anywhere with no external files. The output is written
only when every icon resolves: refs that don't resolve, image hrefs that point at
external files or URLs, and refs to the logo-less AWS Cloud outline (the badge
must carry the AWS logo) are reported instead,
nothing is written, and the script exits with status 1.
"""
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = json.loads((ROOT / "assets" / "icons.json").read_text(encoding="utf-8"))
SETS = BUNDLE["sets"]

# Attribute values may be single- or double-quoted; group 1 is the quote.
REF_RE = re.compile(r'(?:xlink:)?href\s*=\s*(["\'])bundle:([^"\']+)\1')
# The AWS Cloud container always carries the AWS logo; these are the logo-less outlines.
REPLACED = {"group/AWS-Cloud_32": "group/AWS-Cloud-logo_32",
            "group/AWS-Cloud_32_Dark": "group/AWS-Cloud-logo_32_Dark"}
# <image> hrefs that would still need a file or network fetch after embedding.
EXTERNAL_RE = re.compile(
    r'<image\b[^>]*?(?:xlink:)?href\s*=\s*(["\'])(?!data:|bundle:|#)([^"\']+)\1')


def data_uri(setname: str, name: str):
    entry = SETS.get(setname, {}).get(name)
    if entry is None:
        return None
    if entry["type"] == "svg":
        b64 = base64.b64encode(entry["data"].encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{b64}"
    return f"data:image/png;base64,{entry['data']}"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    svg = src.read_text(encoding="utf-8")
    missing, replaced, embedded = [], [], 0

    def repl(m):
        nonlocal embedded
        ref = m.group(2)
        if ref in REPLACED:
            replaced.append(ref)
            return m.group(0)
        setname, _, name = ref.partition("/")
        uri = data_uri(setname, name)
        if uri is None:
            missing.append(ref)
            return m.group(0)
        embedded += 1
        return m.group(0).replace(f"bundle:{ref}", uri)

    out = REF_RE.sub(repl, svg)
    if missing:
        print("MISSING (fix these refs — check names with find_icon.py):")
        for r in missing:
            print(f"  bundle:{r}")
    external = [m.group(2) for m in EXTERNAL_RE.finditer(out)]
    if external:
        print("EXTERNAL (won't render standalone — switch to bundle: refs):")
        for r in external:
            print(f"  {r}")
    if replaced:
        print("NO AWS LOGO (the AWS Cloud badge must include the AWS logo):")
        for r in replaced:
            print(f"  bundle:{r} -> use bundle:{REPLACED[r]}")
    if missing or external or replaced:
        if dst.exists():
            dst.unlink()  # never leave a stale or half-embedded final file behind
        sys.exit(f"Nothing written to {dst}; fix the refs above and re-run.")
    dst.write_text(out, encoding="utf-8")
    print(f"Embedded {embedded} icon(s) -> {dst}")


if __name__ == "__main__":
    main()
