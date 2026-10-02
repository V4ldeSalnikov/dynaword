---
pretty_name: Dummy Dynaword
license: cc0-1.0
license_name: CC0
language:
  - da
domains:
  - Books
  - News
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/*/data.parquet
  - config_name: stories
    data_files:
      - split: train
        path: data/stories/data.parquet
  - config_name: news
    data_files:
      - split: train
        path: data/news/data.parquet
  - config_name: meta
    data_files:
      - split: train
        path: data/*/metadata.parquet
---

# Dummy Dynaword

A synthetic corpus for the smoke test. Run `create.py` to generate its Parquet files.
The test copies this folder to a temporary location before running the workflows.

<!-- START README TABLE -->
| | |
| --- | --- |
| **Version** | 0.1.0 ([Changelog](CHANGELOG.md)) |
<!-- END README TABLE -->

## Dataset Description

<!-- START-SHORT DESCRIPTION -->
Six synthetic Danish documents from two sources.
<!-- END-SHORT DESCRIPTION -->

### Statistics

<!-- START-DESC-STATS -->
<!-- END-DESC-STATS -->

### Sample

<!-- START-SAMPLE -->
<!-- END-SAMPLE -->

### Sources

<!-- START-MAIN TABLE -->
<!-- END-MAIN TABLE -->

### Domains

<!-- START-DOMAIN TABLE -->
<!-- END-DOMAIN TABLE -->

### Licensing

<!-- START-LICENSE TABLE -->
<!-- END-LICENSE TABLE -->

### Languages

<!-- START-LANGUAGE TABLE -->
<!-- END-LANGUAGE TABLE -->

## Additional Information

### Annotations

All annotation values and token counts are synthetic fixture data.
