# Direct Linear Review-Gate Migration

This note scopes the prerequisites for replacing PR-body review metadata with direct Linear validation. It is a recommendation only; it does not change CI enforcement, secrets, branch protection, or merge policy.

## Current Gate

The current required check is `.github/workflows/agent-review.yml`, named `Agent Review Gate / Require agent review status`.

It collects changed files with:

```bash
git diff --name-only "origin/${{ github.base_ref }}...HEAD" > changed-files.txt
```

It then writes the pull request body to `pr-body.txt` and runs:

```bash
python3 scripts/check_pr_review_status.py \
  --head-ref "${{ github.head_ref }}" \
  --pr-url "${{ github.event.pull_request.html_url }}" \
  --pr-body-file pr-body.txt \
  --changed-files-file changed-files.txt
```

`scripts/check_pr_review_status.py` trusts three inputs:

- Markdown-only changed files skip the review requirement.
- `AGENT_REVIEW_STATUS=passed` passes non-Markdown PRs.
- Otherwise, the PR body must contain `review_status: passed`.

Recent PR bodies consistently include a `Review notes` section with `review_status: not_required` for Markdown-only coordinator work or `review_status: passed` for reviewed implementation work. The current mechanism does not verify Linear state directly and does not bind the review status to the exact PR head SHA.

## Recommended Linear-Backed Design

Keep the Markdown-only exemption for coordinator documentation PRs. For every non-Markdown PR, require the gate to query Linear and validate a structured review record tied to the current PR head SHA.

Recommended PR convention:

```text
Linear-Issue: GRO-58
```

Recommended Linear review metadata, stored in the issue description or in the latest agent status comment:

```text
review_status: passed
reviewed_pr: https://github.com/fukac99/grocerlo/pull/NN
reviewed_head_sha: <40-char git sha>
reviewed_at: <ISO-8601 timestamp>
reviewer: <agent or human reviewer>
checks: <commands or CI checks reviewed>
```

The CI script should fail closed unless all of these are true:

- The PR is linked to exactly one `GRO-*` issue.
- The Linear issue belongs to team `GRO`.
- The issue state is `In Review` for an open PR, or `Done` only for post-merge/status reconciliation.
- The issue contains the current PR URL.
- `review_status` is `passed` for implementation or other non-Markdown changes.
- `reviewed_head_sha` exactly equals `github.event.pull_request.head.sha`.
- The metadata was recorded after the review was run and before the gate executes.

For Markdown-only PRs, the script may continue to allow `review_status: not_required`, but it should still report the linked Linear issue and state when available.

## Required Secrets And Permissions

Before CI can query Linear, the repository needs a GitHub Actions secret:

- `LINEAR_API_KEY`: a Linear API token with enough permission to read team `GRO`, issues, issue descriptions, comments, and workflow states.

Optional repository variables:

- `LINEAR_TEAM_KEY=GRO`
- `LINEAR_REQUIRED_REVIEW_STATE=In Review`

The current local workflow uses `credentials.txt` and `LINEAR_TOKEN`; CI should not depend on that file. The secret should be created by the user or repository owner, not by an agent.

## Safe Rollout

1. Add a local parser and unit tests for Linear metadata using fixture JSON, with no CI enforcement change.
2. Add a non-blocking CI dry-run step that queries Linear when `LINEAR_API_KEY` exists and prints the validation result, while the existing PR-body gate remains authoritative.
3. After dry-run stability, switch the required gate to Linear-backed validation for non-Markdown PRs.
4. Update branch protection only after the enforcing workflow name and check behavior are confirmed.

## Failure Modes

- Missing or malformed `Linear-Issue` marker: fail with instructions to link exactly one `GRO-*` issue.
- Missing `LINEAR_API_KEY`: fail only after the team intentionally enables enforcement; before then, dry-run should skip with a clear warning.
- Linear API outage or rate limit: fail closed for enforcing mode, warn for dry-run mode.
- `review_status: passed` without matching `reviewed_head_sha`: fail because the review may be stale after new commits.
- Linked issue not in `In Review`: fail because implementation work should not be merge-ready while the task is unclaimed, blocked, or still in progress.
- Markdown-only PR with no Linear issue: pass the review requirement but warn, so coordinator documentation remains lightweight.

## Current Blockers

Direct enforcement is blocked on a user-provided CI secret and a final choice of the exact Linear metadata location. Agents can safely continue with a narrower implementation follow-up that adds fixture-based parsing and tests without changing secrets, branch protection, or required-check behavior.
