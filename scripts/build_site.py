#!/usr/bin/env python3
"""Build mathThm with mathDef's canonical, content-addressed public v2 feed.

Theorems remain mathThm-owned. Definitions/meanings/links come from mathDef
and are never modified here. The published bundle is checksum verified; if
network access is down, the browser can independently verify the LIVE v2
feed. We never silently fall back to the original-only v1 feed.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from scripts.theorem_schema import validate as validate_theorem_catalog

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
BASE = "https://zengez.github.io/mathDef/api/definitions/v2/"
MANIFEST_SCHEMA = "mathdef.definition-manifest.v2"
SNAPSHOT_SCHEMA = "mathdef.definition-snapshot.v2"


def request_json(url):
    with urllib.request.urlopen(urllib.request.Request(
        url, headers={"User-Agent": "mathThm-v2-consumer/1.0", "Cache-Control": "no-cache"}
    ), timeout=25) as response:
        data = response.read()
    return data, json.loads(data.decode("utf-8"))


def validate_v2(manifest: dict, body: bytes) -> dict:
    if (manifest.get("schema") != MANIFEST_SCHEMA or
            manifest.get("snapshot_schema") != SNAPSHOT_SCHEMA or
            manifest.get("dataset") != "merged" or
            manifest.get("snapshot_path") != "snapshot.json"):
        raise ValueError("Unexpected mathDef v2 manifest or wrong dataset")
    expected = manifest.get("sha256")
    if (not isinstance(expected, str) or len(expected) != 64 or
            any(c not in "0123456789abcdef" for c in expected) or
            manifest.get("version") != "sha256:" + expected):
        raise ValueError("Invalid mathDef v2 content hash")
    if hashlib.sha256(body).hexdigest() != expected:
        raise ValueError("mathDef v2 snapshot checksum mismatch")
    snapshot = json.loads(body.decode("utf-8"))
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("Unexpected mathDef v2 snapshot schema")
    groups = snapshot.get("definitions")
    if not isinstance(groups, list) or len(groups) != manifest.get("definition_count"):
        raise ValueError("Incomplete mathDef v2 term catalog")
    if len({g["id"] for g in groups}) != len(groups):
        raise ValueError("Duplicate mathDef v2 term group")
    meanings = [m for g in groups for m in g["meanings"]]
    forms = [f for g in groups for f in g["formulations"]]
    if (len(meanings) != manifest.get("meaning_count") or
            len(forms) != manifest.get("formulation_count") or
            len({m["id"] for m in meanings}) != len(meanings) or
            len({f["key"] for f in forms}) != len(forms)):
        raise ValueError("Incomplete or duplicate mathDef v2 meanings/formulations")
    if not all(m.get("subject") for m in meanings):
        raise ValueError("mathDef v2 meaning lacks official Subject")
    if not all(f.get("meaning_id") and f.get("subject") for f in forms):
        raise ValueError("mathDef v2 formulation lacks meaning or Subject")
    originals = [oid for g in groups for oid in g.get("original_ids", [])]
    if (len(originals) != manifest.get("original_definition_count") or
            len(originals) != len(set(originals))):
        raise ValueError("Missing or duplicated mathDef historical original IDs")
    aliases = snapshot.get("consolidated_ids")
    if not isinstance(aliases, dict) or not all(
            isinstance(aliases.get(k), dict) for k in
            ("group_aliases", "meaning_aliases", "formulation_aliases")):
        raise ValueError("mathDef v2 missing historical ID redirect registry")
    return snapshot


def verify_theorem_hints(snapshot: dict, theorem_corpus: dict) -> int:
    """Guarantee every existing theorem link hint survives old-ID migration."""
    available = {g["id"] for g in snapshot["definitions"]}
    available.update(oid for g in snapshot["definitions"]
                     for oid in g.get("original_ids", []))
    for key in ("group_aliases", "meaning_aliases", "formulation_aliases"):
        available.update(snapshot["consolidated_ids"][key])
    unresolved = sorted({hint[1] for theorem in theorem_corpus["records"]
                         for hint in theorem.get("link_hints", [])
                         if len(hint) != 2 or hint[1] not in available})
    if unresolved:
        raise ValueError("mathDef v2 lost theorem link hint IDs: " +
                         ", ".join(unresolved[:15]))
    return sum(len(theorem.get("link_hints", []))
               for theorem in theorem_corpus["records"])


def fetch_mathdef(theorem_corpus: dict) -> dict:
    raw, manifest = request_json(BASE + "manifest.json")
    if not isinstance(manifest, dict):
        raise ValueError("mathDef v2 manifest is not a JSON object")
    body, _ = request_json(BASE + "snapshot.json?v=" + manifest.get("sha256", ""))
    snapshot = validate_v2(manifest, body)
    hints = verify_theorem_hints(snapshot, theorem_corpus)
    (SITE / "mathdef-snapshot.json").write_bytes(body)
    (SITE / "mathdef-manifest.json").write_bytes(raw)
    info = {
        "dataset": "mathdef-v2-merged",
        "terms": len(snapshot["definitions"]),
        "meanings": manifest["meaning_count"],
        "formulations": manifest["formulation_count"],
        "historical_original_ids": manifest["original_definition_count"],
        "theorem_link_hints_resolved": hints,
        "snapshot_version": manifest["version"],
    }
    print("Bundled verified mathDef v2: " + json.dumps(info, sort_keys=True))
    return info


def build():
    corpus = json.loads((ROOT / "data/theorems.json").read_text(encoding="utf-8"))
    summary = validate_theorem_catalog(corpus)
    print("Validated accepted theorem catalog: " + json.dumps(summary, sort_keys=True))
    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(ROOT / "web", SITE)
    shutil.copyfile(ROOT / "data/theorems.json", SITE / "theorems.json")
    (SITE / ".nojekyll").touch()
    try:
        fetch_mathdef(corpus)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError,
            json.JSONDecodeError, KeyError, TypeError) as exc:
        # Search/proof data remain independent. Browser live fallback fetches
        # v2 and verifies the SHA; v1 is never bundled as a substitute.
        print("Warning: no VERIFIED mathDef v2 bundle; browser will check the live v2 feed: " + str(exc))
    print(f"Built mathThm prototype with {len(corpus['records'])} research-draft results")


if __name__ == "__main__":
    build()
