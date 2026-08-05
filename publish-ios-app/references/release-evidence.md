# Release Identity and Evidence

Use this reference before reusing earlier work, freezing a candidate, or reporting release status.

## One release identity

Treat a release as this tuple:

```text
source commit + marketing version + build number + product set + metadata set + store-asset set
```

Keep separate rows for local development, a device Debug build, TestFlight, an App Store version, and the currently public version. Never transfer a pass, screenshot, product attachment, or status between rows merely because the app name is the same.

At minimum, record:

| Surface | Required identity/evidence |
| --- | --- |
| source | commit and clean/known working-tree state |
| archive | version, build, bundle identifier, archive SHA-256 |
| upload | Apple build identifier and Apple build number |
| TestFlight | installed/tested build number and test result |
| physical device | installed, launched, and exercised build number |
| store version | version record, selected build, product set, submission ID |
| metadata/assets | localization set and the build/product UI they depict |

If the repository maintains more than one release track, name each track and make its version/build explicit before acting. Future-version work must not silently enter a pending first release, and a pending release's screenshots or approvals do not automatically prove the future version.

## Proof ladder

Use the narrowest accurate statement:

```text
browser preview
  < native payload verified
  < archive validated
  < uploaded and processed
  < selected in a version/submission
  < installed from TestFlight
  < launched and tested on device
  < submitted to App Review
  < approved
  < available on the App Store
```

Important distinctions:

- A successful build is not an archive.
- An archive is not an upload.
- An upload is not processed or selectable.
- `Ready for Review` is still a draft.
- Installation is not successful launch.
- A Debug/device build is not the TestFlight candidate.
- Apple approval is not necessarily public availability when release is manual or phased.

## Reuse and invalidation

Reuse existing evidence only after comparing the full release identity.

| Change | Invalidate |
| --- | --- |
| source code, native configuration, packaged assets, dependency, entitlement | archive, upload, TestFlight, device, performance, critical-path evidence |
| version or build number | archive, upload, TestFlight and device identity evidence |
| product type, identifier, price/trial model, entitlement or paywall | product readiness, purchase tests, monetization copy, IAP screenshot and review notes |
| visible UI or feature scope | affected screenshots, description/release notes and review instructions |
| privacy/data behavior or third-party SDK | privacy manifest/answers, review notes and often the binary |
| metadata-only spelling or URL fix | only affected metadata/link gates; do not rebuild an unchanged binary |
| account/compliance status | refresh the live status; do not rebuild solely for an account-state change |

Do not regenerate screenshots or documents that still depict the exact candidate. Conversely, do not preserve attractive but stale assets after their UI, feature set, localization, or purchase model changed.

## Final native packaging hygiene

Before the final native generation, sync, or archive:

1. Stop development servers, file watchers, hot-reload processes, and other generators that can rewrite build output.
2. Start from the project's documented clean generated-output boundary. Do not delete user files or unknown output.
3. Generate and sync exactly once from the frozen source state.
4. Inspect the native payload for the intended entry point, packaged resources, localizations, privacy files, products, and production endpoints.
5. Reject numbered duplicate files/directories, stale web assets, prior-version resources, placeholders, missing media, or a development-server dependency.
6. Run any project-specific payload inventory or hash check after sync and again against the archive.
7. Archive without changing source, configuration, products, or assets between validation and upload.

For hybrid apps, explicitly prove that the native container launches the intended application edition. A working browser route does not prove what was copied into the iOS bundle.

## Device evidence

Set the physical-device gate only when the exact candidate:

1. was installed;
2. launched past the root screen while unlocked;
3. completed the critical path with all expected controls and packaged assets;
4. survived a cold relaunch;
5. for an update, also launched over realistic data from the previous public version.

Record the tested build number. If launch was blocked by a locked or disconnected device, report only `installed`; the gate remains incomplete.

## Efficient resume

On every invocation:

1. read the project's canonical release record;
2. refresh the smallest set of live Apple statuses that could have changed;
3. build the release-identity rows;
4. invalidate only mismatched evidence;
5. continue from the first dependency blocker;
6. leave external processing as `external wait`, not as work to repeat.
7. after any live store mutation or review response, reconcile the ledger,
   canonical status, agent handoffs and reusable review copy before declaring
   the action delivered.

This prevents the two expensive failure modes: redoing valid work and submitting evidence that belongs to a different candidate.
