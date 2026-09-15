"""
A simple CLI to updates descriptive statistics on all datasets.

Example use:

    uv run  src/dynaword/update_descriptive_statistics.py --dataset wikisource

"""

import argparse
import logging
from pathlib import Path
from typing import cast

import plotly.express as px
from datasets import Dataset, load_dataset

from dynaword.annotations.annotation_stats import compute_annotation_stats
from dynaword.datasheet import DataSheet
from dynaword.descriptive_stats import DescriptiveStatsOverview
from dynaword.paths import repo_path
from dynaword.plots.annotation_profile_plots import (
    add_annotation_profile_section,
    add_corpus_annotation_profile_section,
    plot_annotation_profile,
)
from dynaword.plots.plot_language_distribution import create_language_distribution_plot
from dynaword.plots.plot_tokens_over_time import create_tokens_over_time_plot
from dynaword.plots.plots_dataset_size import create_dataset_size_plot
from dynaword.tables import (
    create_grouped_table_str,
    create_overview_table,
    create_overview_table_str,
)

logger = logging.getLogger(__name__)

main_sheet = DataSheet.load_from_path(repo_path / "README.md")
_datasets = [
    cfg["config_name"]  # type: ignore
    for cfg in main_sheet.frontmatter["configs"]  # type: ignore
    if cfg["config_name"] not in {"default", "meta"}  # type: ignore
]


logger = logging.getLogger(__name__)


def create_domain_distribution_plot(
    save_dir: Path = repo_path,
):
    df = create_overview_table(
        add_readable_tokens=False, add_total_row=False, add_readme_references=False
    )
    if df.empty:
        logger.warning("No data available for domain distribution plot.")
        return

    fig = px.sunburst(df, path=["Domain", "Source"], values="N. Tokens")

    fig.update_traces(textinfo="label+percent entry")
    fig.update_layout(title="Dataset Distribution by Domain and Source")

    img_path = save_dir / "images"
    img_path.mkdir(parents=False, exist_ok=True)
    save_path = img_path / "domain_distribution.png"
    fig.write_image(
        save_path,
        width=800,
        height=800,
        scale=2,
    )


def update_dataset(
    dataset_name: str,
    force: bool = False,
) -> None:
    dataset_path = (
        repo_path / "data" / dataset_name if dataset_name != "default" else repo_path
    )

    if dataset_name == "default":
        readme_name = "README.md"
    else:
        readme_name = f"{dataset_name}.md"

    desc_stats_path = dataset_path / "descriptive_stats.json"
    markdown_path = dataset_path / readme_name

    if desc_stats_path.exists() and force is False:
        logger.info(
            f"descriptive statistics for '{dataset_name}' is already exists (``{desc_stats_path}``), skipping."
        )
        return

    logger.info(f"Updating datasheet for: {dataset_name}")
    sheet = DataSheet.load_from_path(markdown_path)

    if dataset_name != "default":
        ds = load_dataset(str(repo_path), dataset_name, split="train")
        ds = cast(Dataset, ds)
        desc_stats = DescriptiveStatsOverview.from_dataset(ds)
        desc_stats.annotations = compute_annotation_stats(dataset_path)
        sheet.body = sheet.add_dataset_plots(ds, create_plot=True)
        if desc_stats.annotations is not None:
            plot_annotation_profile(
                desc_stats.annotations, sheet.pretty_name, dataset_path
            )
            sheet.body = add_annotation_profile_section(sheet)
    else:
        # compute descriptive stats from existing files
        desc_paths = (repo_path / "data").glob("**/*descriptive_stats.json")
        _desc_stats = [DescriptiveStatsOverview.from_disk(p) for p in desc_paths]
        if _desc_stats:
            desc_stats = sum(_desc_stats[1:], start=_desc_stats[0])
        else:
            desc_stats = DescriptiveStatsOverview(
                number_of_samples=0,
                number_of_tokens=0,
                min_length_tokens=0,
                max_length_tokens=0,
                number_of_characters=0,
                min_length_characters=0,
                max_length_characters=0,
            )
    desc_stats.to_disk(desc_stats_path)

    sheet.body = sheet.add_descriptive_stats(descriptive_stats=desc_stats)
    if dataset_name != "default" or _datasets:
        sheet.body = sheet.add_sample_and_description()
    else:
        sheet.body = sheet.replace_tag(
            package="No sample is available yet because no Faroese source datasets have been added.",
            tag="SAMPLE",
        )

    if dataset_name == "default":
        logger.info("Updating Overview table")
        overview_table = create_overview_table_str()
        sheet.body = sheet.replace_tag(package=overview_table, tag="MAIN TABLE")
        logger.info("Updating domain table")
        domain_table = create_grouped_table_str(group="Domain")
        sheet.body = sheet.replace_tag(package=domain_table, tag="DOMAIN TABLE")
        logger.info("Updating license table")
        domain_table = create_grouped_table_str(group="License")
        sheet.body = sheet.replace_tag(package=domain_table, tag="LICENSE TABLE")
        domain_table = create_grouped_table_str(group="Language")
        sheet.body = sheet.replace_tag(package=domain_table, tag="LANGUAGE TABLE")
        if _datasets:
            create_domain_distribution_plot()
            create_tokens_over_time_plot()
            create_dataset_size_plot()
            create_language_distribution_plot()
            if desc_stats.annotations is not None:
                plot_annotation_profile(
                    desc_stats.annotations, main_sheet.pretty_name, repo_path
                )
                sheet.body = add_corpus_annotation_profile_section(sheet)
        else:
            logger.info("No datasets available; skipping aggregate plot generation.")

    sheet.write_to_path()


def create_parser():
    parser = argparse.ArgumentParser(
        description="Calculated descriptive statistics of the datasets in tha data folder"
    )
    parser.add_argument(
        "--dataset",
        default=None,
        type=str,
        help="Use to specify if you only want to compute the statistics from a singular dataset.",
    )
    parser.add_argument(
        "--logging_level",
        default=20,
        type=int,
        help="Sets the logging level. Default to 20 (INFO), other reasonable levels are 10 (DEBUG) and 30 (WARNING).",
    )
    parser.add_argument(
        "--force",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Should the statistics be forcefully recomputed. By default it checks the difference in commit ids.",
    )
    return parser


def main(
    dataset: str | None = None,
    logging_level: int = 20,
    force: bool = False,
) -> None:
    logging.basicConfig(level=logging_level)

    if dataset:
        update_dataset(dataset, force=force)
    else:
        for dataset_name in _datasets:
            update_dataset(dataset_name, force=force)
        update_dataset("default", force=force)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    main(
        args.dataset,
        logging_level=args.logging_level,
        force=args.force,
    )
