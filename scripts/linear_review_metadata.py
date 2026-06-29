#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


REVIEW_METADATA_KEYS = {
    "review_status",
    "reviewed_pr",
    "reviewed_head_sha",
    "reviewed_at",
    "reviewer",
    "checks",
}


@dataclass(frozen=True)
class LinearReviewMetadata:
    issue_identifier: str
    review_status: str
    reviewed_pr: str | None = None
    reviewed_head_sha: str | None = None
    reviewed_at: str | None = None
    reviewer: str | None = None
    checks: str | None = None
    source: str = "unknown"


def extract_linear_issue_identifiers(text: str, team_key: str = "GRO") -> list[str]:
    """Return unique Linear issue identifiers in first-seen order."""
    pattern = re.compile(rf"\b{re.escape(team_key)}-\d+\b", re.IGNORECASE)
    identifiers: list[str] = []
    seen: set[str] = set()
    for match in pattern.finditer(text):
        identifier = match.group(0).upper()
        if identifier not in seen:
            identifiers.append(identifier)
            seen.add(identifier)
    return identifiers


def parse_review_metadata_block(
    text: str,
    issue_identifier: str,
    source: str = "unknown",
) -> LinearReviewMetadata | None:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        key, separator, value = line.partition(":")
        normalized_key = key.strip().casefold()
        if separator and normalized_key in REVIEW_METADATA_KEYS:
            fields[normalized_key] = value.strip()

    review_status = fields.get("review_status")
    if not review_status:
        return None

    return LinearReviewMetadata(
        issue_identifier=issue_identifier.upper(),
        review_status=review_status.casefold(),
        reviewed_pr=fields.get("reviewed_pr"),
        reviewed_head_sha=fields.get("reviewed_head_sha"),
        reviewed_at=fields.get("reviewed_at"),
        reviewer=fields.get("reviewer"),
        checks=fields.get("checks"),
        source=source,
    )


def parse_linear_issue_review_metadata(
    issue: Mapping[str, Any],
) -> LinearReviewMetadata | None:
    issue_identifier = str(issue.get("identifier", "")).upper()
    if not issue_identifier:
        return None

    # Prefer the newest comment metadata over the description, because reviewers
    # can append a fresh status after new commits without rewriting the issue.
    for source, text in reversed(list(_linear_issue_text_sources(issue))):
        metadata = parse_review_metadata_block(text, issue_identifier, source=source)
        if metadata:
            return metadata
    return None


def validate_linear_review_metadata(
    issue: Mapping[str, Any],
    pr_url: str,
    head_sha: str,
    team_key: str = "GRO",
    allowed_open_states: Sequence[str] = ("In Review",),
) -> list[str]:
    errors: list[str] = []
    identifier = str(issue.get("identifier", "")).upper()
    if not identifier.startswith(f"{team_key.upper()}-"):
        errors.append(f"issue must belong to Linear team {team_key}")

    state_name = _nested_name(issue, "state")
    if state_name not in set(allowed_open_states):
        errors.append(
            "issue state must be one of "
            f"{', '.join(allowed_open_states)} for an open PR; got {state_name!r}"
        )

    metadata = parse_linear_issue_review_metadata(issue)
    if metadata is None:
        errors.append("issue is missing review metadata")
        return errors

    if metadata.review_status != "passed":
        errors.append(f"review_status must be 'passed'; got {metadata.review_status!r}")
    if metadata.reviewed_pr != pr_url:
        errors.append("reviewed_pr must match the pull request URL")
    if metadata.reviewed_head_sha != head_sha:
        errors.append("reviewed_head_sha must match the pull request head SHA")

    return errors


def _linear_issue_text_sources(issue: Mapping[str, Any]) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    description = issue.get("description")
    if isinstance(description, str) and description.strip():
        sources.append(("description", description))

    for index, comment in enumerate(_comment_nodes(issue), start=1):
        body = comment.get("body") if isinstance(comment, Mapping) else None
        if isinstance(body, str) and body.strip():
            sources.append((f"comment[{index}]", body))
    return sources


def _comment_nodes(issue: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    comments = issue.get("comments")
    if not isinstance(comments, Mapping):
        return []
    nodes = comments.get("nodes")
    if not isinstance(nodes, list):
        return []
    return [node for node in nodes if isinstance(node, Mapping)]


def _nested_name(issue: Mapping[str, Any], field: str) -> str | None:
    value = issue.get(field)
    if not isinstance(value, Mapping):
        return None
    name = value.get("name")
    return name if isinstance(name, str) else None
