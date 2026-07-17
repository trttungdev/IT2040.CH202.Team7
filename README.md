# IT2040.CH202.Team7 - [PI Parroting](https://arxiv.org/abs/2602.20580)

## Thành viên nhóm

| Họ và tên | MSSV |
| --- | --- |
| Trần Duy Tùng | 250101075 |
| Trần Thanh Tùng | 250201098 |
| Nguyễn Trần Hoàng Quân | 250201083 |

## Giới thiệu

Bản tái hiện ở quy mô seminar của bài báo **"Personal Information Parroting in
Language Models"** (Subramani, Ghate, Diab — Findings of EACL 2026): tái hiện
bộ detector mà bài báo đề xuất (Section 2 / Appendix A) và phần kiểm chứng nó
so với framework trước đó là WIMBD (Elazar et al., 2023) (Section 2.2,
Figure 1, Table 1).

Chạy trên `NeelNanda/pile-10k` — một mẫu công khai gồm 10.000 tài liệu của bộ
The Pile, đúng bằng corpus pretraining mà bài báo sử dụng — nên đây là dữ liệu
thật ở quy mô có thể chạy được trên laptop.

## Cấu trúc mã nguồn

```
detectors.py       cả hai bộ detector, đặt cạnh nhau để so sánh:
                      rr_*     đề xuất của bài báo (Appendix A)
                      wimbd_*  framework trước đó mà bài báo cải tiến
common.py          hằng số dùng chung + hàm nạp dataset
make_sample.py     bước 1: make_sample() -- quét corpus bằng cả hai detector,
                   ghi data/totals.json (số lượng) + data/sample.csv (mẫu phân
                   tầng để gán nhãn thủ công true/false-positive)
compute_results.py bước 2: compute_results() -- biến mẫu đã gán nhãn thành ba
                   kết quả chính của bài báo -- Table 1, Figure 1, permutation
                   test
demo.py            điểm chạy chính: import make_sample() và compute_results()
                   rồi chạy tuần tự (bỏ qua bước 1 nếu data/sample.csv đã tồn
                   tại, nên nhãn không bao giờ bị ghi đè âm thầm)
data/
  sample.csv       các phát hiện R&R + WIMBD, phân tầng, đã gán nhãn sẵn
  totals.json      tổng số phát hiện (tạo lại bằng make_sample.py)
```

Mỗi bước là một hàm độc lập, có thể import riêng
(`from make_sample import make_sample`, `from compute_results import
compute_results`) -- `demo.py` chỉ là một script mỏng gọi cả hai. `detectors.py`
cũng là một module thuần: `from detectors import rr_detect_all,
wimbd_detect_all`.

## Cách chạy

Không cần cài đặt gì -- bản demo có sẵn chỉ chạy bằng thư viện chuẩn của Python
(nó dùng lại `data/sample.csv` / `data/totals.json` đã gán nhãn sẵn):

```bash
python3 demo.py
```

Lệnh này in ra Table 1, Figure 1, và kết luận về ý nghĩa thống kê của
permutation test.

### Tạo lại mẫu từ đầu

Chỉ cần khi bạn muốn có một mẫu mới (chưa gán nhãn) để tự gán nhãn lại. Bước này
quét corpus The Pile nên cần thư viện HuggingFace `datasets`:

```bash
pip install -r requirements.txt
python3 make_sample.py
# -> mở data/sample.csv, tự tay điền is_true_positive (1/0) cho từng dòng
python3 compute_results.py   # hoặc chạy luôn: python3 demo.py
```

## Hạn chế đã biết (chủ ý để lại làm hướng phát triển)

- Việc phát hiện `ip_v6` có precision ~0% trên các subset nhiều code của Pile
  (GitHub, StackExchange) vì dấu `::` trần là cú pháp phổ biến trong
  Haskell/Fortran/argparse, trùng với ký hiệu rút gọn của IPv6.
- Việc phát hiện `phone` trên subset DM-Mathematics chủ yếu là false positive
  (các đáp án số học tình cờ có 10 chữ số) — cùng loại lỗi mà chính bài báo ghi
  nhận với các false positive kiểu `MAXINT`.
- Kích thước mẫu ở đây (15 mỗi ô) nhỏ hơn nhiều so với bài báo (250 mỗi ô), nên
  các p-value của permutation test trong `compute_results.py` yếu về mặt thống
  kê hơn so với bài báo; tuy nhiên hướng và độ lớn của hiệu ứng vẫn khớp.
