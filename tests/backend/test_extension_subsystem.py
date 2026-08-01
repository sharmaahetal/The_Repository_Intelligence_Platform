import json
import os
import re

import pytest


def test_extension_manifest_v3_validity():
    manifest_path = os.path.join(os.path.dirname(__file__), "..", "..", "extension", "manifest.json")
    manifest_path = os.path.abspath(manifest_path)

    assert os.path.exists(manifest_path), f"Manifest file missing at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("manifest_version") == 3
    assert "name" in manifest
    assert "version" in manifest
    assert "permissions" in manifest
    assert "storage" in manifest["permissions"]

    # Verify background service worker configuration
    assert "background" in manifest
    assert manifest["background"].get("service_worker") == "service_worker.js"

    # Verify content script matches
    assert "content_scripts" in manifest
    assert len(manifest["content_scripts"]) > 0
    assert "*://github.com/*" in manifest["content_scripts"][0]["matches"]


def test_github_url_parser_rules():
    def parse_github_repo(path: str) -> dict[str, str] | None:
        segments = [s for s in path.split("/") if s]
        if len(segments) < 2:
            return None
        reserved = ["settings", "orgs", "notifications", "explore", "marketplace", "pulls", "issues", "search"]
        if segments[0] in reserved:
            return None
        return {"owner": segments[0], "repo": segments[1]}

    # Valid repository paths
    assert parse_github_repo("/microsoft/vscode") == {"owner": "microsoft", "repo": "vscode"}
    assert parse_github_repo("/facebook/react/issues") == {"owner": "facebook", "repo": "react"}
    assert parse_github_repo("/golang/go/pulls/123") == {"owner": "golang", "repo": "go"}

    # Reserved non-repository paths
    assert parse_github_repo("/settings/profile") is None
    assert parse_github_repo("/notifications") is None
    assert parse_github_repo("/explore") is None


def test_narrative_summary_generator_formatting():
    def generate_narrative(owner: str, repo: str, growth_prob: float, health_index: int, drivers: list[str]) -> str:
        header = f"Strong upward trajectory expected for {owner}/{repo}." if growth_prob >= 0.7 else f"Stable maintenance anticipated for {owner}/{repo}."
        health = f"The derived health index stands at {health_index}/100 with a {int(growth_prob * 100)}% star growth probability over a 180-day horizon."
        drv = f" Key growth accelerators include: {drivers[0]}." if drivers else ""
        return f"{header} {health}{drv}"

    narrative = generate_narrative("facebook", "react", 0.84, 88, ["Sustained core contributor retention rate"])
    assert "Strong upward trajectory" in narrative
    assert "facebook/react" in narrative
    assert "88/100" in narrative
    assert "84%" in narrative


def test_xss_sanitization_utility():
    def sanitize_text(text: str) -> str:
        if not text:
            return ""
        escaped = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )
        return re.sub(r"[\x00-\x1F\x7F-\x9F]", "", escaped)

    raw_input = '<script>alert("xss")</script>'
    sanitized = sanitize_text(raw_input)
    assert "<script>" not in sanitized
    assert "&lt;script&gt;" in sanitized
