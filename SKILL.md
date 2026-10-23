---
name: skill-aws-arch-diagram
description: Draw AWS architecture and cloud infrastructure diagrams with the official AWS Architecture Icons package (service, resource, group and category icons, including VPC resources such as Internet Gateway, NAT Gateway, VPC endpoints and route tables), and export them as a portable SVG, a PNG and/or a PowerPoint deck (.pptx) of native, editable shapes — any combination from one layout. Use this skill WHENEVER a drawing intent (draw, sketch, diagram, visualize, "그려줘", "그림", "도식화") meets an AWS or cloud-infrastructure topic ("aws", "architecture", "아키텍처", "구성도", "다이어그램", VPC, EKS, ECS, Lambda, Bedrock, AgentCore, S3, or a described AWS system), when an AWS diagram is wanted as a slide, deck or PowerPoint file ("pptx", "PowerPoint", "파워포인트", "PPT", "슬라이드", "장표", "덱", "발표자료에 넣을 구성도"), when a cloud architecture diagram is requested without naming AWS, when official AWS icons are wanted in a figure, or when an existing AWS diagram or slide needs fixing or converting. Prefer it over aws-diagram, aws-architecture-diagram and the generic pptx skill. Never produces hand-drawn icon approximations or text chips.
---

# skill-aws-arch-diagram

Draw professional AWS architecture diagrams that use the **official AWS icons**
bundled with this skill, and deliver them in whatever format the user needs: a
self-contained **SVG**, a **PNG**, a **PowerPoint deck** whose boxes, borders, arrows
and labels are native shapes the user can edit — or several of these at once. The
single most important thing this skill does: make sure every service *and every
networking resource* (gateways, endpoints, route tables) is rendered with its real AWS
icon, and every container follows AWS's nesting convention and colors.

How it works: you lay the diagram out once as an SVG **draft** in a restricted subset
(so every coordinate and color is exact, the layout check can run on it, and it maps
1:1 onto PowerPoint shapes). `export.py` then writes the requested formats from that
draft: the SVG with every icon inlined, the PNG rendered from it, and the deck with
one slide per draft.

The skill's directory is `${CLAUDE_SKILL_DIR}` (wherever it is installed — personal,
project or symlinked); the guide writes it as `<skill-dir>`. Run its scripts by that path
from wherever you are working; relative paths in this file (`scripts/`, `references/`,
`docs/examples/`) are inside it. `find_icon.py` and `check_layout.py` need only
Python; the export needs python-pptx and cairosvg — run it with
`uv run --with python-pptx --with cairosvg python ...` (no install needed).

The AWS icons are not shipped with the skill. The first script that needs them
downloads the pinned official package from AWS (~14 MB, SHA-256 checked) and builds
`assets/icons.json`; this takes a few seconds once. If the download fails (no network),
tell the user to download the zip from the URL in the error and run
`python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_icons.py --zip <zip>`. If it fails only
inside the session (sandboxed network or writes), ask the user to run
`python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_icons.py` once in their own shell.

## When to use

Any request that pairs a **drawing intent** with an **AWS / cloud-infra topic**. Examples:
- "AWS 아키텍처 그려줘" / "draw the architecture for this system on AWS"
- "이 구성을 다이어그램으로 만들어줘" (about an AWS stack)
- "diagram the VPC / EKS / serverless / AgentCore setup"
- "AWS 아키텍처를 PPT 장표로 만들어줘" / "이 구성도를 파워포인트에서 편집할 수 있게"
- "README에 넣을 SVG랑 발표용 pptx 둘 다"
- Fixing, restyling or converting an existing AWS diagram or slide.
- Any figure or slide that should contain official AWS icons.

If the request is purely conceptual (no drawing) or not AWS-related, this skill
doesn't apply.

**Pick the formats** from the request: a document, README or web page → SVG (plus PNG
when it should preview everywhere, e.g. a repo sample); a slide, deck or "editable in
PowerPoint" → PPTX; both when asked. With no hint, deliver an SVG and its PNG.

## Workflow

Follow these steps in order. Don't skip the icon lookup — guessing names is the
main failure mode, and replacing a missing icon with a text box is the second.

