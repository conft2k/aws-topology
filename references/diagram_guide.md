# AWS Architecture Diagram Guide

How to compose a correct, professional AWS architecture diagram using the bundled
official icons. Read this fully before drawing.

## The AWS visual grammar

AWS diagrams are not arbitrary boxes and arrows. They follow a nesting convention
that readers recognize instantly. Respect the containment order:

```
AWS Cloud (group)
└── Region (group)
    └── VPC (group)
        └── Availability Zone (group, no icon) — when HA matters
            └── Subnet (public or private, group)
            └── Service icons (EC2, ECS, RDS, ...)
```

Not every diagram needs every layer — a serverless diagram may skip VPC/subnets
entirely. But when you show networking (EC2, ALB, RDS, NAT), draw the containers.
Putting a private-only service (like RDS) outside a subnet box is a red flag to
any AWS reviewer.

### Group containers (borders/backgrounds, from the `group` set)
- **AWS-Cloud-logo_32** — outermost "AWS Cloud" boundary, solid dark border, with the
  AWS logo badge top-left. **Always** use the `-logo` variant; never the logo-less
  plain-cloud `AWS-Cloud_32` / `AWS-Cloud_32_Dark` (find_icon hides them and embed.py
  fails on them). On a dark background use `AWS-Cloud-logo_32_Dark`.
- **Region_32** — dashed border.
- **Virtual-private-cloud-VPC_32** — solid purple border, VPC icon top-left.
- **Public-subnet_32** — green border.
- **Private-subnet_32** — teal border (same hue as Region; the solid line and badge tell them apart).
- **Corporate-data-center_32** — for on-prem / hybrid (e.g. EKS Hybrid Nodes, Direct Connect).
- **AWS-Account_32**, **Auto-Scaling-group_32**, **Server-contents_32** — as needed.
- **Availability Zone, Security group, Generic group** — groups with **no badge icon**:
  a labeled rect in the color below, nothing in the corner (`find_icon.py az` says so).

In an SVG you render these as: a **square-cornered** `<rect>` (no `rx`/`ry`) with the
group's signature border color + a small `<image>` of the group icon pinned to the
top-left corner + a text label next to it. The group icon PNGs/SVGs are 32px corner
badges, NOT full frames. The official toolkit draws every group as a plain rectangle;
a rounded border leaves the square badge's corner sticking out past the curve, so
embed.py rejects a rounded rect that carries a group badge.

### Group border colors (use these exact hex values)

A container's border and label color is the color of its own group icon. These values
come from the 2026-07-31 Icon package and the "Groups" slide of its PPTx toolkit
(the toolkit is the only source for groups without an icon, such as Availability
Zone). If a newer package changes a group icon, the border follows it
(`grep -o '#[0-9A-F]\{6\}'` on the group SVG tells you).

| Group | Border / label | Style | Badge |
|---|---|---|---|
| AWS Cloud | `#232F3E` (squid ink) | solid 2px | `AWS-Cloud-logo_32` |
| AWS Account | `#E7157B` | solid 2px | `AWS-Account_32` |
| Region | `#00A4A6` (teal) | dashed 2px, short dashes (`stroke-dasharray="3,3"`) | `Region_32` |
| Availability Zone | `#00A4A6` (teal) | dashed 1.5px, long dashes (`stroke-dasharray="8,4"`) | none — label only |
| VPC | `#8C4FFF` (purple) | solid 2px | `Virtual-private-cloud-VPC_32` |
| Public subnet | `#7AA116` (green) | solid 1.5px | `Public-subnet_32` |
| Private subnet | `#00A4A6` (teal) | solid 1.5px | `Private-subnet_32` |
| Security group | `#DD344C` (red) | solid 1.5px | none — label only |
| Auto Scaling group | `#ED7100` (orange) | dashed 1.5px | `Auto-Scaling-group_32` |
| EC2 instance contents, Spot Fleet, Elastic Beanstalk container | `#ED7100` | solid 1.5px | `EC2-instance-contents_32`, `Spot-Fleet_32`, none |
| Corporate data center, Server contents | `#7D8998` (grey) | solid 2px | `Corporate-data-center_32`, `Server-contents_32` |
| Generic group | `#7D8998` (grey) | dashed or solid 1.5px | none — label only |
| Step Functions workflow | `#E7157B` | solid 1.5px | none — label only |

