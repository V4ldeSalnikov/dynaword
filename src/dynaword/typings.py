from typing import Literal

DOMAIN = Literal[
    "Books",
    "Conversation",
    "Dialect",
    "Encyclopedic",
    "Legal",
    "Medical",
    "News",
    "Other",
    "Readaloud",
    "Social Media",
    "Speeches",
    "Spoken",
    "Subtitles",
    "Web",
    "Report",
]

LICENSE = Literal["cc0-1.0", "other", "cc-by-sa-4.0", "apache-2.0", "cc-by-4.0"]

LICENSE_NAMES_MAPPING = {
    "cc0-1.0": "CC0",
    "cc-by-sa-4.0": "CC BY-SA 4.0",
    "cc-by-4.0": "CC-BY 4.0",
    "apache-2.0": "Apache 2.0",
}
