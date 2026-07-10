# GitHub API client tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from typing import Any

import nacl.encoding
import nacl.public

from project_initializer.github_api import (
    GitHubClient,
    GitHubRepository,
    encrypt_secret,
)


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        payload: dict[str, Any] | None = None,
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.text = text

    def json(self) -> dict[str, Any]:
        if self.payload is None:
            raise ValueError("No JSON payload")
        return self.payload


class FakeSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.requests: list[tuple[str, str, dict[str, Any] | None]] = []
        self.responses: list[FakeResponse] = []

    def get(self, url: str) -> FakeResponse:
        self.requests.append(("GET", url, None))
        return self.responses.pop(0)

    def post(self, url: str, json: dict[str, Any]) -> FakeResponse:
        self.requests.append(("POST", url, json))
        return self.responses.pop(0)

    def patch(self, url: str, json: dict[str, Any]) -> FakeResponse:
        self.requests.append(("PATCH", url, json))
        return self.responses.pop(0)

    def put(self, url: str, json: dict[str, Any]) -> FakeResponse:
        self.requests.append(("PUT", url, json))
        return self.responses.pop(0)


class GitHubApiTests(unittest.TestCase):
    def test_create_repository_uses_empty_public_repo_settings(self) -> None:
        session = FakeSession()
        session.responses.append(
            FakeResponse(
                201,
                {
                    "name": "example-project",
                    "html_url": "https://github.com/example/example-project",
                    "clone_url": "https://github.com/example/example-project.git",
                    "owner": {"login": "example"},
                },
            ),
        )
        client = GitHubClient(
            "https://api.github.com",
            "token",
            session=session,  # type: ignore[arg-type]
        )

        repository = client.create_repository(
            identifier="example-project",
            display_name="Example Project",
        )

        self.assertEqual(repository.owner, "example")
        method, url, payload = session.requests[0]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "https://api.github.com/user/repos")
        self.assertEqual(payload["name"], "example-project")
        self.assertFalse(payload["private"])
        self.assertFalse(payload["has_issues"])
        self.assertFalse(payload["has_projects"])
        self.assertFalse(payload["has_wiki"])
        self.assertFalse(payload["auto_init"])

    def test_actions_variable_creation_falls_back_to_update_on_conflict(self) -> None:
        session = FakeSession()
        session.responses.extend([FakeResponse(409), FakeResponse(204)])
        client = GitHubClient(
            "https://api.github.com",
            "token",
            session=session,  # type: ignore[arg-type]
        )
        repository = GitHubRepository(
            owner="example",
            name="example-project",
            html_url="https://github.com/example/example-project",
            clone_url="https://github.com/example/example-project.git",
        )

        client.set_actions_variable(
            repository,
            name="TELEGRAM_CHAT_ID_CI",
            value="@example",
        )

        self.assertEqual(session.requests[0][0], "POST")
        self.assertEqual(session.requests[1][0], "PATCH")
        self.assertTrue(session.requests[1][1].endswith("/TELEGRAM_CHAT_ID_CI"))

    def test_encrypt_secret_returns_base64_ciphertext(self) -> None:
        private_key = nacl.public.PrivateKey.generate()
        public_key = private_key.public_key.encode(
            encoder=nacl.encoding.Base64Encoder,
        ).decode("utf-8")

        encrypted = encrypt_secret("secret-value", public_key)
        decrypted = nacl.public.SealedBox(private_key).decrypt(
            nacl.encoding.Base64Encoder.decode(encrypted),
        )

        self.assertEqual(decrypted, b"secret-value")


if __name__ == "__main__":
    unittest.main()
