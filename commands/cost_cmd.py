"""cost - show cost of resources matching a tag, over the last N days."""
from collections import defaultdict
from datetime import date, timedelta

import boto3

from commands._common import parse_kv


def run(args):
    """Entry point."""
    tag_key, tag_val = parse_kv(args.tag)
    end = date.today()
    start = end - timedelta(days=args.days)

    ce = boto3.client("ce")
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={"Tags": {"Key": tag_key, "Values": [tag_val]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    totals = defaultdict(float)
    for day in resp.get("ResultsByTime", []):
        for group in day.get("Groups", []):
            service = group.get("Keys", ["Unknown"])[0]
            amount = group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", "0")
            totals[service] += float(amount)

    print(
        f"Cost for {tag_key}={tag_val} over last {args.days} days "
        f"({start.isoformat()} -> {end.isoformat()}):"
    )
    print("-" * 60)
    for service, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        print(f"  {service:<46} $ {amount:8.2f}")
    print("-" * 60)
    print(f"  {'TOTAL':<46} $ {sum(totals.values()):8.2f}")
