#!/usr/bin/env python3
"""Deterministic theorem site build with optional verified mathDef snapshot bundle."""
import hashlib
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
BASE = "https://zengez.github.io/mathDef/api/definitions/v1/"

def request_json(url):
    with urllib.request.urlopen(urllib.request.Request(
        url, headers={"User-Agent": "mathThm-prototype/0.1", "Cache-Control": "no-cache"}
    ), timeout=18) as response:
        data = response.read()
    return data, json.loads(data.decode("utf-8"))

def fetch_mathdef():
    raw, manifest = request_json(BASE + "manifest.json")
    if (manifest.get("schema") != "mathdef.definition-manifest.v1" or
            manifest.get("snapshot_schema") != "mathdef.definition-snapshot.v1" or
            manifest.get("dataset") != "production" or
            manifest.get("snapshot_path") != "snapshot.json"):
        raise ValueError("Unexpected mathDef manifest or non-production dataset")
    expected = manifest.get("sha256", "")
    if len(expected) != 64 or manifest.get("version") != "sha256:" + expected:
        raise ValueError("Invalid mathDef version/digest")
    body, data = request_json(BASE + "snapshot.json?v=" + expected)
    if hashlib.sha256(body).hexdigest() != expected:
        raise ValueError("mathDef snapshot checksum mismatch")
    if data.get("schema") != "mathdef.definition-snapshot.v1" or not isinstance(data.get("definitions"), list):
        raise ValueError("Unexpected mathDef snapshot shape")
    (SITE / "mathdef-snapshot.json").write_bytes(body)
    (SITE / "mathdef-manifest.json").write_bytes(raw)
    print("Bundled verified mathDef production snapshot: " + str(len(data["definitions"])) + " definitions")

def build():
    corpus = json.loads((ROOT / "data/theorems.json").read_text(encoding="utf-8"))
    if corpus.get("schema") != "maththm.theorems.v1":
        raise ValueError("Unknown theorem schema")
    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(ROOT / "web", SITE)
    shutil.copyfile(ROOT / "data/theorems.json", SITE / "theorems.json")
    (SITE / ".nojekyll").touch()
    try:
        fetch_mathdef()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError) as exc:
        print("Warning: could not bundle mathDef snapshot; browser will attempt live refresh: " + str(exc))
    print(f"Built mathThm prototype with {len(corpus['records'])} research-draft results")

if __name__ == "__main__":
    build()
