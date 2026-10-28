#!/usr/bin/env python3
"""Build compact, source-anchored convention atlas from bounded editorial reviews.

No recursive reference research; no automatic theorem hypothesis changes.
The returned lookup is a *lead list*, not a claim of theorem applicability.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.stacks_context_recon import REV

BASE=Path("harvest")
PACKETS=BASE/"stacks_context_sections_2026-10-28_packets.jsonl"
REVIEWS=BASE/"stacks_context_sections_2026-10-28_reviewed_annotations.jsonl"
RECON=BASE/"stacks_context_recon_2026-10-28_files.jsonl"
ATLAS=BASE/"stacks_standing_context_atlas_2026-10-28.jsonl"
LOOKUP=BASE/"stacks_standing_context_lookup_2026-10-28.json"
MANIFEST=BASE/"stacks_standing_context_manifest_2026-10-28.json"
SUMMARY=BASE/"stacks_standing_context_summary_2026-10-28.md"

VALID_SCOPES={
    "global","chapter_heading","chapter_explicit",
    "chapter_claim_with_late_section","from_here_only","not_applicable",
}
VALID_ACTIONS={
    "never_auto_add","disambiguate_if_relevant","expand_named_terms_if_needed",
    "add_quantifier_when_needed","expand_when_cited_or_in_scope","inherit_lookup_only",
}
def build():
    packets=p.load_rows(PACKETS,"context_id")
    reviews=p.load_rows(REVIEWS,"context_id")
    assert len(packets)==len(reviews)==55
    assert set(packets)==set(reviews)
    recon=p.load_rows(RECON,"filename")
    assert len(recon)>=115
    atlas={}
    inherited_edges=[]
    for ident,source in sorted(packets.items()):
        r=reviews[ident]
        assert source["source_revision"]==r["source_revision"]==REV
        assert source["source_url"]==r["source_url"]
        assert r["scope"] in VALID_SCOPES
        assert r["candidate_action"] in VALID_ACTIONS
        assert isinstance(r["review_summary"],str) and len(r["review_summary"])>20
        assert all(isinstance(x,str) and x for x in r["guards"])
        for target in r["inherit_from"]:
            assert target in packets and target!=ident, (ident,target)
            inherited_edges.append({"from_context_id":ident,"to_context_id":target,
                                    "edge_type":"explicit_source_convention_inheritance_or_reuse",
                                    "followed_for_math":False})
        atlas[ident]={
            "context_id":ident,
            "chapter":source["filename"][:-4],
            "filename":source["filename"],
            "chapter_number":source["chapter_number"],
            "chapter_title":source["chapter_title"],
            "book_part":source["book_part"],
            "section_label":source["section_label"],
            "section_title":source["section_title"],
            "section_first_line":source["first_line"],
            "section_last_line":source["last_line"],
            "source_url":source["source_url"],
            "source_revision":REV,
            "context_kind":r["context_kind"],
            "scope_assessment":r["scope"],
            "review_summary":r["review_summary"],
            "candidate_action":r["candidate_action"],
            "inherit_context_ids":r["inherit_from"],
            "guards":r["guards"],
            "context_family":r["context_family"],
            "raw_source_references":source["references"],
            "source_packet_file":str(PACKETS),
            "source_packet_context_id":ident,
            "excerpt_truncated":source["excerpt_truncated"],
            "proofs_omitted":source["proof_blocks_omitted"],
            "review_status":"bounded_source_section_read_not_proven_applicable_to_each_theorem",
            "hypotheses_already_modified":False,
        }
    for edge in inherited_edges:
        a=atlas[edge["from_context_id"]]
        b=atlas[edge["to_context_id"]]
        assert a["context_id"]!=b["context_id"]
    by_chapter=defaultdict(list)
    for x in atlas.values():
        by_chapter[x["chapter"]].append(x["context_id"])
    index={}
    for filename,meta in sorted(recon.items()):
        if filename.removesuffix(".tex") not in {x["chapter"] for x in atlas.values()} and not meta.get("in_main_book_order"):
            continue
        stem=filename.removesuffix(".tex")
        if not meta.get("in_main_book_order"):
            continue
        index[stem]={
            "filename":filename,
            "chapter_number":meta["chapter_number"],
            "title":meta["title"],
            "book_part":meta["book_part"],
            "direct_context_ids":sorted(by_chapter[stem],key=lambda i:atlas[i]["section_first_line"]),
            "has_reviewed_designated_context_section":bool(by_chapter[stem]),
            "global_context_ids":sorted(by_chapter["conventions"],key=lambda i:atlas[i]["section_first_line"]),
            "context_uncovered_by_this_pass":"chapter/section introductions and theorem-neighborhood references",
        }
    assert len(index)==115, len(index)
    assert all(x["chapter"] in index for x in atlas.values())
    ordered=sorted(atlas.values(),key=lambda x:(x["chapter_number"],x["section_first_line"],x["context_id"]))
    p.atomic_text(ATLAS,"".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in ordered))
    families=defaultdict(list)
    for row in ordered:
        if row["context_family"]:
            families[row["context_family"]].append(row["context_id"])
    lookup={
        "schema":"maththm.stacks-standing-context-lookup.v1",
        "source_revision":REV,
        "atlas_file":str(ATLAS),
        "source_packet_file":str(PACKETS),
        "chapter_contexts":index,
        "repeated_context_families":dict(sorted(families.items())),
        "explicit_inheritance_edges":inherited_edges,
        "no_inherited_assumptions_auto_propagated":True,
        "no_auto_hypothesis_expansion":True,
    }
    p.atomic_text(LOOKUP,json.dumps(lookup,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    count_scope=Counter(x["scope_assessment"] for x in ordered)
    manifest={
        "schema":"maththm.stacks-standing-context-review.v1",
        "source_revision":REV,
        "designated_sections_reviewed":len(ordered),
        "unique_chapters_reviewed":len({x["chapter"] for x in ordered}),
        "maintained_chapters_indexed":len(index),
        "explicit_inheritance_edges":len(inherited_edges),
        "repeated_context_families":{k:len(v) for k,v in sorted(families.items())},
        "review_scope_counts":dict(sorted(count_scope.items())),
        "bounded_source_section_review_completed":True,
        "chapter_and_section_intro_extraction_done":False,
        "semantic_theorem_context_expansion_done":False,
        "candidate_records_modified":False,
        "proofs_read_or_verified":False,
        "provisional_mergers_rechecked":False,
        "published_corpus_unchanged":True,
        "limitations":[
            "Chapter-level conventions may be overridden later in the chapter or for individual theorems.",
            "A convention heading alone does not certify the scope of every declaration.",
            "The named Situation in Chow chapters requires per-theorem citation or scope review.",
            "Explicit inheritance references are only mapped one hop; no recursive inference.",
            "A referenced theorem is never silently converted into a standing hypothesis.",
            "Site-size/set-theoretic conventions often belong in metadata, not a theorem's visible hypotheses.",
            "See pinned source and GNU FDL attribution before redistributing extracted excerpts."
        ],
    }
    p.atomic_text(MANIFEST,json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    md=[
        "# Stacks standing-context atlas — first bounded review",
        "",
        "**Pinned Stacks source:** " + REV,
        "",
        "**Completed:** " + str(len(ordered)) + " designated convention/notation/setup sections in "
           + str(manifest["unique_chapters_reviewed"]) + " chapters read at source-excerpt level. "
           "Indexed all 115 main-book chapters for later lookup. No candidate statements or hypotheses changed.",
        "",
        "This index is a **lead resource**, not a transitive theorem-context engine. "
        "Every record preserves a source locator, annotated likely scope, applicability caveats, "
        "and named source-context inheritance if explicitly written.",
        "",
        "## High-value context families and warnings",
        "",
        "- **Global:** ZF with choice, small-category default, commutative unital rings (zero ring allowed), "
        "unitary modules, positive integers beginning at 1.",
        "- **Algebraic spaces:** Many chapters repeat big-fppf-site and fiber-product conventions; "
        "preserved as chapter-specific sources grouped under a shared family.",
        "- **Stacks:** Properties of Stacks defines identification of spaces/schemes with associated stacks "
        "and 2-categorical conventions, then several later chapters explicitly inherit them.",
        "- **Explicit scope changes:** Formal Spaces starts new standing conventions at its Conventions "
        "section (line 620); never retroactively apply them to earlier statements.",
        "- **Named assumptions:** Chow Homology and Chow Groups of Spaces have distinct named setup "
        "situations with base/dimension-function assumptions that matter for standalone statements.",
        "- **Caveats and counterexamples:** Etale Morphisms explicitly says Noetherian hypotheses "
        "will be repeated, so the chapter's frequent Noetherian setting is NOT itself a standing hypothesis; "
        "Moduli chapters override the default base to Spec(Z); one Intersection Theory source uses bold C "
        "for an algebraically closed field of arbitrary characteristic, not necessarily complex numbers.",
        "- **Noncontext:** The Desirables chapter's Conventions section is an editorial wishlist, "
        "not a standing source convention.",
        "",
        "## Files",
        "",
        "- [Reviewed context atlas](stacks_standing_context_atlas_2026-10-28.jsonl): one annotated record per designated section.",
        "- [Chapter lookup and explicit direct inheritance links](stacks_standing_context_lookup_2026-10-28.json): "
          "all 115 chapter entries, global context ids, repeated families and direct edges.",
        "- [Original bounded source review excerpts](stacks_context_sections_2026-10-28_packets.jsonl): "
          "do not treat excerpt text as automatically applicable mathematical assumptions.",
        "- [Manifest and scope counts](stacks_standing_context_manifest_2026-10-28.json).",
        "",
        "## Candidate-review lookup rule",
        "",
        "1. Look up the candidate's source chapter; inspect global and chapter-local entries, applying scope guards.",
        "2. If a direct inherited convention is listed, open its target record. Do not recursively follow unrelated citations.",
        "3. Retrieve the theorem's own section introduction and explicit local references **on demand**.",
        "4. Translate only necessary and applicable source assumptions into fully standalone hypotheses; "
          "keep unrelated earlier results as proof dependencies, not hypotheses.",
        "5. Only after standalone review should duplicate merges be confirmed and proofs screened.",
        "",
        "**Not started:** exhaustive introduction/paragraph indexing, full standalone candidate expansion, "
        "Pass 3 proof checking. Source attribution: The Stacks Project Authors, "
        "The Stacks Project, GNU Free Documentation License; exact text is pinned to source links.",
        "",
    ]
    p.atomic_text(SUMMARY,"\n".join(md))
    print(json.dumps({k:manifest[k] for k in (
        "designated_sections_reviewed","unique_chapters_reviewed","maintained_chapters_indexed",
        "explicit_inheritance_edges","repeated_context_families","review_scope_counts")},sort_keys=True))
    return manifest

def get_candidate_context_leads(filename, *, statement_line=None):
    """Return bounded context leads, *not* validated/expanded assumptions."""
    if statement_line is not None and (not isinstance(statement_line,int) or statement_line<1):
        raise ValueError("statement_line must be a positive integer")
    chapter=Path(filename).stem
    lookup=json.loads(LOOKUP.read_text(encoding="utf-8"))
    byid=p.load_rows(ATLAS,"context_id")
    record=lookup["chapter_contexts"].get(chapter)
    if not record:
        return {"chapter":chapter,"context_leads":[],"unindexed_chapter":True}
    leads=[]
    for ident in list(record["global_context_ids"])+list(record["direct_context_ids"]):
        r=byid[ident]
        if r["scope_assessment"]=="not_applicable" or r["context_kind"]=="source_note":
            continue
        if r["scope_assessment"]=="from_here_only" and statement_line is not None:
            if statement_line < r["section_first_line"]:
                continue
        status=("manual_scope_confirmation_required"
                if r["scope_assessment"] in ("chapter_heading","chapter_claim_with_late_section")
                else "candidate_applicability_not_yet_reviewed")
        leads.append({
            "context_id":ident,
            "review_summary":r["review_summary"],
            "source_url":r["source_url"],
            "scope_assessment":r["scope_assessment"],
            "guards":r["guards"],
            "inherit_context_ids":r["inherit_context_ids"],
            "candidate_status":status,
        })
    return {"chapter":chapter,"context_leads":leads,"unindexed_chapter":False}

if __name__=="__main__":
    build()
