# Input validation
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import re


PROJECT_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_project_identifier(identifier: str) -> None:
    if not PROJECT_IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(
            "Project identifier must start with an ASCII letter or number and "
            "contain only ASCII letters, numbers, dots, underscores, or dashes.",
        )

    if identifier.endswith(".git"):
        raise ValueError('Project identifier must not end with ".git".')

    if identifier in {".", ".."}:
        raise ValueError("Project identifier must not be a reserved path segment.")


def validate_topics(topics: tuple[str, ...]) -> None:
    if not topics:
        raise ValueError("At least one project topic is required.")

    invalid_topics = [
        topic for topic in topics if not TOPIC_PATTERN.fullmatch(topic)
    ]
    if invalid_topics:
        raise ValueError(
            "Project topics must contain only lowercase English letters, "
            "numbers, and single dashes between words: "
            + ", ".join(invalid_topics),
        )


def validate_display_name(display_name: str) -> None:
    if display_name.strip() == "":
        raise ValueError("Project display name must not be empty.")
