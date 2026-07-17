"""Shared constants and dataset loading for the PI-parroting seminar demo."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

DATASET_NAME = "NeelNanda/pile-10k"  # 10k-doc sample of the Pile, same corpus as the paper
DEFAULT_N_DOCS = 10_000
DEFAULT_SEED = 0

SAMPLE_CSV = DATA_DIR / "sample.csv"
TOTALS_JSON = DATA_DIR / "totals.json"


def load_pile_sample(n_docs: int = DEFAULT_N_DOCS):
    """Load the first `n_docs` documents of NeelNanda/pile-10k.

    Imports `datasets` lazily so the shipped demo (which reuses the labeled
    sample.csv/totals.json) runs on the standard library alone -- only a
    fresh corpus scan via make_sample.py needs HuggingFace `datasets`.
    """
    from datasets import load_dataset

    DATA_DIR.mkdir(exist_ok=True)
    return load_dataset(DATASET_NAME, split=f"train[:{n_docs}]")
