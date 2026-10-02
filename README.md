# 🧨 Dynaword tooling

|              |                                                                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Version**  | 0.1.0 ([Changelog](CHANGELOG.md))                                                                                                              |
| **Python**   | 3.12 or newer                                                                                                                                    |
| **License**  | [CC0-1.0](LICENSE), the same as the Dynaword datasets                                                                                          |
| **Used by**  | The [Dynaword](https://huggingface.co/collections/danish-foundation-models/dynawords) dataset repositories                                       |
| **Contact**  | If you have questions about the tooling please create an issue in the discussions of the Dynaword repository you are contributing to            |

## Table of Contents
- [🧨 Dynaword tooling](#-dynaword-tooling)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
    - [Summary](#summary)
    - [What a dataset repository contains](#what-a-dataset-repository-contains)
    - [Installing dependencies](#installing-dependencies)
  - [Adding a new dataset](#adding-a-new-dataset)
    - [Writing create.py](#writing-createpy)
    - [Updating descriptive statistics](#updating-descriptive-statistics)
    - [Running tests](#running-tests)
    - [Bumping the version](#bumping-the-version)
    - [Checklist](#checklist)
  - [Settings](#settings)
  - [Frequently asked questions](#frequently-asked-questions)

## Description

### Summary

The Dynaword tooling is the code shared by all Dynaword dataset repositories. It computes descriptive statistics,
fills in the datasheets and the README, draws the plots, provides the helpers that `create.py` scripts use to
clean and tokenize a dataset, and runs the tests every repository has to pass.

Each repository used to keep its own copy of this code under `src/dynaword`. With the package installed, a
repository only contains its data, dataset cards and `create.py` scripts, and every repository runs the same
version of the tooling.

### What a dataset repository contains

```text
README.md              # main dataset card; its front matter lists every dataset as a config
CHANGELOG.md
CONTRIBUTING.md
pyproject.toml         # dataset version and the dependency on this package
makefile               # the commands below
dynaword.toml          # corpus-specific settings, see Settings
data/
  dataset_name/
    dataset_name.md    # dataset card
    data.parquet       # the documents
    metadata.parquet   # Propella annotations, one row per document
    create.py          # recreates data.parquet from the source
    descriptive_stats.json   # generated
    images/                  # generated
```

The `pyproject.toml`, `makefile` and `dynaword.toml` a repository needs are in [examples/](examples/).

### Installing dependencies

The repositories use `uv` for environment and dependency management. After installing `uv`, run:

```bash
make install
```

## Adding a new dataset

To add a new dataset create a folder under `data/{dataset_name}/` with a dataset card, `data.parquet`,
`metadata.parquet` and a `create.py`, then register the dataset in the `configs` list of the README front matter.
Guidance on writing the dataset card is in the `CONTRIBUTING.md` of the repository.

### Writing create.py

`create.py` recreates the dataset from its source. Use the shared helpers for the final processing steps:

```py
from dynaword.process_dataset import (
    add_token_count,        # token_count column, Llama 3 tokenizer
    ensure_column_order,    # id, text, source, added, created, token_count
    remove_duplicate_text,
    remove_empty_texts,
)

ds = remove_empty_texts(ds)
ds = remove_duplicate_text(ds)
ds = add_token_count(ds)
ds = ensure_column_order(ds)
ds.to_parquet("data.parquet")
```

Declare the package in the script header so `uv run data/{dataset_name}/create.py` works on its own:

```py
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "datasets>=3.0.0",
#     "dynaword>=0.1",
# ]
# ///
```

Until the package is published, add the `[tool.uv.sources]` entry from [examples/pyproject.toml](examples/pyproject.toml)
to the header as well.

### Updating descriptive statistics

```bash
make update-descriptive-statistics
```

This computes `descriptive_stats.json` and the plots for every dataset that does not have them yet, fills in the
marked sections of its dataset card, and then regenerates the tables, plots and statistics of the main README.
To recompute one dataset after changing it:

```bash
uv run python -m dynaword.update_descriptive_statistics --dataset {dataset_name} --force
```

### Running tests

```bash
make test
```

The tests check that every dataset listed in the README loads, has unique ids, matches the schema, has a
complete dataset card, has matching annotations, and contains no duplicate or one-token documents.
The output is written to `test_results.log`.

### Bumping the version

```bash
make bump-version
```

Bumps the patch version of the dataset in `pyproject.toml` and in the README table.

### Checklist

- [ ] I have run `make test`.
- [ ] I have updated descriptive statistics with `make update-descriptive-statistics` after adding or changing a dataset.
- [ ] I have bumped the version with `make bump-version` if the repo contents changed materially.
- [ ] I have updated `CHANGELOG.md` when appropriate.
- [ ] I have declared any extra `create.py` dependencies in the script header.
- [ ] I have reviewed the generated dataset card, README and plot changes before staging them.

## Settings

Values that differ between corpora live in `dynaword.toml` in the repository root. The file is optional; the
corpus name and its languages are read from the README front matter.

| Key                 | Used for                                                                          | Default                      |
| ------------------- | --------------------------------------------------------------------------------- | ---------------------------- |
| `hub_id`            | Links from dataset cards to the annotations section of the main README            | Relative link to `README.md` |
| `reference_corpora` | Dashed reference lines in the tokens-over-time plot (`name` and `tokens` each)    | No lines                     |
| `license_names`     | Licence names grouped under a generic label in the licence table                  | Built-in list                |
| `removed_sources`   | Folders under `data/` removed on purpose and therefore not listed in the README   | None                         |

See [examples/dynaword.toml](examples/dynaword.toml).

## Frequently asked questions

### Do I need `src/` in the repository?

No. Delete it and add the package as a dependency in `pyproject.toml`, as in [examples/pyproject.toml](examples/pyproject.toml).
The make targets keep their names; only the commands behind them change, see [examples/makefile](examples/makefile).

### Can I run the tooling on a repository from another directory?

Yes. The commands work on the current directory; set `DYNAWORD_REPO` to the path of the repository to work on it from elsewhere.

### How do I develop the tooling itself?

Clone this repository, run `make install`, and try your change against a dataset repository with the commands above.
`make lint` formats and checks the code.

Run `uv run pytest` (or `make test`) for the tooling smoke test. It creates a temporary copy of
`tests/fixtures/dummy_dynaword`, generates six synthetic documents across two sources, and runs
the statistics/plot generation, version bump, and existing corpus validation tests on that copy.
The fixture uses synthetic token counts and annotations, so no models or datasets are downloaded.

The smoke test requires Git and Chrome/Chromium for Kaleido's image export. If a compatible browser
is not already installed, run `uv run plotly_get_chrome`. Generated files stay in the temporary copy.
