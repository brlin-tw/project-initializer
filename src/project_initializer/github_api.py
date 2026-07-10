# GitHub REST API client
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import nacl.encoding
import nacl.public
import requests


GITHUB_API_VERSION = "2026-03-10"


class GitHubApiError(RuntimeError):
    """Raised when the GitHub API returns an unexpected response."""


@dataclass(frozen=True)
class GitHubRepository:
    owner: str
    name: str
    html_url: str
    clone_url: str


class GitHubClient:
    def __init__(
        self,
        api_url: str,
        token: str,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
        )

    def get_authenticated_username(self) -> str:
        response = self.session.get(f"{self.api_url}/user")
        data = self._expect_json(response, {200}, "query GitHub user")
        return str(data["login"])

    def repository_exists(self, owner: str, repository: str) -> bool:
        response = self.session.get(f"{self.api_url}/repos/{owner}/{repository}")
        if response.status_code == 404:
            return False

        self._expect_status(response, {200}, "check whether GitHub repository exists")
        return True

    def create_repository(
        self,
        *,
        identifier: str,
        description: str,
    ) -> GitHubRepository:
        payload = {
            "name": identifier,
            "description": description,
            "private": False,
            "has_issues": False,
            "has_projects": False,
            "has_wiki": False,
            "has_pull_requests": False,
            "auto_init": False,
            "has_downloads": True,
        }
        response = self.session.post(f"{self.api_url}/user/repos", json=payload)
        data = self._expect_json(response, {201}, "create GitHub repository")
        owner = str(data["owner"]["login"])
        return GitHubRepository(
            owner=owner,
            name=str(data["name"]),
            html_url=str(data["html_url"]),
            clone_url=str(data["clone_url"]),
        )

    def update_repository_details(
        self,
        repository: GitHubRepository,
        *,
        homepage: str,
    ) -> None:
        payload = {
            "homepage": homepage,
            "has_issues": False,
            "has_projects": False,
            "has_wiki": False,
            "has_pull_requests": False,
            "has_downloads": True,
        }
        response = self.session.patch(
            self._repository_url(repository),
            json=payload,
        )
        self._expect_status(response, {200}, "update GitHub repository details")

    def replace_topics(
        self,
        repository: GitHubRepository,
        topics: tuple[str, ...],
    ) -> None:
        response = self.session.put(
            f"{self._repository_url(repository)}/topics",
            json={"names": list(topics)},
        )
        self._expect_status(response, {200}, "replace GitHub repository topics")

    def set_actions_variable(
        self,
        repository: GitHubRepository,
        *,
        name: str,
        value: str,
    ) -> None:
        url = f"{self._repository_url(repository)}/actions/variables"
        response = self.session.post(url, json={"name": name, "value": value})
        if response.status_code == 409:
            response = self.session.patch(
                f"{url}/{name}",
                json={"name": name, "value": value},
            )
            self._expect_status(
                response,
                {204},
                f"update GitHub Actions variable {name}",
            )
            return

        self._expect_status(
            response,
            {201},
            f"create GitHub Actions variable {name}",
        )

    def set_actions_secret(
        self,
        repository: GitHubRepository,
        *,
        name: str,
        value: str,
    ) -> None:
        key_response = self.session.get(
            f"{self._repository_url(repository)}/actions/secrets/public-key",
        )
        key_data = self._expect_json(
            key_response,
            {200},
            "query GitHub Actions secrets public key",
        )
        encrypted_value = encrypt_secret(value, str(key_data["key"]))
        response = self.session.put(
            f"{self._repository_url(repository)}/actions/secrets/{name}",
            json={
                "encrypted_value": encrypted_value,
                "key_id": str(key_data["key_id"]),
            },
        )
        self._expect_status(
            response,
            {201, 204},
            f"create or update GitHub Actions secret {name}",
        )

    def _repository_url(self, repository: GitHubRepository) -> str:
        return f"{self.api_url}/repos/{repository.owner}/{repository.name}"

    def _expect_json(
        self,
        response: requests.Response,
        expected_statuses: set[int],
        operation: str,
    ) -> dict[str, Any]:
        self._expect_status(response, expected_statuses, operation)
        data = response.json()
        if not isinstance(data, dict):
            raise GitHubApiError(f"Unable to {operation}: unexpected JSON response.")

        return data

    def _expect_status(
        self,
        response: requests.Response,
        expected_statuses: set[int],
        operation: str,
    ) -> None:
        if response.status_code in expected_statuses:
            return

        message = _response_message(response)
        raise GitHubApiError(
            f"Unable to {operation}: GitHub API returned "
            f"{response.status_code}: {message}",
        )


def encrypt_secret(secret_value: str, public_key: str) -> str:
    public_key_object = nacl.public.PublicKey(
        public_key.encode("utf-8"),
        nacl.encoding.Base64Encoder(),
    )
    sealed_box = nacl.public.SealedBox(public_key_object)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def _response_message(response: requests.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text

    if isinstance(data, dict) and "message" in data:
        return str(data["message"])

    return str(data)
