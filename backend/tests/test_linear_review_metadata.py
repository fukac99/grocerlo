import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from linear_review_metadata import (  # noqa: E402
    extract_linear_issue_identifiers,
    parse_linear_issue_review_metadata,
    parse_review_metadata_block,
    validate_linear_review_metadata,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "linear_review_issue_passed.json"
PR_URL = "https://github.com/fukac99/grocerlo/pull/75"
HEAD_SHA = "1111111111111111111111111111111111111111"


def load_issue_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_extract_linear_issue_identifiers_deduplicates_in_order() -> None:
    body = "Linear-Issue: gro-59\nRelated: GRO-58, GRO-59"

    assert extract_linear_issue_identifiers(body) == ["GRO-59", "GRO-58"]


def test_parse_review_metadata_block_normalizes_status() -> None:
    metadata = parse_review_metadata_block(
        "review_status: PASSED\nreviewed_pr: https://example.test/pr/1",
        issue_identifier="gro-59",
        source="comment",
    )

    assert metadata is not None
    assert metadata.issue_identifier == "GRO-59"
    assert metadata.review_status == "passed"
    assert metadata.reviewed_pr == "https://example.test/pr/1"
    assert metadata.source == "comment"


def test_parse_linear_issue_review_metadata_prefers_newest_comment() -> None:
    metadata = parse_linear_issue_review_metadata(load_issue_fixture())

    assert metadata is not None
    assert metadata.review_status == "passed"
    assert metadata.reviewed_pr == PR_URL
    assert metadata.reviewed_head_sha == HEAD_SHA
    assert metadata.reviewed_at == "2026-06-29T10:30:00Z"
    assert metadata.reviewer == "bugbot"
    assert metadata.source == "comment[2]"


def test_validate_linear_review_metadata_accepts_matching_fixture() -> None:
    errors = validate_linear_review_metadata(load_issue_fixture(), PR_URL, HEAD_SHA)

    assert errors == []


def test_validate_linear_review_metadata_rejects_stale_head_sha() -> None:
    errors = validate_linear_review_metadata(load_issue_fixture(), PR_URL, "2" * 40)

    assert "reviewed_head_sha must match the pull request head SHA" in errors


def test_validate_linear_review_metadata_rejects_non_review_state() -> None:
    issue = load_issue_fixture()
    issue["state"]["name"] = "Todo"

    errors = validate_linear_review_metadata(issue, PR_URL, HEAD_SHA)

    assert "issue state must be one of In Review for an open PR; got 'Todo'" in errors


def test_validate_linear_review_metadata_rejects_missing_metadata() -> None:
    issue = copy.deepcopy(load_issue_fixture())
    issue["description"] = "No review marker here."
    issue["comments"]["nodes"] = [{"body": "No review marker here either."}]

    errors = validate_linear_review_metadata(issue, PR_URL, HEAD_SHA)

    assert "issue is missing review metadata" in errors
