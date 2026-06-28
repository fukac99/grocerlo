# Grocery Saver Loop Log

This file keeps historical loop progress out of the active task ledger.

Use `LOOP_TASKS.md` for active, blocked, ready, in-progress, open-PR, or review-gated work. When a task is fully complete and no longer needed for dependency checks, archive it here.

## Archived Tasks

| id | completed | branch | pull_request | summary |
| --- | --- | --- | --- | --- |
| T001 | 2026-06-28 |  |  | Set up local backend environment, installed backend dependencies and Playwright Chromium, verified imports, and ran a low-volume BILLA dry scrape. |
| T004 | 2026-06-28 |  |  | Added Decimal-based EUR price, package size, and unit price normalization utilities with focused pytest coverage. |
| T006 | 2026-06-28 | `task/T006-connect-github-repository` | https://github.com/fukac99/grocerlo/pull/1 | Connected the project to GitHub, initialized `main`, pushed over SSH, installed/authenticated `gh`, and established the PR workflow. |

## Version Notes

### 2026-06-28

- Created the initial product plan in `PRICE_COMPARISON_APP_PLAN.md`.
- Added loop coordination docs in `docs/LOOP_ENGINEERING.md`.
- Added backend/database skeleton, BILLA scraper, one-off scrape CLI, normalization utilities, and GitHub PR workflow.
- Switched loop task tracking to active-task-only context with archived history in this file.
