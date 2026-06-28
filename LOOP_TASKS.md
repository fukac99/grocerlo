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
- Every implementation task with a pull request must track review under the same task row.
- Use review statuses: `none`, `pending`, `in_progress`, `passed`, `changes_requested`, or `blocked`.
- Do not consider a pull request merge-ready until its task has `review_status: passed`.
- The repository connection task may need to bootstrap the base branch first if the remote repository is empty.

## Tasks

| id | status | owner | started | branch | pull_request | pr_status | pr_last_checked | review_status | reviewer | task | files/scope | depends_on | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T002 | Ready |  |  | task/T002-billa-dry-scrape-validation |  | none |  | none |  | Run BILLA dry scrape and inspect sample output | `scripts/scrape_once.py`, `backend/app/scrapers/billa.py` | T001,T006 | Keep volume low: 1 category, max 3 products. |
| T003 | Ready |  |  | task/T003-postgres-store-path |  | none |  | none |  | Start Postgres, run migrations, and test `--store` path | `docker-compose.yml`, `backend/alembic`, database | T001,T002,T006 | Only after dry scrape output looks plausible. |
| T005 | Ready |  |  | task/T005-raw-product-quality-checks |  | none |  | none |  | Add raw product data quality checks | `backend/app`, `scripts` | T004,T006 | Check missing names, missing prices, duplicate source IDs, suspicious unit prices. |
| T007 | Done | coordinator | 2026-06-28 18:44 UTC+2 | task/T007-loop-planning-review-protocol | https://github.com/fukac99/grocerlo/pull/4 | open | 2026-06-28 18:55 UTC+2 | pending |  | Update loop protocol for plan expansion, same-task PR review tracking, and task archiving | `LOOP_TASKS.md`, `LOOP_LOG.md`, `LOOP_STATE.md`, `docs/LOOP_ENGINEERING.md` | T006 | PR #2 and #3 merged before the archive correction; active follow-up PR #4 must pass review before merge. |

## In Progress

No tasks currently claimed.

## Done

Archived in `LOOP_LOG.md`.

## Blocked

No blocked tasks.
