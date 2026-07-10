# Telegram Bot API client tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest
from typing import Any

import requests

from project_initializer.telegram_api import TelegramApiError, TelegramClient


class FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload

    def json(self) -> Any:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.urls: list[str] = []

    def get(self, url: str) -> FakeResponse:
        self.urls.append(url)
        return self.response


class FailingSession:
    def get(self, url: str) -> FakeResponse:
        raise requests.ConnectionError(f"Unable to connect to {url}")


class TelegramApiTests(unittest.TestCase):
    def test_validate_token_uses_get_me(self) -> None:
        session = FakeSession(
            FakeResponse(200, {"ok": True, "result": {"is_bot": True}}),
        )
        client = TelegramClient("123:token", session=session)  # type: ignore[arg-type]

        client.validate_token()

        self.assertEqual(
            session.urls,
            ["https://api.telegram.org/bot123:token/getMe"],
        )

    def test_validate_token_reports_api_error(self) -> None:
        session = FakeSession(
            FakeResponse(401, {"ok": False, "description": "Unauthorized"}),
        )
        client = TelegramClient("bad-token", session=session)  # type: ignore[arg-type]

        with self.assertRaisesRegex(TelegramApiError, "401: Unauthorized"):
            client.validate_token()

    def test_validate_token_does_not_expose_token_on_network_error(self) -> None:
        client = TelegramClient(  # type: ignore[arg-type]
            "secret-token",
            session=FailingSession(),
        )

        with self.assertRaises(TelegramApiError) as raised:
            client.validate_token()

        self.assertNotIn("secret-token", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
