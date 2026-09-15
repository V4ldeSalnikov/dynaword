"""Annotation overview plots (per source and for the full corpus): one stacked
bar per annotation property, drawn from the counts in descriptive_stats.json.

Run as a script to recreate all plots and datasheet sections:

    uv run python src/dynaword/plots/annotation_profile_plots.py
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from dynaword.annotations.annotation_stats import ORDINAL_PROPERTIES
from dynaword.datasheet import DataSheet
from dynaword.descriptive_stats import DescriptiveStatsOverview
from dynaword.paths import data_path, repo_path, settings

logger = logging.getLogger(__name__)

# The binary pii_presence is left out of the plot; it doesn't read as a scale.
PLOT_PROPERTIES = {
    prop: levels
    for prop, levels in ORDINAL_PROPERTIES.items()
    if prop != "pii_presence"
}

PLOT_FILENAME = "annotation_profile.png"
SECTION_TAG = "ANNOTATION PLOTS"
SECTION_HEADER = "### Annotation Overview"
CORPUS_NAME = DataSheet.load_from_path(repo_path / "README.md").pretty_name
ANNOTATION_DOCS_URL = (
    f"https://huggingface.co/datasets/{settings['hub_id']}#annotations"
    if "hub_id" in settings
    else "../../README.md#annotations"
)
SOURCE_SECTION_CONTENT = f"""
Each document comes with annotations describing its content, such as content quality, information density, and educational value.
Each bar shows the share of documents at each level of one annotation, from worst (light) to best (dark).
To learn more about the annotations and how to use them, see the [annotations section]({ANNOTATION_DOCS_URL}) of the main readme.

<p align="center">
<img src="./images/{PLOT_FILENAME}" width="700" style="margin-right: 10px;" />
</p>
"""
CORPUS_SECTION_CONTENT = f"""
Each document in {CORPUS_NAME} comes with annotations describing its content, such as content quality, information density, and educational value.
Each bar shows the share of documents at each level of one annotation, from worst (light) to best (dark).
The same plot is available for every source in its datasheet, and the counts behind it are stored in `descriptive_stats.json` under `annotations`.
To learn more, see the [annotations section](#annotations).

<p align="center">
<img src="./images/{PLOT_FILENAME}" width="700" style="margin-right: 10px;" />
</p>
"""


def _pretty(name: str) -> str:
    """'mostly_complete' -> 'mostly complete'."""
    return name.replace("_", " ")


def plot_annotation_profile(annotations: dict, title: str, save_dir: Path) -> Path:
    """Render the stacked-bar plot for one set of annotation level counts."""
    counts = annotations["property_level_counts"]
    n_docs = annotations["number_of_annotated_documents"]

    properties = list(PLOT_PROPERTIES)[::-1]  # first property at the top
    fig, ax = plt.subplots(figsize=(9, 0.5 * len(properties) + 1.2))
    for y, prop in enumerate(properties):
        levels = PLOT_PROPERTIES[prop]
        total = sum(counts[prop].values())
        colors = plt.cm.Reds(np.linspace(0.15, 0.9, len(levels)))
        left = 0.0
        for level, color in zip(levels, colors):
            pct = 100 * counts[prop][level] / total if total else 0.0
            ax.barh(y, pct, left=left, color=color, edgecolor="white", linewidth=0.8)
            if pct >= 7:  # label only segments wide enough to hold text
                dark_bg = color[:3] @ [0.3, 0.6, 0.1] < 0.5
                ax.text(
                    left + pct / 2,
                    y,
                    f"{_pretty(level)}\n{pct:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="white" if dark_bg else "#333333",
                )
            left += pct
    ax.set_yticks(
        range(len(properties)),
        [_pretty(p).capitalize() for p in properties],
        fontsize=9,
    )
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of documents (light = lowest rating, dark = highest)", fontsize=8)
    ax.set_title(f"{title}  ({n_docs:,} documents)", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    image_dir = save_dir / "images"
    image_dir.mkdir(exist_ok=True)
    save_path = image_dir / PLOT_FILENAME
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    return save_path


def load_annotation_stats(source_dir: Path) -> dict | None:
    """Stored annotation counts for a source, None if it has none."""
    stats_path = source_dir / "descriptive_stats.json"
    if not stats_path.exists():
        return None
    return DescriptiveStatsOverview.from_disk(stats_path).annotations


def _ensure_section(sheet: DataSheet, anchor: str, before: bool = False) -> None:
    """Make sure the datasheet body contains the annotation section markers."""
    tag_start = f"<!-- START-{SECTION_TAG} -->"
    if tag_start in sheet.body:
        return
    section = f"\n\n{SECTION_HEADER}\n{tag_start}\n<!-- END-{SECTION_TAG} -->\n"
    if anchor in sheet.body:
        replacement = f"{section}\n{anchor}" if before else f"{anchor}{section}"
        sheet.body = sheet.body.replace(anchor, replacement, 1)
    else:
        sheet.body += section


def add_annotation_profile_section(sheet: DataSheet) -> str:
    """Insert or update the annotation section of a source datasheet."""
    _ensure_section(sheet, anchor="<!-- END-DATASET PLOTS -->")
    return sheet.replace_tag(package=SOURCE_SECTION_CONTENT, tag=SECTION_TAG)


def add_corpus_annotation_profile_section(sheet: DataSheet) -> str:
    """Insert or update the annotation section of the main README."""
    _ensure_section(sheet, anchor="### Licensing", before=True)
    return sheet.replace_tag(package=CORPUS_SECTION_CONTENT, tag=SECTION_TAG)


def main() -> None:
    for source_dir in sorted(p for p in data_path.iterdir() if p.is_dir()):
        annotations = load_annotation_stats(source_dir)
        if annotations is None:
            logger.warning(f"{source_dir.name}: no annotations, skipping.")
            continue
        sheet = DataSheet.load_from_path(source_dir / f"{source_dir.name}.md")
        plot_annotation_profile(annotations, sheet.pretty_name, source_dir)
        sheet.body = add_annotation_profile_section(sheet)
        sheet.write_to_path()
        logger.info(f"{source_dir.name}: wrote {PLOT_FILENAME} and updated datasheet.")

    corpus_annotations = DescriptiveStatsOverview.from_disk(
        repo_path / "descriptive_stats.json"
    ).annotations
    if corpus_annotations is not None:
        plot_annotation_profile(corpus_annotations, CORPUS_NAME, repo_path)
        sheet = DataSheet.load_from_path(repo_path / "README.md")
        sheet.body = add_corpus_annotation_profile_section(sheet)
        sheet.write_to_path()
        logger.info(f"corpus: wrote {PLOT_FILENAME} and updated README.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
