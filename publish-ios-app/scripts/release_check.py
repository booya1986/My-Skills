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
REVIEW_NOTES_TEMPLATE = SKILL_DIR / "assets" / "review-notes-template.md"
DEFAULT_MANIFEST = Path(".app-store/release.toml")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PAID_MODELS = {"paid", "iap", "subscription"}
VALID_MODELS = {"free", "paid", "iap", "subscription"}
PRODUCT_MODELS = {"iap", "subscription"}
VALID_IAP_TYPES = {"consumable", "non_consumable", "non_renewing_subscription"}
VALID_EULA_MODES = {"apple-standard", "custom"}
APPLE_STANDARD_EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
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

GATE_PHASES = (
    (
        "account",
        ("account_holder_confirmed", "legal_entity_verified", "compliance_complete"),
    ),
    ("commercial-account", ("agreements_active", "banking_complete", "tax_complete")),
    (
        "app-record",
        (
            "app_privacy_complete",
            "age_rating_complete",
            "content_rights_complete",
            "export_compliance_complete",
        ),
    ),
    (
        "monetization",
        (
            "products_ready",
            "iap_review_assets_complete",
            "in_app_legal_links",
            "monetization_copy_matches",
        ),
    ),
    (
        "metadata",
        (
            "metadata_complete",
            "metadata_urls_live",
            "terms_link_in_description",
            "custom_eula_configured",
            "screenshots_complete",
            "review_information_complete",
        ),
    ),
    ("candidate", ("native_payload_verified", "build_uploaded")),
    (
        "testflight-device",
        (
            "testflight_passed",
            "physical_device_passed",
            "cold_launch_passed",
            "critical_path_passed",
            "performance_passed",
        ),
    ),
    ("consistency", ("store_assets_match_build", "release_surfaces_match")),
    ("freeze", ("release_frozen",)),
    ("approval", ("submission_approved",)),
    ("submission", ("submitted",)),
)

