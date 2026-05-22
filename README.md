# costctl - XBrain W6 side challenge

Đây là bài side challenge W6: hoàn thiện một CLI nhỏ để kiểm tra và quản lý tài nguyên AWS liên quan đến chi phí. Source ban đầu đã có sẵn `argparse`, test và helper; phần em làm là implement logic trong các file `commands/*_cmd.py`, chạy test, rồi thử với AWS lab account.

## Kết quả hiện tại

- Final test result: `25/25 passed`
- Lệnh kiểm tra: `python -m pytest -q`
- Region đã test thật: `us-west-2`
- AWS identity đã verify bằng `aws sts get-caller-identity`
- Account lab: `138062776627`

## Các command đã implement

| Command | Trạng thái | Ghi chú |
|---|---:|---|
| `list` | Done | List EC2, RDS, S3, EBS volume; hỗ trợ `--tag` và `--missing-tag` |
| `terminate` | Done | Có confirm mặc định, `--force` cho script/test, xử lý `ClientError` thân thiện |
| `tag` | Done | Gắn tag cho EC2, RDS, S3, volume; riêng S3 có merge tag cũ để không ghi đè mất |
| `cost` | Done | Query Cost Explorer theo tag và group theo service |
| `clean` | Done | Dry-run mặc định, chỉ xoá khi có `--apply`; chỉ target EC2 chưa terminated và volume `available` |
| `idle` | Done | Đọc CloudWatch CPU trung bình để tìm EC2 idle |
| `migrate-gp3` | Done | Dry-run mặc định; `--apply` mới gọi `modify_volume` |

## Minh chứng chạy thật

Đã chạy các lệnh read-only trước để không ảnh hưởng service đang được dùng:

```powershell
python costctl.py --region us-west-2 list ec2
python costctl.py --region us-west-2 list volume
python costctl.py --region us-west-2 list s3
python costctl.py --region us-west-2 list ec2 --missing-tag Application
```

Output đã lưu trong:

- `sample_output/list_ec2_example.txt`
- `sample_output/list_ec2_missing_app_example.txt`
- `sample_output/list_s3_example.txt`

EC2 tìm thấy trong lab:

```text
i-047161c10222eeeac | t3.micro | stopped | Environment=dev, Name=dev-test-stopme
```

Volume tìm thấy:

```text
vol-08db2af6a23a9cdec | gp3-8GB | in-use
```

S3 có nhiều bucket đang được dùng bởi lab/team khác, ví dụ `recruitment-*`, `tu-*`, `aws-cloudtrail-*`, nên em chỉ dùng lệnh `list` để kiểm tra và không chạy xoá trên các bucket này.

## Nguyên tắc an toàn khi demo

Em không dùng các service đang được sử dụng để test lệnh xoá/sửa. Nếu cần demo `tag`, `terminate`, `clean --apply` hoặc `migrate-gp3 --apply`, em sẽ tạo resource test riêng với tag rõ ràng:

```text
Application=CostCtlTest
purpose=practice
Environment=dev
Owner=<email-cua-minh>
```

Không dùng tag quá rộng như `Environment=dev` để clean, vì trong account chung có thể nhiều nhóm cùng dùng tag này.

## Cách chạy lại

Install dependency:

```powershell
python -m pip install -r requirements-dev.txt
```

Run test:

```powershell
python -m pytest -q
```

Run CLI:

```powershell
python costctl.py --region us-west-2 list ec2
python costctl.py --region us-west-2 list s3 --tag Application=RecruitmentApp
python costctl.py --region us-west-2 clean --tag Application=CostCtlTest
```

`clean` mặc định là dry-run. Chỉ dùng `--apply` khi chắc chắn toàn bộ resource trong plan là resource test của mình.

## Team

- <Điền tên sinh viên / nhóm>
