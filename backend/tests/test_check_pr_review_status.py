import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pr_review_status import (  # noqa: E402
    is_markdown_file,
    is_markdown_only_pr,
    read_changed_files,
    resolve_review_status,
)


def test_is_markdown_file_accepts_markdown_only_paths() -> None:
    assert is_markdown_file("README.md")
    assert is_markdown_file("docs/LOOP_ENGINEERING.MD")


def test_is_markdown_file_rejects_non_markdown_paths() -> None:
    assert not is_markdown_file("scripts/check_pr_review_status.py")
    assert not is_markdown_file(".github/workflows/agent-review.yml")


def test_read_changed_files_ignores_blank_lines(tmp_path: Path) -> None:
    changed_files = tmp_path / "changed-files.txt"
    changed_files.write_text("\nREADME.md\n\ndocs/LOOP_ENGINEERING.md\n", encoding="utf-8")

    assert read_changed_files(changed_files) == ["README.md", "docs/LOOP_ENGINEERING.md"]


def test_markdown_only_pr_skips_review() -> None:
    assert is_markdown_only_pr(["README.md", "docs/LOOP_ENGINEERING.md"])


def test_mixed_pr_does_not_skip_review() -> None:
    assert not is_markdown_only_pr(["README.md", "scripts/check_pr_review_status.py"])


def test_empty_changed_files_does_not_skip_review() -> None:
    assert not is_markdown_only_pr([])


def test_resolve_review_status_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_REVIEW_STATUS", "passed")

    class Args:
        pr_body_file = None

    assert resolve_review_status(Args()) == "passed"


def test_resolve_review_status_reads_pr_body(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("AGENT_REVIEW_STATUS", raising=False)
    pr_body = tmp_path / "body.txt"
    pr_body.write_text("Review notes\n\nreview_status: passed\n", encoding="utf-8")

    class Args:
        pr_body_file = pr_body

    assert resolve_review_status(Args()) == "passed"
