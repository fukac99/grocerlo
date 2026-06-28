# Grocery Saver Loop State

This file is the persistent memory for loop-style work on the grocery price comparison app. Future agent runs should read this file together with `PRICE_COMPARISON_APP_PLAN.md` before choosing the next task.

## Current Focus

Prioritize real BILLA Austria data ingest.

## Project Mode

Automatic builder loop every 10 minutes. Do not run recurring scrapes yet.

Loop coordination uses `LOOP_TASKS.md` as the task ledger and lightweight lock file. Tasks must be moved to `In Progress` before local work or subagent launch.

Historical completed tasks and version notes live in `LOOP_LOG.md` so `LOOP_TASKS.md` can stay focused on active, ready, blocked, open-PR, and review-gated work.

Each implementation task should use its own branch and open a GitHub pull request against `https://github.com/fukac99/grocerlo`. The repository connection task should run before other ready tasks that need pull requests.

Every loop run should check existing task pull requests and update `pr_status` plus `pr_last_checked` in `LOOP_TASKS.md`. Downstream tasks should treat prior PR-backed dependencies as complete only after their pull requests are merged.

Every loop run should also compare `LOOP_TASKS.md` against `PRICE_COMPARISON_APP_PLAN.md` and add missing actionable tasks. Every implementation pull request, and every PR that touches non-Markdown files, should track review status on the same task row for architecture, security, bugs, tests, maintainability, and fit with the overall plan. Markdown-only coordinator PRs do not require code review. Implementation and non-Markdown PRs are not merge-ready until their task row has `review_status: passed`. Agents must not merge pull requests unless the user explicitly asks; green PRs should be reported as ready for human review or merge.

Implementation PR descriptions must be detailed enough for review without reconstructing the diff. They should describe user-visible behavior, concrete code/module changes, API/CLI/UI/data-shape changes, tests run, risks, assumptions, and follow-up work.

Every loop run should start with a PM/scoping pass that plans a batch of executor-ready tasks with IDs, branches, dependencies, file/scope boundaries, acceptance criteria, and parallelization notes.

Every loop run should count completed tasks across `LOOP_LOG.md` plus active `Done` rows in `LOOP_TASKS.md`. At each new 100-task boundary, the coordinator must schedule a full-codebase security review before launching additional implementation work.

Last full-codebase security review boundary: 0 completed tasks.

## Retailer Status

| Retailer | Country | Status | Notes |
| --- | --- | --- | --- |
| BILLA | AT | Next | Best first target. Category listing exposes product cards, prices, unit prices, promotions, and pagination. |
| MPREIS | AT | Not started | Needs distinction between regular prices, app-only promotions, and store availability. |
| REWE | DE | Not started | May require selected delivery or pickup market. Store or region context must be recorded. |
| Kaufland | SK | Not started | Needs discovery to determine product listing and price availability. |
| Tesco | SK | Not started | Likely dynamic. May require Playwright and location/session setup. |

## Last Run

2026-06-28 user-prioritized real data ingest:

- User asked to prioritize a full data scrape so development can use real data ASAP.
- Existing status: BILLA is ready for controlled stored ingest; MPREIS is still dry-run/discovery-only and must not be stored yet.
- Added T040 as the top-priority operational task to run approved BILLA stored ingest, sanity report, normalization, and count reporting.
- T040 is blocked only on explicit human scope choice:
  - capped validation: `--store --limit-categories 2 --max-products 50 --max-products-per-category 30 --delay-seconds 2 --confirm-broad-run BILLA_FULL_INGEST`
  - broad run: `--store --all-categories --max-products 0 --max-products-per-category 30 --delay-seconds 2 --confirm-broad-run BILLA_FULL_INGEST`
- After T040 produces real normalized rows, prioritize T029 so the frontend can use the BILLA search API with real data.

2026-06-28 user-requested PR description detail:

- User asked that PR descriptions include detailed summaries of the code changes made.
- Started T039 to add a PR Description Standard to the loop protocol and standing state.
- Updated the open T030 PR description with a more explicit code-changes section.

2026-06-28 user correction on merge autonomy:

