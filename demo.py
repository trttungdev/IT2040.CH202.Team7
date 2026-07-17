"""
Single entry point for the whole demo: imports the two pipeline stages and
runs them in order.

  1. make_sample()      (make_sample.py)   -- only if data/sample.csv or
                                              data/totals.json don't exist yet,
                                              so an already-labeled sample.csv
                                              is never silently overwritten.
  2. compute_results()  (compute_results.py)

Each stage is also a standalone script (`python3 make_sample.py`,
`python3 compute_results.py`) if you want to run or re-label just one step.
"""

import common
from make_sample import make_sample
from compute_results import compute_results


def main() -> None:
    if not common.SAMPLE_CSV.exists() or not common.TOTALS_JSON.exists():
        print("No cached sample/totals found -- generating now.")
        print("NOTE: data/sample.csv will be unlabeled; fill in is_true_positive "
              "(1/0) by eye before results are meaningful.\n")
        make_sample()
        print()
    else:
        print(f"Using existing {common.SAMPLE_CSV} and {common.TOTALS_JSON} "
              f"(delete them, or run make_sample.py directly, to regenerate).\n")

    compute_results()


if __name__ == "__main__":
    main()
