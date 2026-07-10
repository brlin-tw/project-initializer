# Command-line interface tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch

from project_initializer.cli import main


class CliTests(unittest.TestCase):
    @patch("project_initializer.cli.initialize_project")
    @patch("project_initializer.cli.describe_dry_run", return_value=[])
    @patch("project_initializer.cli.validate_remote_preconditions")
    @patch("project_initializer.cli.collect_config")
    def test_dry_run_validates_tokens_without_initializing_project(
        self,
        collect_config: object,
        validate_remote_preconditions: object,
        _describe_dry_run: object,
        initialize_project: object,
    ) -> None:
        config = collect_config.return_value  # type: ignore[attr-defined]

        result = main(["--dry-run"])

        self.assertEqual(result, 0)
        validate_remote_preconditions.assert_called_once_with(  # type: ignore[attr-defined]
            config,
        )
        initialize_project.assert_not_called()  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
