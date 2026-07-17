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

Chạy demo trên dữ liệu đã gán nhãn sẵn trong `data/` (chỉ cần thư viện chuẩn
của Python):

```bash
python3 demo.py
```

Kết quả in ra Table 1, Figure 1 và permutation test.

Muốn tạo lại mẫu từ đầu (cần HuggingFace `datasets`):

```bash
pip install -r requirements.txt
python3 make_sample.py   # rồi gán nhãn is_true_positive (1/0) trong data/sample.csv
python3 compute_results.py
```
