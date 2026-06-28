import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pr_review_status import (  # noqa: E402
    is_markdown_file,
    is_markdown_only_coordinator_pr,
    read_changed_files,
)


def test_is_markdown_file_accepts_markdown_only_paths() -> None:
    assert is_markdown_file("LOOP_TASKS.md")
    assert is_markdown_file("docs/LOOP_ENGINEERING.MD")


def test_is_markdown_file_rejects_non_markdown_paths() -> None:
    assert not is_markdown_file("scripts/check_pr_review_status.py")
    assert not is_markdown_file(".github/workflows/agent-review.yml")


def test_read_changed_files_ignores_blank_lines(tmp_path: Path) -> None:
    changed_files = tmp_path / "changed-files.txt"
    changed_files.write_text("\nLOOP_TASKS.md\n\nREADME.md\n", encoding="utf-8")

    assert read_changed_files(changed_files) == ["LOOP_TASKS.md", "README.md"]


def test_markdown_only_coordinator_pr_skips_review() -> None:
    row = {"owner": "coordinator"}

    assert is_markdown_only_coordinator_pr(row, ["LOOP_TASKS.md", "docs/LOOP_ENGINEERING.md"])


def test_markdown_only_non_coordinator_pr_does_not_skip_review() -> None:
    row = {"owner": "implementation-subagent"}

    assert not is_markdown_only_coordinator_pr(row, ["README.md"])


def test_mixed_coordinator_pr_does_not_skip_review() -> None:
    row = {"owner": "coordinator"}

    assert not is_markdown_only_coordinator_pr(
        row,
        ["LOOP_TASKS.md", "scripts/check_pr_review_status.py"],
    )
