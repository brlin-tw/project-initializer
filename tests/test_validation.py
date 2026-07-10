# Validation tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest

from project_initializer.validation import (
    validate_description,
    validate_display_name,
    validate_project_identifier,
    validate_topics,
)


class ValidationTests(unittest.TestCase):
    def test_accepts_valid_project_identifier(self) -> None:
        validate_project_identifier("project.initializer_1")

    def test_rejects_invalid_project_identifier(self) -> None:
        with self.assertRaises(ValueError):
            validate_project_identifier("-project")

    def test_rejects_git_suffix_project_identifier(self) -> None:
        with self.assertRaises(ValueError):
            validate_project_identifier("project.git")

    def test_accepts_valid_topics(self) -> None:
        validate_topics(("project-initializer", "ci", "gitlab2"))

    def test_rejects_invalid_topics(self) -> None:
        with self.assertRaises(ValueError):
            validate_topics(("Project", "bad_topic"))

    def test_rejects_empty_display_name(self) -> None:
        with self.assertRaises(ValueError):
            validate_display_name("   ")

    def test_rejects_empty_description(self) -> None:
        with self.assertRaises(ValueError):
            validate_description("   ")


if __name__ == "__main__":
    unittest.main()