The official toolkit draws every group with **no fill**. A very light tint of the
border color behind subnets is acceptable when it helps readability; if you use one,
apply it to every subnet of both kinds, never to the VPC or Region.

Both subnets and the AZ share the Region's teal in the private case, so the dash
pattern and the badge are what tell them apart: Region short-dashed with its badge,
AZ long-dashed with only a label, private subnet solid with its badge. Don't color the
VPC green — that's the public-subnet color, and it will clash with the purple VPC badge.

## Service icons

All icons live in one bundle, `assets/icons.json`, organized into sets. Reference them
by `set/name` (see "Finding the right icon"). The relevant sets:

- `service` — service product icons (the primary set).
- `resource` — resource-level icons (`<Service>_<Resource>`, e.g.
  `Amazon-VPC_Internet-Gateway`, `Amazon-EC2_Instance`, `Amazon-DynamoDB_Table`),
  plus the general icons (`Users`, `User`, `Client`, `Internet`, ...). General icons
  default to the light-background variant; append `_Dark` for dark backgrounds.
- `legacy` — service icons that AWS dropped from the current package (retired or
  renamed services such as `Amazon-QuickSight`). Use only when the user's system
  really still has that service.
- `category` — category icons (Compute, Storage...), for legends/agendas.

Load balancers: `alb`, `nlb` and `gwlb` resolve to the typed resource icon
(`resource/Elastic-Load-Balancing_Application-Load-Balancer` etc.); use the generic
`service/Elastic-Load-Balancing` (`elb`) only when the type is unspecified.

### Fully managed multi-AZ services are one node

In a standard reference architecture, a fully managed service that AWS runs across
AZs for you — ALB, NLB, GWLB (and the Auto Scaling group that spans the AZs) — is
drawn **once**, as a single node, not once per AZ. Its per-AZ nodes, ENIs and IPs are
AWS's implementation detail; drawing them makes the reader think they manage
separate load balancers.

- **One icon per load balancer**, placed in the gap between the AZ rows, in the column
  of the tier it serves (public subnets for internet-facing, private for internal), so
  it visibly belongs to every AZ it spans. Keep it clear of the AZ and subnet borders
  (≥8px; make the gap ≥110px so icon and label fit), label it with the short type:
  "ALB", "NLB", "GWLB". Put the IGW on the VPC border at the same height so the path
  IGW → load balancer is one straight line. Keep Users and the IGW in that gap in
  every diagram of the set, even when the IGW fans out to per-AZ nodes (e.g. GWLB
  endpoints) — consistent placement matters more than saving a bend.
- **Keep the main nodes on one line; number the steps when the path detours.** If
  the traffic leaves the line and comes back (e.g. IGW → per-AZ GWLBe → GWLB), keep
  Users, the IGW and the load balancer on the same line anyway. Break the line where
  the branches leave and rejoin it (≥40px apart, so it never looks like one direct
  connector), and add numbered step badges — a 10px-radius squid-ink circle with a
  white bold 12px number next to each hop (① IGW → GWLBe, ② GWLBe → GWLB, ...) —
  plus a one-line legend in the note. Don't move nodes to separate lanes to avoid the
  ambiguity; the numbers resolve it and the alignment stays consistent across the set.
- **One connector from the load balancer to its targets.** Wrap the targets in one
  Auto Scaling group / target group box that spans the AZs, and point a single arrow
  at that box, instead of one arrow per AZ or per instance.
- **Zonal resources stay per AZ**: NAT gateways, subnets, EC2 instances, interface
  endpoint ENIs and RDS primary/standby are drawn in each AZ they live in.
- **Per-AZ nodes only on request**: draw one LB node per AZ only when the diagram is
  about that behavior (static EIP per AZ, cross-zone load balancing, AZ failover) and
  the user asked for it. Say so in the reply.

Each service icon is a self-contained square SVG with the product's colored gradient
tile. Always put a text label directly below the icon (product name), centered, at
the node label size from "Text size" below (14px at S=48).

### One icon size for every node

In a standard architecture diagram every node icon — services and resources (gateways,
endpoints, ALB, users, servers) alike — is drawn at **one size, 48px by default**.
Mixed sizes make some components look more important than others and break the grid.
Pick the size once (`S`) and use it for every `<image>` that represents a component.

