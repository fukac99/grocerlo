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
| T011 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T011-billa-comparison-table-ui |  | none |  | none |  | Build minimal BILLA comparison table UI | `frontend`, minimal README updates if needed | T010 | Blocked until API contract is stable; acceptance: searchable BILLA table with product, brand, package, price, unit price, promotion, last seen, source link. Human decision: frontend scaffold choice if none exists. |
| T016 | Ready |  |  | task/T016-comparison-api-canonical-products |  | none |  | none |  | Add canonical product comparison API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T010,T015 | Ready after T015 merged; acceptance: `GET /comparison?query=...` returns canonical groups with retailer offers, prices, unit prices, promotions, observed dates, and source links. |
| T025 | Blocked | security-review-subagent |  | task/T025-full-codebase-security-review-100 |  | none |  | none |  | Run full-codebase security review at 100 completed tasks | Whole repository, dependency/config surface, scraping/data handling, CI/review gates, generated artifacts | 100 completed tasks | Blocked until completed-task count reaches the first 100-task boundary. Acceptance: run full-codebase security review, record findings, open follow-up tasks for required fixes, and update last security review boundary. |
| T028 | Blocked | pm-scoping-subagent | 2026-06-28 21:08 UTC+2 | task/T028-mpreis-store-normalization |  | none |  | none |  | Add MPREIS low-volume store and normalization path | `backend/app/scrapers/mpreis.py`, `scripts/scrape_once.py`, `scripts/normalize_once.py`, tests | T013,T008 | Blocked until MPREIS store policy is explicitly approved; acceptance: low-volume stored MPREIS rows and normalized retailer products without broad scrape. |
| T029 | Ready |  |  | task/T029-wire-frontend-billa-search-api |  | none |  | none |  | Wire frontend visual shell to BILLA search API | `frontend` | T010,T026 | Ready after T010 merged; acceptance: frontend can query API with fallback/mock state clearly indicated. Do not run in parallel with T032/T034 because they share comparison table scope. |
| T030 | Ready |  |  | task/T030-reconcile-once-cli |  | none |  | none |  | Add one-off reconciliation CLI | `scripts/reconcile_once.py`, `backend/app/matching` | T015 | Ready after T015 merged; acceptance: run matching over normalized retailer products and report candidate match counts/confidence buckets. |
| T034 | Ready |  |  | task/T034-filter-by-cheapest-retailer |  | none |  | none |  | Add retailer filter for products cheapest at selected retailer | `frontend/components/comparison-table.tsx`, focused frontend checks | T032 | Ready after T032 merged. Acceptance: selecting a retailer filter shows only product/package rows where that retailer has the lowest available price; tied cheapest offers should count for every tied retailer; products missing that retailer or cheaper elsewhere are hidden. Do not run in parallel with T029 because they share frontend comparison-table scope. |
| T037 | Done | coordinator | 2026-06-28 21:34 UTC+2 | task/T037-post-batch-ledger-sync |  | none |  | not_required |  | Sync ledger after T015/T022/T032 merges | `LOOP_TASKS.md`, `LOOP_LOG.md`, `LOOP_STATE.md` |  | Markdown-only coordinator PR; archives merged rows and refreshes next ready tasks. |

## In Progress

In-progress tasks are listed in the main task table.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

Blocked tasks are listed in the main task table.
