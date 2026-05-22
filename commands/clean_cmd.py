"""clean - bulk terminate resources matching a tag."""
import boto3

from commands._common import parse_kv, tags_to_dict


def _find_targets(tag_key, tag_val):
    """Return matching EC2 instances and available volumes."""
    ec2 = boto3.client("ec2")
    targets = {"ec2": [], "volume": []}

    instance_paginator = ec2.get_paginator("describe_instances")
    for page in instance_paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                state = instance.get("State", {}).get("Name")
                tags = tags_to_dict(instance.get("Tags", []))
                if state not in ("shutting-down", "terminated") and tags.get(tag_key) == tag_val:
                    targets["ec2"].append(instance["InstanceId"])

    volume_paginator = ec2.get_paginator("describe_volumes")
    for page in volume_paginator.paginate():
        for volume in page.get("Volumes", []):
            tags = tags_to_dict(volume.get("Tags", []))
            if volume.get("State") == "available" and tags.get(tag_key) == tag_val:
                targets["volume"].append(volume["VolumeId"])

    return targets


def run(args):
    """Entry point."""
    tag_key, tag_val = parse_kv(args.tag)
    targets = _find_targets(tag_key, tag_val)
    ec2_ids = targets["ec2"]
    volume_ids = targets["volume"]

    if not ec2_ids and not volume_ids:
        print("Nothing to clean.")
        return

    print(f"Clean plan for {tag_key}={tag_val}:")
    for iid in ec2_ids:
        print(f"  EC2 {iid}")
    for vid in volume_ids:
        print(f"  volume {vid}")

    if not args.apply:
        print("(dry-run - pass --apply to terminate/delete these resources)")
        return

    ec2 = boto3.client("ec2")
    if ec2_ids:
        ec2.terminate_instances(InstanceIds=ec2_ids)
        print(f"Terminated {len(ec2_ids)} EC2 instance(s).")
    for vid in volume_ids:
        ec2.delete_volume(VolumeId=vid)
        print(f"Deleted volume {vid}")
