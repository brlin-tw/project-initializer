# GitLab API automation
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import gitlab


class GitLabApiError(RuntimeError):
    """Raised when GitLab operations fail."""


@dataclass(frozen=True)
class GitLabProject:
    id: int
    web_url: str


class GitLabClient:
    def __init__(self, url: str, token: str) -> None:
        self.client = gitlab.Gitlab(url, private_token=token)

    def create_project(
        self,
        *,
        identifier: str,
        display_name: str,
        topics: tuple[str, ...],
    ) -> GitLabProject:
        try:
            project = self.client.projects.create(
                {
                    "name": display_name,
                    "path": identifier,
                    "visibility": "public",
                    "topics": list(topics),
                },
            )
        except gitlab.GitlabError as error:
            raise GitLabApiError(
                f"Unable to create GitLab project: {error.error_message}",
            ) from error

        return GitLabProject(id=int(project.id), web_url=str(project.web_url))

    def configure_telegram_integration(
        self,
        project_id: int,
        *,
        bot_token: str,
        chat_id: str,
    ) -> None:
        project = self.client.projects.get(project_id)
        integration = project.integrations.get("telegram", lazy=True)

        for key, value in _telegram_integration_attributes(
            bot_token=bot_token,
            chat_id=chat_id,
        ).items():
            setattr(integration, key, value)

        try:
            integration.save()
        except gitlab.GitlabError as error:
            raise GitLabApiError(
                "Unable to configure GitLab Telegram integration: "
                f"{error.error_message}",
            ) from error

    def configure_push_mirror(
        self,
        project_id: int,
        *,
        github_owner: str,
        github_repository: str,
        github_username: str,
        github_mirror_pat: str,
    ) -> None:
        project = self.client.projects.get(project_id)
        mirror_url = build_authenticated_github_push_url(
            owner=github_owner,
            repository=github_repository,
            username=github_username,
            password=github_mirror_pat,
        )
        try:
            project.remote_mirrors.create(
                {
                    "url": mirror_url,
                    "enabled": True,
                    "only_protected_branches": False,
                },
            )
        except gitlab.GitlabError as error:
            raise GitLabApiError(
                f"Unable to configure GitLab push mirror: {error.error_message}",
            ) from error


def build_authenticated_github_push_url(
    *,
    owner: str,
    repository: str,
    username: str,
    password: str,
) -> str:
    escaped_username = quote(username, safe="")
    escaped_password = quote(password, safe="")
    return (
        f"https://{escaped_username}:{escaped_password}"
        f"@github.com/{owner}/{repository}.git"
    )


def _telegram_integration_attributes(
    *,
    bot_token: str,
    chat_id: str,
) -> dict[str, object]:
    return {
        "active": True,
        "token": bot_token,
        "room": chat_id,
        "push_events": True,
        "issues_events": True,
        "confidential_issues_events": True,
        "merge_requests_events": True,
        "tag_push_events": True,
        "note_events": True,
        "confidential_note_events": True,
        "job_events": True,
        "pipeline_events": True,
        "wiki_page_events": True,
        "notify_only_broken_pipelines": False,
        "branches_to_be_notified": "all",
    }
