# Retailer Policy Decisions

This record captures the human-review decisions for Kaufland Slovakia and Tesco Slovakia. It does not approve scraping, storage, normalization, matching, comparison API use, UI exposure, account flows, location selection, or volume increases.

## Current Decision

`GRO-51` and `GRO-52` are resolved for first-version scope: exclude Kaufland Slovakia and Tesco Slovakia from the first multi-retailer version, then revisit them after the BILLA, MPREIS, and REWE policy gates are settled.

The resulting operating rule is:

- Do not scrape `www.kaufland.sk`; it returned verification/bot-protection pages during discovery and no public no-location grocery shelf-price surface was confirmed.
- Do not treat `predajne.kaufland.sk` leaflet/store offers as national grocery shelf prices. They are promotional and store-contextual.
- Do not scrape Tesco Slovakia online groceries. Tesco's own public terms say current prices are shown after registered login, and shopping accuracy depends on delivery slot/store context.
- Do not use search-indexed snippets as product data. They are human discovery hints only, not a stable product payload.
- Keep all future Kaufland/Tesco work blocked until a later revisit issue records the exact approved context, cap, and reason for bringing the retailer back into scope.

## Kaufland Slovakia Decision

Kaufland Slovakia currently has no approved grocery shelf-price scraper path and is excluded from the first multi-retailer version.

Recorded decision from `GRO-51` / T082:

- Approved: yes.
- Scope: exclude Kaufland Slovakia from the first multi-retailer version.
- Revisit condition: reconsider only after BILLA, MPREIS, and REWE policy gates are settled.
- Dependent issues: keep `GRO-32` / T057 and `GRO-36` / T061 blocked; the decision does not approve a dry-run scraper, storage, normalization, matching, API use, or UI exposure.

Future revisit options remain:

- **Reject Kaufland SK for now.** Keep all Kaufland SK runtime scraping and storage blocked. This is the safest choice unless regional leaflet/store-offer comparison is valuable enough to model separately.
- **Approve a no-storage leaflet/store-offer dry run.** Allow a future task to inspect only `predajne.kaufland.sk` offer pages, capped to one page or one category group and at most three products. Outputs must be labeled as store-contextual promotional offers, not regular shelf prices.
- **Approve a named-store policy.** Choose an exact store context before any dry run, then require every output row to carry that store label. This still does not approve storage or UI comparison.
- **Approve default-store observation only.** Permit observing the public default store context if rendered without manual selection, but require the output to say `default public store context observed` and forbid national-price claims.

Minimum approvals required before a Kaufland SK no-storage dry run:

- Whether Kaufland leaflet/store offers are useful for Grocerlo despite not being national shelf prices.
- Whether the run may use a named approved store, or only the default public store context if one renders without manual selection.
- The exact URL family to allow, currently limited to `predajne.kaufland.sk` offer or leaflet pages.
- A cap of one page or one category group, at most three products, no storage, and at least a two-second delay plus jitter.
- A data-modeling rule that separates regular offer price, old price, unit price, package size, category, store/location context, Kaufland Card labels, missing stable IDs, and uncertainty.
- A stop rule for verification pages, CAPTCHA, bot challenges, account/app/Kaufland Card flows, marketplace pages, store-changing controls, geolocation, cookies used to choose a store, carts, checkout, or personalized offers.

## Tesco Slovakia Decision

Tesco Slovakia currently has no approved no-location public price scraper path and is excluded from the first multi-retailer version.

Recorded decision from `GRO-52` / T083:

- Approved: yes.
- Scope: exclude Tesco Slovakia from the first multi-retailer version.
- Revisit condition: reconsider only after BILLA, MPREIS, and REWE policy gates are settled.
- Dependent issues: keep `GRO-33` / T058 and `GRO-37` / T062 blocked; the decision does not approve a dry-run scraper, storage, normalization, matching, API use, UI exposure, account/session use, or location selection.

Future revisit options remain:

- **Reject Tesco SK for now.** Keep all Tesco SK runtime scraping and storage blocked. This is the safest choice unless the project is willing to define an account/location/session test context.
- **Request legal/product review for a manual test context.** Decide whether a registered account, delivery address, postal code, serving store, delivery slot, and session can be used at all. This is required before any Playwright or API inspection.
- **Approve metadata-only human discovery.** Allow documentation-only review of public help, terms, robots, and search-visible snippets, with no automated product capture and no product data stored.
- **Approve a future no-storage account/location dry run.** Only after legal/product review, allow a capped dry run that records context labels and does not store or expose rows.

Minimum approvals required before a Tesco SK no-storage dry run:

- Whether using a Tesco account or registered session is allowed.
- The exact delivery address, postal code, serving store, delivery or Click+Collect mode, and delivery slot policy, or an explicit decision that no such context may be used.
- Whether browser automation is allowed for inspection, and which URLs or public payloads may be touched.
- A cap of one category or one product-listing surface, at most three products, no storage, and at least a two-second delay plus jitter.
- A data-modeling rule that separates current price, Clubcard price, coupons, vouchers, multibuy offers, app labels, Tesco Online Club benefits, availability, fulfillment/store/day context, and source product IDs.
- A stop rule for login/register uncertainty, protection interstitials, CAPTCHA, bot challenges, account-specific APIs, basket/cart, checkout, payment, queued/tokenized URLs, disallowed parameterized paths, or unclear regular-versus-member price separation.

## Recorded Linear Decisions

The Kaufland decision is recorded in `GRO-51`; the Tesco decision is recorded in `GRO-52`.

Any future revisit should include:

- The approving human and timestamp.
- The selected option from this packet, or a narrower written alternative.
- Allowed retailer surface, URLs, location/account/session context, and fields.
- Explicit no-storage status unless storage is separately approved later.
- Exact caps, delay/jitter, and stop conditions.
- Whether the result may be used only for documentation, for a no-storage dry run, or for a later stored-validation proposal.

Until a future revisit records those fields, `GRO-32` / T057, `GRO-33` / T058, `GRO-36` / T061, and `GRO-37` / T062 remain blocked.

## Safe Follow-Up

The first multi-retailer planning path should focus on BILLA plus the still-policy-gated MPREIS and REWE paths. Kaufland Slovakia and Tesco Slovakia should not be reopened for implementation work until a later BILLA/MPREIS/REWE gate summary says there is a reason to revisit them.
