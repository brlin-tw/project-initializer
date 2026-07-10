# GitLab API helper tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch

import gitlab

from project_initializer.gitlab_api import (
    GitLabApiError,
    GitLabClient,
    _telegram_integration_attributes,
    build_authenticated_github_push_url,
)


class GitLabApiTests(unittest.TestCase):
    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_create_project_sets_description(self, gitlab_class: object) -> None:
        project = gitlab_class.return_value.projects.create.return_value  # type: ignore[attr-defined]
        project.id = 1
        project.web_url = "https://gitlab.example.com/example/example-project"
        client = GitLabClient("https://gitlab.example.com", "token")

        client.create_project(
            identifier="example-project",
            display_name="Example Project",
            description="An example project.",
            topics=("example",),
        )

        gitlab_class.return_value.projects.create.assert_called_once_with(  # type: ignore[attr-defined]
            {
                "name": "Example Project",
                "path": "example-project",
                "description": "An example project.",
                "visibility": "public",
                "topics": ["example"],
            },
        )

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_validate_token_accepts_active_token(self, gitlab_class: object) -> None:
        client = GitLabClient("https://gitlab.example.com", "token")
        gitlab_class.return_value.http_get.side_effect = [  # type: ignore[attr-defined]
            {"active": True},
            {"username": "example"},
        ]

        username = client.validate_token()

        self.assertEqual(username, "example")
        self.assertEqual(  # type: ignore[attr-defined]
            gitlab_class.return_value.http_get.call_args_list[1].args,
            ("/user",),
        )

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_validate_token_rejects_inactive_token(self, gitlab_class: object) -> None:
        client = GitLabClient("https://gitlab.example.com", "token")
        gitlab_class.return_value.http_get.return_value = {  # type: ignore[attr-defined]
            "active": False,
        }

        with self.assertRaisesRegex(GitLabApiError, "token is inactive"):
            client.validate_token()

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_project_exists_returns_false_for_not_found(
        self,
        gitlab_class: object,
    ) -> None:
        gitlab_class.return_value.projects.get.side_effect = (  # type: ignore[attr-defined]
            gitlab.GitlabGetError("not found", response_code=404)
        )
        client = GitLabClient("https://gitlab.example.com", "token")

        exists = client.project_exists("example", "example-project")

        self.assertFalse(exists)

    def test_telegram_integration_enables_incident_and_vulnerability_events(
        self,
    ) -> None:
        attributes = _telegram_integration_attributes(
            bot_token="bot-token",
            chat_id="@example",
        )

        self.assertIs(attributes["incident_events"], True)
        self.assertIs(attributes["vulnerability_events"], True)

    def test_build_authenticated_github_push_url_escapes_credentials(self) -> None:
        url = build_authenticated_github_push_url(
            owner="owner",
            repository="repo",
            username="user@example.com",
            password="pat:value/with-symbols",
        )

        self.assertEqual(
            url,
            "https://user%40example.com:pat%3Avalue%2Fwith-symbols"
            "@github.com/owner/repo.git",
        )


if __name__ == "__main__":
    unittest.main()
