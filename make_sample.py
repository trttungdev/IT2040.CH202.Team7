"""
Step 1 of 2: scan the corpus once with both detector suites (R&R and the
WIMBD-style baseline), then write:

  - data/totals.json  total detection counts (R&R vs WIMBD, and R&R by Pile
                       subset category) -- so step 2 doesn't have to re-scan
                       the corpus.
  - data/sample.csv    a stratified sample per (system, PI type) for manual
                       true/false-positive labeling, mirroring the paper's
                       §2.2 methodology.

data/sample.csv ships pre-labeled; run this again only if you want a fresh,
unlabeled sample to re-annotate.

Exposes make_sample() so it can be imported (see demo.py) instead of always
run as a standalone script.
"""

import csv
import json
import random
from collections import defaultdict

import common
from detectors import rr_detect_all, wimbd_detect_all

SAMPLE_PER_CELL = 15  # paper used 250/type/system; scaled down for a seminar


def make_sample() -> None:
    random.seed(common.DEFAULT_SEED)
    print(f"Loading {common.DATASET_NAME} (first {common.DEFAULT_N_DOCS} docs)...")
    ds = common.load_pile_sample()

    totals = defaultdict(lambda: defaultdict(int))       # totals[system][pi_type]
    by_category = defaultdict(lambda: defaultdict(int))  # by_category[category][pi_type], R&R only
    docs_with_pi = 0
    pool = defaultdict(list)  # pool[(system, pi_type)] = [(text, span, start, end, category), ...]

    for row in ds:
        text = row["text"]
        category = row["meta"].get("pile_set_name", "unknown")

        rr_dets = rr_detect_all(text)
        if rr_dets:
            docs_with_pi += 1
        for d in rr_dets:
            totals["R&R"][d.pi_type] += 1
            by_category[category][d.pi_type] += 1
            pool[("R&R", d.pi_type)].append((text, d.span, d.start, d.end, category))

        for d in wimbd_detect_all(text):
            totals["WIMBD"][d.pi_type] += 1
            pool[("WIMBD", d.pi_type)].append((text, d.span, d.start, d.end, category))

    common.DATA_DIR.mkdir(exist_ok=True)
    with open(common.TOTALS_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "total_docs": len(ds),
            "docs_with_pi": docs_with_pi,
            "totals": {s: dict(t) for s, t in totals.items()},
            "by_category": {c: dict(t) for c, t in by_category.items()},
        }, f, indent=2)

    rows = []
    for (system, pi_type), items in sorted(pool.items()):
        random.shuffle(items)
        for text, span, start, end, category in items[:SAMPLE_PER_CELL]:
            rows.append({
                "system": system,
                "pi_type": pi_type,
                "pile_category": category,
                "context_before": text[max(0, start - 60):start],
                "detected_span": span,
                "context_after": text[end:end + 30],
                "is_true_positive": "",  # fill in by eye: 1 or 0
            })

    with open(common.SAMPLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nScanned {len(ds)} documents. Docs with >=1 R&R detection: "
          f"{docs_with_pi} ({100 * docs_with_pi / len(ds):.2f}%)")
    print(f"Wrote totals to {common.TOTALS_JSON}")
    print(f"Wrote {len(rows)} sample rows to {common.SAMPLE_CSV}")
    print("\nNext: open the CSV, fill in is_true_positive (1/0) by eye, "
          "then run compute_results.py")


if __name__ == "__main__":
    make_sample()
