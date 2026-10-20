#!/usr/bin/env python3
"""Find icons in the bundled assets/icons.json.

Usage:
  python scripts/find_icon.py ec2
  python scripts/find_icon.py "api gateway" lambda s3   # multiple at once
  python scripts/find_icon.py --list service            # list a whole set

Prints ranked matches as `set/name`. Icons live inside assets/icons.json
(one file, not hundreds), so reference them by `set/name` and let embed.py
inline the actual SVG/PNG when you build a diagram. Matches whole words,
case/hyphen-insensitive, with common AWS abbreviation aliases.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = json.loads((ROOT / "assets" / "icons.json").read_text(encoding="utf-8"))
SETS = BUNDLE["sets"]

ALIASES = {
    # alb/nlb/gwlb resolve to their resource icon; the generic service icon is "elb".
    "alb": "application load balancer", "nlb": "network load balancer",
    "gwlb": "gateway load balancer",
    "elb": "elastic load balancing", "load balancer": "elastic load balancing",
    "ecs": "elastic container service", "ecr": "elastic container registry",
    "eks": "elastic kubernetes service", "s3": "simple storage service",
    "sqs": "simple queue service", "sns": "simple notification service",
    "ses": "simple email service", "rds": "relational database service",
    "vpc": "virtual private cloud", "ddb": "dynamodb", "apigw": "api gateway",
    "asg": "ec2 auto scaling", "iam": "identity and access management",
    "kms": "key management service", "efs": "elastic file system",
    "ebs": "elastic block store", "msk": "managed streaming for apache kafka",
    "sfn": "step functions", "step functions": "step functions",
    # VPC resources live in the resource set (Amazon-VPC_*)
    "igw": "internet gateway", "nat": "nat gateway", "natgw": "nat gateway",
    "vgw": "vpn gateway", "cgw": "customer gateway", "eni": "elastic network interface",
    "nacl": "network access control list", "pcx": "peering connection",
    "vpce": "vpc endpoints", "endpoint": "vpc endpoints",
    "gateway endpoint": "vpc endpoints", "interface endpoint": "vpc endpoints",
    "s3 gateway endpoint": "vpc endpoints", "dynamodb gateway endpoint": "vpc endpoints",
    "s3 endpoint": "vpc endpoints", "dynamodb endpoint": "vpc endpoints",
    "eice": "vpc endpoints", "instance connect endpoint": "vpc endpoints",
    # the package files its only route table icon under Route 53; it is also the VPC/TGW route table
    "route table": "route 53 route table", "routing table": "route 53 route table",
    "rtb": "route 53 route table", "vpc route table": "route 53 route table",
    "tgw route table": "route 53 route table",
    "ec2 instance connect endpoint": "vpc endpoints", "tgw": "transit gateway",
    "gwlbe": "vpc endpoints", "gwlb endpoint": "vpc endpoints",
    "gateway load balancer endpoint": "vpc endpoints",
    "aws cloud": "aws cloud logo", "cloud": "aws cloud logo",
    "on-prem": "corporate data center", "on-premises": "corporate data center",
    "onprem": "corporate data center", "data center": "corporate data center",
    "datacenter": "corporate data center",
    "agentcore": "bedrock agentcore",
}


# Logo-less AWS Cloud outlines: never offered, the AWS Cloud badge always has the logo.
NO_LOGO = {"group/AWS-Cloud_32", "group/AWS-Cloud_32_Dark"}
# Groups the official toolkit draws without a badge icon (see diagram_guide.md).
NO_ICON_GROUPS = {
    "az": "Availability Zone", "availability zone": "Availability Zone",
    "security group": "Security group", "sg": "Security group",
    "generic group": "Generic group", "step functions workflow": "Step Functions workflow",
}
VENDOR = {"amazon", "aws"}
# Size/theme suffixes on group icons (AWS-Cloud_32_Dark) are not part of the name.
SUFFIX = {"32", "dark", "light"}
# Tie-break order: a service icon beats a resource or category icon of the same score.
SET_ORDER = ["service", "resource", "group", "category", "legacy"]


def norm(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())


def tokens(s: str) -> list:
    return re.findall(r"[a-z0-9]+", s.lower())


def bare(nt: list) -> list:
    """Name tokens without size/theme suffixes."""
    while nt and nt[-1] in SUFFIX:
        nt = nt[:-1]
    return nt


def core(nt: list) -> list:
    """Name tokens without the Amazon/AWS prefix and size/theme suffixes."""
    nt = bare(nt)
    while nt and nt[0] in VENDOR:
        nt = nt[1:]
    return nt


def has_run(qt: list, nt: list) -> bool:
    return any(nt[i:i + len(qt)] == qt for i in range(len(nt) - len(qt) + 1))


def score(query: str, name: str) -> int:
    """Match on whole words so `nat` finds NAT-Gateway, not Alter-nat-e."""
    qt, nt = tokens(query), tokens(name)
    if not qt:
        return 0
    if norm(query) == norm(name):
        return 100
    if qt in (core(nt), bare(nt)) or norm(query) == "".join(core(nt)):
        return 95
    if has_run(qt, core(nt)):
        # The query is the service name (or its tail, e.g. VPC_NAT-Gateway).
        return 85 if nt[-len(qt):] == qt else 75
    if all(t in nt for t in qt):
        return 65
    if all(any(n.startswith(t) for n in nt) for t in qt):
        return 50  # word prefixes: "dynamo" -> DynamoDB
    if len(norm(query)) >= 4 and norm(query) in norm(name):
        return 30
    return 0


def search(query: str, k: int = 5):
    ql = query.lower().strip()
    alias = ALIASES.get(ql, [])
    queries = [query] + ([alias] if isinstance(alias, str) else alias)
    results = []
    for setname, entries in SETS.items():
        for name in entries:
            s = max(score(q, name) for q in queries)
            if f"{setname}/{name}" in NO_LOGO:
                continue  # embed.py rejects these; the -logo variant is the AWS Cloud badge
            if setname == "legacy":
                s -= 20  # retired names only win when nothing current matches
            if s > 0:
                rank = SET_ORDER.index(setname) if setname in SET_ORDER else len(SET_ORDER)
                results.append((s, rank, len(name), f"{setname}/{name}"))
    results.sort(key=lambda r: (-r[0], r[1], r[2]))
    return [(s, ref) for s, _, _, ref in results[:k]]


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        print("Available sets:", ", ".join(f"{k} ({len(v)})" for k, v in SETS.items()))
        sys.exit(1)
    if args[0] == "--list":
        setname = args[1] if len(args) > 1 else "service"
        if setname not in SETS:
            sys.exit(f"Unknown set {setname!r}. Sets: {', '.join(SETS)}")
        for name in sorted(SETS.get(setname, {})):
            if f"{setname}/{name}" not in NO_LOGO:
                print(f"{setname}/{name}")
        return
    for query in args:
        print(f"# {query}")
        group = NO_ICON_GROUPS.get(query.lower().strip())
        if group:
            print(f"  (no icon: {group} is a label-only group — draw a rect in the color from "
                  "diagram_guide.md's group table, no corner badge)")
            print()
            continue
        hits = search(query)
        if not hits:
            print("  (no match — try: find_icon.py --list service, then --list resource)")
        for s, ref in hits:
            print(f"  [{s:3}] {ref}")
        print()


if __name__ == "__main__":
    main()
