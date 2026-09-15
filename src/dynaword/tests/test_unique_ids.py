from collections import Counter
from typing import cast

import pytest
from datasets import Dataset, load_dataset

from dynaword.paths import repo_path
from .conftest import DATASET_NAMES


def test_ensure_ids_are_unique():
    if not DATASET_NAMES:
        pytest.skip("No datasets have been added yet.")

    name = str(repo_path.resolve())
    ds = load_dataset(name, split="train")
    ds = cast(Dataset, ds)
    counter = Counter(ds["id"])
    duplicates = [item for item, count in counter.items() if count > 1]

    assert len(duplicates) == 0, (
        f"Duplicate IDs found: {duplicates[:3]}{'...' if len(duplicates) > 3 else ''}"
    )
