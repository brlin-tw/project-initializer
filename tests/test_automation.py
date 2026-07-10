# Project initialization workflow tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch

from project_initializer.automation import initialize_project
from project_initializer.config import (
    GitHubConfig,
    GitLabConfig,
    InitializerConfig,
    ProjectConfig,
    TelegramConfig,
)
from project_initializer.github_api import GitHubRepository
from project_initializer.gitlab_api import GitLabProject


class AutomationTests(unittest.TestCase):
    @patch("project_initializer.automation.GitHubClient")
    @patch("project_initializer.automation.GitLabClient")
    def test_initialize_project_reports_each_operation(
        self,
        gitlab_client_class: object,
        github_client_class: object,
    ) -> None:
        gitlab_client = gitlab_client_class.return_value  # type: ignore[attr-defined]
        gitlab_client.create_project.return_value = GitLabProject(
            id=1,
            web_url="https://gitlab.com/example/example-project",
        )
        github_client = github_client_class.return_value  # type: ignore[attr-defined]
        github_client.get_authenticated_username.return_value = "example"
        github_client.create_repository.return_value = GitHubRepository(
            owner="example",
            name="example-project",
            html_url="https://github.com/example/example-project",
            clone_url="https://github.com/example/example-project.git",
        )
        progress: list[str] = []

        initialize_project(
            _config(),
            progress=progress.append,
        )

        self.assertEqual(len(progress), 10)
        self.assertIn("TELEGRAM_CHAT_ID_CI", progress[5])
        self.assertIn("TELEGRAM_BOT_API_TOKEN_CI", progress[6])


def _config() -> InitializerConfig:
    return InitializerConfig(
        project=ProjectConfig(
            identifier="example-project",
            display_name="Example Project",
            topics=("example",),
        ),
        gitlab=GitLabConfig(url="https://gitlab.com", token="gitlab-token"),
        github=GitHubConfig(
            api_url="https://api.github.com",
            token="github-token",
            mirror_pat="mirror-token",
        ),
        telegram=TelegramConfig(chat_id="@example", bot_token="bot-token"),
    )


if __name__ == "__main__":
    unittest.main()
