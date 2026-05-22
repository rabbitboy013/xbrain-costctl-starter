# Reflections

## clean --apply blast radius

Nếu lỡ chạy `clean --tag Environment=dev --apply` trong account dùng chung, rủi ro khá lớn vì nhiều nhóm có thể cùng đặt tag `Environment=dev`. Theo em, trước khi cho xoá thật cần có dry-run bắt buộc, in rõ từng resource ID, và nên yêu cầu thêm tag hẹp hơn như `Application=CostCtlTest` hoặc `Owner=<email>`. IAM permission cũng nên giới hạn theo tag ownership để sinh viên không xoá nhầm resource của nhóm khác.

## AI assistance

Em có dùng AI để hỗ trợ đọc test, hiểu yêu cầu trong docstring và implement các command boto3 nhanh hơn. Tuy vậy em vẫn chạy lại `python -m pytest -q`, kiểm tra output thật trên AWS lab, và tự điều chỉnh hướng làm cho an toàn hơn, ví dụ chỉ chạy read-only trước và không dùng service đang được sử dụng để demo xoá.

## W7 carry-over

Nếu mang sang W7, em sẽ giữ `list`, `tag`, `cost` vì các lệnh này giúp kiểm tra tài nguyên và tagging khá thực tế. Em cũng muốn giữ `clean`, nhưng cần thêm lớp bảo vệ như bắt nhập confirm, chỉ cho clean theo tag riêng của team, log lại thao tác và có allowlist account/region. Với `migrate-gp3`, em nghĩ nên để dạng plan trước, khi apply thì chỉ chạy từng volume nhỏ để giảm rủi ro.