- Don't shrink resources such as IGW, NAT gateway or endpoints, and don't enlarge a
  service just because it feels central. Some icons look lighter (outline resource icons vs filled service
  tiles); that is the official artwork — keep the box size the same anyway.
- Exceptions: group/container badges in a container's corner (22–32px, one size per
  container level) and legend or category icons outside the architecture itself.
- If space runs out, enlarge the canvas or shorten labels rather than shrinking a few
  icons. Change `S` for the whole diagram only (e.g. 40px for a dense one).

#### Emphasis is the one exception

Make some icons bigger **only when specific services are meant to stand out** — the
user asked to highlight them, or the diagram's point is that part (e.g. "the new
AgentCore layer", "what changes in this migration"). Then:

- Enlarge only those services, to **one emphasis size `E`, about 1.33 × S**
  (64px when S is 48). Every emphasized icon uses the same `E`; don't grade sizes.
- Keep emphasis rare: a few icons, one group of related services. If most of the
  diagram is "important", nothing is emphasized — keep everything at `S`.
- Keep the icon's center on the grid point it would have at `S` (`x = cx - E/2`), so
  rows and connectors stay aligned; connectors end `E/2 + 4` from the center.
- Shift its label down to `cy + E/2 + 18`, and make it bold if that helps. Don't
  change label size or the icon's colors.
- Never shrink the other icons to make the emphasized ones look bigger.
- Say in the reply which services were emphasized and why.

### VPC networking resources

Gateways and endpoints are resources, not services, so they live in the `resource`
set. Draw every one of them as its icon — never as a text chip, pill or labeled box.

| Thing in the system | Icon | Placement |
|---|---|---|
| Internet gateway | `resource/Amazon-VPC_Internet-Gateway` | on the VPC border; label **"IGW"** (the full name only if the user asks) |
| NAT gateway | `resource/Amazon-VPC_NAT-Gateway` | inside the public subnet |
| Gateway endpoint (S3, DynamoDB) | `resource/Amazon-VPC_Endpoints` | inside the VPC box (outside any subnet — it is a route-table target, not an ENI), near the edge facing the service, on the flow line to it; never on the border |
| Interface endpoint (PrivateLink) | `resource/Amazon-VPC_Endpoints` | inside the subnet that holds its ENIs |
| EC2 Instance Connect Endpoint | `resource/Amazon-VPC_Endpoints` (no dedicated icon) | inside its subnet, labeled "EICE" |
| Gateway Load Balancer endpoint | `resource/Amazon-VPC_Endpoints` (no dedicated icon) | one per AZ in its GWLBe subnet, labeled "GWLBe"; the GWLB itself is one node in the appliance VPC |
| Virtual private gateway (VGW) / customer gateway | `resource/Amazon-VPC_VPN-Gateway` / `_Customer-Gateway` | on the VPC border / on-prem side |
| Peering connection | `resource/Amazon-VPC_Peering-Connection` | between the two VPCs |
| Router, NACL, ENI, Flow Logs | `resource/Amazon-VPC_Router`, `_Network-Access-Control-List`, `_Elastic-Network-Interface`, `_Flow-Logs` | as needed |

#### Internet gateway and VGW sit on the VPC border

An IGW or VGW is the VPC's door, so draw it straddling the VPC rectangle's edge —
half inside, half outside — never fully inside a subnet or floating outside the VPC.
Only these two straddle the border. Everything else that belongs to the VPC, gateway
endpoints included, goes fully inside the VPC box with at least 8px between its label
and the border.

- **Center the icon on the border line.** For a VPC `<rect x=X y=Y width=W height=H>`
  and an icon of size S: on the left edge use `x = X - S/2`, on the right edge
  `x = X + W - S/2`, on the top edge `y = Y - S/2`, on the bottom edge `y = Y + H - S/2`.
  The other coordinate lines it up with the flow it carries.
- **Pick the edge that faces what it connects to.** IGW on the side toward
  Internet/Users; VGW on the side toward the corporate data center / customer gateway.
  When both exist, put them on different edges (or well apart on the same edge) so
  their connectors don't cross.
- **Center the label under the icon**: `text-anchor="middle"` at the icon's center x
  (= the border x on a left/right edge), baseline 18px below the icon's bottom.
  Keep gateway labels short so they fit the mask and don't crowd the border: **"IGW"**
  and **"VGW"** by default; write out "Internet gateway" only when the user asks.