- User clarified that agents should not autonomously merge changes.
- Started T038 to persist the no-autonomous-merge rule in the loop protocol and state.
- Current open PRs: #32, #33, and #34 have green agent review gates and are waiting for human review/merge. Do not merge them without explicit user instruction.

2026-06-28 automatic loop tick after T015/T022/T032 merges:

- Confirmed PR #28, PR #29, and PR #30 are merged and no PRs are currently open.
- Started T037 to archive T015/T022/T032/T036 and refresh active task statuses.
- Marked T016, T030, and T034 ready after their dependencies merged.
- Next safe executor batch after T037 merges: T034 (frontend cheapest-retailer filter), T030 (reconciliation CLI), and T016 (comparison API) can run in parallel by current file scope. Defer T029 because it shares frontend comparison-table scope with T034.
- Completed-task count remains below the 100-task security-review boundary.

2026-06-28 automatic loop tick after T010/T021 completion:

- Confirmed PR #22 and PR #23 are merged and no PRs are currently open.
- Started T036 to archive T010/T021/T027/T031/T033/T035 and refresh active task statuses.
- Marked T022 and T029 ready after T021 and T010 merged.
- Next safe executor batch after T036 merges: T032 (frontend cheapest-cell highlight), T015 (backend matching), and T022 (ingest runbook) can run in parallel by file scope. Defer T029 because it shares frontend comparison-table scope with T032.
- Completed-task count remains below the 100-task security-review boundary.

2026-06-28 user-requested UI retailer filter scoping:

- Added T034 for retailer filtering that shows only products where the selected retailer is the cheapest available option.
- T034 depends on T032 so the filter can reuse the same cheapest-offer calculation as the row highlight.
- Acceptance: tied cheapest offers count for every tied retailer; missing offers and rows cheaper elsewhere are hidden for the selected retailer.
- Added T035 as the Markdown-only coordinator PR for this task-scoping update.

2026-06-28 user-requested UI scoping:

- Added T032 to highlight the cheapest supermarket offer in each frontend comparison row with a light-green cell.
- Acceptance: calculate the lowest available price per product/package row, highlight the cheapest retailer cell, highlight tied cheapest offers, and leave missing offers unhighlighted.
- Added T033 as the Markdown-only coordinator PR for this task-scoping update.

2026-06-28 user-requested review-gate change:

- Started T031 to exempt Markdown-only coordinator PRs from required code review.
- Planned CI/CD change: the agent review gate should pass automatically when a coordinator PR only changes `.md` files.
- Updated loop protocol so implementation and non-Markdown PRs still require `review_status: passed`, while Markdown-only coordinator PRs may use `review_status: none` or `not_required`.

2026-06-28 automatic loop tick:

- Confirmed PR #20 merged and synced local `main`.
- PM/scoping pass found 19 completed tasks, so the 100-task full-codebase security review is not due yet.
- Started T027 to archive merged tasks T008/T009/T013/T020/T023/T024/T026 and unblock T010, T021, and T015.
- Added T028 for MPREIS low-volume store/normalization, T029 for frontend-to-BILLA-search API wiring, and T030 for `reconcile_once.py`.
- Recommended next executor batch after T027 merges: T010 and T021 in parallel; defer T015 while T010 touches model/API scope.

2026-06-28 user-requested frontend table layout:

- User clarified the final visual comparison should use columns for `product`, `package`, then price, source link, and promotion per supermarket.
- Started T026 to align the mock frontend table with that target comparison shape.

2026-06-28 user-requested loop security cadence:

- Added a loop rule to schedule a full-codebase security review at every 100 completed tasks.
- Added T025 as the first blocked full-codebase security review milestone, due when the completed-task count reaches 100.
- The review scope covers the whole repository, dependencies/configuration, scraping/data-handling behavior, secrets exposure, CI/review gates, and generated artifacts.

2026-06-28 user-requested scoping:

- Scoped controlled full-ingest work without launching broad scraping yet.
- Added T021 for a controlled BILLA full-ingest workflow, blocked behind T009 so broad ingest has a sanity-report path.
- Added T022 for a full-ingest readiness runbook across available retailers, blocked behind BILLA ingest workflow and MPREIS discovery notes.
- Added T023 as ready work for a Next.js visual inspection shell using static sample data so app progress can be inspected before backend APIs are complete.

