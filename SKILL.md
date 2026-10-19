---
name: aws-topology
description: Draw AWS architecture and cloud infrastructure diagrams using the official AWS Architecture Icons package (service, resource, group and category icons, including VPC resources such as Internet Gateway, NAT Gateway and VPC endpoints). Use this skill WHENEVER a drawing intent (draw, sketch, diagram, visualize, "그려줘", "그림", "도식화") meets an AWS or cloud-infrastructure topic ("aws", "architecture", "아키텍처", "구성도", "다이어그램", VPC, EKS, ECS, Lambda, Bedrock, AgentCore, S3, or a described AWS system), when a cloud architecture diagram is requested without naming AWS, when official AWS icons are wanted in a figure, or when an existing AWS diagram needs fixing. Prefer it over aws-diagram and aws-architecture-diagram. Produces a self-contained SVG (or HTML) with real AWS icons, never hand-drawn approximations or text chips.
---

# AWS Topology Diagram

Draw professional AWS architecture diagrams that use the **official AWS icons**
bundled with this skill, instead of hand-drawing shapes that don't match what AWS
customers expect to see. The single most important thing this skill does: make sure
every service *and every networking resource* (gateways, endpoints) is rendered with
its real AWS icon, and every container follows AWS's nesting convention and colors.

The skill is installed at `~/.claude/skills/aws-topology/`. Run its scripts by that path
(`python3 ~/.claude/skills/aws-topology/scripts/find_icon.py ...`) from wherever you
are working.

## When to use

Any request that pairs a **drawing intent** with an **AWS / cloud-infra topic**. Examples:
- "AWS 아키텍처 그려줘" / "draw the architecture for this system on AWS"
- "이 구성을 다이어그램으로 만들어줘" (about an AWS stack)
- "diagram the VPC / EKS / serverless / AgentCore setup"
- "show me how CloudFront → ALB → ECS → RDS connects"
- Fixing or restyling an existing AWS diagram.
- Any figure that should contain official AWS icons.

If the request is purely conceptual (no drawing) or not AWS-related, this skill
doesn't apply.

## Workflow

Follow these steps in order. Don't skip the icon lookup — guessing names is the
main failure mode, and replacing a missing icon with a text box is the second.

