from dynaword.datasheet import DataSheet
from dynaword.paths import readme_path

main_sheet = DataSheet.load_from_path(readme_path)

DATASET_NAMES = [
    cfg["config_name"]
    for cfg in main_sheet.frontmatter["configs"]
    if cfg["config_name"] not in {"default", "meta"}
]