- **Mask the border behind the icon *and* the label with one white rect**, drawn before
  both. The icons have transparent backgrounds, and a centered label sits right on the
  border line, which a text halo does not hide (the line still shows between glyphs).
  Size the rect from the label's width:
  - text width `tw` ≈ `0.6 × font-size` per Latin character, `1.0 × font-size` per
    Hangul character (14px: "IGW" ≈ 25px, so the mask is just the icon width; a
    spelled-out "Internet gateway" ≈ 135px needs a 143px mask);
  - `mask_w = max(S, tw + 8)`, `mask_x = cx - mask_w/2`;
  - `mask_y = icon_y`, `mask_h = S + 22` (icon plus one label line; add 16 per extra line).

  No line may cross the label: besides the VPC border, check that no connector, subnet
  border or other container border passes through the mask area. Move the label
  connector or the icon along the edge until the mask covers only the VPC border, and
  check it in the render.
- **Leave room around the mask.** Keep the next container border (Region, subnet) and
  the canvas edge at least 8px clear of the mask on both sides of the VPC edge.
- **Connectors:** the outside flow (Internet → IGW, customer gateway → VGW) ends at the
  outer half; the inside flow (IGW → public subnet / ALB, VGW → private subnet) starts
  at the inner half, both at the icon's center line, never through the label.

```svg
<!-- VPC: x=60 y=70 width=780 height=480 → right edge at x=840, left edge at x=60 -->
<!-- IGW on the right edge, facing the Internet (S=48 → x = 840 - 24 = 816).
     Label "IGW" at 14px ≈ 25px < S → mask_w = S = 48, mask_x = 816 -->
<rect x="816" y="290" width="48" height="70" fill="#FFFFFF"/>
<image href="bundle:resource/Amazon-VPC_Internet-Gateway" x="816" y="290" width="48" height="48"/>
<text x="840" y="356" font-size="14" text-anchor="middle" fill="#232F3E">IGW</text>
<!-- If the user wants the full name: "Internet gateway" ≈ 135px → mask_w = 143, mask_x = 840 - 71.5 = 768.5 -->
<!-- VGW on the left edge, facing on-prem (x = 60 - 24 = 36); label is narrower than the icon -->
<rect x="36" y="400" width="48" height="70" fill="#FFFFFF"/>
<image href="bundle:resource/Amazon-VPC_VPN-Gateway" x="36" y="400" width="48" height="48"/>
<text x="60" y="466" font-size="14" text-anchor="middle" fill="#232F3E">VGW</text>
```

Render resource icons at the same size `S` as service icons, with a short label
below. When an icon sits on a container border or a connector, break the line at the
icon instead of drawing it underneath, and keep its label off the line: put a white rect
behind the label (as for IGW/VGW above) where a line would cross it. A text halo (a
white-stroked copy of the text drawn first, not `paint-order`, which cairosvg ignores)
only helps a line that runs *near* the glyphs; a line crossing the label still shows
between letters.

**Never invent or hand-draw a service icon.** If a service isn't in the bundle,
use the closest category icon or a plain labeled rounded rect — don't approximate the
official mark.

## Bedrock and AgentCore

Bedrock is `service/Amazon-Bedrock`; the AgentCore service as a whole is
`service/Amazon-Bedrock-AgentCore`. AgentCore *components* (Runtime, Gateway, Memory,
Identity, Code Interpreter, Browser, Observability, Policy) have no official icon in
the package yet. Draw them with the no-icon rule: a plain labeled rounded rect in a
neutral color, or one `service/Amazon-Bedrock-AgentCore` tile per component with the
component name as the label. Don't invent component marks. Re-check the package when
a new release lands — once a `Res_Amazon-Bedrock-AgentCore_*` resource icon appears,
`build_bundle.py` picks it up automatically.

## Finding the right icon

Do not guess names — they're specific (`Amazon-EC2`, `AWS-Lambda`, `Amazon-API-Gateway`,
`Amazon-Simple-Storage-Service`, `Amazon-VPC_Internet-Gateway`). Run:

```bash
python3 ~/.claude/skills/aws-topology/scripts/find_icon.py "s3" "step functions" "cloudfront"
```

It prints ranked `set/name` references. List a whole set with
`python3 ~/.claude/skills/aws-topology/scripts/find_icon.py --list service`.

