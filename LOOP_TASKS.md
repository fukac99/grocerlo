# Grocery Saver Loop Tasks

This file is the task ledger and lightweight lock file for automated loop runs.

Before a loop run starts work, it must move any claimed task from `Ready` to `In Progress` and set the `owner` field. This prevents two subagents from choosing the same task.

## Rules

- Only tasks with `status: Ready` can be claimed.
- Set `status: In Progress` before launching a subagent or starting work.
- Set `owner` to the coordinator or subagent role that claimed the task.
- Set `started` when a task is claimed.
- Move finished tasks to `Done`.
- Archive fully complete tasks to `LOOP_LOG.md` once their PR is merged and no review or dependency bookkeeping needs to stay active.
- Keep `LOOP_TASKS.md` focused on active, ready, in-progress, blocked, open-PR, and review-gated work.
- Move blocked tasks to `Blocked` with a short reason.
- Do not launch parallel tasks that edit the same files unless they are explicitly coordinated.
- Prefer one coordinator task plus multiple implementation subagents only when tasks are independent.
- Each implementation task should happen on its own branch and end with a GitHub pull request against the project repository.
- Use branch names like `task/T002-billa-dry-scrape-validation`.
- Record the branch and pull request URL in this ledger.
- On every loop run, check existing pull requests and update `pr_status` and `pr_last_checked`.
- Use PR statuses: `none`, `open`, `merged`, `closed`, `blocked`, or `unknown`.
- On every loop run, compare `LOOP_TASKS.md` against `PRICE_COMPARISON_APP_PLAN.md` and add missing actionable tasks.
- On every loop run, start with a PM/scoping pass that plans a batch of next executor-ready tasks.
- The PM pass should define task IDs, dependencies, file/scope boundaries, branch names, and acceptance criteria.
- Executor agents should only receive tasks that are already scoped in this ledger.
- Every implementation task, and every task that touches non-Markdown files, with a pull request must track review under the same task row.
- Use review statuses: `none`, `pending`, `in_progress`, `passed`, `changes_requested`, `blocked`, or `not_required`.
- Markdown-only coordinator PRs do not require code review and may use `review_status: none` or `not_required`.
- Do not consider an implementation or non-Markdown pull request merge-ready until its task has `review_status: passed`.
- The repository connection task may need to bootstrap the base branch first if the remote repository is empty.

## Tasks

