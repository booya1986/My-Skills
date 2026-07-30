#!/usr/bin/env python3
"""Initialize and validate a privacy-safe iOS App Store release ledger."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    print("Python 3.11 or newer is required (missing tomllib).", file=sys.stderr)
    raise SystemExit(2)


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "release-manifest.toml"
DEFAULT_MANIFEST = Path(".app-store/release.toml")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PAID_MODELS = {"paid", "iap", "subscription"}
VALID_MODELS = {"free", "paid", "iap", "subscription"}
VALID_STATUSES = {
    "draft",
    "prepared",
    "uploaded",
    "testflight-tested",
    "ready",
    "submitted",
    "in-review",
    "approved",
    "released",
    "rejected",
}


class Report:
    def __init__(self) -> None:
        self.blockers: list[str] = []
        self.warnings: list[str] = []
        self.passed: list[str] = []
        self.facts: dict[str, Any] = {}

    def blocker(self, message: str) -> None:
        self.blockers.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def ok(self, message: str) -> None:
        self.passed.append(message)

    def payload(self) -> dict[str, Any]:
        return {
            "ready": not self.blockers,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "passed": self.passed,
            "facts": self.facts,
        }


def absolute(project: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project / path


def png_info(path: Path) -> tuple[int, int, bool] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(26)
        if len(header) < 26 or header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        width, height = struct.unpack(">II", header[16:24])
        color_type = header[25]
        return width, height, color_type in {4, 6}
    except OSError:
        return None


def is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    markers = (
        "example app",
        "com.example.",
        "example.com",
        "choose in app store connect",
        "describe user-visible changes",
        "<",
        ">",
        "todo",
        "replace-me",
    )
    return not lowered or any(marker in lowered for marker in markers)


def table(data: dict[str, Any], key: str, report: Report) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        report.blocker(f"Missing [{key}] table.")
        return {}
    return value


def require_value(section: dict[str, Any], key: str, label: str, report: Report) -> None:
    value = section.get(key)
    if value is None or is_placeholder(value):
        report.blocker(f"{label} is missing or still a placeholder.")
    else:
        report.ok(f"{label} is set.")


def check_sensitive_text(raw: str, report: Report) -> None:
    checks = {
        "a local user-directory path": r"(?:/Users/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)",
        "a private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "an App Store Connect private-key filename": r"\bAuthKey_[A-Z0-9]+\.p8\b",
        "an email address": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "a likely API token": r"\b(?:sk[-_][A-Za-z0-9_-]{16,}|test_[A-Za-z0-9]{20,})\b",
    }
    for label, pattern in checks.items():
        if re.search(pattern, raw, flags=re.IGNORECASE):
            report.blocker(
                f"The release ledger contains {label}; replace it with an environment-variable name."
            )


def discover_project(project: Path, report: Report) -> None:
    excluded = {".git", "node_modules", "Pods", "DerivedData", "build", ".dart_tool"}
    found: dict[str, list[str]] = {
        "xcodeproj": [],
        "xcworkspace": [],
        "capacitor": [],
        "react_native": [],
        "flutter": [],
    }
    for root, directories, files in os.walk(project):
        directories[:] = [name for name in directories if name not in excluded]
        root_path = Path(root)
        relative_root = root_path.relative_to(project)
        for directory in list(directories):
            relative = str(relative_root / directory)
            if directory.endswith(".xcodeproj"):
                found["xcodeproj"].append(relative)
            elif directory.endswith(".xcworkspace"):
                found["xcworkspace"].append(relative)
        file_set = set(files)
        if any(name.startswith("capacitor.config.") for name in files):
            found["capacitor"].append(str(relative_root))
        if "pubspec.yaml" in file_set:
            found["flutter"].append(str(relative_root))
        package_json = root_path / "package.json"
        if package_json.is_file():
            try:
                package_text = package_json.read_text(encoding="utf-8", errors="ignore")
                if '"react-native"' in package_text:
                    found["react_native"].append(str(relative_root))
            except OSError:
                pass
    report.facts["project_detection"] = {key: sorted(set(value)) for key, value in found.items()}
    if found["xcworkspace"] or found["xcodeproj"]:
        report.ok("An Xcode project or workspace was detected.")
    else:
        report.warning("No Xcode project or workspace was detected; native generation or sync may be required.")


def validate_manifest(project: Path, manifest_path: Path, strict: bool) -> Report:
    report = Report()
    if not manifest_path.is_file():
        report.blocker(
            f"Release ledger not found at {manifest_path}. Run the init command in a write-enabled mode."
        )
        discover_project(project, report)
        return report

    raw = manifest_path.read_text(encoding="utf-8")
    check_sensitive_text(raw, report)
    try:
        data = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as error:
        report.blocker(f"Invalid TOML: {error}")
        discover_project(project, report)
        return report

    if data.get("schema_version") != 1:
        report.blocker("schema_version must be 1.")

    app = table(data, "app", report)
    release = table(data, "release", report)
    monetization = table(data, "monetization", report)
    artifacts = table(data, "artifacts", report)
    gates = table(data, "gates", report)

    require_value(app, "name", "App name", report)
    require_value(app, "bundle_id", "Bundle identifier", report)
    if app.get("platform") != "ios":
        report.blocker("app.platform must be 'ios'.")
    else:
        report.ok("Platform is iOS.")
    require_value(app, "primary_locale", "Primary locale", report)

    require_value(release, "version", "Marketing version", report)
    require_value(release, "build", "Build number", report)
    require_value(release, "release_notes", "Release notes", report)
    require_value(release, "privacy_policy_url", "Privacy policy URL", report)
    require_value(release, "support_url", "Support URL", report)
    require_value(release, "category", "Primary category", report)

    status = release.get("status")
    if status not in VALID_STATUSES:
        report.blocker(f"release.status must be one of: {', '.join(sorted(VALID_STATUSES))}.")
    else:
        report.facts["release_status"] = status

    for key, label in (
        ("content_rights", "Content rights"),
        ("encryption", "Encryption/export compliance"),
    ):
        if release.get(key) == "unresolved" or is_placeholder(release.get(key)):
            report.blocker(f"{label} is unresolved.")

    prefix = release.get("review_contact_env_prefix")
    if not isinstance(prefix, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", prefix):
        report.blocker("review_contact_env_prefix must be an uppercase environment-variable prefix.")
    elif strict:
        required_env = [
            f"{prefix}_FIRST_NAME",
            f"{prefix}_LAST_NAME",
            f"{prefix}_EMAIL",
            f"{prefix}_PHONE",
        ]
        missing = [name for name in required_env if not os.environ.get(name)]
        if missing:
            report.blocker(
                "Review contact environment variables are missing: " + ", ".join(missing)
            )
        else:
            report.ok("Review contact environment variables are present; values were not read or printed.")

    model = monetization.get("model")
    if model not in VALID_MODELS:
        report.blocker(f"monetization.model must be one of: {', '.join(sorted(VALID_MODELS))}.")
    else:
        report.facts["monetization_model"] = model

    subscriptions = data.get("subscriptions", [])
    if model == "subscription":
        if not isinstance(subscriptions, list) or not subscriptions:
            report.blocker("Subscription monetization requires at least one [[subscriptions]] entry.")
        else:
            for index, subscription in enumerate(subscriptions, start=1):
                if not isinstance(subscription, dict):
                    report.blocker(f"Subscription {index} is invalid.")
                    continue
                for key in (
                    "product_id",
                    "group_reference",
                    "period",
                    "price_note",
                    "introductory_offer",
                    "entitlement",
                ):
                    if is_placeholder(subscription.get(key)):
                        report.blocker(f"Subscription {index} field '{key}' is missing or a placeholder.")
            report.facts["subscription_count"] = len(subscriptions)
    elif subscriptions:
        report.warning("Subscription entries exist but monetization.model is not 'subscription'.")

    icon_value = artifacts.get("app_icon_1024")
    if not isinstance(icon_value, str) or not icon_value:
        report.blocker("artifacts.app_icon_1024 is missing.")
    else:
        icon_path = absolute(project, icon_value)
        if not icon_path.is_file():
            report.blocker(f"App Store icon not found at {icon_path}.")
        elif icon_path.suffix.lower() != ".png":
            report.blocker("The App Store icon must be a PNG.")
        else:
            info = png_info(icon_path)
            if info is None:
                report.blocker("The App Store icon is not a readable PNG.")
            else:
                width, height, has_alpha = info
                report.facts["app_icon"] = {
                    "path": str(icon_path.relative_to(project)) if icon_path.is_relative_to(project) else icon_path.name,
                    "width": width,
                    "height": height,
                    "alpha_channel": has_alpha,
                }
                if (width, height) != (1024, 1024):
                    report.blocker(f"App Store icon is {width}×{height}; expected 1024×1024.")
                elif has_alpha:
                    report.blocker("App Store icon PNG has an alpha channel; export an opaque icon.")
                else:
                    report.ok("App Store icon is 1024×1024 and opaque.")

    screenshots_value = artifacts.get("screenshots_dir")
    screenshot_count = 0
    if isinstance(screenshots_value, str) and screenshots_value:
        screenshots_dir = absolute(project, screenshots_value)
        if screenshots_dir.is_dir():
            screenshot_count = len(
                [
                    path
                    for path in screenshots_dir.rglob("*")
                    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
                ]
            )
    report.facts["screenshot_count"] = screenshot_count
    if screenshot_count == 0:
        report.blocker("No App Store screenshots were found in artifacts.screenshots_dir.")
    else:
        report.ok(f"Found {screenshot_count} screenshot file(s); verify current Apple dimensions separately.")

    required_gates = {
        "account_holder_confirmed",
        "legal_entity_verified",
        "compliance_complete",
        "app_privacy_complete",
        "age_rating_complete",
        "content_rights_complete",
        "export_compliance_complete",
        "metadata_complete",
        "screenshots_complete",
        "review_information_complete",
        "build_uploaded",
        "testflight_passed",
        "physical_device_passed",
        "release_frozen",
        "submission_approved",
    }
    if model in PAID_MODELS:
        required_gates.update(
            {"agreements_active", "banking_complete", "tax_complete", "products_ready"}
        )

    incomplete = sorted(key for key in required_gates if gates.get(key) is not True)
    report.facts["incomplete_gates"] = incomplete
    if strict and incomplete:
        report.blocker("Incomplete strict gates: " + ", ".join(incomplete))
    elif incomplete:
        report.warning("Incomplete release gates: " + ", ".join(incomplete))
    else:
        report.ok("All required release gates are complete.")

    if gates.get("submitted") is True and status not in {
        "submitted",
        "in-review",
        "approved",
        "released",
        "rejected",
    }:
        report.blocker("gates.submitted is true but release.status is not a post-submission status.")

    if gates.get("release_frozen") is True:
        prerequisites = ("testflight_passed", "physical_device_passed", "build_uploaded")
        missing = [key for key in prerequisites if gates.get(key) is not True]
        if missing:
            report.blocker("Release is frozen before required testing/upload gates: " + ", ".join(missing))

    discover_project(project, report)
    return report


def print_report(report: Report, as_json: bool) -> None:
    payload = report.payload()
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"Ready: {'yes' if payload['ready'] else 'no'}")
    for heading, key in (
        ("BLOCKERS", "blockers"),
        ("WARNINGS", "warnings"),
        ("PASSED", "passed"),
    ):
        items = payload[key]
        if items:
            print(f"\n{heading}")
            for item in items:
                print(f"- {item}")
    if payload["facts"]:
        print("\nFACTS")
        print(json.dumps(payload["facts"], indent=2, sort_keys=True))


def init_manifest(project: Path, manifest: Path) -> int:
    if manifest.exists():
        print(f"Refusing to overwrite existing release ledger: {manifest}", file=sys.stderr)
        return 1
    manifest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE, manifest)
    print(f"Created {manifest}")
    print("Replace placeholders, keep sensitive values in environment variables, then run check.")
    return 0


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(
        description="Initialize and validate an iOS App Store release ledger."
    )
    subparsers = command_parser.add_subparsers(dest="command", required=True)
    for command in ("init", "check"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--project", default=".", help="App repository root.")
        subparser.add_argument(
            "--manifest",
            default=str(DEFAULT_MANIFEST),
            help="Manifest path, relative to the project unless absolute.",
        )
        if command == "check":
            subparser.add_argument("--strict", action="store_true")
            subparser.add_argument("--json", action="store_true")
    return command_parser


def main() -> int:
    args = parser().parse_args()
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"Project directory not found: {project}", file=sys.stderr)
        return 2
    manifest = absolute(project, args.manifest).resolve()
    if args.command == "init":
        return init_manifest(project, manifest)
    report = validate_manifest(project, manifest, args.strict)
    print_report(report, args.json)
    return 0 if not report.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
