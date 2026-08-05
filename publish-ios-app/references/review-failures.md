# Review and Preflight Failures

Use this list immediately before freezing a release and when App Review reports an issue.

## Build and signing

- Bundle identifier does not match the App Store record.
- Version or build number duplicates an uploaded build or does not match the selected version.
- Wrong scheme, target, configuration, signing team, capability, or provisioning profile.
- Archive contains debug endpoints, a development server dependency, placeholder products, or demo menus.
- Hybrid native payload contains the web/marketing edition, a stale route, or the wrong generated entry point.
- A running watcher or repeated sync created numbered duplicate output, stale assets, or mixed resources from different source states.
- Required privacy manifest or SDK signature is missing.
- App icon is missing, transparent, incorrectly sized, or absent from the archive.

## Metadata and assets

- Required screenshot set is missing, has an alpha channel, uses an unsupported size, or shows a materially different UI.
- Screenshots or paid-product Review Information depict a previous build, obsolete product model, or future feature not present in the selected binary.
- Privacy policy or support URL is missing, broken, gated, or unrelated to the app.
- A configured Marketing URL is live but still advertises an obsolete
  subscription, trial, feature, limit or price that conflicts with the submitted
  binary and store metadata.
- Terms of Use is absent from a submitted description localization, points to a broken URL, or conflicts with the configured EULA. For Apple Standard EULA, keep the functional standard-EULA link in the description; for a custom EULA, configure it in App Store Connect and keep user-facing Terms access consistent.
- Description, screenshots, or age rating promise features not in the submitted build.
- Content-rights or export-compliance answer is incomplete.
- Review contact information is missing or unreachable.
- Login is required but credentials or navigation steps are missing.
- Review Notes describe navigation for only one supported form factor. Verify the
  exact reviewer path on every supported device class whose responsive layout
  changes the location, label, visibility, or order of controls (for example,
  an iPhone bottom tab versus an iPad header action).

## Purchases and subscriptions

- Product identifier differs between code, App Store Connect, and the purchase platform.
- Paid Apps Agreement, banking, tax, or compliance status blocks paid products.
- Product localization, price, availability, review notes, or Review Information screenshot is incomplete.
- A first-of-type In-App Purchase is not attached to a new app-version submission when required.
- First auto-renewable subscription or first subscription group is not attached to the new app-version submission.
- A non-consumable is described as auto-renewing, an app-managed free period is described as an App Store trial, or product type and offer copy disagree.
- Paywall does not disclose price, renewal period, or trial terms clearly.
- Restore Purchases or subscription management is absent or broken.
- Entitlement unlock relies on a local flag instead of verified transaction/customer state.
- Review cannot reach or trigger the purchase flow.
- Review Notes name only the general settings area instead of the exact visible
  labels and immediate purchase action. Include device-specific entry points,
  the row/control title, the purchase CTA, and any scrolling required. If an
  app-managed free-access action is shown alongside purchase, state whether the
  reviewer can purchase immediately or must first satisfy a real gate.
- App-version Review Notes or a thread reply were corrected, but the paid
  item's own Review Notes still contain the old device path or imply a different
  purchase gate. Compare every reviewer-facing surface before submitting. If
  Apple has locked a stale field during review, do not cancel reflexively;
  preserve the corrected thread response and update the item field when Apple
  returns it or it becomes editable.

## Functionality and policy

- App crashes, hangs, presents an empty state, or requires unavailable backend/content.
- The candidate was installed but never successfully launched and exercised on the device used as release evidence.
- The release ledger marks iPad support because Apple reviewed on an iPad even
  though the processed binary is iPhone-only. Derive supported families from
  uploaded build metadata and treat the iPad run as a compatibility-layout path.
- An update launches with data from a fresh install but fails with persisted data from the previous public version.
- The primary screen renders but required controls or packaged media are missing in the native archive.
- Permissions are requested without clear purpose strings or before their need is explained.
- External links, media, account deletion, or sign-in flows are incomplete.
- App privacy answers do not include data collected by third-party SDKs.
- The app requires an account but does not meet applicable account-deletion requirements.
- The submission includes unfinished, misleading, copied, or placeholder content.

## Status mistakes

- `Ready for Review` means the item is in a draft submission, not sent to App Review.
- Build processing is not the same as TestFlight availability.
- A locally installed Debug build is not evidence that the uploaded/TestFlight build passed.
- `Installed` does not mean `launched`, and `launched` does not mean the critical path passed.
- TestFlight Beta App Review is not production App Review.
- `Waiting for Review` means Apple received the submission but has not started review.
- A version cannot be called published until its release status confirms availability on the App Store.

## Response workflow

1. Preserve Apple's exact message and guideline reference.
2. Record every affected item, but classify it before fixing anything:
   - `root`: Apple identified a defect in this item;
   - `collateral`: the item was returned only because the associated app/submission failed;
   - `account`: agreement, tax, banking, identity, DSA, or compliance work;
   - `external wait`: Apple is processing or verifying completed work.
3. Reproduce the root issue on the submitted build when possible.
4. Separate code, metadata, account, and reviewer-access causes.
5. Compare the review device with the submitted app's responsive navigation
   before changing code or creating a new build. A correct binary can appear to
   lack a feature when the notes describe only another device class.
6. Fix the smallest root cause. Never create a duplicate product merely because a collateral item also shows `Rejected`.
7. Upload a new build when binary behavior changed.
8. Update metadata only when the binary is already correct.
9. Draft a factual response with reproduction steps and validation evidence.
10. Obtain approval before sending the response or resubmitting.
11. After the live status changes, reconcile the release ledger, canonical
    current-status document, agent handoffs and reusable store/review copy. Run
    the search across the whole repository—including README/agent handoffs,
    every release plan/runbook and unpublished platform metadata or release
    notes—rather than checking only the primary source-of-truth files. Search
    for the prior build, product, submission ID, status, reviewer path and
    verification date. Preserve historical entries but remove stale claims
    from every current-state section and future draft that could be reused.
12. Convert a broadly reusable lesson into a preflight gate; keep the app-specific chronology in its own release ledger.
