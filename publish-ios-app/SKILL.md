---
name: publish-ios-app
description: Audit, prepare, test, upload, submit, monitor, and improve the repeatable pipeline for any iOS App Store release. Use when a user asks to publish or update an iPhone/iPad app, configure App Store Connect, ship through TestFlight, configure free, paid, In-App Purchase, or subscription monetization, verify EULA/privacy/DSA/account gates, resolve or learn from App Review rejection, or determine the shortest safe path to release.
---

# Publish iOS App

Take any existing iOS-capable project from its current state to a verified App Store submission. Preserve release state in the project, automate repeatable checks, resume from the first incomplete gate, and pause only for facts, credentials, legal attestations, or irreversible choices that require the account holder.

## Non-negotiable rules

1. Treat the repository as the source of truth and `.app-store/release.toml` as the release ledger.
2. Never store or print passwords, API private keys, issuer IDs, key IDs, tax identifiers, bank details, personal addresses, phone numbers, reviewer contact details, device identifiers, or provisioning profile contents.
3. Refer to secrets only by environment-variable name. Keep `.p8` files and credentials outside the repository.
4. Never choose legal, tax, treaty, content-rights, encryption, banking, or compliance answers for the user. Explain the field and request the truthful answer.
5. Never accept an agreement or certify a form on the user's behalf. The account holder must review and perform the final attestation.
6. Use current Apple documentation for values that change over time: supported Xcode versions, screenshot sizes, price points, review statuses, and agreement requirements.
7. Do not submit a build that was not tested on a physical device and through TestFlight unless the user explicitly accepts that risk.
8. Freeze product scope before the final archive. Any code, product, entitlement, privacy, or metadata change after the selected build requires a new build and revalidation.
9. Do not remove a live or pending submission, change pricing or availability, or click **Submit for Review** without explicit user authorization.
10. Never report success from a clicked button alone. Re-read the resulting status and record evidence.
11. Treat every Apple message as evidence, not as a diagnosis: separate the root issue from items returned only because their parent app version was rejected.
12. Maintain one evolving pipeline. Add a reusable gate after a review or delivery failure only when it generalizes; keep app-specific history in that app's release ledger or canonical release document.

## Select an operating mode

Infer the narrowest mode that satisfies the request:

- `audit`: Read-only inspection and a blocker report.
- `prepare`: Create or update release state, metadata, assets, product configuration, and app code.
- `testflight`: Archive, validate, upload, process, distribute, and test a build.
- `submit`: Freeze the release, assemble all review items, obtain approval, and submit.
- `monitor`: Poll an existing build or submission and handle actionable status changes.
- `full`: Run all applicable modes in order.

If the user did not specify a mode, inspect the repository and current App Store state, then continue from the first incomplete gate. Do not repeat completed work.

## Establish release state

From the app repository root:

```bash
python3 <skill-dir>/scripts/release_check.py check --project .
```

If `.app-store/release.toml` is missing:

- In `audit` mode, report that it is missing; do not write it.
- In `prepare`, `testflight`, `submit`, or `full` mode, initialize it:

```bash
python3 <skill-dir>/scripts/release_check.py init --project .
```

Replace every placeholder with project-specific values, but keep personal and secret values in environment variables. Re-run `check` after each phase and `check --strict` before submission.

## Run the shortest safe path

For every invocation:

1. Refresh repository and live App Store Connect state before acting; never infer that a previous status still holds.
2. Compare that state with `.app-store/release.toml` and existing release documentation.
3. Reuse evidence only when it belongs to the same source commit, build, product set, metadata, and account state.
4. Invalidate downstream evidence when code, native assets, product type, entitlement, privacy behavior, screenshots, legal copy, or selected build changes.
5. Execute only the first incomplete dependency chain. Do not recreate products, metadata, screenshots, submissions, or documents that already exist and still match.
6. Classify results as `blocker`, `warning`, `external wait`, or `verified` so Apple processing is not mistaken for unfinished implementation.

## Workflow

### 1. Inspect before changing anything

1. Read repository instructions and release documentation.
2. Run `git status -sb`; preserve unrelated user changes.
3. Detect the stack, Xcode project/workspace, schemes, bundle identifier, deployment target, version, build number, entitlements, privacy manifest, app icon set, StoreKit dependencies, and CI/release tooling.
4. Inspect existing App Store Connect state through the API when available. Use the browser for unsupported screens and user-facing legal flows.
5. Compare repository state, the release ledger, the uploaded build, and the App Store version record.
6. Return blockers grouped as `code`, `assets`, `metadata`, `monetization`, `account`, `testing`, or `review`.

