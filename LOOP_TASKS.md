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
| T008 | Done | implementation-subagent | 2026-06-28 20:29 UTC+2 | task/T008-billa-retailer-product-normalization | https://github.com/fukac99/grocerlo/pull/16 | open | 2026-06-28 20:37 UTC+2 | passed | review-subagent | Normalize stored BILLA raw products into retailer products | `backend/app/normalization`, `backend/app/db`, `backend/app/models`, focused tests | T003,T005 | Review passed. Implemented idempotent scrape-run normalization from `raw_products` to `retailer_products`, preserving raw rows/source references and handling price/package/promotion fields. |
| T009 | Done | implementation-subagent | 2026-06-28 20:45 UTC+2 | task/T009-stored-data-sanity-report | https://github.com/fukac99/grocerlo/pull/18 | open | 2026-06-28 20:51 UTC+2 | passed | review-subagent | Add low-volume stored-data sanity report | `scripts`, read-only DB query helpers, docs/README if needed | T003,T005 | Review passed. Added stored scrape-run sanity report CLI with aggregate counts, raw product quality issues, and bad-row identifiers. |
| T010 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T010-billa-product-search-api |  | none |  | none |  | Add BILLA-only product search API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T008 | Blocked until normalized retailer product rows exist; acceptance: `GET /products/search?q=...` returns normalized BILLA products with price/unit/category/source fields. |
| T011 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T011-billa-comparison-table-ui |  | none |  | none |  | Build minimal BILLA comparison table UI | `frontend`, minimal README updates if needed | T010 | Blocked until API contract is stable; acceptance: searchable BILLA table with product, brand, package, price, unit price, promotion, last seen, source link. Human decision: frontend scaffold choice if none exists. |
| T013 | Done | implementation-subagent | 2026-06-28 20:29 UTC+2 | task/T013-mpreis-low-volume-discovery | https://github.com/fukac99/grocerlo/pull/15 | open | 2026-06-28 20:36 UTC+2 | passed | review-subagent | Add MPREIS low-volume discovery dry run | `backend/app/scrapers/mpreis.py`, `scripts/scrape_once.py`, `docs/scraper-notes/mpreis.md`, tests/fixtures if applicable | T003,T005,T012 | Review passed after invalid limits were rejected; dry-run only, 1 category-equivalent page and 3 products. |
| T015 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T015-billa-mpreis-rule-matching |  | none |  | none |  | Add BILLA/MPREIS rule-based product matching | `backend/app/matching`, `backend/app/models`, focused tests | T008,T013 | Blocked until normalized BILLA data and MPREIS discovery/data exist; acceptance: deterministic candidate scoring using brand, name, package, category, and unit compatibility with confidence threshold. |
| T016 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T016-comparison-api-canonical-products |  | none |  | none |  | Add canonical product comparison API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T010,T015 | Blocked until search API and matching foundations exist; acceptance: `GET /comparison?query=...` returns canonical groups with retailer offers, prices, unit prices, promotions, observed dates, and source links. |
| T020 | Done | coordinator | 2026-06-28 20:30 UTC+2 | task/T020-scope-ingest-and-app-work | https://github.com/fukac99/grocerlo/pull/14 | open | 2026-06-28 20:32 UTC+2 | passed | review-subagent | Scope full ingest and visual app work | `LOOP_TASKS.md`, `LOOP_STATE.md`, `LOOP_LOG.md` | T019 | Review passed. T021/T022 keep broad ingest gated; T023 can start as mock-data frontend visual inspection work. |
| T021 | Blocked | pm-scoping-subagent | 2026-06-28 20:30 UTC+2 | task/T021-billa-controlled-full-ingest |  | none |  | none |  | Add controlled BILLA full-ingest workflow | `scripts`, `README.md`, optional read-only quality/report integration | T009 | Blocked until stored-data sanity reporting exists; acceptance: operator-triggered BILLA ingest with explicit broad-run confirmation, rate limiting, resume/limit options, raw storage, run summary, and quality report output. |
| T022 | Blocked | pm-scoping-subagent | 2026-06-28 20:30 UTC+2 | task/T022-retailer-ingest-runbook |  | none |  | none |  | Document full-ingest readiness runbook for available retailers | `docs`, `README.md` if needed | T013,T021 | Blocked until BILLA full-ingest workflow and MPREIS discovery notes exist; acceptance: checklist for which retailers can be ingested, required approvals, rate limits, stop conditions, commands, and rollback/cleanup steps. |
| T023 | Done | implementation-subagent | 2026-06-28 20:45 UTC+2 | task/T023-frontend-visual-inspection-shell | https://github.com/fukac99/grocerlo/pull/19 | open | 2026-06-28 20:54 UTC+2 | passed | review-subagent | Scaffold frontend visual inspection shell | `frontend`, root docs if needed | T006 | Review passed. Added a mock-data Next.js visual inspection shell with searchable/filterable comparison table and local run instructions. |
| T024 | Done | coordinator | 2026-06-28 20:40 UTC+2 | task/T024-security-review-cadence | https://github.com/fukac99/grocerlo/pull/17 | open | 2026-06-28 20:42 UTC+2 | passed | review-subagent | Add 100-task full-codebase security review cadence to loop | `docs/LOOP_ENGINEERING.md`, `LOOP_TASKS.md`, `LOOP_STATE.md` | T020 | Review passed. First full-codebase security review milestone is T025 at 100 completed tasks. |
| T025 | Blocked | security-review-subagent |  | task/T025-full-codebase-security-review-100 |  | none |  | none |  | Run full-codebase security review at 100 completed tasks | Whole repository, dependency/config surface, scraping/data handling, CI/review gates, generated artifacts | 100 completed tasks | Blocked until completed-task count reaches the first 100-task boundary. Acceptance: run full-codebase security review, record findings, open follow-up tasks for required fixes, and update last security review boundary. |

## In Progress

In-progress tasks are listed in the main task table.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

Blocked tasks are listed in the main task table.
