# Grocery Saver Loop State

This file is persistent project context for loop-style work on the grocery price comparison app. Task management lives in Linear team `GRO`: `https://linear.app/grocerlo/team/GRO/active`.

## Current Focus

Prioritize safe all-retailer raw-data ingest after BILLA dedupe cleanup while continuing focused Grocerlo UX improvements.

## Project Mode

Automatic builder loop every 10 minutes. Do not run recurring scrapes yet.

Loop coordination uses Linear as the task source of truth. Agents should claim work by moving a Linear issue to `In Progress`, update the issue with branch/PR/check status, and move it to `In Review`, `Done`, or `Backlog` as appropriate.

Every loop run should:

- Fetch latest remote state before deciding no work is available.
- Read Linear team `GRO`, this state file, and `PRICE_COMPARISON_APP_PLAN.md`.
- Check Linear issues with linked pull requests and update issue comments/state.
- Start with a PM/scoping pass that creates or refines actionable Linear issues.
- Claim or launch at least one dependency-complete Linear `Todo` issue unless a concrete blocker is recorded.
- Use clean worktrees from `origin/main` when the main checkout is dirty, stale, or on another task branch.
- Avoid launching parallel work that edits the same file/scope.
- Merge policy: agents must not merge pull requests autonomously. Agents may open PRs, verify checks, update Linear metadata, and report merge readiness, but merging requires an explicit user instruction for that PR.

Implementation PR descriptions must describe user-visible behavior, concrete code/module changes, API/CLI/UI/data-shape changes, tests run, risks, assumptions, and follow-up work.

Every loop run should count completed work from Linear `Done` issues. At each new 100-task boundary, schedule a full-codebase security review before launching additional implementation work.

Last full-codebase security review boundary: 0 completed tasks.

## Retailer Status

| Retailer | Country | Status | Notes |
| --- | --- | --- | --- |
| BILLA | AT | Clean baseline complete | Controlled post-dedupe stored baseline `scrape_run_id=3` produced 3 raw rows, 3 normalized rows, 3 distinct source IDs, and no duplicate-source-ID issues. |
| MPREIS | AT | Report-only normalization approved; broader downstream blocked | `scrape_run_id=4` stored 3 `no_market_selected` raw rows from one page. Sanity report found 0 quality issues and 0 missing key fields. Report-only normalization may validate parsing for these rows, but matching, comparison UI use, broader volume, and market-selected scraping remain blocked. |
| REWE | DE | Discovery-only; storage blocked | Public no-location pages expose metadata/article numbers but not numeric prices. T074 documents that no location-priced dry-run context is approved yet; price scraping needs an exact human-approved location/market/service context first. |
| Kaufland | SK | Human Review; storage blocked | Discovery and policy recommendation are complete in PR #69. Runtime scraping, storage, matching, API use, and UI exposure remain blocked until a human decides whether a no-storage leaflet/store-offer dry run is useful and which default-store or approved-store context is allowed. |
| Tesco | SK | Human Review; storage blocked | Discovery and policy recommendation are complete in PR #70. Runtime scraping, storage, normalization, matching, API use, and UI exposure remain blocked until a human decides whether account/location/session-specific delivery offers are in scope and approves exact test context, caps, and legal/terms comfort. |
| Tegut on Amazon | DE | Discovery-only; storage blocked | Amazon-hosted grocery surface is postcode/account/platform scoped. T073 found no safe no-location price capture path; any next step needs explicit Amazon/Tegut policy approval. |

## Last Run

2026-06-29 coordinator pass / T084 Linear state refresh:

