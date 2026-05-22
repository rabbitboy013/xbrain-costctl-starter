"""migrate-gp3 - plan or apply gp2 to gp3 EBS migration."""
import boto3

GP2_PRICE = 0.10
GP3_PRICE = 0.08


def _gp2_volumes(ec2):
    resp = ec2.describe_volumes(Filters=[{"Name": "volume-type", "Values": ["gp2"]}])
    return resp.get("Volumes", [])


def _attached_instance(volume):
    attachments = volume.get("Attachments", [])
    if not attachments:
        return "(none)"
    return attachments[0].get("InstanceId", "(none)")


def _monthly_savings(volume):
    return volume.get("Size", 0) * (GP2_PRICE - GP3_PRICE)


def run(args):
    """Entry point."""
    ec2 = boto3.client("ec2")
    volumes = _gp2_volumes(ec2)
    if args.volume_id:
        volumes = [volume for volume in volumes if volume["VolumeId"] == args.volume_id]

    if not volumes:
        print("No gp2 volumes found.")
        return

    if not args.apply:
        print("gp2 volumes (price delta $0.020/GB-month):")
        print("-" * 78)
        total = 0.0
        for volume in volumes:
            savings = _monthly_savings(volume)
            total += savings
            print(
                f"  {volume['VolumeId']:<22} {volume.get('Size', 0):>5}GB  "
                f"attached={_attached_instance(volume):<18} ${savings:5.2f}/mo savings"
            )
        print("-" * 78)
        print(f"  TOTAL projected savings: ${total:.2f}/mo")
        print()
        print("(dry-run - pass --apply --volume-id <id> to migrate one, or --apply to migrate ALL)")
        return

    for volume in volumes:
        vid = volume["VolumeId"]
        ec2.modify_volume(
            VolumeId=vid,
            VolumeType="gp3",
            Iops=3000,
            Throughput=125,
        )
        print(f"  -> modify_volume issued for {vid} (gp3, 3000 IOPS, 125 MiB/s)")

    print()
    print("Volume(s) entering 'modifying' then 'optimizing' state. App stays online.")
    print("Use `costctl list volume` after ~30 minutes to confirm 'in-use' + gp3.")
