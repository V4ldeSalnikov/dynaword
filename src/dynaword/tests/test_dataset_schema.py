from collections import Counter

import pytest
import pyarrow.parquet as pq
from datasets import load_dataset

from dynaword.dataset_structure import SampleSchema
from dynaword.paths import repo_path

from .conftest import DATASET_NAMES


@pytest.mark.parametrize("dataset_name", DATASET_NAMES)
def test_sample_schema(dataset_name: str):
    """Ensure that the dataset samples follow the correct schema"""

    ds = load_dataset(
        str(repo_path.resolve()), dataset_name, split="train", streaming=True
    )
    sample = next(iter(ds))
    SampleSchema(**sample)


@pytest.mark.parametrize("dataset_name", DATASET_NAMES)
def test_dataset_folder_structure(dataset_name: str):
    """tests that the dataset folder structure is as follows.

    dataset_name
    |- dataset_name.md
    |- data.parquet
    |- metadata.parquet

    If there is a python file, there should at least be one called `create.py`, but there can be additional.
    """
    path = repo_path / "data" / dataset_name

    assert (path / "data.parquet").exists()
    assert (path / "metadata.parquet").exists()
    assert (path / f"{path.name}.md").exists()

    if any(p.name.endswith(".py") for p in path.glob("*")):
        assert (path / "create.py").exists()


@pytest.mark.parametrize("dataset_name", DATASET_NAMES)
def test_metadata_matches_text_samples(dataset_name: str):
    """Ensure that each text sample has matching metadata."""

    path = repo_path / "data" / dataset_name

    text_ids = pq.read_table(path / "data.parquet", columns=["id"]).column("id")
    metadata = pq.read_table(
        path / "metadata.parquet", columns=["dataset", "id"]
    )
    metadata_datasets = metadata.column("dataset").to_pylist()
    metadata_ids = metadata.column("id")

    assert metadata.num_rows == len(text_ids)
    assert set(metadata_datasets) == {dataset_name}
    assert Counter(text_ids.to_pylist()) == Counter(metadata_ids.to_pylist())