### 1. Understand the architecture
Extract the components, their AWS services, and the flow (who calls what, what's
public vs private, what's on-prem). If the user gave a stack in prose or an existing
system (CloudFormation, CDK, Terraform, deploy scripts), map each piece to an AWS
service or resource. Ask a brief clarifying question only if the topology is genuinely
ambiguous; otherwise proceed with a sensible default and note assumptions.

### 1b. Start from the closest reference example
`docs/examples/` holds finished, checked reference diagrams — NLB, ALB (3-tier with
WAF and RDS Multi-AZ), GWLB (distributed inspection), Transit Gateway (hub and
spoke in two Regions joined by TGW peering, VPCs as single icons) and AWS Cloud WAN
(core network edges per Region, segments as rows spanning the Regions). When the request resembles
one of them, open its SVG and reuse its layout and coordinates (canvas, AZ rows, tier
columns, gap, IGW, regional-services row, note line) instead of laying out from
scratch. `docs/example.svg` is the minimal skeleton.

### 2. Read the guide
Read `references/diagram_guide.md` in full. It defines the AWS visual grammar
(Cloud > Region > VPC > subnet nesting), the exact group border colors, the VPC
resource icon table, layout rules, and the SVG skeleton.
The diagram will look wrong if you skip it.

### 3. Find the exact icons
All icons live inside a single bundle, `assets/icons.json` (not a folder of files).
For every service, resource and container, look up its exact reference — do not type
it from memory:

```bash
python3 ~/.claude/skills/aws-topology/scripts/find_icon.py ec2 "api gateway" s3 igw "s3 gateway endpoint"
```

It prints ranked `set/name` references (e.g. `service/AWS-Lambda`, `group/AWS-Cloud-logo_32`,
`resource/Amazon-VPC_Internet-Gateway`). Common
abbreviations (alb, ecs, s3, vpc, igw, nat, vpce, eice, ...) are aliased. List a whole
set with `--list resource`. Sets available: `service` (303), `resource` (513),
`group` (15), `category` (26), `legacy` (16 retired service icons).

Bedrock is `service/Amazon-Bedrock` and AgentCore is `service/Amazon-Bedrock-AgentCore`.
AgentCore *components* (Runtime, Gateway, Memory, Identity, ...) have no official icon
yet — see the guide's "Bedrock and AgentCore" for how to draw them.

**Every AWS service or resource in the diagram that has an official icon is drawn as
that icon** — including the ones that are easy to leave as a connector label: Site-to-
Site VPN, Direct Connect, PrivateLink, VPC peering, Transit Gateway, Global
Accelerator, CloudFront, WAF, NAT gateway, endpoints. Run `find_icon.py` on every
service you are about to write as text; if it returns a score-95 `service/` or
`resource/` hit, it becomes a node with its icon on the path. Connector labels carry
only protocols, ports and verbs ("IPsec", "HTTPS :443", "GENEVE :6081", "read/write").
Two exceptions: a service already shown by another node (the GWLBe *is* the
PrivateLink endpoint — drop "PrivateLink" from the label rather than adding a second
icon), and a connection type with no icon in the bundle (TGW peering) stays a label.
`check_layout.py` flags connector labels that name a service with an icon.

If nothing in `service` matches, search `resource` before concluding there is no
icon — gateways, endpoints, instances, tables and buckets are resources. Only if
neither has it, use the closest **category** icon or a plain labeled rounded rect,
and say so to the user. Never hand-draw a fake product mark.

### 4. Compose the SVG
Build a single `.svg` following the skeleton and layout rules in the guide. Reference
each icon with the **`bundle:` scheme** in the `href` — this is how embed.py finds it:

```xml
<image href="bundle:service/AWS-Lambda"   x="200" y="200" width="48" height="48"/>
<image href="bundle:group/AWS-Cloud-logo_32" x="20" y="20" width="32" height="32"/>
<image href="bundle:resource/Amazon-VPC_Endpoints" x="482" y="331" width="48" height="48"/>
```

- Draw group containers first (AWS Cloud, Region, VPC, subnets) as **square-cornered**
  rects (no `rx` — the official style; a rounded border makes the square corner badge
  stick out, and embed.py rejects it) whose border color matches the group icon (VPC is purple `#8C4FFF`) + a corner group-icon
  badge + a label. The AWS Cloud badge is **always** `group/AWS-Cloud-logo_32` (with
  the AWS logo; `_Dark` on dark backgrounds), never the logo-less `group/AWS-Cloud_32`
  — embed.py rejects it.
- Place each service and resource as an `<image href="bundle:...">` with a centered
  label directly below. **Every node icon is the same size** — services, resources
  (IGW, NAT, endpoints, ALB) and users/servers alike, 48px by default.
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
- Connect with consistent 1.5–2px squid-ink (`#232F3E`) arrows using one shared
  arrowhead marker. Label non-obvious connectors (protocol / verb).
- **Traffic flows left → right**: users and entry points on the left, data stores on the
  right, every main-path arrow pointing right. In a VPC that means tiers as columns
  (public → private → data) and AZs as rows. Top-to-bottom only for non-traffic
  diagrams or on request — see the guide's layout rules. Align on a grid.
- **Compact layout, readable text**: containers hug their contents (16–24px padding,
  node centers ~100–120px apart, no empty areas), and text is 14px for node and
  container labels, 12px for connector/secondary labels, never smaller — see the
  guide's "Compact, not empty" and "Text size".
- Root `font-family` starts with a Korean font that is **installed on this machine** —
  check with `fc-list | grep -iE 'CJK KR|Pretendard'` (see the guide's "Font"). cairosvg
  uses only the first family and drops every Hangul label if that one is Arial or isn't
  installed.

### 5. Make it portable and verify
Inline all icons as base64 so the final file renders standalone anywhere:

```bash
python3 ~/.claude/skills/aws-topology/scripts/embed.py draft.svg final.svg
```

It replaces every `bundle:set/name` href with a data: URI from the bundle. It exits
with status 1 and lists the offending hrefs if any `bundle:` ref is unknown or any
`<image>` still points at an external file or URL; fix them (find_icon.py for names)
and re-run until it exits 0.

Run the layout check on the draft and fix everything it reports until it prints
"Layout OK":

```bash
python3 ~/.claude/skills/aws-topology/scripts/check_layout.py draft.svg
```

It flags a connector or container border crossing a label, icon or badge, labels
overlapping each other or an icon, and text under 12px — the defects that otherwise
only show up in a render. Masked crossings (IGW/VGW on the VPC border) are allowed.

Then render it and look at the result before delivering — the check estimates text
widths, and balance, whitespace and readability still need eyes:

```bash
uv run --with cairosvg python -c "import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=2000)" final.svg preview.png
```

cairosvg ignores CSS-class text halos, so a line showing through a haloed label in the
preview is not necessarily a bug in the SVG.

Before delivering, go through this checklist on the render:

- [ ] Main traffic path reads left → right; only return/outbound/management arrows
      go another way, and those are dashed.
- [ ] Tiers are columns, AZs are rows; Users and the IGW sit in the gap between the
      AZ rows, on one line with the load balancer.
- [ ] Each ALB/NLB/GWLB is one node in the AZ gap; zonal resources (NAT gateway,
      GWLBe, instances, RDS primary/standby) appear once per AZ.
- [ ] A path that leaves the main line and comes back has numbered step badges and a
      one-line legend.
- [ ] Group containers are square-cornered, in the official colors and dash styles.
- [ ] Containers hug their contents; no empty areas; text 14px (nodes, containers) /
      12px (connectors, notes).
- [ ] Every AWS service/resource with an official icon is an icon node, not a label.
- [ ] A Site-to-Site VPN path is CGW → Internet → Site-to-Site VPN → TGW/VGW, with the
      Internet and VPN icons outside the AWS Cloud; a Direct Connect path does not pass
      the Internet icon.
- [ ] `check_layout.py` prints "Layout OK" and `embed.py` exits 0.

Save the final SVG where the user asked (in a repo, usually next to the docs that
reference it, e.g. `docs/architecture.svg`). When the diagram is a sample or reference
for a repo, save its PNG render next to it as well (same name, `.png`), since a PNG
previews everywhere. Keep drafts in the scratchpad, and tell the user the paths. If
the user asked for an editable web page, wrap the SVG in a minimal HTML file instead.

## Output format

- Default deliverable: one self-contained, base64-embedded `.svg`.
- Preserve official icon colors; keep containers/text/arrows in AWS neutrals and the
  group colors from the guide.
- Bilingual (Korean/English) labels are expected and fine for FSI/customer diagrams.
- Label the Internet gateway **"IGW"** (and the virtual private gateway "VGW") unless
  the user asks for the full name; long labels on the VPC border hurt readability.

## What NOT to do

- Don't hand-draw or approximate AWS icons — use the bundled ones.
- Don't write an AWS service that has an official icon (Site-to-Site VPN, Direct
  Connect, PrivateLink, ...) as a connector label — draw it as an icon node.
- Don't draw an Internet Gateway, NAT Gateway, VPC endpoint or EICE as a text chip or
  pill — they all have official resource icons (see the guide's VPC table).
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
- Don't deliver an SVG that references external icon files (won't render for the user)
  — always run `embed.py` for the final version.

## Asset inventory

All 873 icons are packed into one JSON bundle (keeps the skill's file count low):

- `assets/icons.json` — the icon bundle, built from the AWS Architecture Icons package
  released 2026-07-31 (`Icon-package_07312026`; re-downloaded and found identical on
  2026-10-19). Sets: `service`, `resource`, `group`, `category`, `legacy`. SVGs stored
  as text.
- `references/diagram_guide.md` — conventions, colors, VPC resources, SVG skeleton (read this).
- `scripts/find_icon.py` — fuzzy lookup → `set/name` reference (with AWS abbreviation aliases).
- `scripts/embed.py` — inline `bundle:set/name` hrefs as base64 for a portable final SVG.
- `scripts/check_layout.py` — flag lines over labels/icons, overlapping labels, text under 12px.
- `scripts/build_bundle.py` — rebuild `icons.json` from a newer official package.
- `docs/examples/` — checked NLB, ALB, GWLB, TGW and Cloud WAN reference diagrams (SVG + PNG) to start from.

## Updating the icon set

AWS publishes a new package a few times a year at
https://aws.amazon.com/architecture/icons/. To pick it up:

1. Download the "Icon package" zip and unzip it into an empty scratch directory.
2. `python3 ~/.claude/skills/aws-topology/scripts/build_bundle.py <unzipped-dir>`
3. Check the printed set counts, re-check the group colors in the guide against the
   new group SVGs and the "Groups" slide of the PPTx toolkit (download it from the same
   page; unzip the .pptx and grep `srgbClr`/`prstDash` in `ppt/slides/slide*.xml` —
   it is the only source for groups without an icon, e.g. Availability Zone), and
   update the package date and counts in this file (the counts live only here).

Services dropped from a new package move to `legacy` automatically.
