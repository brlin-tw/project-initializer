# GitLab API helper tests
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import unittest

from project_initializer.gitlab_api import (
    _telegram_integration_attributes,
    build_authenticated_github_push_url,
)


class GitLabApiTests(unittest.TestCase):
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
