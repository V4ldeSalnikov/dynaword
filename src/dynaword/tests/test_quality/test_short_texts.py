from typing import cast

import pytest
from datasets import Dataset, load_dataset

from dynaword.paths import repo_path

from ..conftest import DATASET_NAMES


@pytest.mark.parametrize("dataset_name", DATASET_NAMES)
def test_no_one_word_documents(dataset_name: str):
    ds = load_dataset(str(repo_path.resolve()), dataset_name, split="train")
    ds = cast(Dataset, ds)

    one_word_docs = ds.filter(lambda x: x["token_count"] <= 1)

    assert len(one_word_docs) == 0, (
        f"Found {len(one_word_docs)} one-word documents in dataset '{dataset_name}'"
    )
