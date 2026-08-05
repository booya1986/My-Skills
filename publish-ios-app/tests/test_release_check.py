from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_check.py"
SPEC = importlib.util.spec_from_file_location("release_check", SCRIPT)
assert SPEC and SPEC.loader
release_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_check)


def png_bytes(width: int, height: int) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + (b"\x00\x00\x00" * width)
    return signature + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(row * height)) + chunk(b"IEND", b"")


class ReleaseCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        (self.project / ".app-store").mkdir()
        (self.project / "store-assets" / "screenshots").mkdir(parents=True)
        (self.project / "store-assets" / "app-icon-1024.png").write_bytes(
            png_bytes(1024, 1024)
        )
        (self.project / "store-assets" / "screenshots" / "home.png").write_bytes(
            png_bytes(100, 200)
        )
        (self.project / ".app-store" / "review-notes.md").write_text(
            "Review the primary path.", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def manifest_text(self) -> str:
        template = release_check.TEMPLATE.read_text(encoding="utf-8")
        replacements = {
            'name = "Example App"': 'name = "Release Test"',
            'bundle_id = "com.example.app"': 'bundle_id = "com.acme.release-test"',
            'release_notes = "Describe user-visible changes."': 'release_notes = "Validated release."',
            'privacy_policy_url = "https://example.com/privacy"': 'privacy_policy_url = "https://acme.test/privacy"',
            'support_url = "https://example.com/support"': 'support_url = "https://acme.test/support"',
            'category = "Choose in App Store Connect"': 'category = "Games"',
            'content_rights = "unresolved"': 'content_rights = "confirmed-by-owner"',
            'encryption = "unresolved"': 'encryption = "confirmed-by-owner"',
            'status = "draft"': 'status = "ready"',
            'model = "unresolved"': 'model = "free"',
            'source_commit = ""': f'source_commit = "{"a" * 40}"',
            'archive_sha256 = ""': f'archive_sha256 = "{"b" * 64}"',
            'uploaded_build_id = ""': 'uploaded_build_id = "build-42"',
            'uploaded_build_number = ""': 'uploaded_build_number = "1"',
            'testflight_tested_build = ""': 'testflight_tested_build = "1"',
            'device_tested_build = ""': 'device_tested_build = "1"',
        }
        for old, new in replacements.items():
            template = template.replace(old, new)
        for gate in (
            "account_holder_confirmed",
            "legal_entity_verified",
            "compliance_complete",
            "app_privacy_complete",
            "age_rating_complete",
            "content_rights_complete",
            "export_compliance_complete",
            "metadata_complete",
            "metadata_urls_live",
            "terms_link_in_description",
            "screenshots_complete",
            "review_information_complete",
            "review_paths_verified",
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
        ):
            template = template.replace(f"{gate} = false", f"{gate} = true")
        return template

    def validate(self, text: str, strict: bool = True):
        manifest = self.project / ".app-store" / "release.toml"
        manifest.write_text(text, encoding="utf-8")
        environment = {
            "ASC_REVIEW_FIRST_NAME": "present",
            "ASC_REVIEW_LAST_NAME": "present",
            "ASC_REVIEW_EMAIL": "present",
            "ASC_REVIEW_PHONE": "present",
        }
        with patch.dict(os.environ, environment, clear=False):
            return release_check.validate_manifest(self.project, manifest, strict)

    def test_free_release_passes_universal_strict_gates(self) -> None:
        report = self.validate(self.manifest_text())
        self.assertEqual([], report.blockers)

    def test_standard_eula_requires_canonical_url(self) -> None:
        text = self.manifest_text().replace(
            release_check.APPLE_STANDARD_EULA, "https://acme.test/terms"
        )
        report = self.validate(text)
        self.assertTrue(any("canonical Apple Standard EULA" in item for item in report.blockers))

    def test_custom_eula_uses_app_store_connect_gate(self) -> None:
        text = self.manifest_text()
        text = text.replace('eula_mode = "apple-standard"', 'eula_mode = "custom"')
        text = text.replace(release_check.APPLE_STANDARD_EULA, "https://acme.test/terms")
        text = text.replace("terms_link_in_description = true", "terms_link_in_description = false")
        text = text.replace("custom_eula_configured = false", "custom_eula_configured = true")
        report = self.validate(text)
        self.assertEqual([], report.blockers)

    def test_iap_requires_matching_product_evidence_and_gates(self) -> None:
        review_dir = self.project / "store-assets" / "iap-review"
        review_dir.mkdir()
        (review_dir / "lifetime.png").write_bytes(png_bytes(100, 200))
        (self.project / ".app-store" / "iap-notes.md").write_text(
            "Open Settings and select Premium.", encoding="utf-8"
        )
        text = self.manifest_text().replace('model = "free"', 'model = "iap"')
        product = """

[[in_app_purchases]]
product_id = "com.acme.release-test.lifetime"
type = "non_consumable"
entitlement = "premium"
first_of_type = true
review_screenshot = "store-assets/iap-review/lifetime.png"
review_notes_file = ".app-store/iap-notes.md"
"""
        text = text.replace("\n[artifacts]\n", product + "\n[artifacts]\n")
        for gate in (
            "agreements_active",
            "banking_complete",
            "tax_complete",
            "products_ready",
            "iap_review_assets_complete",
            "in_app_legal_links",
            "monetization_copy_matches",
        ):
            text = text.replace(f"{gate} = false", f"{gate} = true")
        report = self.validate(text)
        self.assertEqual([], report.blockers)

    def test_completed_test_gate_requires_the_same_release_build(self) -> None:
        text = self.manifest_text().replace(
            'device_tested_build = "1"', 'device_tested_build = "2"'
        )
        report = self.validate(text)
        self.assertTrue(
            any(
                "Physical-device-tested build evidence (2) does not match release.build (1)"
                in item
                for item in report.blockers
            )
        )

    def test_plan_returns_only_the_first_incomplete_phase(self) -> None:
        text = self.manifest_text().replace(
            "metadata_complete = true", "metadata_complete = false"
        )
        manifest = self.project / ".app-store" / "release.toml"
        manifest.write_text(text, encoding="utf-8")
        data = tomllib.loads(text)
        plan = release_check.build_release_plan(
            data["gates"], data["monetization"]["model"], data["release"]["eula_mode"]
        )
        self.assertEqual("metadata", plan["current_phase"])
        self.assertEqual(
            [{"gate": "metadata_complete", "owner": "agent"}], plan["next_gates"]
        )
        self.assertEqual(["submission"], plan["queued_phases"])

    def test_init_autofills_unique_xcode_identity_and_review_notes(self) -> None:
        project = self.project / "Sample Product"
        pbxproj = project / "Sample.xcodeproj" / "project.pbxproj"
        pbxproj.parent.mkdir(parents=True)
        pbxproj.write_text(
            "\n".join(
                (
                    "PRODUCT_BUNDLE_IDENTIFIER = com.acme.sample;",
                    "MARKETING_VERSION = 2.4;",
                    "CURRENT_PROJECT_VERSION = 17;",
                )
            ),
            encoding="utf-8",
        )
        (project / "capacitor.config.ts").write_text(
            "export default { appId: 'com.acme.sample', appName: 'Sample Mobile' };",
            encoding="utf-8",
        )
        manifest = project / ".app-store" / "release.toml"
        self.assertEqual(0, release_check.init_manifest(project, manifest))
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual("Sample Mobile", data["app"]["name"])
        self.assertEqual("com.acme.sample", data["app"]["bundle_id"])
        self.assertEqual("2.4", data["release"]["version"])
        self.assertEqual("17", data["release"]["build"])
        self.assertTrue((project / ".app-store" / "review-notes.md").is_file())


if __name__ == "__main__":
    unittest.main()
