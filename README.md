# aws-topology

A [Claude Code](https://claude.com/claude-code) skill that draws AWS architecture
diagrams with the **official AWS Architecture Icons** — real service, resource and
group icons instead of hand-drawn approximations or text chips — and delivers one
self-contained SVG.

![Example output: AWS Cloud > Region > VPC with an Internet gateway on the VPC border, an ALB in the public subnet and EC2 in the private subnet](docs/example.png)

What it enforces:

- Every service **and every networking resource** (Internet gateway, NAT gateway, VPC
  endpoints, load balancers) is drawn with its official icon, looked up by name from a
  bundled copy of the icon package — never typed from memory.
- AWS's nesting convention (AWS Cloud > Region > VPC > subnets) with the group border
  colors and dash styles taken from the official package and its PowerPoint toolkit,
  including groups that have no icon (Availability Zone, security group).
- One icon size for every node; Internet gateways and virtual private gateways
  centered on the VPC border with the border masked behind icon and label.
- Traffic flows left → right (tiers as columns, AZs as rows); ALB/NLB/GWLB are one
  node across the AZs while zonal resources stay per AZ; detours get numbered steps.
- Square-cornered official group styles, compact containers and readable 14px/12px text.
- A final SVG with all icons inlined as base64, verified to contain no external
  references, checked for lines crossing labels or icons, and rendered to PNG for a
  visual check before delivery.

## Reference examples

Finished diagrams in [`docs/examples/`](docs/examples/) (SVG + PNG), drawn with the skill
and used as its starting layouts:

| NLB | ALB | GWLB |
|---|---|---|
| ![NLB reference architecture](docs/examples/nlb-reference-architecture.png) | ![ALB reference architecture](docs/examples/alb-reference-architecture.png) | ![GWLB reference architecture](docs/examples/gwlb-reference-architecture.png) |
| Internet-facing NLB, TLS listener, ASG target group across two AZs | 3-tier: ALB with AWS WAF, app ASG, RDS Multi-AZ | Distributed inspection: GWLBe per AZ, one GWLB and a firewall ASG in a security VPC |

## Install

```bash
git clone https://github.com/conft2k/aws-topology ~/.claude/skills/aws-topology
```

Or clone it elsewhere and symlink it to `~/.claude/skills/aws-topology`. Restart
Claude Code; the skill triggers on requests like "draw the AWS architecture for …",
"diagram this VPC", or "AWS 아키텍처 그려줘".

Requirements: Python 3.9+ (no third-party packages for the scripts). The optional
PNG preview uses [cairosvg](https://cairosvg.org/) via `uv run --with cairosvg`;
Korean labels in the preview need a CJK font installed (e.g. Noto Sans CJK KR).

## Layout

```
SKILL.md                     the skill: workflow, rules, what not to do
references/diagram_guide.md  AWS visual grammar, group colors, VPC resource table,
                             SVG skeleton, layout and font rules
assets/icons.json            873 icons in one JSON bundle (sets: service, resource,
                             group, category, legacy)
scripts/find_icon.py         fuzzy lookup: `find_icon.py alb igw "s3 gateway endpoint"`
scripts/embed.py             inline bundle: refs as base64; fails on unknown/external refs
                             and on rounded group containers
scripts/check_layout.py      flag lines over labels/icons, overlapping labels, text < 12px
scripts/build_bundle.py      rebuild icons.json from a newly released icon package
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

# then inline them for a portable file (exit 1 lists anything that would not render)
python3 scripts/embed.py draft.svg final.svg
```

## Updating the icon set

AWS releases a new icon package roughly quarterly (end of January, April and July) at
<https://aws.amazon.com/architecture/icons/>. The bundle currently matches
`Icon-package_07312026`.

```bash
unzip Icon-package_*.zip -d /tmp/aws-icons
python3 scripts/build_bundle.py /tmp/aws-icons
```

Services dropped from the new package move to the `legacy` set automatically. After
rebuilding, update the package date and set counts in `SKILL.md`, and re-check the
group colors in `references/diagram_guide.md` (see the "Updating the icon set" section
of `SKILL.md`).

## License

The skill's code and documentation are licensed under the Apache License 2.0
(see [LICENSE](LICENSE)).

`assets/icons.json` repackages the AWS Architecture Icons, which belong to Amazon Web
Services and are **not** covered by that license; they are included unmodified so the
skill can draw AWS diagrams, and your use of them is subject to AWS's terms. See
[NOTICE](NOTICE). This project is not affiliated with or endorsed by AWS.
