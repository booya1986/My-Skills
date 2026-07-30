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
2. Run the project's Capacitor sync command for iOS.
3. Inspect native diffs created by the sync.
4. Build and test the Xcode workspace/project in `ios/`.
5. Verify native plugins, URL schemes, permissions, privacy manifests, and icons.

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
