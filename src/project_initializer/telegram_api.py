# Telegram Bot API client
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from typing import Any

import requests


TELEGRAM_BOT_API_URL = "https://api.telegram.org"


class TelegramApiError(RuntimeError):
    """Raised when the Telegram Bot API returns an unexpected response."""


class TelegramClient:
    def __init__(
        self,
        token: str,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.token = token
        self.session = session or requests.Session()

    def validate_token(self) -> None:
        try:
            response = self.session.get(
                f"{TELEGRAM_BOT_API_URL}/bot{self.token}/getMe",
            )
        except requests.RequestException as error:
            raise TelegramApiError(
                "Unable to validate Telegram bot token: "
                "unable to reach the Telegram API.",
            ) from error

        try:
            data = response.json()
        except ValueError as error:
            raise TelegramApiError(
                "Unable to validate Telegram bot token: "
                "Telegram API returned an unexpected response.",
            ) from error

        if not isinstance(data, dict):
            raise TelegramApiError(
                "Unable to validate Telegram bot token: "
                "Telegram API returned an unexpected response.",
            )

        if response.status_code != 200 or data.get("ok") is not True:
            description = data.get("description", "unexpected response")
            raise TelegramApiError(
                f"Unable to validate Telegram bot token: "
                f"Telegram API returned {response.status_code}: {description}",
            )

        result = data.get("result")
        if not isinstance(result, dict) or result.get("is_bot") is not True:
            raise TelegramApiError(
                "Unable to validate Telegram bot token: "
                "Telegram API returned an unexpected response.",
            )
