"""tag - add or update tags on one resource."""
import boto3
from botocore.exceptions import ClientError

from commands._common import parse_kv


def _to_tags(set_args):
    """Convert ['k1=v1', 'k2=v2'] to [{'Key':'k1','Value':'v1'}, ...]."""
    return [{"Key": key, "Value": value} for key, value in (parse_kv(s) for s in set_args)]


def _tag_ec2(rid, tags):
    boto3.client("ec2").create_tags(Resources=[rid], Tags=tags)


def _tag_rds(rid, tags):
    rds = boto3.client("rds")
    resp = rds.describe_db_instances(DBInstanceIdentifier=rid)
    arn = resp["DBInstances"][0]["DBInstanceArn"]
    rds.add_tags_to_resource(ResourceName=arn, Tags=tags)


def _tag_s3(rid, tags):
    s3 = boto3.client("s3")
    try:
        existing = s3.get_bucket_tagging(Bucket=rid).get("TagSet", [])
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code != "NoSuchTagSet":
            raise
        existing = []

    merged = {tag["Key"]: tag["Value"] for tag in existing}
    merged.update({tag["Key"]: tag["Value"] for tag in tags})
    s3.put_bucket_tagging(
        Bucket=rid,
        Tagging={"TagSet": [{"Key": key, "Value": value} for key, value in merged.items()]},
    )


def _tag_volume(rid, tags):
    boto3.client("ec2").create_tags(Resources=[rid], Tags=tags)


DISPATCH = {
    "ec2": _tag_ec2,
    "rds": _tag_rds,
    "s3": _tag_s3,
    "volume": _tag_volume,
}


def run(args):
    """Entry point."""
    tags = _to_tags(args.set)
    try:
        DISPATCH[args.type](args.id, tags)
    except ClientError as e:
        error = e.response.get("Error", {})
        code = error.get("Code", "Unknown")
        message = error.get("Message", str(e))
        print(f"AWS error [{code}]: {message}")
        return

    tag_text = ", ".join(f"{tag['Key']}={tag['Value']}" for tag in tags)
    print(f"Applied {len(tags)} tag(s) to {args.type} {args.id}: {tag_text}")