| id | status | owner | started | branch | pull_request | pr_status | pr_last_checked | review_status | reviewer | task | files/scope | depends_on | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T010 | Done | implementation-subagent | 2026-06-28 21:13 UTC+2 | task/T010-billa-product-search-api | https://github.com/fukac99/grocerlo/pull/22 | open | 2026-06-28 21:17 UTC+2 | passed | self-review | Add BILLA-only product search API | `backend/app/api`, `backend/app/db`, `backend/app/main.py`, API tests | T008 | Review passed. `GET /products/search?q=...` returns normalized BILLA products with price/unit/category/source fields. |
| T011 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T011-billa-comparison-table-ui |  | none |  | none |  | Build minimal BILLA comparison table UI | `frontend`, minimal README updates if needed | T010 | Blocked until API contract is stable; acceptance: searchable BILLA table with product, brand, package, price, unit price, promotion, last seen, source link. Human decision: frontend scaffold choice if none exists. |
| T015 | Ready |  |  | task/T015-billa-mpreis-rule-matching |  | none |  | none |  | Add BILLA/MPREIS rule-based product matching | `backend/app/matching`, `backend/app/models`, focused tests | T008,T013 | Ready by formal dependencies, but do not run in parallel with T010 because both may touch `backend/app/models`; real cross-retailer E2E still needs stored/normalized MPREIS rows from T028. |
| T016 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T016-comparison-api-canonical-products |  | none |  | none |  | Add canonical product comparison API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T010,T015 | Blocked until search API and matching foundations exist; acceptance: `GET /comparison?query=...` returns canonical groups with retailer offers, prices, unit prices, promotions, observed dates, and source links. |
| T021 | Done | implementation-subagent | 2026-06-28 21:13 UTC+2 | task/T021-billa-controlled-full-ingest | https://github.com/fukac99/grocerlo/pull/23 | open | 2026-06-28 21:17 UTC+2 | passed | self-review | Add controlled BILLA full-ingest workflow | `scripts`, `README.md`, optional read-only quality/report integration | T009 | Review passed. Added guarded BILLA ingest CLI with explicit broad-run confirmation, rate limiting, resume/limit options, raw storage, run summary, and sanity-report output. |
| T022 | Blocked | pm-scoping-subagent | 2026-06-28 20:30 UTC+2 | task/T022-retailer-ingest-runbook |  | none |  | none |  | Document full-ingest readiness runbook for available retailers | `docs`, `README.md` if needed | T013,T021 | Blocked until BILLA full-ingest workflow and MPREIS discovery notes exist; acceptance: checklist for which retailers can be ingested, required approvals, rate limits, stop conditions, commands, and rollback/cleanup steps. |
| T025 | Blocked | security-review-subagent |  | task/T025-full-codebase-security-review-100 |  | none |  | none |  | Run full-codebase security review at 100 completed tasks | Whole repository, dependency/config surface, scraping/data handling, CI/review gates, generated artifacts | 100 completed tasks | Blocked until completed-task count reaches the first 100-task boundary. Acceptance: run full-codebase security review, record findings, open follow-up tasks for required fixes, and update last security review boundary. |
| T027 | Done | coordinator | 2026-06-28 21:08 UTC+2 | task/T027-post-pr20-ledger-sync | https://github.com/fukac99/grocerlo/pull/21 | open | 2026-06-28 21:12 UTC+2 | passed | review-subagent | Sync ledger after frontend and data workflow merges | `LOOP_TASKS.md`, `LOOP_LOG.md`, `LOOP_STATE.md` | T026 | Review passed. Archived merged tasks, refreshed ready tasks, and added next scoped follow-ups. |
| T028 | Blocked | pm-scoping-subagent | 2026-06-28 21:08 UTC+2 | task/T028-mpreis-store-normalization |  | none |  | none |  | Add MPREIS low-volume store and normalization path | `backend/app/scrapers/mpreis.py`, `scripts/scrape_once.py`, `scripts/normalize_once.py`, tests | T013,T008 | Blocked until MPREIS store policy is explicitly approved; acceptance: low-volume stored MPREIS rows and normalized retailer products without broad scrape. |
| T029 | Blocked | pm-scoping-subagent | 2026-06-28 21:08 UTC+2 | task/T029-wire-frontend-billa-search-api |  | none |  | none |  | Wire frontend visual shell to BILLA search API | `frontend` | T010,T026 | Blocked until BILLA search API exists; acceptance: frontend can query API with fallback/mock state clearly indicated. |
| T030 | Blocked | pm-scoping-subagent | 2026-06-28 21:08 UTC+2 | task/T030-reconcile-once-cli |  | none |  | none |  | Add one-off reconciliation CLI | `scripts/reconcile_once.py`, `backend/app/matching` | T015 | Blocked until matching logic lands; acceptance: run matching over normalized retailer products and report candidate match counts/confidence buckets. |
| T031 | Done | coordinator | 2026-06-28 21:13 UTC+2 | task/T031-md-only-coordinator-review-skip | https://github.com/fukac99/grocerlo/pull/24 | open | 2026-06-28 21:20 UTC+2 | passed | review-subagent | Exempt Markdown-only coordinator PRs from review gate | `.github/workflows/agent-review.yml`, `scripts/check_pr_review_status.py`, `docs/LOOP_ENGINEERING.md`, `LOOP_TASKS.md`, tests |  | Review passed. CI/CD now exempts Markdown-only coordinator PRs while non-Markdown PRs still require `review_status: passed`. |
| T032 | Ready |  |  | task/T032-highlight-cheapest-ui |  | none |  | none |  | Highlight cheapest supermarket offer in comparison rows | `frontend/components/comparison-table.tsx`, `frontend/app/globals.css`, focused frontend checks | T026 | User requested light-green highlighting for the cheapest place to buy each product. Acceptance: for each product/package row, the retailer cell with the lowest available price is highlighted light green; ties should highlight all matching cheapest offers; missing offers remain unhighlighted. |
| T033 | Done | coordinator | 2026-06-28 21:21 UTC+2 | task/T033-scope-cheapest-highlight-task | https://github.com/fukac99/grocerlo/pull/25 | open | 2026-06-28 21:23 UTC+2 | not_required |  | Scope UI cheapest-offer highlight task | `LOOP_TASKS.md`, `LOOP_STATE.md` |  | Markdown-only coordinator PR to add T032; code review not required. |
| T034 | Blocked | pm-scoping-subagent | 2026-06-28 21:22 UTC+2 | task/T034-filter-by-cheapest-retailer |  | none |  | none |  | Add retailer filter for products cheapest at selected retailer | `frontend/components/comparison-table.tsx`, focused frontend checks | T032 | Blocked until cheapest-offer row logic exists. Acceptance: selecting a retailer filter shows only product/package rows where that retailer has the lowest available price; tied cheapest offers should count for every tied retailer; products missing that retailer or cheaper elsewhere are hidden. |
| T035 | Done | coordinator | 2026-06-28 21:22 UTC+2 | task/T035-scope-retailer-cheapest-filter |  | none |  | not_required |  | Scope UI cheapest-retailer filter task | `LOOP_TASKS.md`, `LOOP_STATE.md` |  | Markdown-only coordinator PR to add T034; code review not required. |

## In Progress

In-progress tasks are listed in the main task table.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

Blocked tasks are listed in the main task table.
