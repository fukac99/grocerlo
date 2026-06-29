# Loop Engineering For Grocery Saver

This document defines loop-style agent work for the grocery price comparison app.

The goal is not to scrape aggressively or make unchecked product matches. The goal is to create a repeatable workflow that reads current project state, performs a small useful increment, verifies it, and writes down what changed.

## Task Source Of Truth

Task management lives in Linear team `GRO`: `https://linear.app/grocerlo/team/GRO/active`.

Linear credentials are kept out of git in `credentials.txt`. Before using the Linear API from a local shell or subagent worktree, run `source credentials.txt` from the repository root so `LINEAR_TOKEN` is available.

Use these Linear states:

- `Todo`: ready and dependency-complete work.
- `In Progress`: claimed work.
- `In Review`: work has an open pull request waiting for review or merge.
- `Done`: complete work.
- `Human Review`: work that is waiting for explicit user input, approval, or a decision before an agent can safely continue. The user can add the input and move it to `Todo`.
- `Blocked`: blocked work that needs a policy, legal, account, location, anti-bot, dependency, or product-definition decision before it can proceed; add a comment explaining the blocker.
- `Backlog`: not-yet-actionable work that is not currently blocked by a concrete decision.

Each Linear issue should include branch, pull request URL, dependencies, file/scope boundaries, acceptance criteria, review status, checks run, and relevant follow-up notes.

## Loop Principles

- Read Linear team `GRO`, `LOOP_STATE.md`, and `PRICE_COMPARISON_APP_PLAN.md` before choosing work.
- Fetch the latest remote state before deciding no work is available.
- Dirty, stale, or task-branch local checkouts are not blockers; create a clean worktree from `origin/main` for new work.
- If any dependency-complete Linear `Todo` issue exists after PR/status checks and the security-review boundary check, claim or launch at least one eligible issue unless a concrete blocker is recorded.
- Claim work by moving the Linear issue to `In Progress` and adding an owner/start comment before starting work or launching a subagent.
- Before implementation, create or switch to the branch recorded in the Linear issue.
- Each task should end with a GitHub pull request against `https://github.com/fukac99/grocerlo`.
- Pull request descriptions must be detailed enough for a reviewer to understand exactly what changed without reconstructing the whole diff.
- Record pull request URLs and review status in the Linear issue.
- Merge policy: agents must not merge pull requests autonomously. Agents may open PRs, verify checks, update Linear metadata, and report merge readiness, but merging requires an explicit user instruction for that PR.
- Launch multiple subagents only for independent tasks that do not edit the same files and do not depend on each other.
- Open PRs only block new work when they are direct dependencies for the candidate issue or edit the same file/scope.
- Keep scraper runs low-volume until each retailer's behavior is understood.
- Store raw data before normalization.
- Keep matching explainable before adding embeddings.
- Use checks before claiming a scraper, normalizer, matcher, API, or UI workflow works.
- Update Linear and `LOOP_STATE.md` at the end of each loop run.
- Stop implementation work when blocked by legal, account, location, anti-bot, or product-definition decisions. Put blocked implementation issues in `Blocked`, but use `Human Review` when the next step is explicitly waiting for user input or approval. Keep or create policy/scoping issues in `Todo` when an agent can still produce a recommendation, decision-record draft, readiness summary, or narrower safe follow-up.

## Coordinator Protocol

Every automated loop tick should act as a coordinator before doing implementation work:

1. Fetch the latest remote state.
2. Run `source credentials.txt` from the repository root before Linear API calls.
3. Read Linear team `GRO`, `LOOP_STATE.md`, and `PRICE_COMPARISON_APP_PLAN.md`.
4. Check Linear issues with pull request URLs using `gh pr view` or GitHub API.
5. Update the Linear issue state/comment with PR status, review status, and last checked time.
6. Run a PM/scoping pass before executor assignment.
7. Compare the overall plan, Linear issues, and current project state; create or refine missing actionable Linear issues.
8. If implementation work is blocked by legal, account, location, anti-bot, retailer policy, or product-definition decisions, ensure the implementation issue is in `Blocked` and there is a separate `Todo` policy/scoping issue with concrete acceptance criteria for resolving or documenting the blocker.
9. Use `Human Review` only when the next action is explicitly the user's input, approval, or decision. The issue comment should state the exact question, acceptable answer shape, and which issue can move to `Todo` after the user answers.
10. When the user adds a decision to a `Human Review` issue and moves it to `Todo`, apply the decision, update dependent issues, and mark the completed `Human Review` issue `Done`. Do not move reviewed decision issues back to `Human Review`.
11. Do not leave Linear with zero `Todo` issues unless every remaining blocker is truly waiting in `Human Review` and no agent can produce a recommendation, decision-record draft, readiness summary, or narrower safe follow-up.
12. Ensure each PM-scoped issue has dependencies, file/scope boundaries, branch name, acceptance criteria, and parallelization notes.
13. Count completed work from Linear `Done` issues. At each new 100-task boundary, schedule a full-codebase security review before launching additional implementation work.
14. For each implementation or non-Markdown PR with no review status, set review status to pending in Linear.
15. Identify Linear `Todo` issues whose dependencies are complete.
16. Treat a dependency as complete only when its Linear issue is `Done` and any linked PR is merged, unless the task was explicitly completed before the branch/PR rule.
17. Group ready issues by file/scope.
18. Select one or more independent issues.
19. Move each selected issue to `In Progress` and add an owner/start comment.
20. Create or switch to the task branch. If the main checkout is dirty or stale, create a clean worktree from `origin/main`.
21. Launch multiple executor subagents at the same time when issues are independent.
22. Keep one task local if it involves coordination, PM scoping, environment setup, GitHub setup, or state-file updates.
23. When implementation finishes, push the task branch and open a GitHub pull request using the PR Description Standard below.
24. Record the pull request URL, PR status, review status, and checks in the Linear issue.
25. If required checks pass and review status is passed or not required, report that the pull request is ready for user-directed merge and keep the Linear issue in `In Review`.
26. If the PR is not ready for merge, move the Linear issue to `In Review`, `Blocked`, or `Human Review` with a blocker/comment as appropriate.
27. Record checks, PR statuses, review statuses, merge readiness, PM decisions, failures, next actions, and any reason no ready issue was launched in `LOOP_STATE.md`.

## PR Description Standard

Every implementation PR should include:

- `Summary`: 2-5 bullets that name the feature/fix and user-visible or operator-visible behavior.
- `Code changes`: concrete bullets by area or file group, including new modules, changed functions/components, API routes, scripts, models, data flow, CLI flags, or UI states.
- `Behavior and compatibility`: defaults, edge cases, data safety, backwards compatibility, and intentionally deferred work.
- `Tests`: exact commands run and what each validates.
- `Review notes`: risks, assumptions, follow-up issues, and areas where the reviewer should pay special attention.

Avoid vague summaries like "add API" or "update UI" without explaining the actual route, component behavior, data shape, or command semantics.

## Builder Loop Prompt

```text
Read Linear team GRO, LOOP_STATE.md, and PRICE_COMPARISON_APP_PLAN.md. Act as the loop coordinator. Fetch latest remote state, check Linear issues with linked PRs, update Linear state/comments, run a PM/scoping pass, claim at least one dependency-complete Todo issue when available, use clean worktrees for new tasks, open PRs, and report merge-ready PRs for explicit user-directed merge. Do not merge pull requests autonomously, force-merge, or bypass branch protection. Update Linear plus LOOP_STATE.md with progress, merge readiness, and blockers. Stop if blocked by GitHub access, scraping legality, account, store-location, or matching decision.
```

## Scraper Quality Loop

Use this after at least one scraper exists.

```text
Read LOOP_STATE.md and retailer notes. Run one low-volume scrape for the current retailer. Store raw output only when that retailer/storage scope is approved. Run normalization and data quality checks. Report product count, missing fields, duplicate source IDs, parsing failures, suspicious prices, and site-behavior changes. Update LOOP_STATE.md, retailer notes, and the relevant Linear issue. Do not increase scraping volume unless explicitly approved.
```

## Reconciliation Loop

Use this after at least two retailers have normalized product data.

```text
Read LOOP_STATE.md and matching notes. Generate candidate matches for normalized retailer products. Score candidates using brand, name similarity, package size, category, and unit compatibility. Auto-match only high-confidence candidates. Write uncertain candidates to a review queue. Report likely false positives and false negatives. Update LOOP_STATE.md and the relevant Linear issue with matching quality notes.
```

## GitHub Branch Protection

Enable branch protection for `main` in GitHub and require the status check named `Agent Review Gate / Require agent review status`.

The review gate should not depend on Markdown task ledgers. Until direct Linear API validation is configured in CI, the gate may allow Markdown-only documentation PRs and require a passed review marker in pull request metadata for non-Markdown PRs.

## Stop Conditions

Stop the loop and ask for direction when:

- A retailer requires login or account-specific data.
- Prices require selecting a store, postal code, or delivery region and no default has been chosen.
- The site appears to block or challenge automated access.
- Terms or robots guidance raise concerns.
- Product matching has ambiguous semantics that affect user-facing comparisons.
- A check fails in a way that suggests stored data may be misleading.