## Composing the SVG

Output a single self-contained `.svg` (or an HTML wrapper if the user wants a web page).
Reference each icon with the `bundle:` href scheme, then run `scripts/embed.py` to inline
every icon as base64 so the final file is portable and renders anywhere:

```
<image href="bundle:service/AWS-Lambda" x="200" y="200" width="48" height="48"/>
```

Always deliver the embedded version (post-embed.py) so the diagram renders standalone.

### Skeleton

Copy this as the starting point; it follows the nesting order, compact 16–24px
container padding, 14px labels, one icon size, and the IGW-on-the-border rule
(IGW → ALB in the public subnet → EC2 in the private subnet). Grow containers only as
far as their contents need.

```svg
<svg viewBox="0 0 556 312" xmlns="http://www.w3.org/2000/svg" font-family="'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif">
  <!-- one arrowhead marker, reused by every connector -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#232F3E"/>
    </marker>
  </defs>
  <rect width="556" height="312" fill="#FFFFFF"/>

  <!-- AWS Cloud boundary -->
  <rect x="16" y="16" width="524" height="280" fill="none" stroke="#232F3E" stroke-width="2"/>
  <image href="bundle:group/AWS-Cloud-logo_32" x="16" y="16" width="32" height="32"/>
  <text x="58" y="38" font-size="15" fill="#232F3E" font-weight="600">AWS Cloud</text>

  <!-- Region: 20px inside the Cloud, below its header -->
  <rect x="36" y="56" width="484" height="220" fill="none" stroke="#00A4A6" stroke-width="2" stroke-dasharray="3,3"/>
  <image href="bundle:group/Region_32" x="36" y="56" width="24" height="24"/>
  <text x="68" y="74" font-size="14" fill="#00A4A6" font-weight="600">Region ap-northeast-2</text>

  <!-- VPC: left edge at x=96 leaves room for the IGW mask (72–120) inside the Region -->
  <rect x="96" y="88" width="404" height="168" fill="none" stroke="#8C4FFF" stroke-width="2"/>
  <image href="bundle:group/Virtual-private-cloud-VPC_32" x="96" y="88" width="24" height="24"/>
  <text x="128" y="106" font-size="14" fill="#8C4FFF" font-weight="600">VPC 10.0.0.0/16</text>

  <!-- subnets, sized to one node each: header ~28px, icon, 18px to the label, ~18px below -->
  <rect x="136" y="118" width="160" height="118" fill="none" stroke="#7AA116" stroke-width="1.5"/>
  <image href="bundle:group/Public-subnet_32" x="136" y="118" width="24" height="24"/>
  <text x="168" y="136" font-size="14" fill="#7AA116" font-weight="600">Public subnet</text>
  <rect x="320" y="118" width="160" height="118" fill="none" stroke="#00A4A6" stroke-width="1.5"/>
  <image href="bundle:group/Private-subnet_32" x="320" y="118" width="24" height="24"/>
  <text x="352" y="136" font-size="14" fill="#00A4A6" font-weight="600">Private subnet</text>

  <!-- Internet gateway centered on the VPC left border (96 - 48/2 = 72), facing the Internet.
       Label "IGW" (≈ 25px) is narrower than the icon → mask_w = 48, mask_h = S + 22 = 70,
       36px clear of the Region border at x=36. -->
  <rect x="72" y="152" width="48" height="70" fill="#FFFFFF"/>
  <image href="bundle:resource/Amazon-VPC_Internet-Gateway" x="72" y="152" width="48" height="48"/>
  <text x="96" y="218" font-size="14" text-anchor="middle" fill="#232F3E">IGW</text>

  <!-- nodes: every node icon uses the same S=48; 14px labels, baseline 18px below the icon -->
  <image href="bundle:resource/Elastic-Load-Balancing_Application-Load-Balancer" x="192" y="152" width="48" height="48"/>
  <text x="216" y="218" font-size="14" text-anchor="middle" fill="#232F3E">ALB</text>
  <image href="bundle:service/Amazon-EC2" x="376" y="152" width="48" height="48"/>
  <text x="400" y="218" font-size="14" text-anchor="middle" fill="#232F3E">EC2</text>

  <!-- connectors on the icons' center line, all pointing right; the first starts at the IGW's inner half -->
  <line x1="124" y1="176" x2="188" y2="176" stroke="#232F3E" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="244" y1="176" x2="372" y2="176" stroke="#232F3E" stroke-width="1.5" marker-end="url(#arrow)"/>
</svg>
```