- Fetched latest remote state from `origin/main`. The primary checkout is dirty and on another task branch, so T084 used a clean worktree from `origin/main`.
- Checked GitHub PRs. PR #68 (`task/T079-mpreis-report-only-normalization`), PR #69 (`task/T080-kaufland-sk-source-policy-recommendation`), and PR #70 (`task/T081-tesco-sk-source-policy-recommendation`) are open, clean, and green on their latest Agent Review Gate runs. They remain waiting for user-directed review/merge and must not be merged autonomously.
- Loaded Linear credentials with `source credentials.txt` before Linear API calls. Confirmed `GRO-48`, `GRO-49`, and `GRO-50` are `In Review`; `GRO-51` and `GRO-52` are `Human Review`; and `GRO-53` / T084 was the only dependency-complete `Todo`.
- PM/scoping result: no new Linear issue was needed before executor work because T084 already covered the useful coordinator/state refresh. Claimed `GRO-53` and kept the scope to `LOOP_STATE.md` only to avoid overlapping PR #68 implementation files or PR #69/#70 retailer notes.
- Current blockers: Kaufland Slovakia and Tesco Slovakia implementation work requires explicit human policy decisions. Broader MPREIS downstream use remains blocked beyond the narrow report-only validation in PR #68. Non-BILLA stored ingest remains blocked until the relevant policy and dry-run gates are satisfied.
- Checks: `git diff --check`.
- Next action: open the T084 PR, update Linear with PR/check metadata, and keep it `In Review` until user-directed merge. After PR #68-#70 and T084 are reviewed by the user, the next loop should either act on the Kaufland/Tesco Human Review decisions or create another narrow `Todo` recommendation issue if a blocker can be documented without implementation.

2026-06-29 coordinator pass / T063 all-retailer readiness summary:

- Fetched latest remote state from `origin/main`. The local primary checkout is dirty on `task/T042-billa-scale-scrape-dedupe`, so T063 used a clean worktree from `origin/main`.
- Checked GitHub PRs. `gh pr list` reported no open pull requests. PR #64, PR #65, and PR #66 are merged on GitHub; this coordinator pass did not merge any pull request.
- Loaded Linear credentials with `source credentials.txt` before Linear API calls. Confirmed Linear states include `Blocked` and `Human Review`, moved `GRO-44` / T074 and `GRO-45` / T075 to `Done` after observing their PRs merged, and claimed `GRO-38` / T063.
- PM/scoping result: `GRO-38` / T063 and `GRO-48` / T079 were the active Todo issues. Claimed T063 because it is an independent readiness-summary task that can document next gates without overlapping the MPREIS report-only normalization implementation scope.
- Added an all-retailer raw-ingest readiness summary to `docs/retailer-ingest-runbook.md`.
- Readiness decision: BILLA `scrape_run_id=3` remains the only reusable stored/normalized baseline. MPREIS `scrape_run_id=4` remains quarantined and is approved only for report-only normalization via `GRO-48` / T079. REWE, Kaufland Slovakia, Tesco Slovakia, and Tegut on Amazon remain storage-blocked behind explicit location/account/platform or policy decisions.
- Linear count after claiming T063: 32 `Done`, 8 `Blocked`, 1 `Canceled`, 1 `In Progress`, and 1 `Todo` (`GRO-48` / T079). The completed count remains below the 100-task full-codebase security review boundary.
- Opened PR #67: `https://github.com/fukac99/grocerlo/pull/67`. PR #67 is open, clean, mergeable, and its Agent Review Gate passed with `review_status: not_required` because it is Markdown-only coordinator/readiness documentation.
- Checks: `git diff --check`; `python3 -m compileall -q backend/app scripts`; Cursor diagnostics for touched Markdown files.
- Next action: PR #67 is ready for user-directed review/merge and must not be merged autonomously. `GRO-48` / T079 remains Todo as the next independent implementation task for MPREIS report-only normalization.

2026-06-29 coordinator pass / T075 MPREIS downstream policy:

- Fetched latest remote state from `origin/main`. The local primary checkout is dirty on `task/T042-billa-scale-scrape-dedupe`, so T075 used a clean worktree from `origin/main`.
- Checked GitHub PRs. PR #64 and PR #65 are merged on GitHub; this coordinator pass did not merge either PR. No pull requests were open when checked with `gh pr list`.
- Loaded Linear credentials with `source credentials.txt` before Linear API calls, queried team `GRO`, and confirmed `Blocked` and `Human Review` states exist.
- PM/scoping result: `GRO-45` / T075 and `GRO-38` / T063 were the active Todo issues. Claimed T075 because it is an independent policy/scoping task that can unblock a narrower safe MPREIS follow-up without overlapping the dirty checkout.
- T075 decision: the quarantined MPREIS `scrape_run_id=4` rows may be normalized only for report-only parser and data-quality validation. The output must remain labeled non-comparable and must not feed matching, comparison APIs, or UI surfaces.
- Broader MPREIS downstream use remains blocked. A human-approved market, postal code, pickup branch, delivery area, or delivery slot is required before MPREIS rows can be matched, shown in comparison UI, used as a price baseline, or expanded beyond the existing capped validation page.
- App-only labels and app-only numeric prices remain promotion metadata and must not become regular comparable price fields.
- Created `GRO-48` / T079 as a Todo follow-up for narrow report-only normalization of `scrape_run_id=4`, with no scraping and no new raw rows. Added a blocker comment to `GRO-34` / T059 so broader controlled stored ingest and reusable normalization/reporting remain blocked.
- Checks: `git diff --check` and `python3 -m compileall -q backend/app scripts`.
- Next action: open the T075 PR, update Linear with PR/check metadata, and keep it `In Review` until user-directed merge. `GRO-38` / T063 remains Todo for the next readiness-summary pass.

2026-06-29 coordinator pass / T074 REWE location policy:

- Fetched latest remote state from `origin/main`. The local primary checkout is dirty on `task/T042-billa-scale-scrape-dedupe`, so T074 used a clean worktree from `origin/main`.
- Checked GitHub PRs. PR #64 (`task/T078-keep-pm-policy-todo`) is open, clean, and green; it remains waiting for user-directed review/merge and was not merged.
- Loaded Linear credentials with `source credentials.txt` before Linear API calls, queried team `GRO`, and found Todo policy/scoping issues including `GRO-44` / T074, `GRO-45` / T075, and `GRO-38` / T063.
- Claimed `GRO-44` / T074 because its dependencies are Done, it does not overlap open PR #64, and it can document or resolve a blocker without approving implementation prematurely.
- T074 decision: no approved location-priced REWE dry-run context exists yet. REWE price capture and storage remain blocked until a human records the exact postal code, market/service context, run purpose, allowed URLs, caps, delay/jitter, and output expectations.
- Added a safe no-location metadata-only boundary for future REWE scoping: at most three public product pages, no storage, no normalization, no matching, no comparison UI use, preserve missing numeric prices, and stop before satisfying location/account/cart/checkout prompts.
- Opened PR #65: `https://github.com/fukac99/grocerlo/pull/65`. PR #65 Agent Review Gate passed with `review_status: not_required` because it is Markdown-only policy documentation.
- Updated Linear `GRO-44` to `In Review` with branch, PR, checks, review status, and no-autonomous-merge metadata. Added a blocker comment to `GRO-31` / T056 explaining that price-capturing REWE scraper work remains blocked.
- Checks: `python3 -m compileall -q backend/app scripts`; Cursor diagnostics for touched Markdown files.
- Next action: either user-directed review/merge of PR #64 and PR #65, or claim `GRO-45` / T075 to decide MPREIS downstream-use policy. Do not merge any PR unless explicitly instructed for that PR.

2026-06-29 coordinator pass / PR 60-62 merge sync:

- Fetched latest remote state from `origin/main`. The local primary checkout is dirty on `task/T042-billa-scale-scrape-dedupe`, so any repo update used a clean worktree from `origin/main`.
- Checked GitHub PRs. PR #60 (`task/T073-tegut-amazon-price-surface-discovery`), PR #61 (`task/T047-grocerlo-minimalist-detail-disclosure`), and PR #62 (`task/GRO-coordinator-20260629-blocker-sync`) are already merged on GitHub. This coordinator pass did not merge any pull request.
- Loaded Linear credentials with `source credentials.txt` before Linear API calls, queried team `GRO`, and moved `GRO-43`, `GRO-22`, and `GRO-46` from `In Review` to `Done` with merge-status comments.
- Linear count after the sync: 29 `Done`, 11 `Backlog`, 1 `Canceled`, and 0 `Todo`. The completed count remains below the 100-task full-codebase security review boundary.
- PM/scoping pass found no dependency-complete `Todo` issue to claim. The remaining non-Done work is policy-blocked: REWE needs an approved location/market/service policy, MPREIS needs an explicit downstream-use policy, and later non-BILLA storage tasks depend on those gates or dry-run review.
- No executor implementation work was launched because Linear has zero `Todo` issues and the remaining backlog has concrete policy blockers.
- Next action: resolve either `GRO-44` / T074 or `GRO-45` / T075 with explicit policy direction, then move any unblocked dependent implementation issue to `Todo` for the next loop.

