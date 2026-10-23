# AWS Architecture Diagram Guide

How to compose a correct, professional AWS architecture diagram using the bundled
official icons. Read this fully before drawing. You lay the diagram out as an SVG
draft in a restricted subset (see "Composing the layout SVG"); `export.py` turns that
one draft into a portable SVG, a PNG and/or a slide of native PowerPoint shapes, so every
rule below — coordinates, colors, dash patterns, sizes — carries over to every format.

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
  plain-cloud `AWS-Cloud_32` / `AWS-Cloud_32_Dark` (find_icon hides them and export.py
  fails on them). On a dark background use `AWS-Cloud-logo_32_Dark`.
- **Region_32** — dashed border.
- **Virtual-private-cloud-VPC_32** — solid purple border, VPC icon top-left.
- **Public-subnet_32** — green border.
- **Private-subnet_32** — teal border (same hue as Region; the solid line and badge tell them apart).
- **Corporate-data-center_32** — for on-prem / hybrid (e.g. EKS Hybrid Nodes, Direct Connect).
- **AWS-Account_32**, **Auto-Scaling-group_32**, **Server-contents_32** — as needed.
- **Availability Zone, Security group, Generic group** — groups with **no badge icon**:
  a labeled rect in the color below, nothing in the corner (`find_icon.py az` says so).

In the layout SVG you draw these as: a **square-cornered** `<rect>` (no `rx`/`ry`) with the
group's signature border color + a small `<image>` of the group icon pinned to the
top-left corner + a text label next to it. The group icon PNGs/SVGs are 32px corner
badges, NOT full frames. The official toolkit draws every group as a plain rectangle;
a rounded border leaves the square badge's corner sticking out past the curve, so
export.py rejects a rounded rect that carries a group badge.

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

All icons live in one bundle, `assets/icons.json` (built from the official AWS package on
first use), organized into sets. Reference them
by `set/name` (see "Finding the right icon"). The relevant sets:

- `service` — service product icons (the primary set).
- `resource` — resource-level icons (`<Service>_<Resource>`, e.g.
  `Amazon-VPC_Internet-Gateway`, `Amazon-EC2_Instance`, `Amazon-DynamoDB_Table`),
  plus the general icons (`Users`, `User`, `Client`, `Internet`, ...). General icons
  default to the light-background variant; append `_Dark` for dark backgrounds.
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
  (≥8px). Make the gap ≥110px in a document; on a slide 86px is the minimum (the
  70px IGW mask plus 8px above and below), label it with the short type:
  "ALB", "NLB", "GWLB". Put the IGW on the VPC border at the same height so the path
  IGW → load balancer is one straight line. Keep Users and the IGW in that gap in
  every diagram of the set, even when the IGW fans out to per-AZ nodes (e.g. GWLB
  endpoints) — consistent placement matters more than saving a bend.
