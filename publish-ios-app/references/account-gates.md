# Account and Business Gates

Use this reference before working in App Store Connect's Business module.

## Responsibility boundary

The agent may navigate, explain fields, identify missing statuses, and verify the result. The account holder must:

- accept agreements;
- certify legal entity, bank, tax, treaty, content-rights, encryption, or compliance statements;
- provide government, tax, banking, address, identity, or contact information;
- choose answers whose truth depends on personal or business facts.

Never infer a tax-treaty article, withholding rate, legal capacity, business type, beneficial owner, or content-rights declaration. Recommend a qualified tax or legal professional when the user is unsure.

## Order of operations for paid apps and purchases

1. Confirm the Apple Developer Program membership and the user's Account Holder authority.
2. Resolve any compliance or legal-entity review.
3. Review and accept the current Paid Apps Agreement.
4. Add and verify banking information.
5. Complete the tax forms App Store Connect requests for the account's actual jurisdiction.
6. Complete any Digital Services Act or other storefront compliance shown by Apple.
7. Re-open Agreements and verify the displayed status.

Apple may show intermediate states such as `Pending User Info`, `Processing`, or `Verifying`. Record the exact state; do not convert it to `Active` in the release ledger.

## Secure compliance documents

When Apple requests an identity, address, tax, bank, or other compliance document:

1. Verify the request in the original Apple message and use only Apple's official secure upload destination.
2. Ask the user to choose or explicitly approve the exact document and destination. Prefer the single accepted document that exposes the least unrelated personal data.
3. Never attach the document to ordinary email when Apple supplied a secure upload link.
4. In the native macOS file chooser, select by absolute path and re-check filename, type, and size before sending.
5. Wait until the upload page displays an explicit terminal success such as `Completed`; progress or a click is not evidence.
6. Reply in the original support thread when Apple requests it, without reattaching the sensitive document, and verify the reply appears in Sent.
7. Record the case number, action time, and pending Apple status without recording document numbers or sensitive contents.

An uploaded document is not an approved compliance status. Keep the gate as an `external wait` until App Store Connect or Apple Support confirms verification.

## Safe browser workflow

1. Keep only the relevant App Store Connect page in scope.
2. Read the full visible prompt and identify whether it is informational or an attestation.
3. Fill non-sensitive app facts only when they are verified in the project.
4. Stop at personal, financial, tax, legal, or irreversible confirmation fields.
5. Tell the user what the field means and which factual source they should consult.
6. Let the user enter sensitive values and perform the certification.
7. Continue after the user confirms completion; verify the resulting status.

Do not capture or persist screenshots that show bank, tax, identity, address, or contact details unless the user explicitly requests a secure local record.

## Release interpretation

- A free app can usually proceed under the developer-program agreement.
- Selling the app or offering in-app purchases requires an effective Paid Apps Agreement.
- Receiving proceeds also requires valid banking and tax information.
- A pending verification may be an external wait, not an implementation failure.
- Agreement requirements can change. Use the current App Store Connect UI and Apple's current documentation rather than old screenshots.
