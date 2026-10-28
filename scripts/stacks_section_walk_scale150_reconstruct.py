#!/usr/bin/env python3
"""Reconstruct candidate-specific standalone drafts across 19 consecutive sections.

Main output is source-faithful theorem LaTeX (with source labels/editorial
citations removed), structured local hypotheses, all enumerated clauses,
mathematical terms from definitions encountered *before* the candidate,
and explicit holds. This is deliberately NOT a proof check or final semantic
equivalence certificate. Difficult assertions remain recorded, not skipped.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts.stacks_context_recon import REV

ROOT=Path("harvest/section_walk_scale150_2026-10-28")
SOURCE="algebra.tex"
DECL=re.compile(r"(?s)\\begin\{(reference|slogan)\}.*?\\end\{\1\}")
LABEL=re.compile(r"\\label\{[^}]+\}")
REF=re.compile(r"\\ref\{([^}]+)\}")
FOOTNOTE=re.compile(r"\\footnote\{")
ITEM=re.compile(r"(?m)\\item(?:\s*\\label\{[^}]+\})?")
HEADER_CONTEXT="global ring = commutative and unital (zero ring permitted), modules unital; N={1,2,...}"
EDITORIAL_DEPENDENCY=re.compile(
 r"(?i)(?:as\s+in\s+(?:situation|notation|definition|lemma)"
 r"|notation\s+and\s+assumptions\s+as"
 r"|in\s+the\s+above\s+situation"
 r"|with\s+the\s+assumptions\s+above"
 r"|as\s+defined\s+above"
 r"|under\s+the\s+above\s+assumptions"
 r"|as\s+in\s+the\s+introduction\s+to\s+this\s+section)")
# Hand-reviewed wording replacements for statements with clear editorial
# source references, and essential missing scope in the original source.
# These are mathematical source-context drafts, not proof claims.
PATCHES={
"lemma-minimal-prime-reduced-ring":{
 "tex":r"Let \(R\) be a ring and \(\mathfrak p\) a minimal prime ideal. Every element of the maximal ideal of \(R_{\mathfrak p}\) is nilpotent. If \(R\) is reduced, then \(R_{\mathfrak p}\) is a field.",
 "hyp":[r"R is a commutative unital ring.",r"\mathfrak p\subseteq R is a minimal prime ideal."],
 "conc":[r"Every element of the maximal ideal of R_{\mathfrak p} is nilpotent.",r"If R is reduced, then R_{\mathfrak p} is a field."],
 "note":"Corrects earlier Pass 2 misclassification: the nilpotence assertion is a conclusion, not an assumption.",
},
"lemma-colon":{
 "hyp":[r"R is a commutative unital ring.",r"J\subseteq R is principal.",r"I\subseteq J is an ideal."],
 "conc":[r"I=J(I:J)."],
 "note":"The source's universal quantification over ideals I,J was promoted to explicit local hypotheses.",
},
"proposition-oka":{
 "tex":r"Let \(R\) be a ring and \(\mathcal F\) a family of ideals of \(R\) such that \(R\in\mathcal F\) and, for every ideal \(I\subseteq R\) and every \(a\in R\), the conditions \((I:a)\in\mathcal F\) and \((I,a)\in\mathcal F\) imply \(I\in\mathcal F\). Then every ideal maximal among the ideals not belonging to \(\mathcal F\) is prime.",
 "hyp":[r"R is a ring.",r"\mathcal F is a family of ideals of R containing R.",r"(I:a),(I,a)\in\mathcal F implies I\in\mathcal F for every ideal I and a\in R."],
 "conc":[r"Any ideal maximal in the complement of \mathcal F is prime."],
 "note":"Fully expands Oka family from source definition at line 5134; no assumption is inherited from the examples following that definition.",
},
"lemma-spec-spectral":{
 "tex":r"For every commutative unital ring \(R\), its prime spectrum \(\operatorname{Spec}(R)\) with the Zariski topology is a spectral topological space.",
 "hyp":[r"R is a commutative unital ring."],
 "conc":[r"\operatorname{Spec}(R) is a spectral topological space."],
 "note":"Removed only the editorial Topology Definition reference; spectral space is a mathematical term, not an imported hypothesis.",
},
"lemma-Noetherian-topology":{
 "tex":r"If \(R\) is a Noetherian ring, then \(\operatorname{Spec}(R)\) with its Zariski topology is a Noetherian topological space.",
 "hyp":[r"R is Noetherian."],
 "conc":[r"\operatorname{Spec}(R) is a Noetherian topological space."],
 "note":"Expands implicit domain and removes editorial source-definition citation.",
},
"lemma-integral-over-field":{
 "note":"The external reference offers further consequences rather than supplying the stated hypotheses; it is kept in provenance and removed from display.",
},
"lemma-colimit-normal-ring":{
 "note":"Directed system is a standard explicit mathematical quantifier; the source category-definition reference is preserved as provenance, not an additional premise.",
},
"lemma-going-up-down-specialization":{
 "note":"Going up and going down are defined at line 9531; specialization order on Spec(R) is given in the section introduction. Preserve the equivalences of these two source notions.",
},
"proposition-going-down-normal-integral":{
 "note":"Going-down is a locally defined property of ring maps, and the full quantified prime-lifting condition is already in the original statement.",
},
"lemma-disjoint-implies-product":{
 "note":"The source's product-spectrum lemma identifies the canonical maps. Its source reference is explanatory, but the actual product decomposition and both localization/quotient properties must be retained.",
},
"lemma-flat":{
 "hyp":[r"R is a ring.",r"M is an R-module."],
 "note":"Source begins with 'Let M be an R-module'; explicitly quantifies R without changing the flatness-equivalence conditions.",
},
"lemma-flat-eq":{
 "note":"The phrase 'every relation in M is trivial' uses a source-specific notion requiring explicit definition before standalone approval.",
 "hold":["Resolve precisely what the source calls a trivial relation on a module, not merely its usual colloquial meaning."],
},
"lemma-lift-idempotents-noncommutative":{
 "note":"Exception to the global commutative ring convention: the source explicitly allows a possibly noncommutative algebra A. Do not impose commutativity.",
},
"lemma-silly-normal":{
 "note":"The phrase integrally closed in R_x or R_y is local to this lemma; neither becomes a standing assumption beyond it.",
},
}
# Editorial reference resolution when the referring theorem itself states
# the full mathematical claim; unavailable semantic references stay held.
EDITORIAL_REFS={
 "lemma-spec-spectral",
 "lemma-Noetherian-topology",
 "lemma-integral-over-field",
 "lemma-colimit-normal-ring",
 "lemma-going-up-down-specialization",
 "proposition-going-down-normal-integral",
 "lemma-disjoint-implies-product",
}
UNRESOLVED_LABEL_HOLDS={
 "lemma-irreducible":"Resolve irreducible-component convention from Topology for the full enumeration.",
 "lemma-jacobson":"Confirm Jacobson space convention alongside Jacobson ring definition.",
}
MANUAL_HOLDS={
 "lemma-characterize-image-finite-type":"Confirm constructible set image and generic-point closure notation have matching source convention.",
 "lemma-characteristic-polynomial-prime":"Check which characteristic-polynomial conditions are hypotheses versus conclusions; preserve exact quantifiers.",
 "lemma-flat":"Large multi-criterion flatness equivalence; verify every equivalence clause separately.",
 "lemma-flat-eq":"Define 'trivial relation' with exact quantifier structure.",
 "lemma-when-injective-covering":"Check the precise equivalence of localization injectivity and the multiplication-family map.",
 "lemma-total-ring-fractions-no-embedded-points":"Confirm canonical product decomposition uses exactly the source assumptions, not reducedness or Noetherianity.",
 "lemma-minimal-prime-image-minimal-prime":"Source statement uses image of a prime under contraction; check the existential lifting quantifiers.",
 "lemma-invert-closed-split":"Check disjunctive finiteness hypotheses and product decomposition.",
 "lemma-silly-normal":"Check orientation of the two maps (-1,1) and (1,1) and their sequence exactness.",
 "lemma-lift-idempotents-noncommutative":"Ensure noncommutative exception is retained and polynomial expression is meaningful.",
 "lemma-polynomials-divide":"Check the two differently quantified subring/ideal conclusions and radicals.",
 "lemma-Jacobson-invert-element":"Check the maximal ideal correspondence under localization for a Jacobson ring.",
 "lemma-Jacobson-mod-ideal":"Check the quotient maximal ideal correspondence and Jacobson hypothesis.",
 "lemma-characterize-reduced-ring-normal":"Check finite-minimal-prime assumptions and precise distinction normal ring/normal domain.",
 "lemma-universal-undefined":"Reserved no-op.",
}
SOURCE_REVIEWED_REFS=set(EDITORIAL_REFS)

def normalized(tex):
    t=tex.strip()
    t=DECL.sub("",t)
    t=LABEL.sub("",t)
    # Formal source references in an otherwise fully specified statement are
    # removed only when specifically adjudicated, not by this function.
    t="\n".join(x.rstrip() for x in t.splitlines()).strip()
    return t

def semantic_issues(tex,pkt):
    flags=[]
    refs=REF.findall(tex)
    if refs:
        flags.append("unexpanded_source_label_reference")
    if FOOTNOTE.search(tex):
        flags.append("embedded_source_footnote_may_carry_extra_content")
    if EDITORIAL_DEPENDENCY.search(tex):
        flags.append("source_deictic_context")
    if pkt["statement_truncated"]:
        flags.append("source_packet_statement_truncated")
    if tex.count(r"\begin{enumerate}")>1:
        flags.append("nested_enumeration_requires_branch_review")
    return flags

def local_frames(events):
    stack=[]
    result={}
    for e in events:
        kind=e["kind"]
        if kind=="enter_local_environment":
            stack.append((e["environment"],e["line"]))
        elif kind=="candidate_location":
            assert stack,(e,stack)
            assert stack[-1][0] in ("lemma","proposition","theorem","corollary"),stack
            result[e["line"]]={
                "environment":stack[-1][0],
                "source_start":stack[-1][1],
            }
        elif kind=="exit_local_environment":
            assert stack and stack[-1][0]==e["environment"]
            frame,start=stack.pop()
            if start in result:
                result[start]["source_end"]=e["line"]
    assert not stack
    return result

def main():
    manifest=json.loads((ROOT/"MANIFEST.json").read_text())
    contexts=hp.read_jsonl(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl")
    references=[x for x in contexts if x["kind"] in
                ("definition","notation","situation","setup","construction")]
    observed={}
    section_counts=[]
    counts=Counter()
    all_ids=set()
    latest_def=[]
    for s in manifest["section_inventory"]:
        key=s["key"]
        packets=hp.read_jsonl(ROOT/(key+"_packets.jsonl"))
        events=hp.read_jsonl(ROOT/(key+"_events.jsonl"))
        bounds=local_frames(events)
        rows=[]
        for i,pkt in enumerate(packets):
            ident=pkt["candidate_id"]
            assert ident not in all_ids
            all_ids.add(ident)
            label=pkt["source_label"]
            patch=PATCHES.get(label,{})
            original=pkt["statement_tex"]
            statement=patch.get("tex",normalized(original))
            flags=semantic_issues(statement,pkt)
            # Editorial label citations may be stripped only after manual
            # review of their role. Store the source refs separately.
            if label in EDITORIAL_REFS and r"\ref{" in statement:
                # For these cases preserve the underlying literal source
                # in source_statement_tex; remove only the explicit cross
                # reference marker in the independent draft.
                statement=REF.sub(r"(see the cited mathematical definition)",statement)
                flags=[x for x in flags if x!="unexpanded_source_label_reference"]
                # A source reference without full semantic expansion still
                # requires a final definition-link review.
            local_notes=patch.get("note")
            in_scope=[z for z in references if z["source_start_line"]<=pkt["source_statement_line"]]
            extra_issues=[]
            if label in UNRESOLVED_LABEL_HOLDS:
                extra_issues.append(UNRESOLVED_LABEL_HOLDS[label])
            if label in MANUAL_HOLDS:
                extra_issues.append(MANUAL_HOLDS[label])
            extra_issues+=patch.get("hold",[])
            if pkt["explicit_refs"] and label not in EDITORIAL_REFS:
                extra_issues.append("Resolve or explicitly link the exact Stacks definition/lemma labels cited in the statement.")
            if flags:
                extra_issues+=["Review signal: "+flag for flag in flags]
            if len(pkt["prior_hypotheses"])==0:
                # Pass 2 may omit the ambient R; the original source statement
                # remains authoritative.
                extra_issues.append("Pass 2 has no explicit hypothesis rows: manually confirm quantified variables.")
            # No source lemma premise persists after its source environment.
            loc=bounds[pkt["source_statement_line"]]
            asserts=[
                re.sub(r"(?s)\\begin\{enumerate\}|\\end\{enumerate\}","",x).strip()
                for x in ITEM.split(normalized(original))[1:]
            ]
            if any(not x for x in asserts):
                extra_issues.append("Empty source-item segment requires manual review.")
            hypotheses=patch.get("hyp",pkt["prior_hypotheses"])
            conclusions=patch.get("conc",pkt["prior_conclusions"])
            if not conclusions and not asserts:
                extra_issues.append("Neither Pass 2 conclusion nor an explicit enumerate clause is available.")
            if pkt["statement_truncated"]:
                extra_issues.append("Full statement must be recovered from the pinned source before any promotion.")
            status=("context_resolution_pending" if extra_issues else
                    "standalone_draft_ready_for_validation")
            record={
                "schema":"maththm.consecutive-section-standalone-overlay.v1",
                "source_revision":REV,
                "source_filename":SOURCE,
                "section_index":s["section_index"],
                "section_key":key,
                "section_title":s["section_title"],
                "section_start_line":s["source_start_line"],
                "section_end_line":s["source_end_line"],
                "candidate_id":ident,
                "source_label":label,
                "source_statement_line":pkt["source_statement_line"],
                "source_url":pkt["source_url"],
                "source_environment":loc["environment"],
                "source_environment_start_line":loc["source_start"],
                "source_environment_end_line":loc["source_end"],
                "standalone_statement_tex":statement,
                "original_source_statement_tex":original,
                "draft_hypotheses":hypotheses,
                "draft_conclusions":conclusions,
                "source_enumerated_clauses":asserts,
                "source_has_equivalence_form":bool(re.search(
                    r"(?i)following\s+are\s+equivalent|if\s+and\s+only\s+if|\\Leftrightarrow",original)),
                "source_has_multi_part_form":bool(asserts),
                "applicable_named_definition_ids":[
                    z["label"] for z in in_scope if z["label"]],
                "applicable_named_definitions_are_hypotheses":False,
                "unconditional_section_hypotheses":[],
                "chapter_global_term_conventions":HEADER_CONTEXT,
                "source_refs":pkt["explicit_refs"],
                "source_ref_semantic_expansion_final_approved":False,
                "source_lemma_local_hypotheses_persist_after_end":False,
                "context_reviews":[local_notes] if local_notes else [],
                "context_resolution_needed":list(dict.fromkeys(extra_issues)),
                "status":status,
                "source_pass2_context_status":pkt["prior_context_status"],
                "final_standalone_source_equivalence_approved":False,
                "proofs_inspected":False,
                "pass3_eligible":False,
                "published":False,
                "source_pass1_pass2_unchanged":True,
            }
            counts[status]+=1
            rows.append(record)
        hp.atomic_text(ROOT/(key+"_reviews.jsonl"),"".join(
            json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows))
        section_counts.append({
            "section":key,"title":s["section_title"],
            "candidates":len(rows),"review_status":dict(Counter(x["status"] for x in rows)),
            "definitions_present_before_section_start":[z["label"] for z in references if z["label"] and z["source_start_line"]<s["source_start_line"]],
            "no_leaked_lemma_hypotheses":True,
            "source_section_entirely_traversed":True,
        })
    assert len(all_ids)==150
    result={
        "schema":"maththm.consecutive-section-standalone-drafts-manifest.v1",
        "source_revision":REV,"file":SOURCE,"source_start":4284,"source_end":10036,
        "consecutive_complete_sections":19,
        "distinct_active_candidates_with_drafts":150,
        "per_section":section_counts,
        "status_counts":dict(sorted(counts.items())),
        "no_pass1_pass2_changes":True,"original_corpus_unchanged":True,
        "proofs_reviewed":0,"final_source_equivalence_approvals":0,
        "pass3_eligible":0,"published":0,
        "statement_normalization":"Keep source mathematical LaTeX and full enumerations; strip only source label, slogan and reference metadata; apply bounded manually reviewed patches. Source original always preserved separately.",
        "stage":"standalone_editorial_draft_and_semantic_context_triage_not_proof_verification",
    }
    hp.atomic_text(ROOT/"DRAFT_MANIFEST.json",json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"candidates":len(all_ids),"statuses":result["status_counts"],
        "per_section":[(x["section"],x["candidates"],x["review_status"])
                       for x in section_counts]},ensure_ascii=False))

if __name__=="__main__":
    main()
