"""idle - find idle EC2 instances by N-hour CPU average."""
from datetime import datetime, timedelta, timezone
from statistics import mean

import boto3

from commands._common import tags_to_dict


def _avg_cpu(cw, instance_id, hours):
    """Return average CPU percent over the last N hours, or None if no datapoints."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    resp = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=3600,
        Statistics=["Average"],
    )
    datapoints = resp.get("Datapoints", [])
    if not datapoints:
        return None
    return mean(point["Average"] for point in datapoints)


def run(args):
    """Entry point."""
    ec2 = boto3.client("ec2")
    cw = boto3.client("cloudwatch")
    idle = []

    print(
        f"Scanning running EC2 (excluding keep=true) - "
        f"threshold {args.threshold:.1f}% over {args.hours}h:"
    )
    print("-" * 78)

    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}],
    ):
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                tags = tags_to_dict(instance.get("Tags", []))
                if tags.get("keep", "").lower() == "true":
                    continue

                iid = instance["InstanceId"]
                avg = _avg_cpu(cw, iid, args.hours)
                if avg is None:
                    print(f"  {iid:<22} {instance.get('InstanceType', ''):<12} cpu_{args.hours}h=NO DATA")
                    continue

                marker = "  <- IDLE" if avg < args.threshold else ""
                if marker:
                    idle.append(iid)
                print(
                    f"  {iid:<22} {instance.get('InstanceType', ''):<12} "
                    f"cpu_{args.hours}h={avg:5.2f}%{marker}"
                )

    print("-" * 78)
    print()
    print(f"Idle: {len(idle)} instance(s): {idle}")
    print("Tip: combo with terminate ->  ./costctl.py terminate ec2 --id <id>")