2026-06-29 coordinator pass / T073 Tegut Amazon discovery:

- Fetched latest remote state from `origin/main`. PR #59 (`task/T072-linear-credentials-instructions`) is already merged on GitHub with the Agent Review Gate passing; no pull requests are currently open, and no merge action was taken.
- Loaded Linear credentials with `source credentials.txt` before Linear API calls, queried team `GRO`, and counted 26 completed issues, below the 100-task full-codebase security review boundary.
- PM/scoping result: no new Linear issues were required before executor work because `GRO-43` / T073 was already an actionable dependency-free `Todo`. Other active Todo issues either overlap frontend comparison-table scope or remain blocked by retailer discovery/storage gates.
- Claimed `GRO-43` by moving it to `In Progress` and adding a start comment. Work used a clean `origin/main` worktree on `task/T073-tegut-amazon-price-surface-discovery`.
- Added `docs/scraper-notes/tegut.md` documenting the Amazon-hosted Tegut grocery surface, category/storefront URL candidates, issue-provided Brot/Backwaren snapshot fields, robots/help context, postcode/account/deployment constraints, source-platform modeling, stop conditions, and go/no-go decision.
- Decision: no-go for price-capturing dry-run scraper or storage. Numeric prices were not confirmed in safe public no-location context, the source category returned `404` through the fetcher, and Amazon grocery availability/delivery is postcode-dependent with account/platform semantics.
- Checks: `python3 -m compileall -q backend/app scripts` and documentation diff review for the Markdown-only change.
- Next action: open the T073 PR, update Linear with PR/check metadata, and keep the issue `In Review` until user-directed merge.
2026-06-29 coordinator pass / T047 Grocerlo minimalist detail disclosure:

- Fetched latest remote state from `origin/main` and checked GitHub PRs. PR #59 is merged. PR #60 is the only open pull request; it is clean, has a passing Agent Review Gate, tracks GRO-43 / T073, and must remain waiting for user-directed review/merge.
- Checked Linear team `GRO` after sourcing `credentials.txt`. GRO-43 remains `In Review`; GRO-8 is `Done`.
- PM/scoping cleanup: canceled GRO-9 / T029 because GRO-23 / T048 already completed the frontend-to-BILLA backend data wiring that T029 described.
- Claimed GRO-22 / T047 in Linear and implemented it from a clean `origin/main` worktree on `task/T047-grocerlo-minimalist-detail-disclosure`.
- Updated the frontend metadata and hero to use Grocerlo branding, and changed comparison rows so product/category metadata plus offer unit price, country, source, promotion, and last-seen details live behind accessible disclosure controls while the visible table prioritizes product, package, retailer price, and savings.
- Checks passed after installing locked frontend dependencies in the clean worktree: `npm run lint`, `npm run typecheck`, and `npm run build`. `npm ci` emitted an engine warning because `eslint-visitor-keys@5.0.1` prefers Node `^20.19.0 || ^22.13.0 || >=24` while the local Node is `v20.14.0`.
- Opened PR #61: `https://github.com/fukac99/grocerlo/pull/61`.
- PR #61 status: open and not merge-ready. The Agent Review Gate failed because `review_status: pending`; this is expected until a review is run and the PR body/metadata is updated to `review_status: passed`.
- Updated GRO-22 to `In Review` with branch, PR, local check, review status, and no-autonomous-merge metadata.
- Next action: run the required review for PR #61, update review metadata if it passes, then re-check the gate. Do not merge PR #60 or PR #61 unless the user explicitly asks for that specific PR.
2026-06-29 coordinator pass / Linear blocker cleanup:

