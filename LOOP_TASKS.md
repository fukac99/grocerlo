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
| T002 | Done | billa-validation-subagent | 2026-06-28 19:17 UTC+2 | task/T002-billa-dry-scrape-validation | https://github.com/fukac99/grocerlo/pull/6 | open | 2026-06-28 19:36 UTC+2 | passed | review-subagent | Run BILLA dry scrape and inspect sample output | `scripts/scrape_once.py`, `backend/app/scrapers/billa.py` | T001,T006 | Review passed. Residual risks: validation notes are representative, not broad parser proof; scraper-specific parser tests still future work. |
| T003 | Ready |  |  | task/T003-postgres-store-path |  | none |  | none |  | Start Postgres, run migrations, and test `--store` path | `docker-compose.yml`, `backend/alembic`, database | T001,T002,T006 | Only after dry scrape output looks plausible. |
| T005 | Done | quality-checks-subagent | 2026-06-28 19:17 UTC+2 | task/T005-raw-product-quality-checks | https://github.com/fukac99/grocerlo/pull/7 | open | 2026-06-28 19:35 UTC+2 | passed | review-subagent | Add raw product data quality checks | `backend/app`, `scripts` | T004,T006 | Review passed. Follow-ups: add dict/JSON payload test later; scope duplicate checks to a single scrape run for stored DB rows. |
| T008 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T008-billa-retailer-product-normalization |  | none |  | none |  | Normalize stored BILLA raw products into retailer products | `backend/app/normalization`, `backend/app/db`, `backend/app/models`, focused tests | T003,T005 | Blocked until storage path is validated and quality checks land; acceptance: repeatable conversion from `raw_products` to `retailer_products` preserving raw rows and handling captured price/package/promotion fields. |
| T009 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T009-stored-data-sanity-report |  | none |  | none |  | Add low-volume stored-data sanity report | `scripts`, read-only DB query helpers, docs/README if needed | T003,T005 | Blocked until storage path and quality checks land; acceptance: summarize latest scrape run counts, missing fields, duplicate source IDs, suspicious prices/unit prices. Decide JSON, text, or both. |
| T010 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T010-billa-product-search-api |  | none |  | none |  | Add BILLA-only product search API | `backend/app/api`, `backend/app/db`, `backend/app/models`, API tests | T008 | Blocked until normalized retailer product rows exist; acceptance: `GET /products/search?q=...` returns normalized BILLA products with price/unit/category/source fields. |
| T011 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T011-billa-comparison-table-ui |  | none |  | none |  | Build minimal BILLA comparison table UI | `frontend`, minimal README updates if needed | T010 | Blocked until API contract is stable; acceptance: searchable BILLA table with product, brand, package, price, unit price, promotion, last seen, source link. Human decision: frontend scaffold choice if none exists. |
| T012 | Ready |  |  | task/T012-retailer-discovery-checklist |  | none |  | none |  | Document retailer expansion discovery checklist | `docs`, maybe `PRICE_COMPARISON_APP_PLAN.md` only | T002,T005 | Docs-only and can run in parallel after reviews pass; acceptance: checklist for MPREIS/REWE/Kaufland/Tesco discovery covering price availability, location dependence, promotions/app-only flags, source IDs, robots/terms notes, low-volume limits. |
| T013 | Blocked | pm-scoping-subagent | 2026-06-28 19:34 UTC+2 | task/T013-mpreis-low-volume-discovery |  | none |  | none |  | Add MPREIS low-volume discovery dry run | `backend/app/scrapers/mpreis.py`, `scripts/scrape_once.py`, tests/fixtures if applicable | T003,T005,T012 | Blocked on storage/quality/docs and low-volume request policy; dry-run only, no broad scrape. |

## In Progress

No tasks currently claimed.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

No blocked tasks.