## Layout rules that make it look professional

- **Traffic flows left to right.** When the diagram shows how traffic moves (requests,
  packets, data), lay it out so the flow reads left → right: users/clients/on-prem on
  the left, entry points (Route 53, CloudFront, IGW, VGW) next, then load balancers,
  compute, and data stores on the right. Every main-path arrow points right; only
  return, outbound (e.g. to a NAT gateway) or control/management connectors may go
  another way, and those are dashed. To make that work in a VPC, put the **tiers in
  columns** (public subnet → private subnet → data subnet) and the **AZs in rows**;
  the IGW then sits on the VPC's left border. Use top-to-bottom only for diagrams that
  aren't about traffic (account/org structure, a deployment pipeline) or when the user
  asks for it.
- **Align icons on a grid.** Same y for a horizontal tier, same x for a vertical tier.
  Even spacing. Misaligned icons look amateurish.
- **Label everything.** Every icon gets a product-name label. Every connector that
  isn't obvious gets a verb/protocol label ("HTTPS", "invoke", "read/write").
- **Compact, not empty.** Size every container to what it holds: 16–24px between a
  container's border and its children (the header row — badge + label — takes ~28px
  at the top), and node centers about 2–2.5 × S apart (100–120px at S=48). Don't leave
  empty quadrants or a subnet much larger than its contents; shrink the box or the
  canvas instead. The diagram should fill its canvas with ≤24px outer margin. Only the
  rules that need room get it: ≥8px around an IGW/VGW mask, ≥8px between labels and
  borders, and a gap between AZ rows tall enough for a load balancer and its label.
- **Text size.** Labels must stay readable when the diagram is scaled down into a doc
  or slide. At S=48: node labels **14px**, container labels **14px bold** (AWS Cloud
  15px), connector and secondary labels (protocol, sub-captions, notes) **12px**.
  Never go below 12px. Scale the sizes with `S` (≈ 0.3 × S for node labels) if you
  change it, and give each label line 16–18px of height when you compute spacing.
- **Color discipline.** Icons carry their own colors; keep containers, text, and
  connectors in the AWS neutrals (squid ink `#232F3E`, group border colors above).
  Don't add rainbow connectors.
- **One arrowhead style, consistent stroke width** (1.5–2px) for all connectors.
- **Legend** only if the diagram has non-obvious symbols.

## Font

AWS decks use **Pretendard** for Korean/bilingual content and Arial/Amazon Ember for
English. Put a Korean-capable family **that is installed on the machine doing the
render** first in the root `font-family`. Browsers fall back per glyph, but cairosvg
(used for the preview) uses only the first family, with no fallback when it is
missing: with Arial or an uninstalled font first, every Hangul label silently
disappears from the render.

Check before choosing:

```bash
fc-list | grep -iE 'CJK KR|Pretendard'
```

- Noto Sans CJK KR installed → `font-family="'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif"`
- Only Pretendard installed → `font-family="'Pretendard', 'Noto Sans CJK KR', Arial, sans-serif"`
- Neither → tell the user the preview will drop Hangul, or keep labels in English.

Both Korean fonts include Latin glyphs, so English labels are unaffected. Korean labels
are fine and common for FSI customer diagrams.

## Common diagram types & which layers to draw

- **3-tier web app**: AWS Cloud > Region > VPC > public subnet (ALB) + private subnets
  (ECS/EC2, RDS). Show AZ split if HA matters, with one ALB across the AZs (see
  "Fully managed multi-AZ services are one node").
- **Serverless**: skip VPC. API Gateway > Lambda > DynamoDB, with S3/CloudFront front.
- **Container (EKS/ECS)**: VPC > subnets > cluster; show ALB, node groups, ECR.
- **Hybrid (EKS Hybrid Nodes, Direct Connect)**: Corporate-data-center group on one side,
  AWS Cloud on the other, connected via Direct Connect / VPN / Transit Gateway icon.
- **Agentic AI (AgentCore)**: `service/Amazon-Bedrock` for the models,
  `service/Amazon-Bedrock-AgentCore` for the agent platform (see "Bedrock and
  AgentCore" for components), and standard icons for the surrounding infra.