- Fetched latest remote state from `origin/main` and checked open GitHub PRs.
- PR #60 (`task/T073-tegut-amazon-price-surface-discovery`) is open, clean, and green. It remains `In Review` / `review_status: not_required` in Linear and must not be merged without explicit user instruction.
- PR #61 (`task/T047-grocerlo-minimalist-detail-disclosure`) is open, clean, and green on its latest Agent Review Gate run. It remains `In Review` / `review_status: passed` in Linear and must not be merged without explicit user instruction.
- Confirmed Linear current state: `GRO-43` and `GRO-22` are `In Review`; `GRO-8` is `Done`.
- PM/scoping pass found no dependency-complete `Todo` implementation issue after policy checks. REWE price scraping is blocked until an approved location/market/service context exists, and MPREIS downstream normalization/comparison use is blocked after the capped raw validation.
- Moved miscategorized blocked issues `GRO-31`, `GRO-34`, and `GRO-35` from `Todo` to `Backlog` with blocker comments.
- Created policy follow-ups `GRO-44` / T074 for REWE approved-location dry-run policy and `GRO-45` / T075 for MPREIS downstream-use policy after raw validation. Both are `Backlog` until the required user/policy decisions are available.
- No implementation work was launched because Linear now has zero `Todo` issues and the remaining work is policy-blocked.
- Next action: user or PM pass should resolve either `GRO-44` or `GRO-45`; after one is approved, move the dependent implementation issue back to `Todo` and launch it from a clean `origin/main` worktree.

2026-06-29 coordinator pass / T028 MPREIS capped raw validation:

- Fetched latest remote state from `origin/main` and checked GitHub PRs. No pull requests are currently open; PR #56 (`task/T071-disable-self-merge`) is already merged on GitHub with the agent review gate passing.
- Linear remains the source of truth, but this local agent session has no Linear MCP/tool or `LINEAR_*` environment access. Could not update Linear issue state/comments directly from this pass.
- PM/scoping result: BILLA dedupe and the clean post-dedupe baseline are merged; REWE, Kaufland Slovakia, and Tesco Slovakia remain storage-blocked; MPREIS is the eligible independent implementation scope because GRO-29 / T054 approved exactly one capped `no_market_selected` raw validation path.
- Claimed T028 / GRO-8 locally on `task/T028-mpreis-capped-raw-validation` from a clean `origin/main` worktree.
- Narrowed `scripts/scrape_once.py` so MPREIS storage is allowed only inside the approved cap: one category-equivalent page and no more than three raw products. Broader stored MPREIS runs exit before scraping.
- Extended the stored-data sanity report CLI to accept MPREIS runs and fixed unit-price normalization for price-first MPREIS strings such as `7,96 € /kg`, `1,85 € /l`, and `0,60 € /Stk`.
- Ran the approved capped MPREIS stored validation against the existing local Postgres service: `python3 scripts/scrape_once.py --retailer mpreis --limit-categories 1 --max-products 3 --store`.
- Result: `scrape_run_id=4`, 3 raw rows, all with `raw_payload_json.location_context = no_market_selected`, all with app-only labels stored as `raw_promotion_text`, no normalization or matching performed.
- Sanity report command: `python3 scripts/stored_data_sanity_report.py --retailer mpreis --scrape-run-id 4`. Result: 3 raw rows, 0 quality issues, 0 missing key fields, 0 bad rows.
- Checks passed: `python3 -m pytest backend/tests/test_scrape_once.py backend/tests/test_mpreis_scraper.py backend/tests/test_normalization.py backend/tests/test_stored_data_sanity_report.py`.
- Updated MPREIS/runbook notes and the loop builder prompt to align with the narrowed guard, validation result, and the no-autonomous-merge policy.
- Opened PR #57: `https://github.com/fukac99/grocerlo/pull/57`.
- PR #57 status: open and mergeable, but not merge-ready. The Agent Review Gate failed because `review_status: pending`; this is expected until a review is run and the PR body records `review_status: passed`.
- Next action: run the required agent review for PR #57, update review metadata if it passes, then re-check the gate. A follow-up PM issue should review whether the quarantined MPREIS raw run can be normalized or whether a market/location policy is needed first.

