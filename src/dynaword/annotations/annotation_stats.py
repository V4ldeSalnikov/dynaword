"""Document counts per annotation level, stored under the "annotations" key of
each source's descriptive_stats.json. Counts add across sources."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Ordinal annotation properties, worst -> best (from the propella-1 framework).
ORDINAL_PROPERTIES = {
    "content_integrity": [
        "severely_degraded",
        "fragment",
        "mostly_complete",
        "complete",
    ],
    "content_ratio": [
        "mostly_navigation",
        "minimal_content",
        "mixed_content",
        "mostly_content",
        "complete_content",
    ],
    "content_length": ["minimal", "brief", "moderate", "substantial"],
    "information_density": ["empty", "thin", "moderate", "adequate", "dense"],
    "content_quality": ["unacceptable", "poor", "adequate", "good", "excellent"],
    "educational_value": ["none", "minimal", "basic", "moderate", "high"],
    "reasoning_indicators": [
        "none",
        "minimal",
        "basic_reasoning",
        "explanatory",
        "analytical",
    ],
    "content_safety": ["illegal", "harmful", "nsfw", "mild_concerns", "safe"],
    "pii_presence": ["contains_pii", "no_pii"],
}


def compute_annotation_stats(source_dir: Path) -> dict | None:
    """Counts per level for one source (None if it has no annotations)."""
    metadata_path = source_dir / "metadata.parquet"
    if not metadata_path.exists():
        return None
    df = pd.read_parquet(metadata_path, columns=list(ORDINAL_PROPERTIES))
    df = df.dropna(how="all")
    if df.empty:
        return None
    return {
        "number_of_annotated_documents": len(df),
        "property_level_counts": {
            prop: df[prop].value_counts().reindex(levels, fill_value=0).to_dict()
            for prop, levels in ORDINAL_PROPERTIES.items()
        },
    }


def sum_annotation_stats(stats: list[dict | None]) -> dict | None:
    """Sum counts across sources, ignoring None entries."""
    stats = [s for s in stats if s is not None]
    if not stats:
        return None
    return {
        "number_of_annotated_documents": sum(
            s["number_of_annotated_documents"] for s in stats
        ),
        "property_level_counts": {
            prop: {
                level: sum(s["property_level_counts"][prop][level] for s in stats)
                for level in levels
            }
            for prop, levels in ORDINAL_PROPERTIES.items()
        },
    }
