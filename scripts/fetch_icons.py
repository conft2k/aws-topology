#!/usr/bin/env python3
"""Download the official AWS Architecture Icons package and build assets/icons.json.

The icons belong to AWS and are not shipped in this repository. Each install downloads
the pinned package from aws.amazon.com/architecture/icons, checks its SHA-256 and packs
it into assets/icons.json. find_icon.py, embed.py and svg2pptx.py call load_sets(),
which does this on first use, so running it by hand is optional:

    python3 scripts/fetch_icons.py               # download and build (no-op if current)
    python3 scripts/fetch_icons.py --force       # rebuild even if icons.json is current
    python3 scripts/fetch_icons.py --zip PKG.zip # build from a zip downloaded by hand

To move to a newer package, update PACKAGE, URL and SHA256 below (see SKILL.md,
"Updating the icon set").
"""
import argparse
import hashlib
import json
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_bundle  # noqa: E402

PACKAGE = "Icon-package_07312026"
URL = ("https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/"
       "architecture-icon-release/Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92.zip")
SHA256 = "d2d166c453526471749d520e0db022c459abef759d2946cf2dd1d1c992dc6526"
USER_AGENT = "skill-aws-arch-diagram (+https://github.com/conft2k/skill-aws-arch-diagram)"
OUT = build_bundle.OUT


def log(msg):
    print(msg, file=sys.stderr)  # stdout stays clean for the calling script's output


def current():
    """The bundle's sets if icons.json exists and was built from PACKAGE, else None."""
    if not OUT.exists():
        return None
    bundle = json.loads(OUT.read_text(encoding="utf-8"))
    return bundle["sets"] if bundle.get("package") == PACKAGE else None


def download(dest: Path):
    log(f"Downloading {PACKAGE} from AWS (~14 MB) ...")
    req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        while chunk := resp.read(1 << 20):
            f.write(chunk)


def build_from_zip(zip_path: Path):
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if digest != SHA256:
        sys.exit(f"SHA-256 mismatch for {zip_path.name}\n  expected {SHA256} ({PACKAGE})\n  got      {digest}\n"
                 "Not the pinned package, or AWS replaced it; nothing was written.")
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp, [n for n in z.namelist() if not n.startswith("__MACOSX/")])
        build_bundle.build(Path(tmp), PACKAGE)


def fetch():
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / f"{PACKAGE}.zip"
        try:
            download(zip_path)
        except OSError as e:
            sys.exit(f"Could not download the AWS icon package: {e}\n"
                     f"Download it by hand from {URL}\n"
                     f"and run: python3 {Path(__file__).resolve()} --zip <downloaded.zip>")
        build_from_zip(zip_path)


def load_sets():
    """Return the icon sets, downloading and building the bundle first if needed."""
    sets = current()
    if sets is None:
        fetch()
        sets = current()
    return sets


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--force", action="store_true", help="rebuild even if icons.json is current")
    ap.add_argument("--zip", type=Path, help="build from this package zip instead of downloading")
    a = ap.parse_args()
    if a.zip:
        build_from_zip(a.zip)
    elif a.force or current() is None:
        fetch()
    else:
        log(f"{OUT} is already built from {PACKAGE}; use --force to rebuild.")


if __name__ == "__main__":
    main()
