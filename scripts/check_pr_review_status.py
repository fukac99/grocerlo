#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path


def main() -> int:
    args = parse_args()
    changed_files = read_changed_files(args.changed_files_file)

    if is_markdown_only_pr(changed_files):
        print("Markdown-only pull request; review is not required.")
        return 0

    review_status = resolve_review_status(args)

    if review_status != "passed":
        print(
            f"Pull request is not merge-ready: review_status={review_status!r}. "
            "Run the agent review and record `review_status: passed` in the PR body "
            "or provide AGENT_REVIEW_STATUS=passed.",
            file=sys.stderr,
        )
        return 1

    print("Pull request review_status is passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Require non-Markdown pull requests to have review_status passed."
    )
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--pr-url", required=True)
    parser.add_argument("--pr-body-file", type=Path)
    parser.add_argument(
        "--changed-files-file",
        type=Path,
        help="Optional newline-delimited changed-file list. Markdown-only PRs skip review.",
    )
    return parser.parse_args()


def read_changed_files(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def is_markdown_file(path: str) -> bool:
    return Path(path).suffix.casefold() == ".md"


def is_markdown_only_pr(changed_files: list[str]) -> bool:
    return bool(changed_files) and all(is_markdown_file(path) for path in changed_files)


def resolve_review_status(args: argparse.Namespace) -> str:
    env_status = os.environ.get("AGENT_REVIEW_STATUS", "").strip().casefold()
    if env_status:
        return env_status

    if args.pr_body_file and args.pr_body_file.exists():
        body = args.pr_body_file.read_text(encoding="utf-8")
        match = re.search(r"review_status\s*:\s*([A-Za-z_-]+)", body, re.IGNORECASE)
        if match:
            return match.group(1).strip().casefold()

    return "missing"


if __name__ == "__main__":
    raise SystemExit(main())
