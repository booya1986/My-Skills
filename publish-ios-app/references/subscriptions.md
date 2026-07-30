# Subscriptions and Entitlements

Use this reference when the release includes auto-renewable subscriptions or another purchase platform.

## Product model

Freeze these identifiers before implementation:

- App Store product identifier;
- subscription group reference name;
- duration;
- base storefront price and availability;
- introductory-offer type and duration;
- app entitlement name;
- purchase-platform project, offering, and package identifiers when applicable.

Identifiers must match across App Store Connect, StoreKit code, purchase-platform configuration, tests, and review notes. Never reuse obsolete identifiers merely because they already exist.

## Native implementation

For a new native implementation, prefer StoreKit 2:

1. Load products by identifier.
2. Display Apple's localized price and period.
3. Purchase and verify the transaction.
4. Finish verified transactions.
5. Derive access from current verified entitlements.
6. Observe transaction updates for changes made outside the current session.
7. Provide Restore Purchases and subscription-management entry points.
8. Handle pending, user-cancelled, unverified, expired, revoked, grace-period, and billing-retry states.

Do not grant premium access solely from a local boolean or from a purchase sheet returning success.

## Purchase platforms

When the project intentionally uses a maintained purchase platform:

- use its current SDK and recommended UI components;
- configure the SDK once at app startup;
- map the App Store product to one offering/package and one stable entitlement;
- check authoritative customer information at launch and after purchase/restore;
- observe customer-information changes;
- present platform paywalls only after their products and offering are available;
- expose the platform's customer center when it adds useful cancellation, refund-request, billing, or support flows;
- keep secret/admin API keys server-side and outside the repository;
- treat client/public app keys as project configuration and avoid publishing real account-specific keys in reusable templates.

The App Store receipt and verified platform customer state remain authoritative. Cache only for responsive UI, not permanent access.

## Trials and introductory offers

Create a free trial as an introductory offer in App Store Connect. Verify:

- the duration is supported for the base subscription period;
- the correct storefronts and dates are selected;
- eligibility is based on Apple's subscription-group rules;
- the paywall uses localized product data and does not promise eligibility before it is known;
- the post-trial price and renewal period are prominent;
- sandbox tests cover eligible and ineligible users.

Never hardcode a currency-formatted price as the purchase source of truth.

## First-subscription rule

The first auto-renewable subscription and its first subscription group must be submitted with a new app version in the same review submission. Add the subscription product for review, attach it to the version submission, and include its Review Information screenshot.

After the first subscription is approved, later subscription products may follow Apple's current standalone submission rules.

## Test matrix

Test at minimum:

- products load;
- localized price and trial render;
- successful purchase unlocks immediately;
- cancellation leaves access unchanged until expiration;
- restore on a fresh install restores access;
- expired or revoked access locks correctly;
- purchase pending does not unlock prematurely;
- network and StoreKit errors produce recoverable UI;
- subscription management opens;
- app relaunch refreshes entitlement;
- sandbox account with prior introductory use is not shown as eligible.

Record the environment and build number, but never record sandbox credentials in the repository.

## Review information

Provide a screenshot showing where the purchase begins inside the app. In review notes:

- explain how to reach the paywall;
- name the feature unlocked;
- explain any login requirement;
- clarify external hardware, location, account, or content dependencies;
- provide demo credentials through the secure App Store Connect field, not source control.