2026-06-28 T055 BILLA post-dedupe baseline ingest:

- Ran the smallest approved stored BILLA baseline after the dedupe cleanup: `python3 scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3 --store`.
- Stored `scrape_run_id=3` with 3 raw rows, then normalized it with `python3 scripts/normalize_once.py 3`.
- Normalization created 3 retailer products, found 0 existing rows, and skipped 0 raw products.
- Sanity report: 3 raw rows, 0 quality issues, 3 distinct source product IDs, 0 duplicate-source-ID groups, 2 missing unit prices, and 0 missing package sizes.
- Cleanup decision: keep the run as the clean controlled BILLA baseline. Missing unit prices are limited to two product rows, package sizes are present, and no duplicate source IDs or stop-condition quality issues were observed.
- Next action: non-BILLA stored ingest may proceed only through the already documented retailer-specific gates and caps.

2026-06-28 T054 MPREIS location and app-only storage policy:

- Decided that MPREIS `no_market_selected` public rows may be stored only for one capped raw validation run.
- Kept market selection, account/app flows, broad scraping, normalization, matching, and comparison use blocked.
- Required app-only labels and coupons to remain promotion metadata, not comparable regular price fields.
- Unblocked T028 / GRO-8 only for implementing the one-page, three-product raw validation and sanity-report path.

2026-06-28 T069 temporary agent merge policy:

- User explicitly asked to let agents merge changes for now.
- Updated loop instructions so agents may merge their own PRs after required checks pass and review status is passed or not required.
- Superseded on 2026-06-28 by PR #56 / T071: agents must not merge pull requests autonomously.

2026-06-28 T068 remove legacy Markdown task ledgers:

- User asked to remove the legacy Markdown task ledger and task log files completely from the repository and from all references.
- Deleted both legacy files.
- Rewrote loop engineering guidance to be Linear-only.
- Rewrote this state file to preserve only current project context and Linear coordination rules.
- Updated the review gate so it no longer reads a Markdown task ledger.
- Updated docs/tests/runbook references to use Linear issues.
- Updated Linear issue `GRO-41` to track this removal work.

2026-06-28 T066 Linear ledger cleanup:

- Restored Linear-first loop instructions after all previous PRs merged.
- Clarified that Linear team `GRO` is the active task source of truth.
- Created follow-up Linear issue `GRO-41` to remove the remaining CI dependency on legacy Markdown task metadata.

2026-06-28 T044 country-cheapest product filter:

- Added a country-cheapest filter to the frontend comparison table.
- Added country metadata to normalized frontend offers and sample data.
- Added savings copy for absolute EUR and percent savings versus the next-best available offer, with tied-cheapest and no-comparison states.
- Frontend lint, typecheck, and build passed.

2026-06-28 T051 REWE public price discovery:

- Completed safe read-only public discovery for REWE without selecting a postal code, market, delivery/pickup slot, account, cart, checkout, or storage path.
- Finding: no-location public product pages expose product metadata and article numbers, but not numeric prices or availability.
- Decision: no-go for no-location price-capturing REWE dry-run scraper. A future dry run needs explicit approval of exact test location/market/service context.

2026-06-28 real-data ingest status:

- User approved a broad BILLA scrape across all categories/products to test scale.
- Broad BILLA stored ingest succeeded with 21 categories, 700 raw rows, 700 normalized retailer products, and 473 distinct source product IDs.
- Sanity findings included duplicate source IDs, missing unit prices, and missing package sizes, which led to BILLA category/dedupe cleanup work.

## Next Actions

- Use Linear team `GRO` `Todo` issues for all new work; do not use deprecated Markdown task ledgers.
- Keep green open PRs in `In Review` and report merge readiness without merging unless the user explicitly names that PR for merge.
- Prioritize Human Review decisions for Kaufland Slovakia and Tesco Slovakia before any dry-run implementation for those retailers.
- Prioritize retailer policy/dry-run gates before any non-BILLA stored ingest or downstream comparison use.
- Migrate the review gate to direct Linear validation once a suitable CI secret and issue/PR linking convention are available.
