# Project initialization workflow
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from project_initializer.config import InitializerConfig
from project_initializer.github_api import GitHubClient, GitHubRepository
from project_initializer.gitlab_api import GitLabClient, GitLabProject
from project_initializer.validation import (
    validate_display_name,
    validate_project_identifier,
    validate_topics,
)


@dataclass(frozen=True)
class InitializationResult:
    gitlab_project_url: str
    github_repository_url: str


ProgressReporter = Callable[[str], None]


def validate_config(config: InitializerConfig) -> None:
    validate_project_identifier(config.project.identifier)
    validate_display_name(config.project.display_name)
    validate_topics(config.project.topics)


def initialize_project(
    config: InitializerConfig,
    *,
    progress: ProgressReporter | None = None,
) -> InitializationResult:
    _report_progress(progress, "Validating configuration.")
    validate_config(config)

    gitlab_client = GitLabClient(config.gitlab.url, config.gitlab.token)
    github_client = GitHubClient(config.github.api_url, config.github.token)
    github_mirror_client = GitHubClient(
        config.github.api_url,
        config.github.mirror_pat,
    )

    _report_progress(progress, "Validating GitLab and GitHub access tokens.")
    gitlab_client.validate_token()
    github_username = github_client.get_authenticated_username()
    github_mirror_username = github_mirror_client.get_authenticated_username()
    if github_mirror_username != github_username:
        raise ValueError(
            "The GitHub repository management and mirroring tokens must belong "
            "to the same account.",
        )
    _report_progress(
        progress,
        f"Creating GitLab project {config.project.identifier}.",
    )
    gitlab_project = gitlab_client.create_project(
        identifier=config.project.identifier,
        display_name=config.project.display_name,
        topics=config.project.topics,
    )
    _report_progress(
        progress,
        f"Creating GitHub repository {config.project.identifier}.",
    )
    github_repository = github_client.create_repository(
        identifier=config.project.identifier,
        display_name=config.project.display_name,
    )

    _configure_github_repository(
        github_client=github_client,
        repository=github_repository,
        gitlab_project=gitlab_project,
        config=config,
        progress=progress,
    )
    _configure_gitlab_project(
        gitlab_client=gitlab_client,
        gitlab_project=gitlab_project,
        github_repository=github_repository,
        github_username=github_username,
        config=config,
        progress=progress,
    )

    return InitializationResult(
        gitlab_project_url=gitlab_project.web_url,
        github_repository_url=github_repository.html_url,
    )


def describe_dry_run(config: InitializerConfig) -> list[str]:
    validate_config(config)
    return [
        "Validate project identifier, display name, and topics.",
        f"Create public GitLab project {config.project.identifier}.",
        "Configure GitLab Telegram integration with all supported triggers.",
        "Create public empty GitHub repository "
        f"{config.project.identifier} with issues, projects, wiki, and pull "
        "requests disabled.",
        "Replace GitHub repository topics.",
        "Create or update GitHub Actions repository variable "
        "TELEGRAM_CHAT_ID_CI.",
        "Create or update GitHub Actions repository secret "
        "TELEGRAM_BOT_API_TOKEN_CI.",
        "Configure GitLab push mirror to the GitHub repository.",
        "Set GitHub repository homepage to the GitLab project URL.",
    ]


def _configure_github_repository(
    *,
    github_client: GitHubClient,
    repository: GitHubRepository,
    gitlab_project: GitLabProject,
    config: InitializerConfig,
    progress: ProgressReporter | None,
) -> None:
    _report_progress(progress, "Replacing GitHub repository topics.")
    github_client.replace_topics(repository, config.project.topics)
    _report_progress(
        progress,
        "Creating or updating GitHub Actions variable TELEGRAM_CHAT_ID_CI.",
    )
    github_client.set_actions_variable(
        repository,
        name="TELEGRAM_CHAT_ID_CI",
        value=config.telegram.chat_id,
    )
    _report_progress(
        progress,
        "Creating or updating GitHub Actions secret "
        "TELEGRAM_BOT_API_TOKEN_CI.",
    )
    github_client.set_actions_secret(
        repository,
        name="TELEGRAM_BOT_API_TOKEN_CI",
        value=config.telegram.bot_token,
    )
    _report_progress(progress, "Updating GitHub repository details.")
    github_client.update_repository_details(
        repository,
        homepage=gitlab_project.web_url,
    )


def _configure_gitlab_project(
    *,
    gitlab_client: GitLabClient,
    gitlab_project: GitLabProject,
    github_repository: GitHubRepository,
    github_username: str,
    config: InitializerConfig,
    progress: ProgressReporter | None,
) -> None:
    _report_progress(progress, "Configuring GitLab Telegram integration.")
    gitlab_client.configure_telegram_integration(
        gitlab_project.id,
        bot_token=config.telegram.bot_token,
        chat_id=config.telegram.chat_id,
    )
    _report_progress(progress, "Configuring GitLab push mirror.")
    gitlab_client.configure_push_mirror(
        gitlab_project.id,
        github_owner=github_repository.owner,
        github_repository=github_repository.name,
        github_username=github_username,
        github_mirror_pat=config.github.mirror_pat,
    )


def _report_progress(
    progress: ProgressReporter | None,
    operation: str,
) -> None:
    if progress is not None:
        progress(operation)
