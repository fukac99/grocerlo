# Loop Engineering For Grocery Saver

This document defines how to use loop-style agent work for the grocery price comparison app.

The goal is not to make the agent scrape aggressively or make unchecked product matches. The goal is to create a repeatable workflow that reads project state, performs a small useful increment, verifies it, and writes down what changed.

## Loop Principles

- Read `LOOP_STATE.md` and `PRICE_COMPARISON_APP_PLAN.md` before choosing work.
- Read `LOOP_TASKS.md` before claiming or launching work.
- Prefer the smallest useful next task.
- Claim tasks by moving them to `In Progress` before starting work or launching a subagent.
- Before implementation, create or switch to the task branch recorded in `LOOP_TASKS.md`.
- Each task should end with a GitHub pull request against `https://github.com/fukac99/grocerlo`.
- Record the branch name and pull request URL in `LOOP_TASKS.md`.
- On every loop run, check existing task pull requests and update `pr_status` plus `pr_last_checked`.
- On every loop run, compare `LOOP_TASKS.md` with `PRICE_COMPARISON_APP_PLAN.md` and add missing actionable tasks.
- Every implementation PR should get a separate review task for architecture, security, bugs, tests, maintainability, and fit with the overall plan.
- Review tasks do not recursively create review tasks unless the review task changes code or workflow files.
- Launch multiple subagents only for independent tasks that do not edit the same files and do not depend on each other.
- Keep scraper runs low-volume until each retailer's behavior is understood.
- Store raw data before normalization.
- Keep matching explainable before adding embeddings.
- Use checks before claiming a scraper, normalizer, or matcher works.
- Update `LOOP_TASKS.md` and `LOOP_STATE.md` at the end of each loop run.
- Stop when blocked by legal, account, location, anti-bot, or product-definition decisions.

## Coordinator Protocol

Every automated loop tick should act as a coordinator before doing implementation work:

1. Read `LOOP_TASKS.md`, `LOOP_STATE.md`, and `PRICE_COMPARISON_APP_PLAN.md`.
2. Check every row with a `pull_request` URL using `gh pr view` or GitHub API.
3. Update `pr_status` and `pr_last_checked` for those rows before claiming new work.
4. Re-read the overall plan and compare it with the task ledger.
5. Add missing actionable tasks for the next plan steps, avoiding duplicates and preserving dependencies.
6. For every implementation task that has an open pull request and no review task, add a separate review task.
7. Identify tasks with `status: Ready` whose dependencies are complete.
8. Treat a dependency as complete only when its task is `Done` and its `pr_status` is `merged`, unless the task was explicitly completed before the branch/PR rule and has `pr_status: none`.
9. Treat review tasks as eligible when the implementation PR they review is open, unless the task notes say to wait for merge.
10. Group ready tasks by file/scope.
11. Select one or more independent tasks.
12. Move each selected task to `In Progress`, set `owner`, and set `started`.
13. Ensure the task has a branch name. If it does not, add one before launch.
14. Create or switch to the task branch before implementation tasks.
15. Launch multiple subagents at the same time when there are independent ready tasks; do not assign two agents to the same files/scope.
16. Keep one task local if it involves coordination, environment setup, GitHub setup, or state-file updates.
17. When implementation work finishes, push the task branch and open a GitHub pull request.
18. Record the pull request URL, `pr_status: open`, and `pr_last_checked` in `LOOP_TASKS.md`.
19. For each new implementation PR, create a review task if one does not already exist.
20. Move tasks to `Done` or `Blocked`.
21. Record checks, PR statuses, newly planned tasks, failures, and next actions in `LOOP_STATE.md`.

Do not launch two subagents against the same file/scope unless the task ledger explicitly says the work is coordinated.

If the GitHub repository is empty or the local checkout is not a git repository, run the repository connection task first. That task should establish the base branch and remote before other implementation tasks try to open pull requests.

## Main Loops

### Builder Loop

Use this while the MVP is still being built.

Prompt:

```text
Read LOOP_TASKS.md, LOOP_STATE.md, and PRICE_COMPARISON_APP_PLAN.md. Act as the loop coordinator. First check existing task pull requests and update pr_status plus pr_last_checked in LOOP_TASKS.md. Re-read the overall plan and add missing actionable tasks, avoiding duplicates. For every implementation PR without a review task, add a separate review task for architecture, security, bugs, tests, maintainability, and fit with the plan. Claim eligible Ready tasks by marking them In Progress before starting work. Use the task branch recorded in LOOP_TASKS.md, or add one before work starts. If multiple independent tasks are available, launch multiple subagents at the same time; do not assign two agents to the same files/scope. Each completed implementation task should push its branch and open a GitHub pull request, then record the PR URL, pr_status, and pr_last_checked in LOOP_TASKS.md. Review tasks should review the target PR and report findings; they do not spawn review tasks unless they change files. Implement or coordinate scoped changes. Run relevant checks. Update LOOP_TASKS.md and LOOP_STATE.md with progress, PR statuses, newly planned tasks, failures, and next actions. Stop if blocked by a decision about GitHub access, scraping legality, accounts, store location, or product matching semantics.
```

Recommended cadence:

- Manual at first.
- Later, every few hours only if the project has clear tests and small tasks.

Good tasks for this loop:

- Add database schema.
- Add scraper interface.
- Implement one retailer discovery step.
- Add normalization utilities.
- Add data quality checks.
- Build a small API endpoint.
- Improve the comparison table.

### Scraper Quality Loop

