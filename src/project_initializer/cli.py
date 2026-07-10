# Command-line interface
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from project_initializer.automation import describe_dry_run, initialize_project
from project_initializer.config import DEFAULT_CONFIG_PATH, collect_config


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        config = collect_config(
            args.config,
            interactive=not args.no_interactive,
        )
        if args.dry_run:
            for operation in describe_dry_run(config):
                print(f"- {operation}")
            return 0

        result = initialize_project(config, progress=_print_progress)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("Project initialization completed.")
    print(f"GitLab project: {result.gitlab_project_url}")
    print(f"GitHub repository: {result.github_repository_url}")
    return 0


def _print_progress(operation: str) -> None:
    print(operation, flush=True)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create and configure matching GitLab and GitHub projects.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=(
            "Path to the TOML configuration file "
            f"(default: {DEFAULT_CONFIG_PATH})."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input and print planned operations without API calls.",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Do not prompt for missing configuration values.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
