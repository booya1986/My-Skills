# Review and Preflight Failures

Use this list immediately before freezing a release and when App Review reports an issue.

## Build and signing

- Bundle identifier does not match the App Store record.
- Version or build number duplicates an uploaded build or does not match the selected version.
- Wrong scheme, target, configuration, signing team, capability, or provisioning profile.
- Archive contains debug endpoints, a development server dependency, placeholder products, or demo menus.
- Required privacy manifest or SDK signature is missing.
- App icon is missing, transparent, incorrectly sized, or absent from the archive.

## Metadata and assets

- Required screenshot set is missing, has an alpha channel, uses an unsupported size, or shows a materially different UI.
- Privacy policy or support URL is missing, broken, gated, or unrelated to the app.
- Description, screenshots, or age rating promise features not in the submitted build.
- Content-rights or export-compliance answer is incomplete.
- Review contact information is missing or unreachable.
- Login is required but credentials or navigation steps are missing.

## Purchases and subscriptions

- Product identifier differs between code, App Store Connect, and the purchase platform.
- Paid Apps Agreement, banking, tax, or compliance status blocks paid products.
- Product localization, price, availability, review notes, or Review Information screenshot is incomplete.
- First subscription or first subscription group is not attached to the new app-version submission.
- Paywall does not disclose price, renewal period, or trial terms clearly.
- Restore Purchases or subscription management is absent or broken.
- Entitlement unlock relies on a local flag instead of verified transaction/customer state.
- Review cannot reach or trigger the purchase flow.

## Functionality and policy

- App crashes, hangs, presents an empty state, or requires unavailable backend/content.
- Permissions are requested without clear purpose strings or before their need is explained.
- External links, media, account deletion, or sign-in flows are incomplete.
- App privacy answers do not include data collected by third-party SDKs.
- The app requires an account but does not meet applicable account-deletion requirements.
- The submission includes unfinished, misleading, copied, or placeholder content.

## Status mistakes

- `Ready for Review` means the item is in a draft submission, not sent to App Review.
- Build processing is not the same as TestFlight availability.
- TestFlight Beta App Review is not production App Review.
- `Waiting for Review` means Apple received the submission but has not started review.
- A version cannot be called published until its release status confirms availability on the App Store.

## Response workflow

1. Preserve Apple's exact message and guideline reference.
2. Reproduce the issue on the submitted build when possible.
3. Separate code, metadata, account, and reviewer-access causes.
4. Fix the smallest root cause.
5. Upload a new build when binary behavior changed.
6. Update metadata only when the binary is already correct.
7. Draft a factual response with reproduction steps and validation evidence.
8. Obtain approval before sending the response or resubmitting.
