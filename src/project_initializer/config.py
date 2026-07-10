# Configuration loading and prompting helpers
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pwinput import pwinput

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only used on Python < 3.11
    import tomli as tomllib


DEFAULT_CONFIG_PATH = Path(".project-initializer.toml")
DEFAULT_GITLAB_URL = "https://gitlab.com"
DEFAULT_GITHUB_API_URL = "https://api.github.com"


@dataclass(frozen=True)
class ProjectConfig:
    identifier: str
    display_name: str
    topics: tuple[str, ...]


@dataclass(frozen=True)
class GitLabConfig:
    url: str
    token: str


@dataclass(frozen=True)
class GitHubConfig:
    api_url: str
    token: str
    mirror_pat: str


@dataclass(frozen=True)
class TelegramConfig:
    chat_id: str
    bot_token: str


@dataclass(frozen=True)
class InitializerConfig:
    project: ProjectConfig
    gitlab: GitLabConfig
    github: GitHubConfig
    telegram: TelegramConfig


def load_config_data(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("rb") as config_file:
        loaded = tomllib.load(config_file)

    if not isinstance(loaded, dict):
        raise ValueError("The configuration file root must be a TOML table.")

    return loaded


def collect_config(path: Path, *, interactive: bool = True) -> InitializerConfig:
    data = load_config_data(path)

    project = _table(data, "project")
    gitlab = _table(data, "gitlab")
    github = _table(data, "github")
    telegram = _table(data, "telegram")

    identifier = _value(project, "identifier")
    display_name = _value(project, "display_name")
    topics = project.get("topics")

    gitlab_url = str(gitlab.get("url", DEFAULT_GITLAB_URL))
    gitlab_token = _value(gitlab, "token")
    github_api_url = str(github.get("api_url", DEFAULT_GITHUB_API_URL))
    github_token = _value(github, "token")
    github_mirror_pat = _value(github, "mirror_pat")
    telegram_chat_id = _value(telegram, "chat_id")
    telegram_bot_token = _value(telegram, "bot_token")

    if interactive:
        identifier = _prompt_if_missing(identifier, "Project identifier")
        display_name = _prompt_if_missing(display_name, "Project display name")
        topics = _prompt_topics_if_missing(topics)
        gitlab_token = _prompt_if_missing(
            gitlab_token,
            "GitLab authentication token",
            secret=True,
        )
        github_token = _prompt_if_missing(
            github_token,
            "GitHub authentication token",
            secret=True,
        )
        github_mirror_pat = _prompt_if_missing(
            github_mirror_pat,
            "GitHub personal access token for repository mirroring",
            secret=True,
        )
        telegram_chat_id = _prompt_if_missing(
            telegram_chat_id,
            "Telegram channel/group identifier",
        )
        telegram_bot_token = _prompt_if_missing(
            telegram_bot_token,
            "Telegram bot token",
            secret=True,
        )

    missing = _missing_values(
        {
            "project.identifier": identifier,
            "project.display_name": display_name,
            "project.topics": topics,
            "gitlab.token": gitlab_token,
            "github.token": github_token,
            "github.mirror_pat": github_mirror_pat,
            "telegram.chat_id": telegram_chat_id,
            "telegram.bot_token": telegram_bot_token,
        },
    )
    if missing:
        raise ValueError(
            "Missing required configuration values: " + ", ".join(missing),
        )

    return InitializerConfig(
        project=ProjectConfig(
            identifier=str(identifier),
            display_name=str(display_name),
            topics=_normalize_topics(topics),
        ),
        gitlab=GitLabConfig(url=gitlab_url, token=str(gitlab_token)),
        github=GitHubConfig(
            api_url=github_api_url.rstrip("/"),
            token=str(github_token),
            mirror_pat=str(github_mirror_pat),
        ),
        telegram=TelegramConfig(
            chat_id=str(telegram_chat_id),
            bot_token=str(telegram_bot_token),
        ),
    )


def _table(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"The [{name}] configuration value must be a table.")

    return value


def _value(table: dict[str, Any], name: str) -> Any | None:
    value = table.get(name)
    if value == "":
        return None

    return value


def _prompt_if_missing(value: Any | None, label: str, *, secret: bool = False) -> str:
    if value not in (None, ""):
        return str(value)

    prompt = f"Please enter your {label}: "
    if secret:
        return pwinput(prompt, mask="*")

    return input(prompt)


def _prompt_topics_if_missing(value: Any | None) -> Any:
    if value not in (None, ""):
        return value

    raw_topics = input("Project topic tags, comma-separated: ")
    return [topic.strip() for topic in raw_topics.split(",") if topic.strip()]


def _missing_values(values: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for name, value in values.items():
        if value in (None, ""):
            missing.append(name)
        elif name == "project.topics" and _normalize_topics(value) == ():
            missing.append(name)

    return missing


def _normalize_topics(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        topics = [topic.strip() for topic in value.split(",")]
    elif isinstance(value, list | tuple):
        topics = [str(topic).strip() for topic in value]
    else:
        raise ValueError("project.topics must be a list or comma-separated string.")

    return tuple(topic for topic in topics if topic)
