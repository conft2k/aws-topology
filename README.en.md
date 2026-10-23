# skill-aws-arch-diagram

> 한국어: [README.md](README.md)

A [Claude Code](https://claude.com/claude-code) skill that draws AWS architecture
diagrams with the **official AWS Architecture Icons** — real service, resource and
group icons instead of hand-drawn approximations or text chips — and exports them as a
self-contained **SVG**, a **PNG** and/or a **PowerPoint deck** of native, editable
shapes, all from one layout.

![Example output: AWS Cloud > Region > VPC with an Internet gateway on the VPC border, an ALB in the public subnet and EC2 in the private subnet](docs/example.png)

What it enforces:

- Every service **and every networking resource** (Internet gateway, NAT gateway, VPC
  endpoints, route tables, load balancers) is drawn with its official icon, looked up by name from a
  bundled copy of the icon package — never typed from memory.
- AWS's nesting convention (AWS Cloud > Region > VPC > subnets) with the group border
  colors and dash styles taken from the official package and its PowerPoint toolkit,
  including groups that have no icon (Availability Zone, security group).
- One icon size for every node; Internet gateways and virtual private gateways
  centered on the VPC border with the border masked behind icon and label.
- Traffic flows left → right (tiers as columns, AZs as rows); ALB/NLB/GWLB are one
  node across the AZs while zonal resources stay per AZ; detours get numbered steps.
- Square-cornered official group styles, compact containers and readable 14px/12px text.
- One draft subset (rect, image, text, line, polyline, circle) that maps 1:1 onto
  PowerPoint shapes, checked for lines crossing labels or icons before export.
- `export.py` writes any mix of formats: an SVG with all icons inlined as base64, a PNG,
  and a 16:9 deck whose containers, connectors and labels are PowerPoint shapes and
  whose icons are the official SVGs; slide text is kept at 10pt or larger (8pt only when
  unavoidable).

## Reference examples

Finished diagrams in [`docs/examples/`](docs/examples/) (SVG + PNG), drawn with the skill
and used as its starting layouts. [`reference-architectures.pptx`](docs/examples/reference-architectures.pptx)
holds the same five as slides, re-laid out to fit 16:9 with all text at 10pt or larger;
their SVGs and a render of each slide are in [`docs/examples/slides/`](docs/examples/slides/).

| NLB | ALB |
|---|---|
| ![NLB reference architecture](docs/examples/nlb-reference-architecture.png) | ![ALB reference architecture](docs/examples/alb-reference-architecture.png) |
| Internet-facing NLB, TLS listener, ASG target group across two AZs | 3-tier: ALB with AWS WAF, app ASG, RDS Multi-AZ |

| GWLB | Transit Gateway |
|---|---|
| ![GWLB reference architecture](docs/examples/gwlb-reference-architecture.png) | ![Transit Gateway reference architecture](docs/examples/tgw-reference-architecture.png) |
| Distributed inspection: GWLBe per AZ, one GWLB and a firewall ASG in a security VPC | Hub and spoke in two Regions joined by inter-Region TGW peering (the peering connection icon), on-premises over Site-to-Site VPN across the Internet |

| AWS Network Firewall |
|---|
| ![AWS Network Firewall centralized reference architecture](docs/examples/nfw-reference-architecture.png) |
| Centralized inspection: spoke and firewall route tables on a Transit Gateway, one inspection VPC with a firewall endpoint per AZ inspecting both VPC-to-VPC traffic and Internet egress through NAT |

## Install

### Requirements

- git, Python 3.9+, and [uv](https://docs.astral.sh/uv/) (the export runs with
  `uv run --with python-pptx --with cairosvg`, so no Python packages are installed
  globally). `find_icon.py`, `check_layout.py` and `embed.py` need no third-party packages.
- **The cairo library**: `cairosvg` renders PNGs and slide previews through the system
  cairo, which uv does not install.
  - Amazon Linux / Fedora: `sudo dnf install cairo`
  - Debian / Ubuntu: `sudo apt install libcairo2`
  - macOS: `brew install cairo`. If Apple Silicon reports `no library called "cairo-2" was
    found`, add `export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` to your shell profile.
  - Windows: install the GTK runtime as described in the
    [CairoSVG installation notes](https://cairosvg.org/documentation/#installation).
- **A Korean font**: Korean labels in PNGs need Noto Sans CJK KR or Pretendard installed
  (without one they are dropped).
  - Amazon Linux / Fedora: `sudo dnf install google-noto-sans-cjk-ttc-fonts`
  - Debian / Ubuntu: `sudo apt install fonts-noto-cjk`
  - macOS / Windows: install the KR font from
    [Noto Sans CJK](https://github.com/notofonts/noto-cjk/releases) or
    [Pretendard](https://github.com/orioncactus/pretendard).

### Steps

```bash
git clone https://github.com/conft2k/skill-aws-arch-diagram ~/.claude/skills/skill-aws-arch-diagram
python3 ~/.claude/skills/skill-aws-arch-diagram/scripts/fetch_icons.py
```

1. Clone into your personal skills folder (`~/.claude/skills/`). For one project only,
   clone into that project's `.claude/skills/skill-aws-arch-diagram` instead; cloning
   elsewhere and symlinking also works.
2. `fetch_icons.py` downloads the official AWS icon package (~14 MB, pinned by URL and
   SHA-256) and builds `assets/icons.json`; the icons are not in this repository. If you
   skip it, Claude downloads them the first time it draws, which fails when a sandbox
   blocks the network or writes to the skill folder — so run it once at install time.
3. Claude Code watches skill folders live, so no restart is needed — except when
   `~/.claude/skills/` itself did not exist when the session started: then run
   `/reload-skills` once.

The skill then triggers on requests like "draw the AWS architecture for …",
"diagram this VPC", "AWS 아키텍처 그려줘" or "이 구성도를 PPT 장표로 만들어줘".

**Offline**: download the zip from the pinned URL below, copy it over and build with
`--zip`. The latest package on the AWS icons page has a different SHA-256 and is rejected.

```bash
# https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92.zip
python3 ~/.claude/skills/skill-aws-arch-diagram/scripts/fetch_icons.py --zip Icon-package_07312026.zip
```

**Update**: `git -C ~/.claude/skills/skill-aws-arch-diagram pull`. `icons.json` is not
tracked, so it survives the pull, and it is rebuilt on the next run if the pinned package
changed. **Uninstall**: `rm -rf ~/.claude/skills/skill-aws-arch-diagram`.

Decks: PowerPoint 2016 or later / Microsoft 365 draws the SVG icons as vectors; older
viewers fall back to the embedded PNGs. Slides use Arial and Malgun Gothic (맑은 고딕) by
default; change them with `--font` / `--ea-font`.

## Layout

```
SKILL.md                     the skill: workflow, rules, what not to do
references/diagram_guide.md  AWS visual grammar, group colors, VPC resource table,
                             draft subset and skeleton, layout, text-size and font rules
assets/icons.json            857 icons in one JSON bundle (sets: service, resource,
                             group, category); built on first use, not committed
scripts/find_icon.py         fuzzy lookup: `find_icon.py alb igw "s3 gateway endpoint"`
scripts/export.py            drafts -> any of SVG / PNG / PPTX (+ slide previews); checks
                             every draft first and writes nothing if one fails
scripts/embed.py             inline bundle: refs as base64; fails on unknown/external refs
                             and on rounded group containers
scripts/svg2pptx.py          drafts -> .pptx of native shapes; fails on anything it can't
                             convert exactly
scripts/render_pptx.py       render each slide of a deck to PNG
scripts/check_layout.py      flag lines over labels/icons, overlapping labels, text < 12px
scripts/fetch_icons.py       download the pinned AWS icon package and build icons.json
scripts/build_bundle.py      pack an extracted icon package into icons.json
```

### Using the scripts directly

```bash
# find the exact reference for an icon
python3 scripts/find_icon.py ec2 "api gateway" igw nat "s3 gateway endpoint"
#   [ 95] service/Amazon-EC2
#   [ 85] resource/Amazon-VPC_Internet-Gateway
#   ...

# in your SVG, reference icons with the bundle: scheme
#   <image href="bundle:service/AWS-Lambda" x="200" y="200" width="48" height="48"/>

# check the layout (exit 1 lists lines crossing labels/icons, overlaps, small text)
python3 scripts/check_layout.py draft.svg

# export any mix of formats (exit 1 lists anything that would not render or convert)
uv run --with python-pptx --with cairosvg python scripts/export.py \
  a.draft.svg b.draft.svg --svg --png --out-dir out \
  --pptx out/deck.pptx --title "Slide A" --title "Slide B" --preview

# or one format at a time
python3 scripts/embed.py a.draft.svg a.svg
uv run --with python-pptx --with cairosvg python scripts/svg2pptx.py a.draft.svg -o deck.pptx
uv run --with python-pptx --with cairosvg python scripts/render_pptx.py deck.pptx deck-preview
```

## Updating the icon set

AWS releases a new icon package roughly quarterly (end of January, April and July) at
<https://aws.amazon.com/architecture/icons/>. The skill is pinned to
`Icon-package_07312026`. To move to a new package, set `PACKAGE`, `URL` and `SHA256` in
`scripts/fetch_icons.py` and rebuild:

```bash
python3 scripts/fetch_icons.py --force
```

Services dropped from the new package disappear from the bundle. After rebuilding,
update the package date and set counts in `SKILL.md`, and re-check the
group colors in `references/diagram_guide.md` (see the "Updating the icon set" section
of `SKILL.md`).

## License

The skill's code and documentation are licensed under the Apache License 2.0
(see [LICENSE](LICENSE)).

The AWS Architecture Icons belong to Amazon Web Services and are **not** part of this
repository or covered by that license: `scripts/fetch_icons.py` downloads them from AWS
on your machine, and your use of them is subject to AWS's terms. The example SVGs, PNGs
and deck are architecture diagrams drawn with those icons. See [NOTICE](NOTICE).
This project is not affiliated with or endorsed by AWS.