2026-06-28 automatic loop tick:

- Confirmed PR #11 merged after successful Postgres store validation.
- PM/scoping pass marked T008, T009, and T013 as ready; T010/T011/T015/T016 remain blocked behind normalization, discovery, matching, or API work.
- Started T019 to archive completed merged tasks, refresh stale PR statuses, and prepare the next executor batch.
- Recommended next executor batch is T008 and T013 in parallel; T009 can run separately or in parallel only if it avoids overlapping DB helper edits with T008.

2026-06-28 automatic loop tick:

- Docker daemon is still unavailable, so T003 remains blocked and PR #11 is intentionally not merge-ready.
- Confirmed PR #10 merged and PR #9 merged.
- Started T018 to correct stale active-ledger statuses on `main`: T003 blocked/changes requested, T012 merged, and T017 merged.
- No new executor work should start until T003 storage validation is unblocked or a PM pass scopes work independent of stored data.

2026-06-28 automatic loop tick:

- Confirmed PR #8 merged and synced local `main`.
- PM/scoping pass confirmed T003 and T012 are the only executor-ready tasks and can run in parallel with non-overlapping scopes.
- Refreshed stale merged PR bookkeeping for T007 and T014; archived T014 to `LOOP_LOG.md`.
- Added future blocked tasks T015 and T016 for rule-based matching and canonical comparison API work.
- Claimed T003 for Postgres `--store` validation and T012 for retailer discovery documentation.

2026-06-28 automatic loop tick:

- GitHub review gates for PR #6, PR #7, and PR #8 were failing.
- Fixed PR #6 and PR #7 by pushing their passed review statuses into their own PR branches, because the CI gate checks the PR branch copy of `LOOP_TASKS.md`.
- Added T014 for PR #8 so the coordinator ledger update PR has its own review-gated task row.
- Corrected T003 and T012 from `Ready` to `Blocked` because their PR-backed dependencies are not complete until T002 and T005 merge.
- PR #6 and PR #7 then merged; updated their `pr_status` values and marked T003 and T012 `Ready`.
- Merged latest `main` into PR #8 and resolved loop ledger/state conflicts.

2026-06-28 T005 raw product quality checks:

- Added pure raw product quality checks for missing names, missing prices, duplicate source IDs, suspicious prices/unit prices, and missing source URLs.
- Added focused pytest coverage for payload-shaped data, stored raw product-shaped data, duplicate scoping, suspicious values, and custom thresholds.
- Created T005 pull request: https://github.com/fukac99/grocerlo/pull/7.
- Next action: merge the T005 pull request after the review gate passes.

2026-06-28 T002 BILLA dry scrape validation:

- Ran the constrained BILLA dry scrape with 1 category and 3 products, without `--store`.
- Sample output looked plausible: product names, EUR prices, package sizes, source URLs, source IDs, and compact raw payload text were present.
- Unit price extraction worked where BILLA exposed a numeric unit price; variable-weight meat samples only exposed `per 1 kg` in raw text, so no numeric unit price was extracted.
- Opened T002 pull request: https://github.com/fukac99/grocerlo/pull/6.
- Next action: merge PR #6 after the review gate passes; if it merges, T003 can test the Postgres `--store` path.

2026-06-28 PR #6 review update:

- Review subagent completed T002 / PR #6 review with no blocking findings.
- Updated T002 `review_status` to `passed`.

2026-06-28 PR #7 review update:

- Review subagent completed T005 / PR #7 review with no blocking findings.
- Updated T005 `review_status` to `passed`.

2026-06-28 PM scoping result:

- PM scoping proposed future executor tasks T008-T013.
- Added T008-T013 to `LOOP_TASKS.md` with dependencies, file scopes, and acceptance notes.
- Most new tasks are blocked behind T002/T003/T005; T012 is docs-only and can run once active reviews clear.

2026-06-28 executor task completion:

- T002 completed implementation and opened PR #6: https://github.com/fukac99/grocerlo/pull/6.
- T005 completed implementation and opened PR #7: https://github.com/fukac99/grocerlo/pull/7.
- Both PRs are open with `review_status: pending`; next loop work should review them before merge.

