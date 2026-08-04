# Project Stack Routing

Use the existing project conventions first. The commands below are discovery patterns, not a replacement for repository instructions.

## Native Swift or Objective-C

Signals:

- `.xcodeproj` or `.xcworkspace`;
- Swift Package Manager, CocoaPods, or Xcode-managed dependencies;
- SwiftUI, UIKit, or Objective-C application targets.

Actions:

1. Prefer the workspace when dependency tooling created one.
2. List schemes and build settings with `xcodebuild`.
3. Resolve packages before archiving.
4. Build and test the Release configuration.
5. Archive with a generic iOS destination.
6. Inspect the produced `.xcarchive` before export.

Do not guess the shared scheme. If the intended scheme is not shared, make the minimum project change and explain its CI impact.

## Capacitor

Signals:

- `capacitor.config.*`;
- an `ios/App` native project;
- web build output synced into the iOS container.

Actions:

1. Run the project's package-manager checks and production web build.
2. Stop the development server, hot reload, and file watchers before the final sync.
3. Run the project's Capacitor sync command for iOS exactly once from the frozen source state.
4. Inspect native diffs and generated output for numbered duplicates, stale routes/assets, and the intended native entry point.
5. Build and test the Xcode workspace/project in `ios/`.
6. Verify native plugins, URL schemes, permissions, privacy manifests, and icons.

Never archive stale web assets. The commit, web build, synced native assets, archive, and uploaded build must represent the same source state.

## React Native

Signals:

- `react-native` dependency;
- `ios/Podfile`;
- Metro configuration.

Actions:

1. Use the repository's package manager and lockfile.
2. Install pods only when required and preserve the lockfile.
3. Build the intended workspace and scheme.
4. Confirm the Release bundle is embedded and does not depend on a development server.
5. Verify native permissions and privacy manifests for third-party SDKs.

## Flutter

Signals:

- `pubspec.yaml`;
- `ios/Runner.xcworkspace`;
- Flutter-generated iOS configuration.

Actions:

1. Use the pinned Flutter version when the project defines one.
2. Fetch packages and run analysis/tests.
3. Build the iOS archive or IPA with the project flavor and entry point.
4. Inspect the Runner archive, bundle identifier, version/build, icons, entitlements, and embedded frameworks.

## Shared archive checks

For every stack:

- build from a known commit and record the source state;
- use the intended Release configuration;
- confirm no debug server, menu, entitlement, certificate, or test product leaks into the archive;
- inspect the archived `Info.plist`, entitlements, frameworks, privacy manifests, and icons;
- ensure the archive version/build match the App Store Connect version record;
- validate with the installed current Apple toolchain before upload.
- record the Apple build number used by upload, TestFlight, and physical-device validation and require it to match the release ledger.

## Universal device regression

Before freezing any first release or update:

- install the exact candidate on a physical supported device and record its build number;
- cold-launch it and verify the root screen is interactive rather than blank;
- for an update, install over realistic data from the previous public version and preserve user state;
- exercise every control on the primary user journey, not only the first rendered screen;
- verify packaged images, audio, video, fonts, localized resources, and offline fallbacks load from native paths;
- test relaunch and interruption recovery;
- inspect crashes, hangs, responsiveness, Reduce Motion, and accessibility behavior.

Browser, simulator, and Debug evidence are useful but do not prove that the uploaded Release/TestFlight payload behaves the same way.
Installation evidence alone is also insufficient: if the device was locked or the launch was not observed, record only `installed` and leave the physical-device gate incomplete.
