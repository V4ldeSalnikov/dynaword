"""Paths of the dataset repo the tooling works on.

The repo is the current working directory, unless DYNAWORD_REPO points elsewhere.
Optional settings (hub_id, reference_corpora, license_names, removed_sources) are
read from <repo>/dynaword.toml.
"""

import os
import tomllib
from pathlib import Path

repo_path = Path(os.environ.get("DYNAWORD_REPO", Path.cwd())).resolve()
pyproject_path = repo_path / "pyproject.toml"
readme_path = repo_path / "README.md"
data_path = repo_path / "data"
settings_path = repo_path / "dynaword.toml"


def load_settings() -> dict:
    if not settings_path.exists():
        return {}
    with settings_path.open("rb") as f:
        return tomllib.load(f)


settings = load_settings()