ACCOUNT_HOLDER_GATES = {
    "account_holder_confirmed",
    "legal_entity_verified",
    "agreements_active",
    "banking_complete",
    "tax_complete",
    "compliance_complete",
    "content_rights_complete",
    "export_compliance_complete",
    "submission_approved",
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


def require_https_url(section: dict[str, Any], key: str, label: str, report: Report) -> str:
    value = section.get(key)
    require_value(section, key, label, report)
    if not isinstance(value, str) or is_placeholder(value):
        return ""
    if not re.fullmatch(r"https://[^\s]+", value.strip(), flags=re.IGNORECASE):
        report.blocker(f"{label} must be a complete HTTPS URL.")
        return ""
    report.ok(f"{label} uses HTTPS; live reachability still requires an external check.")
    return value.strip()


def require_project_file(
    project: Path, section: dict[str, Any], key: str, label: str, report: Report
) -> None:
    value = section.get(key)
    if not isinstance(value, str) or is_placeholder(value):
        report.blocker(f"{label} is missing or still a placeholder.")
        return
    path = absolute(project, value)
    if not path.is_file():
        report.blocker(f"{label} not found at {path}.")
    else:
        report.ok(f"{label} exists.")


def require_matching_build(
    evidence: dict[str, Any], key: str, label: str, release_build: Any, report: Report
) -> None:
    value = evidence.get(key)
    if value is None or is_placeholder(value):
        report.blocker(f"{label} is missing or still a placeholder.")
        return
    if str(value) != str(release_build):
        report.blocker(
            f"{label} ({value}) does not match release.build ({release_build})."
        )
    else:
        report.ok(f"{label} matches release.build.")


def required_release_gates(model: Any, eula_mode: Any) -> set[str]:
    required = {
        "account_holder_confirmed",
        "legal_entity_verified",
        "compliance_complete",
        "app_privacy_complete",
        "age_rating_complete",
        "content_rights_complete",
        "export_compliance_complete",
        "metadata_complete",
        "metadata_urls_live",
        "screenshots_complete",
        "review_information_complete",
        "native_payload_verified",
        "store_assets_match_build",
        "release_surfaces_match",
        "build_uploaded",
        "testflight_passed",
        "physical_device_passed",
        "cold_launch_passed",
        "critical_path_passed",
        "performance_passed",
        "release_frozen",
        "submission_approved",
    }
    if eula_mode == "apple-standard":
        required.add("terms_link_in_description")
    elif eula_mode == "custom":
        required.add("custom_eula_configured")
    if model in PAID_MODELS:
        required.update({"agreements_active", "banking_complete", "tax_complete"})
    if model in PRODUCT_MODELS:
        required.update(
            {
                "products_ready",
                "iap_review_assets_complete",
                "in_app_legal_links",
                "monetization_copy_matches",
            }
        )
    return required


def build_release_plan(
    gates: dict[str, Any], model: Any, eula_mode: Any
) -> dict[str, Any]:
    required = required_release_gates(model, eula_mode) | {"submitted"}
    queue: list[dict[str, Any]] = []
    for phase, phase_gates in GATE_PHASES:
        pending = [gate for gate in phase_gates if gate in required and gates.get(gate) is not True]
        if pending:
            queue.append(
                {
                    "phase": phase,
                    "gates": [
                        {
                            "gate": gate,
                            "owner": "account-holder" if gate in ACCOUNT_HOLDER_GATES else "agent",
                        }
                        for gate in pending
                    ],
                }
            )
    return {
        "complete": not queue,
        "current_phase": queue[0]["phase"] if queue else None,
        "next_gates": queue[0]["gates"] if queue else [],
        "queued_phases": [entry["phase"] for entry in queue[1:]],
        "remaining_gate_count": sum(len(entry["gates"]) for entry in queue),
    }


def unique_project_values(project: Path, setting: str) -> set[str]:
    values: set[str] = set()
    excluded = {".git", "node_modules", "Pods", "DerivedData", "build", ".dart_tool"}
    pattern = re.compile(rf"\b{re.escape(setting)}\s*=\s*([^;]+);")
    for path in project.rglob("project.pbxproj"):
        if any(part in excluded for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in pattern.finditer(text):
            value = match.group(1).strip().strip('"')
            if value and "$" not in value and not is_placeholder(value):
                values.add(value)
    return values


def unique_config_values(project: Path, key: str) -> set[str]:
    values: set[str] = set()
    excluded = {".git", "node_modules", "Pods", "DerivedData", "build", ".dart_tool"}
    pattern = re.compile(rf"(?:['\"]{re.escape(key)}['\"]|\b{re.escape(key)})\s*:\s*['\"]([^'\"]+)['\"]")
    for path in project.rglob("capacitor.config.*"):
        if any(part in excluded for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        values.update(match.group(1).strip() for match in pattern.finditer(text))
    return {value for value in values if value and not is_placeholder(value)}


def discover_release_defaults(project: Path) -> dict[str, str]:
    defaults: dict[str, str] = {}
    app_names = unique_config_values(project, "appName")
    if len(app_names) == 1:
        defaults["name"] = next(iter(app_names))
    else:
        xcode_names = {
            path.stem
            for path in project.rglob("*.xcodeproj")
            if path.stem not in {"App", "Runner", "Pods"}
        }
        defaults["name"] = next(iter(xcode_names)) if len(xcode_names) == 1 else project.name

    bundle_ids = unique_project_values(project, "PRODUCT_BUNDLE_IDENTIFIER")
    bundle_ids.update(unique_config_values(project, "appId"))
    candidates = {
        "bundle_id": bundle_ids,
        "version": unique_project_values(project, "MARKETING_VERSION"),
        "build": unique_project_values(project, "CURRENT_PROJECT_VERSION"),
    }
    for key, values in candidates.items():
        if len(values) == 1:
            defaults[key] = next(iter(values))
    return defaults


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

    if data.get("schema_version") != 3:
        report.blocker(
            "schema_version must be 3. Reconcile the project ledger with the current template; "
            "do not overwrite verified release facts."
        )

    app = table(data, "app", report)
    release = table(data, "release", report)
    monetization = table(data, "monetization", report)
    artifacts = table(data, "artifacts", report)
    evidence = table(data, "evidence", report)
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
    require_https_url(release, "privacy_policy_url", "Privacy policy URL", report)
    require_https_url(release, "support_url", "Support URL", report)
    terms_url = require_https_url(release, "terms_of_use_url", "Terms of Use URL", report)
    eula_mode = release.get("eula_mode")
    if eula_mode not in VALID_EULA_MODES:
        report.blocker(
            "release.eula_mode must be one of: " + ", ".join(sorted(VALID_EULA_MODES)) + "."
        )
    elif eula_mode == "apple-standard":
        if terms_url != APPLE_STANDARD_EULA:
            report.blocker(
                "Apple Standard EULA mode requires the canonical Apple Standard EULA URL."
            )
        else:
            report.ok("Apple Standard EULA URL matches the canonical URL.")
    else:
        report.ok("Custom EULA mode is recorded; App Store Connect configuration requires verification.")
    require_value(release, "category", "Primary category", report)
    require_project_file(
        project,
        release,
        "review_notes_file",
        "App Review notes",
        report,
    )

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
    in_app_purchases = data.get("in_app_purchases", [])
    if model == "subscription":
        if not isinstance(monetization.get("first_subscription"), bool):
            report.blocker("monetization.first_subscription must be true or false.")
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
                require_project_file(
                    project,
                    subscription,
                    "review_screenshot",
                    f"Subscription {index} review screenshot",
                    report,
                )
                require_project_file(
                    project,
                    subscription,
                    "review_notes_file",
                    f"Subscription {index} review notes",
                    report,
                )
            report.facts["subscription_count"] = len(subscriptions)
    elif subscriptions:
        report.warning("Subscription entries exist but monetization.model is not 'subscription'.")

    if model == "iap":
        if not isinstance(in_app_purchases, list) or not in_app_purchases:
            report.blocker("IAP monetization requires at least one [[in_app_purchases]] entry.")
        else:
            for index, product in enumerate(in_app_purchases, start=1):
                if not isinstance(product, dict):
                    report.blocker(f"In-App Purchase {index} is invalid.")
                    continue
                for key in ("product_id", "entitlement"):
                    if is_placeholder(product.get(key)):
                        report.blocker(
                            f"In-App Purchase {index} field '{key}' is missing or a placeholder."
                        )
                product_type = product.get("type")
                if product_type not in VALID_IAP_TYPES:
                    report.blocker(
                        f"In-App Purchase {index} type must be one of: "
                        + ", ".join(sorted(VALID_IAP_TYPES))
                        + "."
                    )
                if not isinstance(product.get("first_of_type"), bool):
                    report.blocker(
                        f"In-App Purchase {index} first_of_type must be true or false."
                    )
                require_project_file(
                    project,
                    product,
                    "review_screenshot",
                    f"In-App Purchase {index} review screenshot",
                    report,
                )
                require_project_file(
                    project,
                    product,
                    "review_notes_file",
                    f"In-App Purchase {index} review notes",
                    report,
                )
            report.facts["in_app_purchase_count"] = len(in_app_purchases)
    elif in_app_purchases:
        report.warning("In-App Purchase entries exist but monetization.model is not 'iap'.")

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

    required_gates = required_release_gates(model, eula_mode)

    incomplete = sorted(key for key in required_gates if gates.get(key) is not True)
    report.facts["incomplete_gates"] = incomplete
    report.facts["release_identity"] = {
        "app": app.get("name"),
        "bundle_id": app.get("bundle_id"),
        "version": release.get("version"),
        "build": release.get("build"),
        "status": status,
    }
    report.facts["release_plan"] = build_release_plan(gates, model, eula_mode)
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

    if gates.get("build_uploaded") is True:
        require_value(evidence, "uploaded_build_id", "Uploaded build evidence", report)
        require_matching_build(
            evidence,
            "uploaded_build_number",
            "Uploaded build number evidence",
            release.get("build"),
            report,
        )

    if gates.get("testflight_passed") is True:
        require_matching_build(
            evidence,
            "testflight_tested_build",
            "TestFlight-tested build evidence",
            release.get("build"),
            report,
        )

    if gates.get("physical_device_passed") is True:
        require_matching_build(
            evidence,
            "device_tested_build",
            "Physical-device-tested build evidence",
            release.get("build"),
            report,
        )

    if gates.get("submitted") is True:
        require_value(evidence, "submission_id", "Submission ID evidence", report)
        checked_at = evidence.get("status_checked_at")
        require_value(evidence, "status_checked_at", "Status verification time", report)
        if isinstance(checked_at, str) and not is_placeholder(checked_at):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})", checked_at):
                report.blocker("evidence.status_checked_at must be an ISO-8601 timestamp with timezone.")

    if gates.get("release_frozen") is True:
        prerequisites = (
            "testflight_passed",
            "physical_device_passed",
            "cold_launch_passed",
            "critical_path_passed",
            "performance_passed",
            "build_uploaded",
            "native_payload_verified",
            "store_assets_match_build",
            "release_surfaces_match",
        )
        missing = [key for key in prerequisites if gates.get(key) is not True]
        if missing:
            report.blocker("Release is frozen before required testing/upload gates: " + ", ".join(missing))
        source_commit = evidence.get("source_commit")
        if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-fA-F]{7,64}", source_commit):
            report.blocker("Frozen release requires evidence.source_commit as a Git commit hash.")
        archive_sha256 = evidence.get("archive_sha256")
        if not isinstance(archive_sha256, str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", archive_sha256
        ):
            report.blocker("Frozen release requires evidence.archive_sha256 as 64 hex characters.")

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


