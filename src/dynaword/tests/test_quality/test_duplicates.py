from typing import cast

import pytest
from datasets import Dataset, load_dataset

from dynaword.paths import repo_path
from ..conftest import DATASET_NAMES


@pytest.mark.parametrize("dataset_name", DATASET_NAMES)
def test_no_within_data_duplicates(dataset_name: str):
    ds = load_dataset(str(repo_path.resolve()), dataset_name, split="train")
    ds = cast(Dataset, ds)

    assert len(set(ds["text"])) == len(ds)


@pytest.mark.skip(
    "This tests takes too long to run"
)  # there seems to be some duplicate across
def test_no_data_duplicates():
    ds = load_dataset(str(repo_path.resolve()), split="train")
    ds = cast(Dataset, ds)

    assert len(set(ds["text"])) == len(ds)
