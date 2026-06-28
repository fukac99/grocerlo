#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


def main() -> int:
    args = parse_args()
    rows = parse_task_rows(args.tasks_file)
    matching_rows = [
        row
        for row in rows
        if row.get("branch") == args.head_ref or row.get("pull_request") == args.pr_url
    ]

    if not matching_rows:
        print(
            "No LOOP_TASKS.md row found for this pull request. "
            f"Expected branch={args.head_ref!r} or pull_request={args.pr_url!r}.",
            file=sys.stderr,
        )
        return 1

    row = matching_rows[0]
    review_status = row.get("review_status", "").strip().casefold()
    task_id = row.get("id", "<unknown>")

    if review_status != "passed":
        print(
            f"Task {task_id} is not merge-ready: review_status={review_status!r}. "
            "Run the agent review and update the same task row to review_status: passed.",
            file=sys.stderr,
        )
        return 1

    print(f"Task {task_id} review_status is passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Require the current pull request task row to have review_status passed."
    )
    parser.add_argument("--tasks-file", type=Path, default=Path("LOOP_TASKS.md"))
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--pr-url", required=True)
    return parser.parse_args()


def parse_task_rows(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    table_lines = [line for line in lines if line.startswith("|")]
    if len(table_lines) < 2:
        return []

    header = split_markdown_row(table_lines[0])
    rows: list[dict[str, str]] = []

    for line in table_lines[2:]:
        cells = split_markdown_row(line)
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells, strict=True)))

    return rows


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


if __name__ == "__main__":
    raise SystemExit(main())