Read [project-stacks.md](references/project-stacks.md) when identifying or building a non-native stack.

### 2. Clear account gates early

Before preparing a paid app or in-app purchase, verify the Paid Apps Agreement, legal entity, banking, tax, and compliance statuses. A free app does not require paid-business gates unless it contains paid products.

Read [account-gates.md](references/account-gates.md) before working in the Business module. Mark a gate complete only after its displayed status confirms completion or processing.

### 3. Freeze the product definition

Record the following before the release archive:

- app name, bundle identifier, supported devices, primary locale, and category;
- version and build number, and whether this is a first release or an update;
- free, paid, in-app-purchase, or subscription model;
- product types, identifiers, subscription groups, periods, prices, trials or app-managed free access, entitlements, and availability;
- login requirements and reviewer path;
- data collection, tracking, third-party SDK behavior, encryption, and content rights;
- icon, screenshots, support URL, privacy URL, Terms of Use URL, EULA mode, description, keywords, and release notes.

Resolve conflicts explicitly. Do not silently preserve an obsolete product, trial, entitlement, or feature.

### 4. Prepare code and monetization

1. Make the smallest scoped implementation needed for the frozen release.
2. Use StoreKit 2 for a new native purchase implementation unless the project intentionally uses a maintained purchase platform.
3. Keep a single authoritative entitlement check. Restore purchases, observe customer changes, handle cancellation and billing states, and provide subscription management.
4. Use sandbox StoreKit accounts or platform test configuration; never simulate a successful purchase in production code.
5. If using a purchase platform, keep its public app key outside committed source when project policy requires it and never include secret/admin keys in the client.
6. Verify product identifiers match App Store Connect exactly.
7. Classify each paid item as paid app, consumable, non-consumable, non-renewing subscription, or auto-renewable subscription. Do not preserve an obsolete type merely because its object already exists.
8. Submit the first item of each In-App Purchase type with a new app version when Apple's current rules require it. For a first auto-renewable subscription, attach the group and product to that app-version submission.
9. Distinguish app-managed free access from an App Store introductory offer. Never promise automatic conversion or renewal for a non-consumable.

Read [subscriptions.md](references/subscriptions.md) for purchase, subscription, trial, and entitlement gates.

### 5. Build and verify

1. Run the project's existing lint, type, unit, and integration checks.
2. Sync generated/native files for hybrid frameworks.
3. Build the Release configuration with the intended scheme and destination.
4. Verify bundle identifier, version, build, signing team selection, entitlements, minimum OS, orientations, privacy manifest, and icon in the archived app.
5. Ensure the archive contains no development-only menus, placeholder data, demo products, debug endpoints, or test credentials.
6. Validate the archive with current Apple tooling before upload.
7. Record the source commit and archive fingerprint. Rebuild if the archived native payload does not match the source and synchronized assets that passed checks.

Do not repair signing by replacing certificates or deleting profiles unless the exact target is known and the user authorized it.

### 6. Test through TestFlight

1. Upload with Xcode, Transporter, or an established automated release tool.
2. Wait for processing and resolve export-compliance questions truthfully.
3. Add the build to an internal TestFlight group.
4. Install from TestFlight on a physical supported device.
5. Test a fresh install and an upgrade over realistic data from the previous public version. Include cold launch, onboarding, permissions, offline/error behavior, the primary journey, every critical control, packaged media/assets, purchase, trial or free-access copy, restore, entitlement refresh, external links, and relaunch.
6. Review crash, hang, and console evidence.
7. Check perceived smoothness, hangs, long tasks, Reduce Motion behavior, and accessibility on the critical path.
8. Record the tested build number and set `testflight_passed`, `physical_device_passed`, `cold_launch_passed`, `critical_path_passed`, and `performance_passed` only after real success.

External TestFlight testers may require Beta App Review. Do not confuse Beta App Review with App Review.

### 7. Prepare App Store review

Verify all of the following:

- processed build is selected for the intended version;
- name, subtitle, description, keywords, categories, copyright, URLs, and release notes are complete;
- the Terms of Use model is explicit: Apple Standard EULA or a configured custom EULA;
- for Apple Standard EULA, its functional link appears in every submitted description localization; for a custom EULA, the agreement is configured for the intended regions in App Store Connect;
- the Privacy, Terms, and Support URLs were opened successfully during this release;
- paid-product screens expose working Terms and Privacy links; auto-renewable subscriptions meet Apple's current in-app disclosure requirements;
- screenshots meet Apple's current specification, show the real app, contain no alpha, and match supported devices;
- the 1024×1024 App Store icon is present and opaque;
- age rating, app privacy, content rights, encryption/export compliance, and availability are complete;
- Review Information includes a reachable contact through environment-held values, accurate notes, and valid demo access when login is required;
- each in-app purchase or subscription has localization, price, availability, review notes, and its required review screenshot;
- first-of-type In-App Purchases and the first subscription/group are included with the new app version when applicable;
- product type, localized StoreKit price, trial/free-access language, renewal behavior, entitlement, app UI, description, screenshot, and Review Notes all describe the same offer;
- agreements and finance gates are active or in an Apple-confirmed acceptable state.

Read [review-failures.md](references/review-failures.md) before declaring readiness.

### 8. Freeze and submit

1. Set `release_frozen = true` only after the selected build and product scope match.
2. Re-run:

```bash
python3 <skill-dir>/scripts/release_check.py check --project . --strict
```

3. Present the user with the exact version, build, app, monetization items, release method, and remaining warnings.
4. Obtain explicit approval for the final submission.
5. Record `submission_approved = true`.
6. Add the app version and all required in-app purchase items for review.
7. Submit the assembled review submission.
8. Re-read the resulting status. A draft marked `Ready for Review` is not submitted; confirm `Waiting for Review`, `In Review`, or another post-submit status.

### 9. Monitor

Monitor without changing scope:

- build processing;
- TestFlight review;
- App Review status;
- unresolved issues or metadata rejection;
- agreement or compliance changes that block release.

When Apple requests information, quote or summarize the exact issue, map it to the relevant file or App Store field, propose a response, and wait for approval before sending messages or changing the submission. Record the final status in the release ledger.

### Review-response loop

1. Preserve the exact message, affected submission ID, app version/build, item statuses, and guideline reference without copying personal data into the repository.
2. Classify each reported item as `root`, `collateral`, `account`, or `external wait`. A subscription or IAP returned with a rejected app is not automatically a separate product defect.
3. Fix only the smallest verified root cause. Do not create a replacement product or submission unless the product definition changed or Apple requires it.
4. Re-run every gate invalidated by the change. Metadata-only fixes do not justify an untested binary change; binary fixes require a new build number and device/TestFlight validation.
5. Reply in the original App Review or support thread after the requested action is complete, then verify the sent message and resulting Apple status.
6. Add a generalized prevention rule to `review-failures.md`, the manifest, or `release_check.py` when the lesson can prevent the same class of failure for other apps.

## Tool policy

- Prefer local inspection and deterministic scripts for project facts.
- Prefer App Store Connect API or established release automation for repeatable metadata and status operations.
- Use Xcode/Transporter for binary upload according to the installed toolchain and current Apple guidance.
- Use browser automation for pages without reliable API coverage, especially agreements, banking, tax, legal entity, content-rights, and interactive review forms.
- Keep the browser focused on the one page requiring user input; close unrelated tabs only when the user asks.
- Ask before any destructive signing, certificate, submission, pricing, availability, or live-release action.

## Completion criteria

Do not call the release complete until:

1. all strict local gates pass;
2. the exact uploaded build passed TestFlight and physical-device testing;
3. required paid products are included and reviewable;
4. the submission status proves Apple received it;
5. the release ledger records the source commit, archive fingerprint, version, build, submission ID, verified status time, and any external wait.

If Apple is processing or reviewing, report the release as submitted and waiting, not published.

## Resources

- [account-gates.md](references/account-gates.md): agreements, legal entity, bank, tax, and compliance boundaries.
- [subscriptions.md](references/subscriptions.md): product types, StoreKit, purchase platforms, trials/free access, entitlements, and first-of-type submission.
- [project-stacks.md](references/project-stacks.md): native, Capacitor, React Native, and Flutter release preparation.
- [review-failures.md](references/review-failures.md): common preflight and App Review failures.
- [official-sources.md](references/official-sources.md): current Apple documentation entry points.
- `assets/release-manifest.toml`: generic release-ledger template.
- `scripts/release_check.py`: initialize and validate project release state without sending data anywhere.