2026-06-28 loop PM scoping update:

- Updated loop rules so every tick starts with a PM/scoping pass before executor agents are launched.
- PM scoping should add or refine batches of executor-ready tasks from the overall plan.

2026-06-28 PR review update:

- Review subagent completed PR #5 review with no blocking findings.
- Updated T007 `review_status` to `passed`.

2026-06-28 loop protocol update:

- Added T007 to update the loop protocol for plan expansion and PR review tasks.
- Updated coordinator rules so every tick re-reads the overall plan, adds missing actionable tasks, and tracks review status on implementation task rows.
- Removed separate review tasks from the protocol so pull requests cannot be treated as independent of their reviews.
- Added `LOOP_LOG.md` and archived fully completed historical tasks to keep `LOOP_TASKS.md` smaller.
- Clarified that multiple independent ready tasks can be launched as parallel subagents.
- Added a GitHub Actions review gate that fails PRs unless their `LOOP_TASKS.md` row has `review_status: passed`.
- Created T007 pull request: https://github.com/fukac99/grocerlo/pull/2.
- PR #2 merged before the same-task review correction landed; created follow-up PR #3 for that correction: https://github.com/fukac99/grocerlo/pull/3.
- PR #3 merged before the archive correction landed; created follow-up PR #4 for that correction: https://github.com/fukac99/grocerlo/pull/4.
- PR #4 merged before the CI gate landed; created follow-up PR #5 for that correction: https://github.com/fukac99/grocerlo/pull/5.

2026-06-28 automatic builder loop, immediate coordinator run:

- Restarted the automatic 10-minute loop.
- Claimed T006 for GitHub repository connection.
- Initialized local git on `main`.
- Added `origin` as `https://github.com/fukac99/grocerlo.git`.
- Created local bootstrap commits.
- Push and PR creation are blocked because HTTPS git authentication is not configured and `gh` is not installed.
- Switched `origin` to SSH as `git@github.com:fukac99/grocerlo.git`.
- Verified GitHub SSH authentication for `fukac99`.
- Pushed `main` to GitHub over SSH.
- PR creation remains blocked because `gh` is not installed.
- Installed GitHub CLI `gh` 2.95.0.
- `gh auth status` reports no logged-in GitHub hosts, so PR creation remains blocked until `gh auth login` is completed.
- `gh auth login` completed for GitHub account `fukac99`.
- Created T006 pull request: https://github.com/fukac99/grocerlo/pull/1.

2026-06-28 automatic builder loop, coordinator pass:

- Armed the automatic 30-minute loop.
- Added `LOOP_TASKS.md` as the coordination ledger and task lock file.
- Claimed T001 for environment setup and T004 for normalization utilities.
- T004 completed: added Decimal-based EUR price, package size, and unit price normalization utilities with pytest coverage.
- T001 completed: local backend environment, dependencies, and Playwright Chromium are installed; required imports passed.
- A low-volume BILLA dry scrape ran successfully with 1 category and 3 products.

2026-06-27 manual builder loop, iteration 2:

- Added BILLA scraper implementation with category discovery and low-volume product extraction.
- Added `scripts/scrape_once.py` one-off scraper CLI.
- CLI defaults to JSON dry-run output and only writes to Postgres when `--store` is passed.
- Added lazy DB imports so dry-run mode does not require database dependencies or a running database.
- Added `README.md` with local setup, migration, dry-run, and store commands.
- Ran `python3 -m compileall -q backend/app scripts`.
- Checked editor diagnostics for touched scraper and CLI files; no linter errors found.
- Tried `python3 scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3`; runtime is currently blocked because local scraper dependencies are not installed (`beautifulsoup4` provides `bs4`).

Previous run:

- Added backend and database skeleton.
- Added PostgreSQL Docker Compose service.
- Added FastAPI health endpoint.
- Added SQLAlchemy models for `scrape_runs`, `raw_products`, `retailer_products`, `canonical_products`, and `product_matches`.
- Added Alembic configuration and initial schema migration.
- Added shared scraper interface with `Category`, `RawProductPayload`, and `RetailerScraper`.
- Ran `python3 -m compileall -q backend/app backend/alembic`.
- Checked editor diagnostics for touched files; no linter errors found.

