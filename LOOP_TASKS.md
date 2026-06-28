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
- Every implementation task with a pull request must track review under the same task row.
- Use review statuses: `none`, `pending`, `in_progress`, `passed`, `changes_requested`, or `blocked`.
- Do not consider a pull request merge-ready until its task has `review_status: passed`.
- The repository connection task may need to bootstrap the base branch first if the remote repository is empty.

## Tasks

| id | status | owner | started | branch | pull_request | pr_status | pr_last_checked | review_status | reviewer | task | files/scope | depends_on | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T008 | Ready |  |  | task/T008-billa-retailer-product-normalization |  | none |  | none |  | Normalize stored BILLA raw products into retailer products | `backend/app/normalization`, `backend/app/db`, `backend/app/models`, focused tests | T003,T005 | Ready after T003/T005 merged; acceptance: repeatable conversion from `raw_products` to `retailer_products`, preserving raw rows and handling price/package/promotion fields. Include a low-volume CLI path where practical. |
| T009 | Ready |  |  | task/T009-stored-data-sanity-report |  | none |  | none |  | Add low-volume stored-data sanity report | `scripts`, read-only DB query helpers, docs/README if needed | T003,T005 | Ready after stored scrape validation and quality checks merged; acceptance: summarize latest scrape run counts, missing fields, duplicate source IDs, suspicious prices/unit prices. Avoid overlapping T008 DB helper edits if run in parallel. |
| T010 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T010-billa-product-search-api |  | none |  | none |  | Add BILLA-only product search API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T008 | Blocked until normalized retailer product rows exist; acceptance: `GET /products/search?q=...` returns normalized BILLA products with price/unit/category/source fields. |
| T011 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T011-billa-comparison-table-ui |  | none |  | none |  | Build minimal BILLA comparison table UI | `frontend`, minimal README updates if needed | T010 | Blocked until API contract is stable; acceptance: searchable BILLA table with product, brand, package, price, unit price, promotion, last seen, source link. Human decision: frontend scaffold choice if none exists. |
| T013 | In Progress | implementation-subagent | 2026-06-28 20:29 UTC+2 | task/T013-mpreis-low-volume-discovery |  | none |  | none |  | Add MPREIS low-volume discovery dry run | `backend/app/scrapers/mpreis.py`, `scripts/scrape_once.py`, `docs/scraper-notes/mpreis.md`, tests/fixtures if applicable | T003,T005,T012 | Ready after storage, quality checks, and retailer discovery checklist merged; dry-run only, 1 category and no more than 3 products. |
| T015 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T015-billa-mpreis-rule-matching |  | none |  | none |  | Add BILLA/MPREIS rule-based product matching | `backend/app/matching`, `backend/app/models`, focused tests | T008,T013 | Blocked until normalized BILLA data and MPREIS discovery/data exist; acceptance: deterministic candidate scoring using brand, name, package, category, and unit compatibility with confidence threshold. |
| T016 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T016-comparison-api-canonical-products |  | none |  | none |  | Add canonical product comparison API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T010,T015 | Blocked until search API and matching foundations exist; acceptance: `GET /comparison?query=...` returns canonical groups with retailer offers, prices, unit prices, promotions, observed dates, and source links. |
| T019 | Done | coordinator | 2026-06-28 20:24 UTC+2 | task/T019-post-merge-ledger-sync | https://github.com/fukac99/grocerlo/pull/13 | open | 2026-06-28 20:25 UTC+2 | passed | review-subagent | Sync loop ledger after T003 merge and scope next batch | `LOOP_TASKS.md`, `LOOP_STATE.md`, `LOOP_LOG.md` | T003,T012,T018 | Review passed. Next executor batch can claim T008 and T013 in parallel after this PR merges. |

## In Progress

In-progress tasks are listed in the main task table.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

Blocked tasks are listed in the main task table.
