# GitLab API helper tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

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
    def test_create_project_includes_namespace_id_when_provided(
        self,
        gitlab_class: object,
    ) -> None:
        project = gitlab_class.return_value.projects.create.return_value  # type: ignore[attr-defined]
        project.id = 1
        project.web_url = "https://gitlab.example.com/group/example-project"
        client = GitLabClient("https://gitlab.example.com", "token")

        client.create_project(
            identifier="example-project",
            display_name="Example Project",
            description="An example project.",
            topics=("example",),
            namespace_id=42,
        )

        gitlab_class.return_value.projects.create.assert_called_once_with(  # type: ignore[attr-defined]
            {
                "name": "Example Project",
                "path": "example-project",
                "description": "An example project.",
                "visibility": "public",
                "topics": ["example"],
                "namespace_id": 42,
            },
        )

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_get_namespace_id_returns_id(self, gitlab_class: object) -> None:
        namespace_obj = gitlab_class.return_value.namespaces.get.return_value  # type: ignore[attr-defined]
        namespace_obj.id = 42
        client = GitLabClient("https://gitlab.example.com", "token")

        namespace_id = client.get_namespace_id("my-group")

        self.assertEqual(namespace_id, 42)
        gitlab_class.return_value.namespaces.get.assert_called_once_with(  # type: ignore[attr-defined]
            "my-group",
        )

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_get_namespace_id_raises_on_error(self, gitlab_class: object) -> None:
        gitlab_class.return_value.namespaces.get.side_effect = (  # type: ignore[attr-defined]
            gitlab.GitlabGetError("not found", response_code=404)
        )
        client = GitLabClient("https://gitlab.example.com", "token")

        with self.assertRaisesRegex(GitLabApiError, 'Unable to query GitLab namespace "my-group"'):
            client.get_namespace_id("my-group")

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

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_project_exists_returns_true_for_matching_project(
        self,
        gitlab_class: object,
    ) -> None:
        project = MagicMock()
        project.path = "example-project"
        project.path_with_namespace = "example/example-project"
        project.attributes = {"marked_for_deletion_at": None}
        gitlab_class.return_value.projects.get.return_value = project  # type: ignore[attr-defined]
        client = GitLabClient("https://gitlab.example.com", "token")

        exists = client.project_exists("example", "example-project")

        self.assertTrue(exists)

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_project_exists_returns_false_for_redirect_target(
        self,
        gitlab_class: object,
    ) -> None:
        project = MagicMock()
        project.path = "renamed-project"
        project.path_with_namespace = "example/renamed-project"
        project.attributes = {}
        gitlab_class.return_value.projects.get.return_value = project  # type: ignore[attr-defined]
        client = GitLabClient("https://gitlab.example.com", "token")

        exists = client.project_exists("example", "example-project")

        self.assertFalse(exists)

    @patch("project_initializer.gitlab_api.gitlab.Gitlab")
    def test_project_exists_returns_false_for_project_marked_for_deletion(
        self,
        gitlab_class: object,
    ) -> None:
        project = MagicMock()
        project.path = "example-project"
        project.path_with_namespace = "example/example-project"
        project.attributes = {"marked_for_deletion_at": "2026-09-13"}
        gitlab_class.return_value.projects.get.return_value = project  # type: ignore[attr-defined]
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
