# Project initialization workflow tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

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
        gitlab_client.validate_token.return_value = "gitlab-owner"
        gitlab_client.project_exists.return_value = False
        gitlab_client.create_project.return_value = GitLabProject(
            id=1,
            web_url="https://gitlab.com/example/example-project",
        )
        github_client = github_client_class.return_value  # type: ignore[attr-defined]
        github_client.get_authenticated_username.return_value = "example"
        github_client.repository_exists.return_value = False
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

        gitlab_client.validate_token.assert_called_once_with()
        gitlab_client.create_project.assert_called_once_with(
            identifier="example-project",
            display_name="Example Project",
            description="An example project.",
            topics=("example",),
        )
        github_client.create_repository.assert_called_once_with(
            identifier="example-project",
            description="An example project.",
        )
        self.assertEqual(len(progress), 10)
        self.assertIn("TELEGRAM_CHAT_ID_CI", progress[5])
        self.assertIn("TELEGRAM_BOT_API_TOKEN_CI", progress[6])

    @patch("project_initializer.automation.GitHubClient")
    @patch("project_initializer.automation.GitLabClient")
    def test_token_validation_finishes_before_repository_creation(
        self,
        gitlab_client_class: object,
        github_client_class: object,
    ) -> None:
        gitlab_client = gitlab_client_class.return_value  # type: ignore[attr-defined]
        github_client = MagicMock()
        github_client.get_authenticated_username.return_value = "management-owner"
        github_mirror_client = MagicMock()
        github_mirror_client.get_authenticated_username.return_value = "mirror-owner"
        github_client_class.side_effect = [  # type: ignore[attr-defined]
            github_client,
            github_mirror_client,
        ]

        with self.assertRaisesRegex(ValueError, "must belong to the same account"):
            initialize_project(_config())

        gitlab_client.validate_token.assert_called_once_with()
        gitlab_client.create_project.assert_not_called()
        github_client.create_repository.assert_not_called()

    @patch("project_initializer.automation.GitHubClient")
    @patch("project_initializer.automation.GitLabClient")
    def test_existing_projects_are_reported_before_repository_creation(
        self,
        gitlab_client_class: object,
        github_client_class: object,
    ) -> None:
        gitlab_client = gitlab_client_class.return_value  # type: ignore[attr-defined]
        gitlab_client.validate_token.return_value = "gitlab-owner"
        gitlab_client.project_exists.return_value = True
        github_client = github_client_class.return_value  # type: ignore[attr-defined]
        github_client.get_authenticated_username.return_value = "github-owner"
        github_client.repository_exists.return_value = True

        with self.assertRaisesRegex(
            ValueError,
            "already exists in GitLab and GitHub",
        ):
            initialize_project(_config())

        gitlab_client.create_project.assert_not_called()
        github_client.create_repository.assert_not_called()


def _config() -> InitializerConfig:
    return InitializerConfig(
        project=ProjectConfig(
            identifier="example-project",
            display_name="Example Project",
            description="An example project.",
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
