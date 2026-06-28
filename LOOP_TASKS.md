# Grocery Saver Loop Tasks

This file is the task ledger and lightweight lock file for automated loop runs.

Before a loop run starts work, it must move any claimed task from `Ready` to `In Progress` and set the `owner` field. This prevents two subagents from choosing the same task.

## Rules

- Only tasks with `status: Ready` can be claimed.
- Set `status: In Progress` before launching a subagent or starting work.
- Set `owner` to the coordinator or subagent role that claimed the task.
- Set `started` when a task is claimed.
- Move finished tasks to `Done`.
- Move blocked tasks to `Blocked` with a short reason.
- Do not launch parallel tasks that edit the same files unless they are explicitly coordinated.
- Prefer one coordinator task plus multiple implementation subagents only when tasks are independent.
- Each implementation task should happen on its own branch and end with a GitHub pull request against the project repository.
- Use branch names like `task/T002-billa-dry-scrape-validation`.
- Record the branch and pull request URL in this ledger.
- On every loop run, check existing pull requests and update `pr_status` and `pr_last_checked`.
- Use PR statuses: `none`, `open`, `merged`, `closed`, `blocked`, or `unknown`.
- On every loop run, compare `LOOP_TASKS.md` against `PRICE_COMPARISON_APP_PLAN.md` and add missing actionable tasks.
- Every implementation task with a pull request must track review under the same task row.
- Use review statuses: `none`, `pending`, `in_progress`, `passed`, `changes_requested`, or `blocked`.
- Do not consider a pull request merge-ready until its task has `review_status: passed`.
- The repository connection task may need to bootstrap the base branch first if the remote repository is empty.

## Tasks

| id | status | owner | started | branch | pull_request | pr_status | pr_last_checked | review_status | reviewer | task | files/scope | depends_on | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T001 | Done | env-setup-subagent | 2026-06-28 18:06 UTC+2 |  |  | none |  | none |  | Set up local backend environment and install dependencies | `.venv`, backend deps, Playwright Chromium |  | Completed before branch/PR rule; imports verified and low-volume BILLA dry scrape ran successfully. |
| T002 | Ready |  |  | task/T002-billa-dry-scrape-validation |  | none |  | none |  | Run BILLA dry scrape and inspect sample output | `scripts/scrape_once.py`, `backend/app/scrapers/billa.py` | T001,T006 | Keep volume low: 1 category, max 3 products. |
| T003 | Ready |  |  | task/T003-postgres-store-path |  | none |  | none |  | Start Postgres, run migrations, and test `--store` path | `docker-compose.yml`, `backend/alembic`, database | T001,T002,T006 | Only after dry scrape output looks plausible. |
| T004 | Done | normalization-subagent | 2026-06-28 18:06 UTC+2 |  |  | none |  | none |  | Add EUR price and unit normalization utilities | `backend/app/normalization` |  | Completed before branch/PR rule with Decimal-based utilities and focused pytest coverage. |
| T005 | Ready |  |  | task/T005-raw-product-quality-checks |  | none |  | none |  | Add raw product data quality checks | `backend/app`, `scripts` | T004,T006 | Check missing names, missing prices, duplicate source IDs, suspicious unit prices. |
| T006 | Done | coordinator | 2026-06-28 18:31 UTC+2 | task/T006-connect-github-repository | https://github.com/fukac99/grocerlo/pull/1 | open | 2026-06-28 18:39 UTC+2 | none |  | Connect this project to `https://github.com/fukac99/grocerlo` | git remote, branch strategy, GitHub PR setup |  | Completed before same-row review rule; local git repo initialized, `origin` switched to SSH, `main` pushed to GitHub, `gh` installed and authenticated. |
| T007 | Done | coordinator | 2026-06-28 18:44 UTC+2 | task/T007-loop-planning-review-protocol | https://github.com/fukac99/grocerlo/pull/3 | open | 2026-06-28 18:53 UTC+2 | pending |  | Update loop protocol for plan expansion and same-task PR review tracking | `LOOP_TASKS.md`, `LOOP_STATE.md`, `docs/LOOP_ENGINEERING.md` | T006 | PR #2 merged before the same-task review correction; active follow-up PR #3 must pass review before merge. |

## In Progress

No tasks currently claimed.

## Done

- Created product plan in `PRICE_COMPARISON_APP_PLAN.md`.
- Created loop guide in `docs/LOOP_ENGINEERING.md`.
- Added backend/database skeleton.
- Added BILLA scraper and one-off scrape CLI.
- T001: Set up local backend environment, installed dependencies, installed Playwright Chromium, and ran low-volume BILLA dry scrape.
- T004: Added EUR price, package size, and unit price normalization utilities with tests.

## Blocked

No blocked tasks.
