# Configuration tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import stat
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from project_initializer.config import (
    _prompt_if_missing,
    collect_config,
    load_config_data,
)


class ConfigTests(unittest.TestCase):
    def test_loading_config_restricts_file_permissions_to_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            config_path.write_text("[project]\n", encoding="utf-8")
            config_path.chmod(0o644)

            with self.assertWarnsRegex(
                UserWarning,
                "accessible by group or other users",
            ):
                load_config_data(config_path)

            mode = stat.S_IMODE(config_path.stat().st_mode)

        self.assertEqual(mode, 0o600)

    def test_collects_complete_config_without_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            config_path.write_text(
                textwrap.dedent(
                    """
                    [project]
                    identifier = "example-project"
                    display_name = "Example Project"
                    topics = ["example", "automation"]

                    [gitlab]
                    token = "gitlab-token"

                    [github]
                    token = "github-token"
                    mirror_pat = "mirror-token"

                    [telegram]
                    chat_id = "@example"
                    bot_token = "telegram-token"
                    """,
                ),
                encoding="utf-8",
            )
            config_path.chmod(0o600)

            config = collect_config(config_path, interactive=False)

        self.assertEqual(config.project.identifier, "example-project")
        self.assertEqual(config.project.topics, ("example", "automation"))
        self.assertEqual(config.gitlab.url, "https://gitlab.com")
        self.assertEqual(config.github.api_url, "https://api.github.com")

    def test_reports_missing_values_when_not_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            config_path.write_text("[project]\n", encoding="utf-8")
            config_path.chmod(0o600)

            with self.assertRaisesRegex(ValueError, "Missing required"):
                collect_config(config_path, interactive=False)

    @patch("project_initializer.config.pwinput", return_value="secret-value")
    def test_secret_prompt_masks_input_with_asterisks(self, pwinput: object) -> None:
        value = _prompt_if_missing(None, "Authentication token", secret=True)

        self.assertEqual(value, "secret-value")
        pwinput.assert_called_once_with(  # type: ignore[attr-defined]
            "Please enter your Authentication token: ",
            mask="*",
        )


if __name__ == "__main__":
    unittest.main()