Use this after at least one scraper exists.

Prompt:

```text
Read LOOP_STATE.md and retailer notes. Run one low-volume scrape for the current retailer. Store raw output. Run normalization and data quality checks. Report product count, missing fields, duplicate source IDs, parsing failures, suspicious prices, and site-behavior changes. Update LOOP_STATE.md and scraper notes. Do not increase scraping volume unless explicitly approved.
```

Recommended cadence:

- Manual during development.
- Daily at most once the scraper is stable.

Checks this loop should run:

- Raw product count is non-zero.
- Required fields are present for most products.
- Prices parse correctly.
- Unit prices parse correctly where available.
- Duplicate source IDs are expected or explained.
- Source URLs are stored.
- Promotions are preserved as raw text.

### Reconciliation Loop

Use this after at least two retailers have normalized product data.

Prompt:

```text
Read LOOP_STATE.md and matching notes. Generate candidate matches for normalized retailer products. Score candidates using brand, name similarity, package size, category, and unit compatibility. Auto-match only high-confidence candidates. Write uncertain candidates to a review queue. Report likely false positives and false negatives. Update LOOP_STATE.md with matching quality notes.
```

Recommended cadence:

- Manual until matching quality is understood.
- Later, after each successful scrape run.

Checks this loop should run:

- High-confidence matches have compatible brand and package size.
- Private-label products are not matched to branded products by generic names alone.
- Organic and non-organic products are not merged unless explicitly intended.
- Loose produce is treated carefully.

## Suggested Cursor Commands

Manual builder run:

```text
Read LOOP_TASKS.md, LOOP_STATE.md, and PRICE_COMPARISON_APP_PLAN.md. Act as the loop coordinator. First check existing task pull requests and update pr_status plus pr_last_checked in LOOP_TASKS.md. Re-read the overall plan and add missing actionable tasks, avoiding duplicates. For every implementation PR without a review task, add a separate review task for architecture, security, bugs, tests, maintainability, and fit with the plan. Claim eligible Ready tasks by marking them In Progress before starting work. Use the task branch recorded in LOOP_TASKS.md, or add one before work starts. If multiple independent tasks are available, launch multiple subagents at the same time; do not assign two agents to the same files/scope. Each completed implementation task should push its branch and open a GitHub pull request, then record the PR URL, pr_status, and pr_last_checked in LOOP_TASKS.md. Review tasks should review the target PR and report findings; they do not spawn review tasks unless they change files. Implement or coordinate scoped changes. Run relevant checks. Update LOOP_TASKS.md and LOOP_STATE.md with progress, PR statuses, newly planned tasks, failures, and next actions.
```

In-session recurring builder loop:

```text
/loop 10m Read LOOP_TASKS.md, LOOP_STATE.md, and PRICE_COMPARISON_APP_PLAN.md. Act as the loop coordinator. First check existing task pull requests and update pr_status plus pr_last_checked in LOOP_TASKS.md. Re-read the overall plan and add missing actionable tasks, avoiding duplicates. For every implementation PR without a review task, add a separate review task for architecture, security, bugs, tests, maintainability, and fit with the plan. Claim eligible Ready tasks by marking them In Progress before starting work. Use the task branch recorded in LOOP_TASKS.md, or add one before work starts. If multiple independent tasks are available, launch multiple subagents at the same time; do not assign two agents to the same files/scope. Each completed implementation task should push its branch and open a GitHub pull request, then record the PR URL, pr_status, and pr_last_checked in LOOP_TASKS.md. Review tasks should review the target PR and report findings; they do not spawn review tasks unless they change files. Implement or coordinate scoped changes. Run relevant checks. Update LOOP_TASKS.md and LOOP_STATE.md with progress, PR statuses, newly planned tasks, failures, and next actions. Stop if blocked by GitHub access, scraping legality, account, store-location, or matching decision.
```

Daily scraper quality loop:

```text
/loop 1d Read LOOP_STATE.md. Run one low-volume scrape for the current retailer. Store raw output, normalize it, run data quality checks, and update LOOP_STATE.md with counts, parse failures, suspicious data, and next action. Do not increase scraping volume unless explicitly approved.
```

## State Updates

Every loop run should update `LOOP_STATE.md` with:

- What was attempted.
- What changed.
- What checks were run.
- What failed or was skipped.
- What the next smallest task should be.
- Any blocker requiring human decision.

Every loop run should update `LOOP_TASKS.md` with:

- Claimed tasks moved to `In Progress`.
- Completed tasks moved to `Done`.
- Blocked tasks moved to `Blocked` with the reason.
- Newly discovered tasks added as `Ready` if they are actionable.
- Branch names recorded for all new implementation tasks.
- Pull request URLs recorded for completed tasks.
- Pull request status and last checked timestamp updated on every loop run.
- Missing tasks from the overall plan added with dependencies.
- Review tasks added for implementation pull requests.

## Stop Conditions

Stop the loop and ask for direction when:

- A retailer requires login or account-specific data.
- Prices require selecting a store, postal code, or delivery region and no default has been chosen.
- The site appears to block or challenge automated access.
- Terms or robots guidance raise concerns.
- Product matching has ambiguous semantics that affect user-facing comparisons.
- A check fails in a way that suggests stored data may be misleading.

## First Recommended Loop Run

The first builder loop should:

1. Set up the backend/database skeleton.
2. Add initial models and migrations.
3. Add the shared scraper interface.
4. Leave BILLA scraping implementation as the next task if the skeleton is not already complete.
