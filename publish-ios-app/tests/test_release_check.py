from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib


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
            'source_commit = ""': f'source_commit = "{"a" * 40}"',
            'archive_sha256 = ""': f'archive_sha256 = "{"b" * 64}"',
            'uploaded_build_id = ""': 'uploaded_build_id = "build-42"',
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


if __name__ == "__main__":
    unittest.main()
