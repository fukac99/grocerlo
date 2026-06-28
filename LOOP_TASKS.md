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
| T002 | Done | billa-validation-subagent | 2026-06-28 19:17 UTC+2 | task/T002-billa-dry-scrape-validation | https://github.com/fukac99/grocerlo/pull/6 | merged | 2026-06-28 19:50 UTC+2 | passed | review-subagent | Run BILLA dry scrape and inspect sample output | `scripts/scrape_once.py`, `backend/app/scrapers/billa.py`, `docs/scraper-notes/billa.md` | T001,T006 | Review passed and PR merged. Residual risks: validation notes are representative, not broad parser proof; scraper-specific parser tests remain future work. |
| T003 | Blocked | postgres-store-subagent | 2026-06-28 19:55 UTC+2 | task/T003-postgres-store-path | https://github.com/fukac99/grocerlo/pull/11 | open | 2026-06-28 20:14 UTC+2 | changes_requested | review-subagent | Start Postgres, run migrations, and test `--store` path | `docker-compose.yml`, `backend/alembic`, database | T001,T002,T006 | Changes requested: Docker daemon remains unavailable, so Postgres startup, migrations, and `scripts/scrape_once.py --store` have not run. Low-volume dry BILLA scrape passed for 1 category and 3 products. T008/T009 remain blocked until stored validation succeeds. |
| T005 | Done | quality-checks-subagent | 2026-06-28 19:17 UTC+2 | task/T005-raw-product-quality-checks | https://github.com/fukac99/grocerlo/pull/7 | merged | 2026-06-28 19:50 UTC+2 | passed | review-subagent | Add raw product data quality checks | `backend/app`, `scripts` | T004,T006 | Review passed and PR merged. Follow-ups: run checks against low-volume raw scrape output; add dict/JSON payload test later if needed. |
| T008 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T008-billa-retailer-product-normalization |  | none |  | none |  | Normalize stored BILLA raw products into retailer products | `backend/app/normalization`, `backend/app/db`, `backend/app/models`, focused tests | T003,T005 | Blocked until storage path is validated and quality checks land; acceptance: repeatable conversion from `raw_products` to `retailer_products` preserving raw rows and handling captured price/package/promotion fields. |
| T009 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T009-stored-data-sanity-report |  | none |  | none |  | Add low-volume stored-data sanity report | `scripts`, read-only DB query helpers, docs/README if needed | T003,T005 | Blocked until storage path and quality checks land; acceptance: summarize latest scrape run counts, missing fields, duplicate source IDs, suspicious prices/unit prices. Decide JSON, text, or both. |
| T010 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T010-billa-product-search-api |  | none |  | none |  | Add BILLA-only product search API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T008 | Blocked until normalized retailer product rows exist; acceptance: `GET /products/search?q=...` returns normalized BILLA products with price/unit/category/source fields. |
| T011 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T011-billa-comparison-table-ui |  | none |  | none |  | Build minimal BILLA comparison table UI | `frontend`, minimal README updates if needed | T010 | Blocked until API contract is stable; acceptance: searchable BILLA table with product, brand, package, price, unit price, promotion, last seen, source link. Human decision: frontend scaffold choice if none exists. |
| T012 | Done | retailer-discovery-subagent | 2026-06-28 19:59 UTC+2 | task/T012-retailer-discovery-checklist | https://github.com/fukac99/grocerlo/pull/10 | merged | 2026-06-28 20:14 UTC+2 | passed | review-subagent | Document retailer expansion discovery checklist | `docs`, maybe `PRICE_COMPARISON_APP_PLAN.md` only | T002,T005 | Review passed and PR merged. Legal/robots conclusions are intentionally deferred to per-retailer discovery notes before scraper implementation. |
| T013 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T013-mpreis-low-volume-discovery |  | none |  | none |  | Add MPREIS low-volume discovery dry run | `backend/app/scrapers/mpreis.py`, `scripts/scrape_once.py`, tests/fixtures if applicable | T003,T005,T012 | Blocked on storage/quality/docs and low-volume request policy; dry-run only, no broad scrape. |
| T015 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T015-billa-mpreis-rule-matching |  | none |  | none |  | Add BILLA/MPREIS rule-based product matching | `backend/app/matching`, `backend/app/models`, focused tests | T008,T013 | Blocked until normalized BILLA data and MPREIS discovery/data exist; acceptance: deterministic candidate scoring using brand, name, package, category, and unit compatibility with confidence threshold. |
| T016 | Blocked | pm-scoping-subagent | 2026-06-28 19:55 UTC+2 | task/T016-comparison-api-canonical-products |  | none |  | none |  | Add canonical product comparison API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T010,T015 | Blocked until search API and matching foundations exist; acceptance: `GET /comparison?query=...` returns canonical groups with retailer offers, prices, unit prices, promotions, observed dates, and source links. |
| T017 | Done | coordinator | 2026-06-28 19:55 UTC+2 | task/T017-refresh-merged-pr-statuses | https://github.com/fukac99/grocerlo/pull/9 | merged | 2026-06-28 20:14 UTC+2 | passed | review-subagent | Refresh merged PR statuses and scope next tasks | `LOOP_TASKS.md`, `LOOP_STATE.md`, `LOOP_LOG.md` |  | Review passed and PR merged. |
| T018 | Done | coordinator | 2026-06-28 20:14 UTC+2 | task/T018-correct-loop-ledger-after-merges | https://github.com/fukac99/grocerlo/pull/12 | open | 2026-06-28 20:15 UTC+2 | passed | review-subagent | Correct loop ledger after merged and blocked PRs | `LOOP_TASKS.md`, `LOOP_STATE.md` | T017 | Review passed. T003 remains blocked until Docker/Postgres store validation succeeds. |

## In Progress

In-progress tasks are listed in the main task table.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

Blocked tasks are listed in the main task table.