- **Keep the main nodes on one line; number the steps when the path detours.** If
  the traffic leaves the line and comes back (e.g. IGW → per-AZ GWLBe → GWLB), keep
  Users, the IGW and the load balancer on the same line anyway. Break the line where
  the branches leave and rejoin it (≥40px apart, so it never looks like one direct
  connector), and add numbered step badges — a 10px-radius squid-ink circle with a
  white bold 12px number on **every** hop from where the path leaves the main line until
  it rejoins it (① IGW → GWLBe,
  ② GWLBe → GWLB, ...), its bottom 4px above that hop's own line, at the middle of the
  longest horizontal part of the line between container borders (a connector's protocol or name
  label goes near the middle of that same part) (a hop drawn inside an AZ row gets its number
  inside that row, above its line — never on another hop's line; hops that share or run side by side through the AZ gap
  get one number between them, and on a slide the "keep it clear of the AZ boxes" rule
  wins over the middle-of-the-line rule); when the hop also has a protocol
  label, put the label below the line. The legend in the note names exactly the hop
  each number sits on, and draws each number as the same badge (see **Step legend**),
  never as a circled-digit glyph (①). Don't move nodes to separate lanes to avoid the
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
| VPC peering connection / TGW peering attachment | `resource/Amazon-VPC_Peering-Connection` (AWS uses it for both) | on the link between the two VPCs or the two TGWs, the line broken at the icon; across Regions or accounts, in the gap between their boxes (it belongs to neither); label "VPC peering" / "TGW peering" |
| Route table (VPC subnet route table, TGW route table) | `resource/Amazon-Route-53_Route-Table` (the package's only route table icon; filed under Route 53 but used for every route table) | inside the VPC outside the subnets (TGW route table: next to the TGW), with the table name as label and the key route as a 12px sub-caption ("10.0.0.0/8 → TGW"); never a text chip |
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
behind the label (as for IGW/VGW above) where a line would cross it. Don't use text
halos (a white-stroked copy of the text): PowerPoint text boxes have no stroke, so
export.py rejects stroked text — the white mask rect is the only way to keep a line
off a label.

**A service with an official icon is never just text.** If a connector would carry
the name of an AWS service or resource — "Site-to-Site VPN", "Direct Connect",
"PrivateLink", "VPC peering" — and `find_icon.py` finds its icon, put that icon on the
path as a node (with its label below, the same size `S` as every node) and keep only
the protocol on the connector ("IPsec", "GENEVE :6081"). Place it where the reader
expects it on the path: a Site-to-Site VPN is the link between on-premises and AWS, so
its icon sits **outside the AWS Cloud box**, between the Internet icon and the Cloud
border (see below). Don't add a duplicate when
another node already is that service (a GWLBe is the PrivateLink endpoint). A TGW
peering is drawn the way the AWS docs draw it: the peering connection icon
(`resource/Amazon-VPC_Peering-Connection`) on the TGW–TGW line, labeled "TGW peering".
Only a connection with no icon in the bundle stays a connector label.

**Show what a hybrid connection runs over.** A Site-to-Site VPN is IPsec over the
public Internet, so its path is customer gateway → `resource/Internet` →
`service/AWS-Site-to-Site-VPN` → TGW/VGW, with the Internet and VPN icons both
**outside the AWS Cloud box**, between the on-premises group and the Cloud border, and
"IPsec" on the Internet → VPN segment. Leave 220–280px between the on-premises group and
the Cloud border for those two hops (enough for both icons, their labels and the
"IPsec" label with 8px around each), and pull the Cloud and Region borders in so they
hug their contents rather than leaving the space empty inside. A Direct
Connect path is private and never passes the Internet icon: customer router →
`service/AWS-Direct-Connect` (the DX location, outside the Region) → Direct Connect
gateway / TGW. When both exist, draw them as two separate paths so the difference is
visible.

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
`Amazon-Simple-Storage-Service`, `Amazon-VPC_Internet-Gateway`). Run (`<skill-dir>` is the
skill's directory, `${CLAUDE_SKILL_DIR}` in SKILL.md):

```bash
python3 <skill-dir>/scripts/find_icon.py "s3" "step functions" "cloudfront"
```

It prints ranked `set/name` references. List a whole set with
`python3 <skill-dir>/scripts/find_icon.py --list service`.

## Composing the layout SVG

The SVG is a layout draft, not the deliverable: `scripts/export.py` checks it and writes
the formats asked for — a portable SVG with every icon inlined, a PNG, and/or a slide of
native PowerPoint shapes. Reference each icon with the `bundle:` href scheme; the export
looks it up in the bundle (inlined as base64 in the SVG, an SVG picture on the slide):

```
<image href="bundle:service/AWS-Lambda" x="200" y="200" width="48" height="48"/>
```

Use the same subset whatever the format, so one draft serves them all — the export checks
it even when only an SVG or PNG is wanted:

| SVG | PowerPoint |
|---|---|
| `<rect>` (`fill`, `stroke`, `stroke-width`, `stroke-dasharray`, `rx` for no-icon boxes only) | rectangle / rounded rectangle; the dash pattern is kept exactly |
| `<image href="bundle:set/name">` (or an inlined `data:` URI) | picture with the official SVG icon and a PNG fallback |
| `<text>` (`font-size`, `font-weight`, `fill`, `text-anchor`), one line each | text box, no wrap, same anchor |
| `<line>`, `<polyline fill="none">` with `marker-start` / `marker-end` | straight connector / open freeform with triangle arrowheads |
| `<circle>` | oval (step badges, junction dots) |
| `<g transform="translate(x,y)">` | offset applied to its children |
| `<defs>`, `<marker>` | read for the arrowheads only |

No `<path>` outside markers, no other transforms (scale, rotate), no CSS classes or
`style=""`, no stroked text. Colors as `#RRGGBB`. The full-canvas white background rect
is dropped (the slide is white). One draft is one slide; the export scales it to fit a
16:9 slide, so the canvas size decides the slide's text size (see "Text size").

### Skeleton

Copy this as the starting point; it follows the nesting order, compact 16–24px
container padding, 14px labels, one icon size, AZs as rows and tiers as columns, one
ALB node in the gap between the AZ rows, the IGW-on-the-border rule, and one arrow to
a target group spanning the AZs with a zonal EC2 instance in each (it is
`docs/example.svg`). Grow containers only as far as their contents need.

```svg
<svg viewBox="0 0 670 574" xmlns="http://www.w3.org/2000/svg" font-family="'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif">
  <!-- one arrowhead marker, reused by every connector; arrowStart is its mirror for
       two-way links (marker-start), since cairosvg ignores orient="auto-start-reverse" -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#232F3E"/>
    </marker>
    <marker id="arrowStart" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto">
      <path d="M8,0 L0,3 L8,6 Z" fill="#232F3E"/>
    </marker>
  </defs>
  <rect width="670" height="574" fill="#FFFFFF"/>

  <!-- AWS Cloud boundary -->
  <rect x="16" y="16" width="638" height="542" fill="none" stroke="#232F3E" stroke-width="2"/>
  <image href="bundle:group/AWS-Cloud-logo_32" x="16" y="16" width="32" height="32"/>
  <text x="58" y="38" font-size="15" fill="#232F3E" font-weight="600">AWS Cloud</text>

  <!-- Region: 20px inside the Cloud, below its header -->
  <rect x="36" y="56" width="598" height="482" fill="none" stroke="#00A4A6" stroke-width="2" stroke-dasharray="3,3"/>
  <image href="bundle:group/Region_32" x="36" y="56" width="24" height="24"/>
  <text x="68" y="74" font-size="14" fill="#00A4A6" font-weight="600">Region ap-northeast-2</text>

  <!-- VPC: left edge at x=96 leaves room for the IGW mask (72–120) inside the Region -->
  <rect x="96" y="88" width="518" height="430" fill="none" stroke="#8C4FFF" stroke-width="2"/>
  <image href="bundle:group/Virtual-private-cloud-VPC_32" x="96" y="88" width="24" height="24"/>
  <text x="128" y="106" font-size="14" fill="#8C4FFF" font-weight="600">VPC 10.0.0.0/16</text>

  <!-- AZs as rows (label only, long dashes); the 86px gap between them (270–356) holds
       the main line y=302: IGW → ALB → target group -->
  <rect x="106" y="118" width="498" height="152" fill="none" stroke="#00A4A6" stroke-width="1.5" stroke-dasharray="8,4"/>
  <text x="118" y="136" font-size="14" fill="#00A4A6" font-weight="600">Availability Zone 1</text>
  <rect x="106" y="356" width="498" height="152" fill="none" stroke="#00A4A6" stroke-width="1.5" stroke-dasharray="8,4"/>
  <text x="118" y="374" font-size="14" fill="#00A4A6" font-weight="600">Availability Zone 2</text>

  <!-- tiers as columns: public subnet (118–264) → app subnet (276–592), one of each per AZ.
       The public subnets hold the ALB's per-AZ nodes, which are not drawn: the ALB is one node. -->
  <rect x="118" y="148" width="146" height="114" fill="none" stroke="#7AA116" stroke-width="1.5"/>
  <image href="bundle:group/Public-subnet_32" x="118" y="148" width="24" height="24"/>
  <text x="150" y="166" font-size="14" fill="#7AA116" font-weight="600">Public subnet</text>
  <rect x="276" y="148" width="316" height="114" fill="none" stroke="#00A4A6" stroke-width="1.5"/>
  <image href="bundle:group/Private-subnet_32" x="276" y="148" width="24" height="24"/>
  <text x="308" y="166" font-size="14" fill="#00A4A6" font-weight="600">App subnet</text>

  <rect x="118" y="386" width="146" height="114" fill="none" stroke="#7AA116" stroke-width="1.5"/>
  <image href="bundle:group/Public-subnet_32" x="118" y="386" width="24" height="24"/>
  <text x="150" y="404" font-size="14" fill="#7AA116" font-weight="600">Public subnet</text>
  <rect x="276" y="386" width="316" height="114" fill="none" stroke="#00A4A6" stroke-width="1.5"/>
  <image href="bundle:group/Private-subnet_32" x="276" y="386" width="24" height="24"/>
  <text x="308" y="404" font-size="14" fill="#00A4A6" font-weight="600">App subnet</text>

  <!-- one Auto Scaling group / target group spanning both AZs, 8px inside the app subnets and
       right of their headers (so its border crosses no header); zonal EC2 instances stay per AZ -->
  <rect x="400" y="156" width="184" height="336" fill="none" stroke="#ED7100" stroke-width="1.5" stroke-dasharray="6,3"/>
  <image href="bundle:group/Auto-Scaling-group_32" x="400" y="156" width="24" height="24"/>
  <text x="432" y="174" font-size="14" fill="#ED7100" font-weight="600">ASG · target group</text>

  <!-- nodes: every node icon uses the same S=48; 14px labels, baseline 16px below the icon -->
  <image href="bundle:service/Amazon-EC2" x="468" y="186" width="48" height="48"/>
  <text x="492" y="250" font-size="14" text-anchor="middle" fill="#232F3E">EC2</text>
  <image href="bundle:service/Amazon-EC2" x="468" y="416" width="48" height="48"/>
  <text x="492" y="480" font-size="14" text-anchor="middle" fill="#232F3E">EC2</text>

  <!-- one ALB (a managed multi-AZ service), in the gap between the AZ rows, in the public column -->
  <image href="bundle:resource/Elastic-Load-Balancing_Application-Load-Balancer" x="167" y="278" width="48" height="48"/>
  <text x="191" y="342" font-size="14" text-anchor="middle" fill="#232F3E">ALB</text>

  <!-- Internet gateway centered on the VPC left border (96 - 48/2 = 72), on the main line.
       Label "IGW" (≈ 25px) is narrower than the icon → mask_w = 48, mask_h = S + 22 = 70,
       8px clear of both AZ rows and 36px clear of the Region border at x=36. -->
  <rect x="72" y="278" width="48" height="70" fill="#FFFFFF"/>
  <image href="bundle:resource/Amazon-VPC_Internet-Gateway" x="72" y="278" width="48" height="48"/>
  <text x="96" y="342" font-size="14" text-anchor="middle" fill="#232F3E">IGW</text>

  <!-- connectors on the main line, all pointing right; the first starts at the IGW's inner half,
       the second ends at the target group box (one arrow to the group, not one per instance) -->
  <line x1="124" y1="302" x2="163" y2="302" stroke="#232F3E" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="219" y1="302" x2="396" y2="302" stroke="#232F3E" stroke-width="1.5" marker-end="url(#arrow)"/>
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
  On the slide the px sizes become points through the fit-to-slide scale, so the
  canvas size decides the result: every label must come out at **≥ 10pt** (a titled
  canvas of at most 1108 × 540), and only when that is unavoidable down to **8pt**
  (~1380 × 675), never smaller. Tighten or split the diagram before going under 10pt.
- **Color discipline.** Icons carry their own colors; keep containers, text, and
  connectors in the AWS neutrals (squid ink `#232F3E`, group border colors above).
  Don't add rainbow connectors.
- **One arrowhead style, one stroke width** (1.5px) for all connectors, inter-Region
  links included: a TGW peering is marked by its icon and label, a Cloud WAN backbone by
  its "AWS 백본" label, not by a thicker line (the AWS docs draw every line alike). A
  genuinely two-way link
  (GWLBe ⇄ GWLB, GWLB ⇄ appliances over GENEVE, TGW ⇄ an inspection attachment) gets
  the mirrored `arrowStart` marker on its other end; ordinary request/response flows
  stay one-way.
- **Topology diagrams may drop the arrowheads.** A diagram that shows what is attached
  to what rather than how traffic flows (TGW hub and spoke, VPC peering mesh) draws its
  attachment lines solid, without arrowheads, in any direction; the left → right and
  "other directions are dashed" rules apply to traffic-flow diagrams only.
- **Several connectors into one node: separate when they are separate things, one
  trunk when they are the same route.** When each line is its own attachment, ENI or
  endpoint (spoke VPCs → TGW, GWLBe ⇄ GWLB per AZ), give each its own arrowhead, entering
  the node's side 8px above and below its center (10px left and right of center when
  they come in from above or below; topology lines without arrowheads too). When every
  line is the same route to the same target (each AZ's NAT gateway → the IGW), join them
  in a corridor outside the AZ boxes and enter the node as one line with one arrowhead
  on its center line — two arrowheads a few px apart only add noise.
- **Outbound through a NAT gateway** is the dashed private-node → NAT gateway hop; the
  NAT gateway → IGW hop may be left implied when the IGW is already on the diagram
  for inbound traffic. Draw it when egress is the point of the diagram (centralized
  egress, inspection).
- **Regional services row.** Services that live in the Region but outside the VPC
  (ACM, AWS WAF for an ALB/API Gateway, CloudWatch, S3 for logs) go in one row inside
  the Region, above the VPC, on an even grid (~160px apart), each with its name and a
  12px sub-caption saying what it does here ("HTTPS 리스너 인증서", "ALB 액세스 로그").
  Draw a connector only for what is on the traffic path; a service attached to a
  resource (AWS WAF on an ALB, ACM on a listener) gets its caption, not a connector.
- **Global services sit outside the Region.** Route 53, CloudFront, AWS Global
  Accelerator, IAM and AWS WAF for CloudFront are global: put them inside the AWS Cloud
  box but outside every Region box, in a narrow strip to the left of the Region (the
  side the users are on), at the height of the request they serve (Route 53: where the
  users' dashed DNS lookup reaches it, any height that keeps that line short); the rest of that
  strip staying empty is expected, not an "empty area". Never put them in the regional
  services row. The DNS lookup from the users to Route 53 stays a dashed connector.
- **Regional services on a slide.** When a row above the VPC doesn't fit the slide's
  height, stack the regional services in a column beside the VPC (inside the Region),
  one per slot — a slot is an AZ row or the gap between rows — on the same grid; with
  more services than slots, use two columns. A slot may stay empty. Keep the node size S the same on every slide of a deck — fit the slide by
  re-arranging, not by shrinking the icons.
- **Database hops** carry the engine and port when known ("MySQL :3306",
  "PostgreSQL :5432"), otherwise "SQL".
- **Subnet color follows the route table.** A subnet is a public subnet (green) only if
  its route table sends traffic straight to an IGW (0.0.0.0/0 → IGW): NAT gateway,
  GWLBe and internet-facing load balancer subnets. A subnet whose default route goes to
  a GWLBe, a firewall endpoint, a NAT gateway or a TGW is private (teal), even when its
  instances have public IPs.
- **Write routes in full CIDR form** — "0.0.0.0/0", "10.0.0.0/8", "10.1.0.0/16" — the
  same way everywhere; add "같은 AZ" when the target is per-AZ.
- **ASG and target group boxes inside a subnet** keep 8px from the subnet's borders
  and 8px between their own border and every label inside; start the box to the right
  of the subnet's header label, or below it.
- **Short container labels.** Name subnets by role — "Public subnet", "App subnet",
  "DB subnet", "GWLBe subnet", "Appliance subnet" — not "Private subnet (App)": a long
  header runs into the badge or border of a box that spans it (an ASG, a replication
  line), and the badge color already says public or private.
- **Room outside the AWS Cloud.** Users/clients sit outside the AWS Cloud box; leave
  enough space between them and the Cloud border (≈80px at 12px) for the connector's
  protocol label to sit clear of the Cloud and Region borders.
- **Note line.** The note goes **below the diagram, outside the AWS Cloud box**,
  left-aligned with the leftmost element of the diagram (the Users icon or on-premises
  box when they sit left of the Cloud, otherwise the Cloud's left edge), 8px or more
  below the Cloud's bottom border, 12px, never inside a
  container. At most two lines, 16px apart, each no wider than the canvas: what the
  diagram is ("Internet-facing NLB · ...") or the step legend, and — when the routes
  don't fit as sub-captions — the routes ("라우팅: ..."). A qualifier shared by several
  routes may be said once ("방화벽 · NAT 경로는 같은 AZ"). On a slide the note counts
  toward the canvas height (≤ 540); the Region's bottom padding may shrink to 8px to
  make room.
- **Step legend.** A diagram with step badges explains them in the note with the
  **same badge** the diagram uses — a 10px-radius squid-ink `#232F3E` circle with the
  white bold 12px number — never a circled-digit glyph (①) or a bare "1.". Each item
  is the badge followed by its text: 12px, `#545B64`, `text-anchor="start"`, starting
  8px right of the badge (`x = cx + 18`), baseline at `cy + 4`. Everything is
  left-aligned on the note's left edge (badge `cx = left + 10`); never center the
  legend or put it in a frame.
  - **Document:** one step per row, rows 24px apart, in step order. Lines that aren't
    steps (summary, routes, security groups, test inputs) follow as plain 12px
    lines, 16px apart, starting at the same left edge, 8px below the last badge.
    The note's two-line limit doesn't count the step rows.
  - **Slide** (canvas height ≤ 540): when one row per step doesn't fit, flow the items
    in one row, 20px between an item's text end and the next badge; wrap to a second
    row 24px below at the same left edge rather than shrinking the text.

  ```svg
  <!-- step legend: same badges as the diagram, one row per step, left-aligned -->
  <circle cx="26" cy="660" r="10" fill="#232F3E"/><text x="26" y="664" font-size="12" font-weight="700" text-anchor="middle" fill="#FFFFFF">1</text>
  <text x="44" y="664" font-size="12" fill="#545B64">IGW → GWLBe (인그레스 라우팅)</text>
  <circle cx="26" cy="684" r="10" fill="#232F3E"/><text x="26" y="688" font-size="12" font-weight="700" text-anchor="middle" fill="#FFFFFF">2</text>
  <text x="44" y="688" font-size="12" fill="#545B64">GWLBe ⇄ GWLB</text>
  <text x="16" y="714" font-size="12" fill="#545B64">라우팅 (같은 AZ): ...</text>
  ```
- **When routes must be shown.** A diagram whose point is the routing — inspection
  (Network Firewall, GWLB), centralized egress, ingress routing, TGW / peering between
  VPCs or Regions — lists every route its flows need (sub-captions or the note). Other
  diagrams may leave routes out. When routes are shown, every VPC (and on-premises
  network) carries its CIDR — in its container header, or as a 12px sub-caption under a
  single-icon VPC node or the customer gateway — and the routes use those CIDRs, not
  placeholders like "app subnet CIDR". A route to a subnet CIDR names the subnet in
  parentheses: "10.0.1.0/24 (AZ1 App) → GWLBe". TGW propagation captions ("VPC A · B
  전파") name attachments and need no CIDR.
- **How gaps are measured.** Every "N px between a label and X" rule is measured from
  the label's glyph box — baseline − 0.75 × font size to baseline + 0.25 × font size —
  the same box check_layout.py uses.
- **Clearances at a glance:** label ↔ container border 8px (a container's own header
  label follows the fixed header geometry instead, 7.5px below its top border);
  label ↔ an icon it doesn't label 8px; group badge ↔ node icon 8px; connector ↔ a
  node or header label 4px; label ↔ label side by side 4px. check_layout.py enforces
  all of them.
- **Connector labels** (protocol, name) sit near the middle of the longest horizontal
  part of their line between container borders, 4–8px above it (below it when a step
  number takes the space above).
- **Fixed header geometry.** A container's header label sits at baseline container.y +
  18; any box nested inside starts at container.y + 30 or lower (VPC → AZ, AZ → subnet).
  The AWS Cloud's 15px label sits at baseline Cloud.y + 22, so the Region starts at
  Cloud.y + 34 or lower.
  The first node icon inside a subnet starts at subnet.y + 28 or lower (6px under the
  header label).
- **Side-by-side Regions** (or VPCs drawn as boxes) sit 24–40px apart.
- **Slide vertical budget.** On a titled slide (540px) a two-AZ diagram fits with: Cloud
  header 34, Region / VPC headers 30 each, AZ rows of 144 (AZ header 30 + a 106px
  subnet: icon at +28, 48px icon, label baseline 18 below it, 8px under the label —
  + 8px padding; ≈152 when an ASG header sits in the row), an 86px AZ gap, 8px paddings and a two-line note (≈30). When split
  connectors (±8) and a step badge share the gap and there is no room for 90px, keep
  the badge horizontally clear of the AZ boxes instead. Budget these
  before placing nodes; if they don't add up, split the diagram rather than shrinking
  icons or fonts.
- **Padding between nested containers:** 16–24px in a document; on a slide it may
  shrink to 8px to fit the 540px height. One draft shared by the document
  and the slide follows the slide values. Wider gaps are expected
  where something sits in them: the IGW/VGW mask on a VPC border, the global-services
  strip, a regional-services row or column, a connector and its label, or the width a
  container's header label needs. Two labels side by side keep at least 4px apart. A canvas hugs its contents even on a slide
  — "close to 16:8" is a target, not a reason to leave empty space.
- **An ASG / target group spanning AZ rows** crosses the AZ and subnet borders by
  design; put its badge and label inside the first subnet it covers, either to the
  right of that subnet's header label (8px clear of it, any height) or 8px below it,
  and 8px clear of every icon.
- **Legend** only if the diagram has non-obvious symbols.

## Font

Put a Korean-capable family **that is installed on the machine doing the render** first
in the draft's root `font-family`. It is the font of the SVG deliverable and of the PNG,
and `check_layout.py` estimates widths from it. Browsers fall back per glyph, but
cairosvg (used for the PNG) uses only the first family, with no fallback when it is
missing: with Arial or an uninstalled font first, every Hangul label silently
disappears from the render. Check before choosing:

```bash
fc-list | grep -iE 'CJK KR|Pretendard'
```

- Noto Sans CJK KR installed → `font-family="'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif"`
- Only Pretendard installed → `font-family="'Pretendard', 'Noto Sans CJK KR', Arial, sans-serif"`
- Neither → tell the user the PNG will drop Hangul, or keep labels in English.

The slide's fonts are set by the PowerPoint export, not by the `font-family`: Latin text
in **Arial** and Korean in **Malgun Gothic (맑은 고딕)** by default, which ship with
Windows and Microsoft Office. Override with `--font` / `--ea-font` when the deck uses
another typeface (AWS Korean decks often use Pretendard: `--ea-font Pretendard`), and
tell the user the font has to be installed where the deck is opened — PowerPoint
substitutes a missing font. The slide preview (`--preview`) picks an installed Korean
font by itself.

Korean labels are fine and common for FSI customer diagrams. Real fonts are a little
wider or narrower than the estimate, so slide text boxes get slack on both sides and
never wrap; keep ≥8px between a label and the nearest border, as the layout rules say.

## Technical correctness

A diagram that looks right but would not work as drawn is wrong. Before delivering,
check every hop and caption against how the services actually behave:

- **Label each hop with the protocol on that hop.** A load balancer that terminates
  TLS changes the protocol: the client hop is "HTTPS :443" / "TLS :443", and the target
  hop shows the target group protocol — plaintext on a plaintext port for offload
  ("HTTP :80", "TCP :8080"), or "HTTPS :443" / "TLS :443" for re-encryption. Never put a
  plaintext protocol on a TLS port ("TCP :443") after termination; a TCP listener
  (pass-through) carries "TCP :443" on both hops and needs no certificate.
- **Gateway Load Balancer.** GWLBe → GWLB runs over PrivateLink (the GWLBe node already
  says so; no protocol label). GENEVE (UDP 6081) is only between the GWLB and its
  appliances, so "GENEVE :6081" goes on that hop and nowhere else. In the distributed
  model the IGW's edge route table sends inbound traffic to the GWLBe in the same AZ.
- **Routes in both directions.** A route sub-caption must include every route the drawn
  flows need, return traffic included, or the reader builds a broken network. For a
  centralized inspection VPC behind a TGW (AWS Network Firewall or GWLB):
  spoke subnets `0.0.0.0/0 → TGW`; spoke TGW route table `0.0.0.0/0 → inspection attachment`;
  inspection (firewall) TGW route table: spoke CIDRs propagated; TGW subnet
  `0.0.0.0/0 → firewall endpoint (same AZ)`; firewall subnet `0.0.0.0/0 → NAT`, `10.0.0.0/8 → TGW`;
  NAT (public) subnet `0.0.0.0/0 → IGW` **and** `10.0.0.0/8 → firewall endpoint (same AZ)`;
  appliance mode on the inspection VPC attachment. For distributed GWLB inspection of
  inbound traffic: IGW edge route table `<app subnet CIDR> → GWLBe (same AZ)` (one route
  per AZ, with the real CIDRs); app subnet
  `0.0.0.0/0 → GWLBe (same AZ)`; GWLBe subnet `0.0.0.0/0 → IGW`. When the routes don't
  fit as sub-captions, list them in the note.
- **TGW hub and spoke / peering routes:** VPC subnets `<all other VPCs' and
  on-premises CIDRs> → TGW` (or 0.0.0.0/0 → TGW); VPC and VPN (BGP) attachments
  propagate into the TGW route table; across a TGW peering only static routes work —
  each TGW needs `<remote Region CIDRs> → peering`, and the remote TGW needs
  `<on-premises CIDR> → peering` for on-premises ↔ remote-Region traffic.
- **TGW attachments are lines.** A VPC, VPN or peering attachment is the connector
  between the TGW and what it attaches (a peering attachment also carries the peering
  connection icon on its line, as above); `resource/AWS-Transit-Gateway_Attachment` is
  only for the attachment's ENIs drawn inside their subnets ("TGW ENI"). A VPC drawn as
  a single node uses `service/Amazon-Virtual-Private-Cloud`.
- **Credit each mechanism with what it does.** TGW appliance mode keeps both directions
  of a flow on the same AZ's attachment ENI; the per-AZ steering to the firewall is done
  by the subnet routes. A NAT gateway translates source addresses, it doesn't inspect.
- **Use AWS terms only in their AWS meaning.** "Shared VPC" is a VPC shared through
  AWS RAM; a VPC that hosts common services is a "Shared services VPC" (or "Services
  VPC"). Likewise "Transit VPC" is the legacy appliance-based hub, not a TGW.
- **Identical hops look identical.** The same hop repeated per AZ (IGW → GWLBe,
  GWLB ⇄ GWLBe) gets the same arrow ends, label and dash style in every AZ; when the
  per-AZ lines join into one trunk (NAT → IGW), they share its single arrowhead.
- **Captions say what the service does here, accurately.** Health checks are done by
  the load balancer (or Route 53 health checks), not CloudWatch — CloudWatch is
  "지표 · 경보" / "로그". An NLB access log needs a TLS listener; RDS Multi-AZ standby
  replicates synchronously and serves no reads; TGW peering is static-routed.
- **Global vs regional placement.** See "Global services sit outside the Region".

## Common diagram types & which layers to draw

- **3-tier web app**: AWS Cloud > Region > VPC > public subnet (ALB) + private subnets
  (ECS/EC2, RDS). Show AZ split if HA matters, with one ALB across the AZs (see
  "Fully managed multi-AZ services are one node").
- **Serverless**: skip VPC. API Gateway > Lambda > DynamoDB, with S3/CloudFront front.
- **Container (EKS/ECS)**: VPC > subnets > cluster; show ALB, node groups, ECR.
- **Hybrid (EKS Hybrid Nodes, Direct Connect)**: Corporate-data-center group on one side,
  AWS Cloud on the other, connected via Direct Connect / VPN / Transit Gateway icon.
- **Global network (AWS Cloud WAN)**: Regions as columns. The **core network is a
  container** that holds everything that belongs to it — the segments and the core
  network edges: a purple `#8C4FFF` dashed 2px band across every Region, with the
  `service/AWS-Cloud-WAN` icon as its 24px corner badge and the label "Core network"
  (no group icon exists for it; keep the label short so the Region borders don't cross
  it). Inside it, top to bottom: one segment row, the edge row on the main line (one
  `resource/AWS-Cloud-WAN_Core-Network-Edge` per Region, joined by an "AWS 백본"
  line), another segment row. Each segment row is a grey dashed box across every
  Region, led by a `resource/AWS-Cloud-WAN_Segment-Network` icon with the segment
  name. **VPCs stay outside the core network** (above and below it, in their Region
  column); each attachment is one plain line from the VPC through its segment row to
  its Region's edge, with a 5px grey junction dot where it crosses that row to mark
  the segment membership (explain the dot in the note).
- **Agentic AI (AgentCore)**: `service/Amazon-Bedrock` for the models,
  `service/Amazon-Bedrock-AgentCore` for the agent platform (see "Bedrock and
  AgentCore" for components), and standard icons for the surrounding infra.