def print_plan(report: Report, as_json: bool) -> None:
    identity = report.facts.get("release_identity", {})
    plan = report.facts.get("release_plan")
    payload = {
        "release": identity,
        "plan": plan,
        "configuration_blockers": report.blockers,
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if identity:
        print(
            "Release: "
            f"{identity.get('app')} {identity.get('version')} ({identity.get('build')}) "
            f"[{identity.get('status')}]"
        )
    if report.blockers:
        print("\nCONFIGURATION BLOCKERS")
        for blocker in report.blockers:
            print(f"- {blocker}")
    if not isinstance(plan, dict):
        print("\nNo dependency plan is available until the manifest is valid enough to read.")
        return
    if plan["complete"]:
        print("\nNext: none; every release and submission gate is complete.")
        return
    print(f"\nNext phase: {plan['current_phase']}")
    for entry in plan["next_gates"]:
        print(f"- {entry['gate']} [{entry['owner']}]")
    if plan["queued_phases"]:
        print("Queued: " + " -> ".join(plan["queued_phases"]))
    print(f"Remaining gates: {plan['remaining_gate_count']}")


def init_manifest(project: Path, manifest: Path) -> int:
    if manifest.exists():
        print(f"Refusing to overwrite existing release ledger: {manifest}", file=sys.stderr)
        return 1
    defaults = discover_release_defaults(project)
    text = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        'name = "Example App"': f"name = {json.dumps(defaults['name'])}",
    }
    if "bundle_id" in defaults:
        replacements['bundle_id = "com.example.app"'] = (
            f"bundle_id = {json.dumps(defaults['bundle_id'])}"
        )
    if "version" in defaults:
        replacements['version = "1.0.0"'] = f"version = {json.dumps(defaults['version'])}"
    if "build" in defaults:
        replacements['build = "1"'] = f"build = {json.dumps(defaults['build'])}"
    for old, new in replacements.items():
        text = text.replace(old, new, 1)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(text, encoding="utf-8")
    review_notes = project / ".app-store" / "review-notes.md"
    if not review_notes.exists():
        shutil.copyfile(REVIEW_NOTES_TEMPLATE, review_notes)
    print(f"Created {manifest}")
    discovered = ", ".join(sorted(defaults))
    print(f"Auto-filled unique project facts: {discovered}.")
    print(f"Created {review_notes}")
    print("Replace remaining placeholders, keep sensitive values in environment variables, then run plan.")
    return 0


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(
        description="Initialize and validate an iOS App Store release ledger."
    )
    subparsers = command_parser.add_subparsers(dest="command", required=True)
    for command in ("init", "check", "plan"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--project", default=".", help="App repository root.")
        subparser.add_argument(
            "--manifest",
            default=str(DEFAULT_MANIFEST),
            help="Manifest path, relative to the project unless absolute.",
        )
        if command in {"check", "plan"}:
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
    if args.command == "plan":
        print_plan(report, args.json)
    else:
        print_report(report, args.json)
    return 0 if not report.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