## Current Assumptions

- One-off scraping comes before recurring scheduling.
- Raw scraped data should be stored before normalization.
- Scrapers should extract source data, not fully interpret it.
- Product reconciliation should start with explainable rule-based matching.
- Low-volume scraping is preferred while site behavior and terms are being evaluated.

## Open Questions

- Do any target retailers require a selected market before prices are available?
- Which retailers expose stable source product IDs?
- Which fields are visible without login or account-specific context?
- How should app-only promotions be represented in comparisons?
- Should the first UI compare unmatched retailer products, matched canonical products, or both?

## Next Actions

1. Use `LOOP_TASKS.md` to claim eligible `Ready` tasks.
2. Use `LOOP_LOG.md` for archived completed dependencies and version history.
3. Run a PM/scoping pass to add or refine executor-ready task batches from the overall plan.
4. Re-read `PRICE_COMPARISON_APP_PLAN.md` and add missing actionable tasks.
5. Track review status on implementation task rows and require `review_status: passed` before merge readiness.
6. Archive fully complete tasks to `LOOP_LOG.md` once no longer needed in the active ledger.
7. Continue using SSH remote `git@github.com:fukac99/grocerlo.git`.
8. Merge reviewed PRs once checks pass, then update dependency statuses in `LOOP_TASKS.md`.
9. Claim T008 to normalize stored BILLA raw products into retailer products.
10. Claim T013 for MPREIS low-volume discovery, T009 for a stored-data sanity report if its scope avoids T008 DB helper edits, or T023 for a frontend visual inspection shell.

## Loop Log

### 2026-06-27

- Created `PRICE_COMPARISON_APP_PLAN.md`.
- Created this loop state file.
- Ran the first manual builder loop.
- Added the backend/database skeleton, initial schema migration, shared scraper interface, and local PostgreSQL Compose service.
- Verified Python syntax with `python3 -m compileall -q backend/app backend/alembic`.
- Checked editor diagnostics for touched files; no linter errors found.
- Current recommended next step is BILLA category discovery and low-volume raw product extraction.
- Ran the second manual builder loop.
- Added BILLA scraper discovery/extraction code and the `scripts/scrape_once.py` CLI.
- Added `README.md` with environment setup and scraper commands.
- Verified Python syntax with `python3 -m compileall -q backend/app scripts`.
- Checked editor diagnostics for touched scraper and CLI files; no linter errors found.
- BILLA dry-run execution is blocked until backend dependencies and Playwright Chromium are installed.
- Added `LOOP_TASKS.md` as the task ledger and lightweight lock file for automated loop coordination.
- Updated loop instructions to support a 30-minute automated builder loop and parallel subagents for independent claimed tasks.

### 2026-06-28

- Armed the automatic 30-minute builder loop.
- Added and started using `LOOP_TASKS.md` as the task ledger and lock file.
- T004 completed with price, package size, and unit price normalization utilities plus tests.
- T001 completed with backend dependencies installed, Playwright Chromium installed, required imports verified, and a successful low-volume BILLA dry scrape.
- Added T006 to connect the project to `https://github.com/fukac99/grocerlo`.
- Updated loop rules so future tasks use dedicated branches and GitHub pull requests.
- Added PR status tracking so each loop tick records whether previous task pull requests are open, merged, closed, blocked, or unknown.
- Restarted the automatic 10-minute loop and ran the coordinator once immediately.
- T006 is blocked after local git initialization because GitHub push/PR creation needs authentication tooling.
- Switched GitHub remote to SSH and pushed `main` successfully.
- Installed GitHub CLI `gh` 2.95.0.
- T006 remains blocked only on `gh auth login` for pull request creation.
- `gh` authentication completed for account `fukac99`; T006 branch and PR creation can proceed.
- Created T006 pull request: https://github.com/fukac99/grocerlo/pull/1.
- Added loop protocol updates for plan expansion, same-task review tracking, and parallel subagent launch rules.
- Added `LOOP_LOG.md` for archived tasks and version notes, and pruned completed rows from `LOOP_TASKS.md`.
- Added CI enforcement for same-task agent review status.
