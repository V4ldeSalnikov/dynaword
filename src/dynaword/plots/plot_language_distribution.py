import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dynaword.paths import repo_path
from dynaword.tables import create_overview_table

logger = logging.getLogger(__name__)


def plot_language_distribution(df: pd.DataFrame) -> go.Figure:
    """Plot language distribution using a pie chart."""

    # Create pie chart
    fig = px.sunburst(
        df,
        path=["Language", "Source"],
        values="N. Tokens",
        title="Dataset Distribution by Language",
    )
    fig.update_traces(textinfo="label+percent entry")

    return fig


def create_language_distribution_plot():
    logger.info("Creating language distribution plot...")
    df = create_overview_table(
        add_readable_tokens=False, add_total_row=False, add_readme_references=False
    )
    if df.empty:
        logger.warning("No data available for language distribution plot.")
        return

    fig = plot_language_distribution(df)

    save_path = repo_path / "images" / "language_distribution.html"
    save_path_svg = repo_path / "images" / "language_distribution.svg"

    logger.info(f"Saving dataset size plot to {save_path} and {save_path_svg}.")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(save_path)
    fig.write_image(save_path_svg)


if __name__ == "__main__":
    create_language_distribution_plot()
