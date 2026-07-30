---
name: publish-ios-app
description: Audit, prepare, test, upload, submit, and monitor iOS App Store releases from an existing app project. Use when a user asks to publish or update an iPhone/iPad app, configure App Store Connect, ship a build through TestFlight, add paid apps or auto-renewable subscriptions, resolve App Review blockers, or determine what remains before release.
---

# Publish iOS App

Take an existing iOS-capable project from its current state to a verified App Store submission. Preserve release state in the project, automate repeatable checks, and pause only for facts, credentials, legal attestations, or irreversible choices that require the account holder.

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
- version and build number;
- free, paid, in-app-purchase, or subscription model;
- product identifiers, subscription groups, periods, prices, trials, entitlements, and availability;
- login requirements and reviewer path;
- data collection, tracking, third-party SDK behavior, encryption, and content rights;
- icon, screenshots, support URL, privacy URL, description, keywords, and release notes.

Resolve conflicts explicitly. Do not silently preserve an obsolete product, trial, entitlement, or feature.

### 4. Prepare code and monetization

1. Make the smallest scoped implementation needed for the frozen release.
2. Use StoreKit 2 for a new native purchase implementation unless the project intentionally uses a maintained purchase platform.
3. Keep a single authoritative entitlement check. Restore purchases, observe customer changes, handle cancellation and billing states, and provide subscription management.
4. Use sandbox StoreKit accounts or platform test configuration; never simulate a successful purchase in production code.
5. If using a purchase platform, keep its public app key outside committed source when project policy requires it and never include secret/admin keys in the client.
6. Verify product identifiers match App Store Connect exactly.
7. For a first auto-renewable subscription, attach the subscription group and subscription product to the same new app-version submission.

Read [subscriptions.md](references/subscriptions.md) for subscription and entitlement gates.

### 5. Build and verify

1. Run the project's existing lint, type, unit, and integration checks.
2. Sync generated/native files for hybrid frameworks.
3. Build the Release configuration with the intended scheme and destination.
4. Verify bundle identifier, version, build, signing team selection, entitlements, minimum OS, orientations, privacy manifest, and icon in the archived app.
5. Ensure the archive contains no development-only menus, placeholder data, demo products, debug endpoints, or test credentials.
6. Validate the archive with current Apple tooling before upload.

Do not repair signing by replacing certificates or deleting profiles unless the exact target is known and the user authorized it.

### 6. Test through TestFlight

1. Upload with Xcode, Transporter, or an established automated release tool.
2. Wait for processing and resolve export-compliance questions truthfully.
3. Add the build to an internal TestFlight group.
4. Install from TestFlight on a physical supported device.
5. Test first launch, onboarding, permissions, offline/error behavior, purchase, trial display, restore, entitlement refresh, subscription management, external links, and relaunch.
6. Review crash, hang, and console evidence.
7. Record the tested build number and set both `testflight_passed` and `physical_device_passed` only after real success.

External TestFlight testers may require Beta App Review. Do not confuse Beta App Review with App Review.

### 7. Prepare App Store review

Verify all of the following:

- processed build is selected for the intended version;
- name, subtitle, description, keywords, categories, copyright, URLs, and release notes are complete;
- screenshots meet Apple's current specification, show the real app, contain no alpha, and match supported devices;
- the 1024×1024 App Store icon is present and opaque;
- age rating, app privacy, content rights, encryption/export compliance, and availability are complete;
- Review Information includes a reachable contact through environment-held values, accurate notes, and valid demo access when login is required;
- each in-app purchase or subscription has localization, price, availability, review notes, and its required review screenshot;
- the first subscription and its group are included with the new app version when applicable;
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
5. the release ledger records the version, build, status, and any external wait.

If Apple is processing or reviewing, report the release as submitted and waiting, not published.

## Resources

- [account-gates.md](references/account-gates.md): agreements, legal entity, bank, tax, and compliance boundaries.
- [subscriptions.md](references/subscriptions.md): StoreKit, purchase platforms, trials, entitlements, and first-subscription submission.
- [project-stacks.md](references/project-stacks.md): native, Capacitor, React Native, and Flutter release preparation.
- [review-failures.md](references/review-failures.md): common preflight and App Review failures.
- [official-sources.md](references/official-sources.md): current Apple documentation entry points.
- `assets/release-manifest.toml`: generic release-ledger template.
- `scripts/release_check.py`: initialize and validate project release state without sending data anywhere.
