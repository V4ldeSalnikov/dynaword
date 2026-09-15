import pytest
from datasets import load_dataset

from dynaword.datasheet import DataSheet
from dynaword.paths import repo_path, settings

# data that has been removed due to legal disputes, question about legality, or similar
REMOVED_DATA = settings.get("removed_sources", [])


def test_dataset_loads():
    """Ensures that the dataset can load as intended"""
    ds_sheet = DataSheet.load_from_path(repo_path / "README.md")
    dataset_names = [
        cfg["config_name"]
        for cfg in ds_sheet.frontmatter["configs"]
        if cfg["config_name"] not in {"default", "meta"}
    ]
    if not dataset_names:
        pytest.skip("No datasets have been added yet.")

    name = str(repo_path.resolve())
    ds = load_dataset(name, split="train", streaming=True)
    sample = next(iter(ds))
    assert isinstance(sample, dict)


def test_all_datasets_in_yaml():
    ds_sheet = DataSheet.load_from_path(repo_path / "README.md")

    ds_names = {
        cfg["config_name"]
        for cfg in ds_sheet.frontmatter["configs"]
        if cfg["config_name"] not in {"default", "meta"}
    }

    data_folder = repo_path / "data"
    datasets = (dataset for dataset in data_folder.glob("*") if dataset.is_dir())

    for dataset in datasets:
        if dataset.name not in REMOVED_DATA:
            assert dataset.name in ds_names
