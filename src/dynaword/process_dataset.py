""""""

import logging
from functools import partial
from typing import Any

from datasets import Dataset
from transformers import AutoTokenizer

from dynaword.dataset_structure import COLUMN_ORDER, ColumnNames

logger = logging.getLogger(__name__)

# TODO: Add a step to compute the size categories and update the frontmatter


def _tokenize_function(
    examples: dict[str, Any], tokenizer: AutoTokenizer
) -> dict[str, Any]:
    encodings = tokenizer(
        examples["text"],
        padding=False,
        truncation=False,
        return_length=True,  # much faster, avoids storing all IDs
    )  # type: ignore
    return {"token_count": encodings["length"]}


def add_token_count(
    ds: Dataset,
    tokenizer_name: str = "AI-Sweden-Models/Llama-3-8B-instruct",
    num_proc: int = 4,
) -> Dataset:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)

    tokenize = partial(_tokenize_function, tokenizer=tokenizer)  # type: ignore

    ds = ds.map(tokenize, batched=True, num_proc=num_proc)
    return ds


def _filter_duplicates(example: dict[str, Any], seen_set: set) -> bool:
    if example[ColumnNames.text.value] in seen_set:
        return False
    seen_set.add(example[ColumnNames.text.value])
    return True


def remove_duplicate_text(ds: Dataset) -> Dataset:
    logger.info("Removing duplicate texts")
    seen_texts = set()
    len_ds = len(ds)
    ds = ds.filter(
        partial(_filter_duplicates, seen_set=seen_texts),
        desc="Removing duplicates",
        num_proc=1,  # num_proc=1 to ensure seen_set is consistent
    )
    logger.info(f"Filtered {len_ds - len(ds)} duplicate examples")
    return ds


def _filter_empty(example: dict[str, Any]) -> bool:
    return len(example[ColumnNames.text.value].strip()) > 0


def remove_empty_texts(ds: Dataset, num_proc: int = 4) -> Dataset:
    logger.info("Removing empty texts")
    len_ds = len(ds)
    ds = ds.filter(_filter_empty, num_proc=num_proc, desc="Removing empty texts")
    logger.info(f"Filtered {len_ds - len(ds)} empty examples")

    return ds


def ensure_column_order(ds: Dataset) -> Dataset:
    logger.info("Ensuring columns are in the correct order and are present")
    ds = ds.select_columns(COLUMN_ORDER)
    return ds