### 1. Understand the architecture
Extract the components, their AWS services, and the flow (who calls what, what's
public vs private, what's on-prem). If the user gave a stack in prose or an existing
system (CloudFormation, CDK, Terraform, deploy scripts), map each piece to an AWS
service or resource. Ask a brief clarifying question only if the topology is genuinely
ambiguous; otherwise proceed with a sensible default and note assumptions. For a deck,
settle the slide titles (one line each, or none) and the list of slides.

### 1b. Start from the closest reference example
`docs/examples/` holds finished, checked reference layouts — NLB, ALB (3-tier with
WAF and RDS Multi-AZ), GWLB (distributed inspection), Transit Gateway (hub and
spoke in two Regions joined by TGW peering drawn as the peering connection icon between
the Regions, VPCs as single icons) and AWS Network
Firewall (centralized inspection VPC behind a Transit Gateway, with spoke and firewall
route tables and NAT egress) — as document-size drafts (`*.svg`) with their PNGs.
`slides/` holds a slide-size version of each (`slides/*.svg`, ≤ 1108 × 540, all text
≥ 10pt on a titled slide), the deck made from them (`reference-architectures.pptx`)
and a render of each slide (`slides/*.png`). When the request resembles one of them,
open its SVG — the `slides/` one for a deck — and reuse its layout and coordinates
(canvas, AZ rows, tier columns, gap, IGW, regional services, note line) instead of
laying out from scratch.
`docs/example.svg` is the minimal skeleton.

### 2. Read the guide
Read `references/diagram_guide.md` in full. It defines the AWS visual grammar
(Cloud > Region > VPC > subnet nesting), the exact group border colors, the VPC
resource icon table, layout rules, the draft subset and the skeleton. The diagram will
look wrong if you skip it.

### 3. Find the exact icons
All icons live inside a single bundle, `assets/icons.json` (not a folder of files; built from
the official package on first use).
For every service, resource and container, look up its exact reference — do not type
it from memory:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/find_icon.py ec2 "api gateway" s3 igw "s3 gateway endpoint"
```

It prints ranked `set/name` references (e.g. `service/AWS-Lambda`, `group/AWS-Cloud-logo_32`,
`resource/Amazon-VPC_Internet-Gateway`). Common
abbreviations (alb, ecs, s3, vpc, igw, nat, vpce, eice, rtb, ...) are aliased. List a whole
set with `--list resource`. Sets available: `service` (303), `resource` (513),
`group` (15), `category` (26).

Bedrock is `service/Amazon-Bedrock` and AgentCore is `service/Amazon-Bedrock-AgentCore`.
AgentCore *components* (Runtime, Gateway, Memory, Identity, ...) have no official icon
yet — see the guide's "Bedrock and AgentCore" for how to draw them.

**Every AWS service or resource in the diagram that has an official icon is drawn as
that icon** — including the ones that are easy to leave as a connector label or a text
box: Site-to-Site VPN, Direct Connect, PrivateLink, VPC peering, TGW peering, Transit Gateway, Global
Accelerator, CloudFront, WAF, NAT gateway, endpoints, route tables. Run `find_icon.py`
on every service or resource you are about to write as text; if it returns a score-95
`service/` or `resource/` hit, it becomes a node with its icon. Connector labels carry
only protocols, ports and verbs ("IPsec", "HTTPS :443", "GENEVE :6081", "read/write").
Two exceptions: a service already shown by another node (the GWLBe *is* the
PrivateLink endpoint — drop "PrivateLink" from the label rather than adding a second
icon), and a connection type with no icon in the bundle stays a label. A TGW peering
is the peering connection icon (`resource/Amazon-VPC_Peering-Connection`) on the
TGW–TGW line, as in the AWS docs — across Regions, in the gap between the Region boxes.
`check_layout.py` flags connector labels that name a service with an icon.

If nothing in `service` matches, search `resource` before concluding there is no
icon — gateways, endpoints, instances, tables and buckets are resources. An icon filed
under another service still counts when it is the package's only icon for the thing
(route tables are `resource/Amazon-Route-53_Route-Table`). Only if neither set has it,
use the closest **category** icon or a plain labeled rounded rect, and say so to the
user. Never hand-draw a fake product mark.

### 4. Compose the draft
Build one `.svg` draft per diagram (one per slide for a deck) in the scratchpad, named
`<name>.draft.svg`, following the skeleton and layout rules in the guide. Reference
each icon with the **`bundle:` scheme** in the `href` — this is how the export finds it:

```xml
<image href="bundle:service/AWS-Lambda"   x="200" y="200" width="48" height="48"/>
<image href="bundle:group/AWS-Cloud-logo_32" x="20" y="20" width="32" height="32"/>
<image href="bundle:resource/Amazon-VPC_Endpoints" x="482" y="331" width="48" height="48"/>
```

Use only the elements of the draft subset (guide: "Composing the layout SVG"), whatever
formats are wanted: `rect`, `image`, one-line `text`, `line`, `polyline fill="none"`,
`circle`, `g transform="translate(...)"`, and arrow markers in `defs`. Presentation
attributes only (no `style=`/`class=`), `#RRGGBB` colors, no `<path>` outside markers,
and no text halos — mask a label with a white rect instead.

- Draw group containers first (AWS Cloud, Region, VPC, subnets) as **square-cornered**
  rects (no `rx` — the official style; a rounded border makes the square corner badge
  stick out, and the export rejects it) whose border color matches the group icon (VPC
  is purple `#8C4FFF`) + a corner group-icon badge + a label. The AWS Cloud badge is
  **always** `group/AWS-Cloud-logo_32` (with the AWS logo; `_Dark` on dark
  backgrounds), never the logo-less `group/AWS-Cloud_32` — the export rejects it.
- Place each service and resource as an `<image href="bundle:...">` with a centered
  label directly below. **Every node icon is the same size** — services, resources
  (IGW, NAT, endpoints, route tables, ALB) and users/servers alike, 48px by default.
  Availability Zones and security groups have no badge icon — label-only rects in the
  guide's group colors.
  Only container corner badges (22–32px) and legend icons differ. If space is tight,
  change the size for the whole diagram, never for a few icons. **Exception:** when
  specific services are meant to be highlighted, enlarge just those to one emphasis
  size (~1.33×, 64px) on the same grid centers — see the guide's "Emphasis is the one
  exception".
- Draw a **fully managed multi-AZ service (ALB, NLB, GWLB) as one node**, not one per
  AZ: a single icon in the gap between the AZ rows, in its tier's column, with one arrow to a
  target group / Auto Scaling group box that spans the AZs. Zonal resources (NAT
  gateways, instances, subnets) stay per AZ. Per-AZ LB nodes only when the user asks
  about per-AZ behavior — see the guide's "Fully managed multi-AZ services are one node".
- Put every Internet gateway and VGW (virtual private gateway) **on the VPC border**:
  icon centered on the border line (e.g. `x = vpcX + vpcW - S/2` for the right edge),
  on the edge facing the Internet / on-prem side, label centered directly below it —
  **"IGW"** / **"VGW"** by default (the full "Internet gateway" only if the user asks). Draw
  one white rect behind the icon and its label first so the border (and any other line)
  never crosses the text. See the guide's "Internet gateway and VGW sit on the VPC
  border" for the mask sizing.
- Connect with consistent 1.5px squid-ink (`#232F3E`) arrows using one shared
  arrowhead marker. Label non-obvious connectors (protocol / verb).
- **Traffic flows left → right**: users and entry points on the left, data stores on the
  right, every main-path arrow pointing right. In a VPC that means tiers as columns
  (public → private → data) and AZs as rows. Top-to-bottom only for non-traffic
  diagrams or on request — see the guide's layout rules. Align on a grid.
- **Compact layout, readable text**: containers hug their contents (16–24px padding,
  node centers ~100–120px apart, no empty areas), and text is 14px for node and
  container labels, 12px for connector/secondary labels, never smaller — see the
  guide's "Compact, not empty" and "Text size".
- **Size the canvas for the format.** A document SVG/PNG can be as large as its content
  needs (the reference layouts are up to 1180 × 768). A slide is scaled to fit 16:9
  (below the title band if there is one), so the canvas decides the slide's text size:
  - **Slide text is 10pt or larger.** Every label on the slide — the 12px connector and
    secondary labels included — must land at **≥ 10pt**: with a title a canvas of at
    most **1108 × 540** (1108 × 600 without a title), close to 16:8 (16:9 without)
    so it fills the slide. Get there by tightening the layout, shortening labels or
    splitting the diagram over two slides.
  - Only when that is genuinely impossible — the diagram can't be split or tightened
    without losing what it shows — may the smallest text go down to **8pt**, never below
    (canvas up to about 1380 × 675 with a title, 1380 × 755 without). Then tell the user
    which slide is under 10pt, its smallest size and why it couldn't be avoided.
  - When the same diagram is wanted as a document image *and* a slide, use one draft if
    it fits the slide limits; otherwise draw a compact slide draft next to the document
    one (same grammar and icons, fewer rows or a split) and tell the user.
  - The document-size reference layouts come out at 8pt or less on a titled slide; for
    a slide start from their `docs/examples/slides/` versions instead.
- Root `font-family` starts with a Korean font that is **installed on this machine** —
  check with `fc-list | grep -iE 'CJK KR|Pretendard'` (see the guide's "Font"). cairosvg
  uses only the first family and drops every Hangul label from the PNG if that one is
  Arial or isn't installed. The deck's fonts are set separately (`--font`/`--ea-font`).

### 5. Check, export and verify
Run the layout check on each draft and fix everything it reports until it prints
"Layout OK":

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check_layout.py name.draft.svg
```

It flags a connector or container border crossing a label, icon or badge, labels
overlapping each other or an icon, text under 12px, an arrowhead on a stub under
20px, a trunk squeezed against a container border, a container CIDR outside its header, and circled-digit step legends — the defects that otherwise
only show up in a render. Masked crossings (IGW/VGW on the VPC border) are allowed.

Then export the formats you need — any combination, from the same drafts:

```bash
uv run --with python-pptx --with cairosvg python ${CLAUDE_SKILL_DIR}/scripts/export.py \
  a.draft.svg b.draft.svg --svg --png --out-dir docs \
  --pptx docs/architecture.pptx --title "Slide A" --title "Slide B" --preview
```

- `--svg` writes `<out-dir>/<name>.svg` per draft with every icon inlined as base64, so
  it renders standalone anywhere; `--png` renders it to `<name>.png` (`--png-width`,
  default 2000).
- `--pptx DECK` writes one 16:9 deck, one slide per draft in order, `--title` once per
  slide; `--font` / `--ea-font` change the Latin / Korean typeface (default Arial /
  Malgun Gothic). `--preview` renders each slide back to `DECK-1.png`, `DECK-2.png`, ...
  from what the .pptx actually contains (not PowerPoint: text uses the installed Korean
  font, so widths differ a little; if PowerPoint or LibreOffice is available, also open
  the deck there).
- Every draft is checked before anything is written: unknown `bundle:` refs, an
  `<image>` pointing at an external file, an AWS Cloud badge without the logo, a rounded
  group container, or anything outside the draft subset (`<path>`, scale/rotate
  transforms, `style=`, text halos). The export exits with status 1, writes nothing and
  lists the offending elements; fix them and re-run until it exits 0.
- For each slide under 10pt it prints a note, and under 8pt a WARNING — a slide with
  that warning is not deliverable.

The single-format scripts behind it also run on their own: `embed.py draft.svg out.svg`,
`svg2pptx.py drafts... -o deck.pptx [--title ...]`, `render_pptx.py deck.pptx preview`.

Look at every PNG / slide render before delivering — the check estimates text widths,
and balance, whitespace and readability still need eyes. Go through this checklist:

- [ ] Main traffic path reads left → right; only return/outbound/management arrows
      go another way, and those are dashed.
- [ ] Tiers are columns, AZs are rows; Users and the IGW sit in the gap between the
      AZ rows, on one line with the load balancer.
- [ ] Every arrowhead sits on a segment ≥ 20px long, and a trunk that joins per-AZ
      lines keeps ≥ 12px from the AZ boxes (widen the corridor, not the canvas on a
      slide).
- [ ] Each ALB/NLB/GWLB is one node in the AZ gap; zonal resources (NAT gateway,
      GWLBe, instances, RDS primary/standby) appear once per AZ.
- [ ] A path that leaves the main line and comes back has numbered step badges, and
      the note's legend repeats those same badges (not ①), left-aligned — in a
      document one step per row with a bold hop and a sentence on the route and what
      happens there; on a slide short items flowed in one or two rows. The legend
      holds only the steps — no unnumbered rows mixed in.
- [ ] Every VPC and subnet CIDR is in its container's header (top-left), not a caption
      inside the box; a spanning box that would cross a header moves instead.
- [ ] Group containers are square-cornered, in the official colors and dash styles.
- [ ] Containers hug their contents; no empty areas; text 14px (nodes, containers) /
      12px (connectors, notes); a slide is filled without crowding the title.
- [ ] Slides: the export printed no note — all slide text is ≥ 10pt; 8–10pt only when
      unavoidable and the user is told; never under 8pt.
- [ ] Every AWS service/resource with an official icon is an icon node, not a label or
      text box.
- [ ] A Site-to-Site VPN path is CGW → Internet → Site-to-Site VPN → TGW/VGW, with the
      Internet and VPN icons outside the AWS Cloud; a Direct Connect path does not pass
      the Internet icon.
- [ ] Technically sound (guide, "Technical correctness"): each hop carries the protocol
      really on it (no "TCP :443" after TLS termination; GENEVE only GWLB ⇄ appliances);
      route captions include return routes; global services (Route 53, CloudFront)
      are outside the Region; captions don't credit a service with another's job;
      identical per-AZ hops are drawn identically.
- [ ] The note (legend / routes) is outside the AWS Cloud box. In a document it is in
      the note panel at the bottom, full canvas width with 16px each side; on a slide,
      a panel only if the canvas stays ≤ 540, else plain lines left-aligned with the
      Cloud.
- [ ] `check_layout.py` prints "Layout OK" and `export.py` exits 0.

Save the outputs where the user asked (in a repo, usually next to the docs that
reference them, e.g. `docs/architecture.svg`, `docs/architecture.pptx`). When a diagram
is a sample or reference for a repo, save the PNG next to the SVG and the slide renders
next to the deck (`--preview`), since a PNG previews everywhere. Keep drafts in the
scratchpad unless the user wants the layout source too, and tell the user the paths.
If the user asked for an editable web page, wrap the exported SVG in a minimal HTML
file.

## Output format

- **SVG**: one self-contained file per diagram, every icon inlined as base64.
- **PNG**: rendered from that SVG, 2000px wide by default.
- **PPTX**: 16:9, one architecture per slide. The diagram on each slide is one group
  named "Architecture diagram" — it moves and scales as a unit, and ungrouping it gives
  the individual shapes. Containers, connectors and labels are PowerPoint shapes; icons
  are pictures carrying the official SVG (PowerPoint 2016+/Microsoft 365 draw the vector
  and can "Convert to Shape"; older viewers show the embedded PNG fallback), each named
  after its icon (`Amazon-EC2`, ...). Tell the user which fonts the deck uses (default
  Arial + Malgun Gothic).
- Preserve official icon colors; keep containers/text/arrows in AWS neutrals and the
  group colors from the guide.
- Bilingual (Korean/English) labels are expected and fine for FSI/customer diagrams.
- Label the Internet gateway **"IGW"** (and the virtual private gateway "VGW") unless
  the user asks for the full name; long labels on the VPC border hurt readability.

## What NOT to do

- Don't hand-draw or approximate AWS icons — use the bundled ones, and don't swap in
  PowerPoint's built-in icons or clip art.
- Don't build a slide with python-pptx by hand or with the generic pptx skill — lay it
  out as a draft and export it, so the layout check and the exact group styles apply.
- Don't write an AWS service that has an official icon (Site-to-Site VPN, Direct
  Connect, PrivateLink, ...) as a connector label — draw it as an icon node.
- Don't draw an Internet Gateway, NAT Gateway, VPC endpoint, EICE or route table as a
  text chip or pill — they all have official resource icons (see the guide's VPC table;
  route tables use `resource/Amazon-Route-53_Route-Table`, the package's only route
  table icon, even though it is filed under Route 53).
- Don't put an Internet gateway or VGW inside a subnet, fully inside the VPC, or
  floating outside it — center it on the VPC border.
- Don't put anything else on the VPC border. Gateway endpoints (S3, DynamoDB) go
  inside the VPC box, outside the subnets; interface endpoints go inside their subnet.
- Don't color the VPC border green; it's purple `#8C4FFF`.
- Don't put private services (RDS, internal ALB) outside a subnet container.
- Don't draw an ALB, NLB or GWLB once per AZ in a standard reference diagram — one
  load balancer is one node.
- Don't route the main traffic path up/down or right-to-left in a traffic diagram;
  rearrange the containers (tiers as columns) until it flows left → right.
- Don't mix icon sizes (e.g. 56px services next to 36px gateways) — one size for every
  node icon, unless you are deliberately emphasizing specific services.
- Don't use rainbow connectors or inconsistent arrow styles.
- Don't cram several architectures onto one slide — one diagram per slide, more slides
  if needed.
- Don't deliver an SVG that references external icon files or `bundle:` refs (won't
  render for the user) — always deliver the exported version.

## Asset inventory

All 857 icons are packed into one JSON bundle (keeps the skill's file count low):

- `assets/icons.json` — the icon bundle, not in the repository: `scripts/fetch_icons.py`
  downloads the AWS Architecture Icons package released 2026-07-31
  (`Icon-package_07312026`, pinned by URL and SHA-256) and builds it on first use.
  Sets: `service`, `resource`, `group`, `category`. SVGs stored as text.
- `references/diagram_guide.md` — conventions, colors, VPC resources, the draft subset and skeleton (read this).
- `scripts/find_icon.py` — fuzzy lookup → `set/name` reference (with AWS abbreviation aliases).
- `scripts/check_layout.py` — flag lines over labels/icons, overlapping labels, text under 12px.
- `scripts/export.py` — check drafts and write any of SVG, PNG and PPTX in one step.
- `scripts/embed.py` — inline `bundle:set/name` hrefs as base64 for a portable SVG.
- `scripts/svg2pptx.py` — convert drafts into a deck of native PowerPoint shapes.
- `scripts/render_pptx.py` — render each slide of a deck to PNG for the visual check.
- `scripts/fetch_icons.py` — download the pinned official package and build `icons.json`
  (`--force` rebuilds, `--zip` builds from a zip downloaded by hand).
- `scripts/build_bundle.py` — pack an extracted package into `icons.json` (called by
  `fetch_icons.py`).
- `scripts/macos_cairo.py` — imported before cairosvg so it finds Homebrew's cairo on
  Apple Silicon without shell setup.
- `docs/examples/` — checked NLB, ALB, GWLB, TGW and Network Firewall reference layouts
  (drafts + PNG); `slides/` has their slide-size versions, the deck made from those and
  a render of each slide.

## Updating the icon set

AWS publishes a new package a few times a year at
https://aws.amazon.com/architecture/icons/. To pick it up:

1. Copy the new "Icon package" zip link from the page, download it, and take its
   `sha256sum`.
2. Set `PACKAGE`, `URL` and `SHA256` in `scripts/fetch_icons.py`, then run
   `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_icons.py`.
3. Check the printed set counts, re-check the group colors in the guide against the
   new group SVGs and the "Groups" slide of the PPTx toolkit (download it from the same
   page; unzip the .pptx and grep `srgbClr`/`prstDash` in `ppt/slides/slide*.xml` —
   it is the only source for groups without an icon, e.g. Availability Zone), and
   update the package date and counts in this file (the counts live only here).

Services dropped from a new package disappear from the bundle; drafts that use them stop
resolving, so redraw those nodes with the successor service's icon.
