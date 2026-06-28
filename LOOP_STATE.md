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
- Temporary merge policy: agents may merge their own pull requests after required checks pass, review status is passed or not required, Linear has the PR URL/status recorded, and there are no known blockers. Do not force-merge or bypass branch protection.

Implementation PR descriptions must describe user-visible behavior, concrete code/module changes, API/CLI/UI/data-shape changes, tests run, risks, assumptions, and follow-up work.

Every loop run should count completed work from Linear `Done` issues. At each new 100-task boundary, schedule a full-codebase security review before launching additional implementation work.

Last full-codebase security review boundary: 0 completed tasks.

## Retailer Status

| Retailer | Country | Status | Notes |
| --- | --- | --- | --- |
| BILLA | AT | Cleanup first | Broad stored ingest succeeded, but duplicate-heavy category overlap needs the merged dedupe cleanup before BILLA becomes the baseline for non-BILLA ingest. |
| MPREIS | AT | Policy-approved for capped raw validation | GRO-29 / T054 allows one `no_market_selected` raw stored validation run only: one page, three products, app-only labels as promotion metadata, no normalization or matching until later approval. |
| REWE | DE | Discovery-only; storage blocked | Public no-location pages expose metadata/article numbers but not numeric prices. Price scraping needs an approved location/market/service context first. |
| Kaufland | SK | Discovery-only; storage blocked | Needs discovery to distinguish grocery, marketplace, leaflet, store, loyalty, and app-specific price surfaces. |
| Tesco | SK | Discovery-only; storage blocked | Needs discovery for public price visibility, dynamic loading, address/slot/session requirements, and Clubcard labels. |

## Last Run

2026-06-28 T054 MPREIS location and app-only storage policy:

- Decided that MPREIS `no_market_selected` public rows may be stored only for one capped raw validation run.
- Kept market selection, account/app flows, broad scraping, normalization, matching, and comparison use blocked.
- Required app-only labels and coupons to remain promotion metadata, not comparable regular price fields.
- Unblocked T028 / GRO-8 only for implementing the one-page, three-product raw validation and sanity-report path.

2026-06-28 T069 temporary agent merge policy:

- User explicitly asked to let agents merge changes for now.
- Updated loop instructions so agents may merge their own PRs after required checks pass and review status is passed or not required.
- The policy remains conservative: no force-merges, no branch-protection bypass, and Linear must be updated with PR/check/merge status.

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

- Use Linear `Todo` issues for all new work.
- Prioritize remaining UX issues one at a time when they touch the comparison table.
- Prioritize retailer discovery/policy issues before any non-BILLA stored ingest.
- Migrate the review gate to direct Linear validation once a suitable CI secret and issue/PR linking convention are available.
