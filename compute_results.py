"""
Step 2 of 2: turn the labels in data/sample.csv (+ data/totals.json from
make_sample.py) into the paper's three headline results:

  - Table 1: total detections x precision -> expected true PI count
  - Figure 1: precision per PI type, R&R vs. WIMBD
  - the permutation-test significance claim (two-sample diff. of means,
    10,000 resamples)

Exposes compute_results() so it can be imported (see demo.py) instead of
always run as a standalone script.
"""

import csv
import json
import random
from collections import defaultdict

import common

N_RESAMPLES = 10_000


def load_labels(csv_path) -> dict:
    labels = defaultdict(list)
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            v = row["is_true_positive"].strip()
            if v in ("0", "1"):
                labels[(row["system"], row["pi_type"])].append(int(v))
    return labels


def permutation_test(a: list, b: list, n_resamples: int, rng: random.Random) -> float:
    """Two-sample difference-of-means permutation test.
    Returns the two-sided p-value for observed mean(a) - mean(b)."""
    observed = abs(sum(a) / len(a) - sum(b) / len(b))
    pooled = a + b
    n_a = len(a)
    count_ge = 0
    for _ in range(n_resamples):
        rng.shuffle(pooled)
        stat = abs(sum(pooled[:n_a]) / n_a - sum(pooled[n_a:]) / (len(pooled) - n_a))
        if stat >= observed:
            count_ge += 1
    return count_ge / n_resamples


def compute_results() -> None:
    rng = random.Random(common.DEFAULT_SEED)

    with open(common.TOTALS_JSON, encoding="utf-8") as f:
        totals = json.load(f)["totals"]

    labels = load_labels(common.SAMPLE_CSV)
    all_types = sorted({pt for (_, pt) in labels})

    print("=" * 78)
    print("Table 1: total detections vs. precision-adjusted expected PI count (R&R)")
    print("=" * 78)
    print(f"  {'PI type':14s} {'total_det':>10s} {'precision':>10s} {'expected_PI':>12s}")
    for pt in all_types:
        rr_labels = labels.get(("R&R", pt))
        total = totals.get("R&R", {}).get(pt, 0)
        if not rr_labels:
            print(f"  {pt:14s} {total:10d} {'--':>10s} {'--':>12s}")
            continue
        p = sum(rr_labels) / len(rr_labels)
        print(f"  {pt:14s} {total:10d} {p:10.2f} {round(total * p):12d}")

    print("\n" + "=" * 78)
    print("Figure 1: precision per PI type, R&R vs. WIMBD (from labeled sample)")
    print("=" * 78)
    print(f"  {'PI type':14s} {'R&R total':>10s} {'WIMBD total':>12s} "
          f"{'R&R prec.':>10s} {'WIMBD prec.':>12s}")
    for pt in all_types:
        rr_total = totals.get("R&R", {}).get(pt, 0)
        wimbd_total = totals.get("WIMBD", {}).get(pt)
        rr_labels = labels.get(("R&R", pt))
        wimbd_labels = labels.get(("WIMBD", pt))
        rr_p = f"{sum(rr_labels)/len(rr_labels):.2f}" if rr_labels else "--"
        wimbd_p = f"{sum(wimbd_labels)/len(wimbd_labels):.2f}" if wimbd_labels else "n/a"
        wimbd_total_s = str(wimbd_total) if wimbd_total is not None else "n/a"
        print(f"  {pt:14s} {rr_total:10d} {wimbd_total_s:>12s} {rr_p:>10s} {wimbd_p:>12s}")

    print("\n" + "=" * 78)
    print(f"Permutation test (two-sample diff. of means, {N_RESAMPLES:,} resamples)")
    print("H0: R&R and WIMBD have equal precision for this PI type")
    print("=" * 78)
    for pt in all_types:
        rr_labels = labels.get(("R&R", pt))
        wimbd_labels = labels.get(("WIMBD", pt))
        if not rr_labels:
            continue
        if not wimbd_labels:
            print(f"  {pt:14s} WIMBD has no detector for this type -- R&R wins by definition")
            continue
        p_value = permutation_test(rr_labels, wimbd_labels, N_RESAMPLES, rng)
        sig = "significant (p<0.05)" if p_value < 0.05 else "not significant"
        print(f"  {pt:14s} p={p_value:.4f}  -> {sig}")


if __name__ == "__main__":
    compute_results()
