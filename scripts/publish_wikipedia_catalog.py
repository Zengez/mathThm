#!/usr/bin/env python3
"""Materialize and publish the 920 already-edited Wikipedia theorem results.

Only intake and publication structure is checked here. Editorial hypothesis /
conclusion divisions are preserved as given, and Wikipedia proof sections have
only undergone proof-presence screening (NOT mathematical validation).

The frozen Wikipedia publication file is made once from 706 original and 214
recovered screened candidates; routine site builds subsequently read only that
canonical file, not transient review queues or live Wikipedia.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "data/wikipedia_theorems.jsonl"
FIRST = ROOT / "work/wikipedia-proof-screen/20261104/proof_screened_candidates.jsonl"
RETRIED = ROOT / "work/wikipedia-proof-screen/20261104/one-time-retry/newly_screened_candidates.jsonl"
EXPECTED_FIRST = 706
EXPECTED_RETRIED = 214
EXPECTED = EXPECTED_FIRST + EXPECTED_RETRIED
BATCH_ID = "wikipedia-editorial-proof-screen-20261104"

# Conservative *editorial convenience* taxonomy from explicit subject terms in
# titles/lead paragraphs; no claim of mathematical classification correctness.
# Uncertain topics stay under Mathematics rather than inventing a subject.
AREAS = [
    ("Algebraic Geometry", r"\balgebraic (?:geometry|variet(?:y|ies)|curve|space|scheme)\b|"
                           r"\b(?:scheme|variet(?:y|ies)|morphism|sheaf|cohomology)\b"),
    ("Differential Geometry", r"\bdifferential geometry\b|\b(?:Riemannian|symplectic|"
                              r"curvature|manifold|geodesic)\b"),
    ("Graph Theory", r"\b(?:graph|digraph|spanning tree|planar|chromatic|Eulerian)\b"),
    ("Number Theory", r"\b(?:number theory|prime|divisib|congruence|Diophantine|"
                      r"quadratic reciprocity|Fermat|Euler totient)\b"),
    ("Probability", r"\b(?:probability|stochastic|random|martingale|Markov|"
                    r"Brownian|expectation|distribution|Bayesian)\b"),
    ("Statistics", r"\b(?:statistics?|statistical|regression|estimation|"
                   r"hypothesis testing|confidence interval)\b"),
    ("Topology", r"\b(?:topolog|homotop|homolog|fundamental group|"
                 r"homeomorph|compactif|knot)\b"),
    ("Analysis", r"\b(?:real analysis|complex analysis|functional analysis|"
                 r"continuity|integral|convergence|Fourier|Lebesgue|"
                 r"differentiab|derivative|Banach|Hilbert|harmonic)\b"),
    ("Logic", r"\b(?:mathematical logic|predicate|first.order|"
              r"proof theory|completeness theorem|incompleteness|model theory)\b"),
    ("Set Theory", r"\b(?:set theory|ordinal|cardinal|axiom of choice|"
                   r"continuum hypothesis|forcing)\b"),
    ("Category Theory", r"\b(?:category theory|Yoneda|adjunction|functor|"
                        r"natural transformation)\b"),
    ("Combinatorics", r"\b(?:combinator|Ramsey|permutation|enumerat|"
                      r"counting|pigeonhole)\b"),
    ("Linear Algebra", r"\b(?:matrix|matrices|determinant|eigenvalue|"
                       r"vector space|linear algebra)\b"),
    ("Differential Equations", r"\b(?:differential equation|ODE|PDE|"
                              r"initial.value problem)\b"),
    ("Geometry", r"\b(?:geometry|triangle|circle|polygon|Euclid|"
                  r"projective geometry|point.line)\b"),
    ("Algebra", r"\b(?:group theory|ring theory|field theory|"
                 r"module theory|Galois|group action)\b"),
]
AREA_REGEX = [(area, re.compile(pattern, re.I)) for area,pattern in AREAS]
VALID_ID = re.compile(r"^candidate\.wikipedia\.[0-9a-f]{20}$")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def checked_strings(xs, label: str, allow_empty: bool = True) -> list[str]:
    if not isinstance(xs,list) or (not allow_empty and not xs) or not all(
            isinstance(x,str) and x.strip() for x in xs):
        raise ValueError("Malformed " + label)
    return list(xs)


def normalized_sides(value, cid):
    if value is None:
        return []
    if not isinstance(value,list):
        raise ValueError("Invalid equivalence sides for "+cid)
    if all(isinstance(v,str) for v in value):
        return [[v] for v in checked_strings(value,"equivalence_sides")]
    if all(isinstance(v,list) and v for v in value):
        return [checked_strings(v,"equivalence_sides",allow_empty=False) for v in value]
    raise ValueError("Invalid equivalence sides for "+cid)


def area_of(row: dict) -> tuple[str,str]:
    title = row["title"]
    excerpt = row.get("source_excerpt") or ""
    # Prefer explicit article-title subject over a vague source lead.
    for area,pattern in AREA_REGEX:
        if pattern.search(title):
            return area,"title_subject_keyword"
    head = excerpt[:500]
    m = re.search(
        r"(?:in|within|from|of) (?:the (?:field|area|branch) of )?"
        r"(?:mathematics[,; ]+)?"
        r"(?:the theory of )?([a-zA-Z][a-zA-Z -]{3,45}?)[,.:;]",
        head, flags=re.I)
    if m:
        field = m.group(1)
        for area,pattern in AREA_REGEX:
            if pattern.search(field):
                return area,"lead_explicit_subject"
    return "Mathematics","not_assigned"


def valid_proof_source(row: dict):
    cid = row.get("candidate_id")
    if not isinstance(cid,str) or not VALID_ID.fullmatch(cid):
        raise ValueError("Invalid canonical Wikipedia ID: "+str(cid))
    if row.get("status") != "standalone_prepared" or (
            row.get("editorial_status") != "standalone_prepared"):
        raise ValueError("Only editorially prepared candidates may be published: "+cid)
    if not isinstance(row.get("statement"),str) or not row["statement"].strip():
        raise ValueError("Missing source-faithful standalone statement: "+cid)
    checked_strings(row.get("hypotheses"),cid+" hypotheses")
    checked_strings(row.get("conclusions"),cid+" conclusions",allow_empty=False)
    article = row.get("url")
    p = urlsplit(article if isinstance(article,str) else "")
    if p.scheme!="https" or p.netloc!="en.wikipedia.org" or not p.path.startswith("/wiki/"):
        raise ValueError("Unexpected Wikipedia source article: "+cid)
    if not isinstance(row.get("title"),str) or not row["title"].strip():
        raise ValueError("Missing Wikipedia article title: "+cid)
    pinfo = row.get("proof_screening")
    if not isinstance(pinfo,dict) or pinfo.get("status")!="appears_to_contain_proof" or (
            pinfo.get("candidate_id") != cid or pinfo.get("url") != article):
        raise ValueError("Missing successful structural proof-presence screening: "+cid)
    if not isinstance(pinfo.get("proof_heading"),str) or not pinfo["proof_heading"].strip():
        raise ValueError("Missing actual proof heading: "+cid)
    proof_url = pinfo.get("proof_url")
    if not isinstance(proof_url,str) or not proof_url.startswith(article+"#") or len(proof_url)<=len(article)+1:
        raise ValueError("Proof URL must be a real anchored section on same article: "+cid)
    listed = row.get("proofs")
    if not isinstance(listed,list) or len(listed)!=1 or (
            listed[0].get("url") != proof_url or listed[0].get("screening")!="cursory_screened"):
        raise ValueError("Proof source does not match verified screening: "+cid)
    if row.get("acquisition",{}).get("status")!="cursory_screened":
        raise ValueError("Screened Wikipedia acquisition metadata missing: "+cid)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",str(pinfo.get("inspection_date",""))):
        raise ValueError("Missing proof screening date: "+cid)
    return pinfo


def make_public(row: dict) -> dict:
    proof = valid_proof_source(row)
    cid = row["candidate_id"]
    area,method = area_of(row)
    notes = row.get("editorial_note") or ""
    if not isinstance(notes,str):
        raise ValueError("Non-text editorial note: "+cid)
    source_section = row.get("source_section") or "Lead"
    cases = row.get("structured_cases") or []
    if not isinstance(cases,list):
        raise ValueError("Malformed source cases: "+cid)
    t = {
        "id": cid,
        "entry_type": "theorem" if re.search(r"\btheorem\b",row["title"],re.I)
                      else "lemma" if re.search(r"\blemma\b",row["title"],re.I)
                      else "corollary" if re.search(r"\bcorollary\b",row["title"],re.I)
                      else "proposition" if re.search(r"\bproposition\b",row["title"],re.I)
                      else "other_result",
        "title": row["title"],
        "area": area,
        "statement": row["statement"],
        "hypotheses": list(row["hypotheses"]),
        "conclusions": list(row["conclusions"]),
        "hypothesis_tags": [],
        "conclusion_tags": [],
        "source_url": row["url"],
        "statement_provenance": {
            "basis": "editorial_restatement_unverified",
            "transcription_status": "not_transcribed",
            "source_text": None,
            "locator": source_section+" (Wikipedia article)",
            "editorial_notes": "Stage A editorial restatement; source formula/excerpt checked for standalone formulation, not mathematically validated. "+notes,
        },
        "proofs": [{
            "url": proof["proof_url"],
            "locator": proof["proof_heading"],
            "screening": "cursory_screened",
            "accessed_on": proof["inspection_date"],
        }],
        "acquisition": {
            "status": "cursory_screened",
            "batch_id": BATCH_ID,
            "collected_on": proof["inspection_date"],
        },
        "mathematical_audit": {"status":"not_audited"},
        "review_status": "cursory_screened_unverified",
        "tag_provenance_defaults": {"hypotheses":"initial_editorial","conclusions":"initial_editorial"},
        "tag_annotations": [],
        "link_hints": [],
        "link_exclusions": [],
        "equivalence_sides": normalized_sides(row.get("equivalence_sides"),cid),
        "structured_cases": cases,
        "source_attribution": "Wikipedia contributors",
        "statement_editorial": "Hypotheses and conclusions prepared by Wikipedia Stage A editorial workers. Proof-section presence screened, not correctness or completeness; verify independently before relying on results.",
        "wikipedia_provenance": {
            "candidate_id": cid,
            "editorial_worker": row.get("stage_a_worker"),
            "input_index": row.get("input_index"),
            "editorial_status": row.get("editorial_status"),
            "proof_presence_basis": proof["reason"],
            "proof_section_index": proof.get("proof_section_index"),
            "source_excerpt_fidelity": row.get("source_fidelity"),
            "area_assignment": method,
            "source_restatement_reviewed_for_mathematical_equivalence": False,
            "mathematical_proof_verified": False,
        },
    }
    return t


def compile_screened(original: Path = FIRST, retry: Path = RETRIED) -> list[dict]:
    a, b = read_jsonl(original), read_jsonl(retry)
    if len(a)!=EXPECTED_FIRST or len(b)!=EXPECTED_RETRIED:
        raise ValueError(f"Expected {EXPECTED_FIRST} original and {EXPECTED_RETRIED} retry successes; found {len(a)}/{len(b)}")
    rows = a+b
    ids = [r.get("candidate_id") for r in rows]
    urls = [r.get("url") for r in rows]
    if len(set(ids))!=EXPECTED or len(set(urls))!=EXPECTED:
        raise ValueError("Duplicate Wikipedia candidate IDs or source articles")
    if len({r["input_index"] for r in rows})!=EXPECTED:
        raise ValueError("Duplicate original Wikipedia intake indices")
    return [make_public(r) for r in sorted(rows,key=lambda r:r["input_index"])]


def save_canonical(path: Path = CANONICAL) -> dict:
    records = compile_screened()
    if len(records)!=EXPECTED:
        raise ValueError("Wikipedia publication candidate count changed")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n"
                            for r in records),encoding="utf-8")
    return {"canonical_path":str(path),"materialized_records":len(records),
            "unverified_proof_presence_only": True,
            "by_area":dict(sorted(Counter(r["area"] for r in records).items()))}


def load_published(path: Path = CANONICAL) -> list[dict]:
    records = read_jsonl(path)
    if len(records)!=EXPECTED:
        raise ValueError("Canonical Wikipedia publication input must contain exactly 920 records")
    ids = [r["id"] for r in records]
    urls = [r["source_url"] for r in records]
    if len(set(ids))!=EXPECTED or len(set(urls))!=EXPECTED:
        raise ValueError("Duplicate published Wikipedia IDs/URLs")
    for r in records:
        if not VALID_ID.fullmatch(r["id"]) or r.get("review_status")!="cursory_screened_unverified":
            raise ValueError("Unsupported Wikipedia publication record identity/status")
        if not r.get("wikipedia_provenance") or r["wikipedia_provenance"].get("candidate_id")!=r["id"]:
            raise ValueError("Missing Wikipedia ID provenance")
        if r.get("mathematical_audit",{}).get("status")!="not_audited":
            raise ValueError("Wikipedia proof may not be labeled mathematically audited")
        if r.get("acquisition",{}).get("status")!="cursory_screened":
            raise ValueError("Missing proof-screen acquisition")
        proof = r.get("proofs")
        if not isinstance(proof,list) or len(proof)!=1 or (
                proof[0].get("screening")!="cursory_screened" or
                not proof[0].get("url","").startswith(r["source_url"]+"#")):
            raise ValueError("Wikipedia proof must link to a screened section")
    return records


def append_wikipedia(existing: list[dict], canonical: Path = CANONICAL) -> dict:
    wiki = load_published(canonical)
    before = len(existing)
    ids = {r["id"] for r in existing}
    urls = {r.get("source_url") for r in existing}
    collisions = [r["id"] for r in wiki if r["id"] in ids or r["source_url"] in urls]
    if collisions:
        raise ValueError("Wikipedia publication collisions with existing catalog: "+", ".join(collisions[:10]))
    existing.extend(wiki)
    return {
        "wikipedia_published":len(wiki),
        "catalog_before_wikipedia":before,
        "catalog_after_wikipedia":len(existing),
        "wikipedia_proof_presence_only":True,
        "wikipedia_mathematical_proofs_validated":False,
        "wikipedia_area_counts":dict(sorted(Counter(r["area"] for r in wiki).items())),
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--materialize",action="store_true",
                        help="One-shot: create frozen data/wikipedia_theorems.jsonl from 706 + 214 screenings")
    parser.add_argument("--validate",action="store_true",
                        help="Read permanent published 920-record corpus and confirm identity/proof provenance")
    args=parser.parse_args()
    if args.materialize:
        print(json.dumps(save_canonical(),indent=2))
    if args.validate:
        from scripts.theorem_schema import validate
        entries=load_published()
        sample={"schema":"maththm.theorems.v1","contract_revision":2,"total":len(entries),"records":entries}
        print(json.dumps(validate(sample),sort_keys=True))
    if not args.materialize and not args.validate:
        parser.error("Select --materialize and/or --validate")


if __name__=="__main__":
    main()
