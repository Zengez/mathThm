#!/usr/bin/env python3
"""Draft 300 source-ordered mathematical statements in consecutive full sections.

This stage DOES reconstruct source-grounded standalone editorial statements,
explicit local hypotheses, conclusions/equivalences and defined terminology.
Complex or unclear logical scopes are kept on named holds. It does NOT check
proof correctness, establish final source-equivalence or publish theorems.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts.stacks_context_recon import REV
from scripts.stacks_section_walk_scale150_reconstruct import (
    normalized,split_source_enumeration,local_frames
)

ROOT=Path("harvest/section_walk_scale300_2026-10-28")
READY="standalone_draft_ready_for_validation"
HOLD="context_resolution_pending"
REF=re.compile(r"\\ref\{([^}]+)\}")
FOOTNOTE=re.compile(r"\\footnote\{")
DEICTIC=re.compile(r"(?i)\b(?:as in (?:the|our|this|that) (?:situation|notation|setup)"
                   r"|notation and assumptions as"
                   r"|as (?:in|mentioned|defined|stated) above"
                   r"|under (?:these|the above|the preceding) (?:assumptions|conditions)"
                   r"|with (?:the|these) assumptions (?:above|as before)"
                   r"|in the setting of (?:the|this|that)"
                   r"|the functor above|in the preceding|as in the previous)\b")
EXISTENTIAL=re.compile(r"(?is)\b(?:there exist|there exists|we can find|one can find)\b")
INTRO_CONCEPT=re.compile(r"(?is)^\s*(?:let|suppose|assume|given|if|for any|for every|consider)\b")

SOURCE_LABEL_PATCHES={
 "lemma-inverse-systems-affine":{
   "term_explanations":["The name Coh(X,I) means coherent inverse systems annihilated stagewise by I^n with compatible transition quotients, as defined in the section opening."],
   "hypotheses":["X=Spec(A) for a Noetherian ring A.","I⊂A is an ideal.","I is the corresponding quasi-coherent ideal sheaf on X."],
   "conclusions":["The category Coh(X,I) is equivalent to finite modules over the I-adic completion of A."],
   "review_holds":[],
 },
 "lemma-inverse-systems-abelian":{
   "term_explanations":["Coh(X,I) is the inverse-system category defined in the Coherent formal modules section opening."],
   "hypotheses":["X is a Noetherian scheme.","I is a quasi-coherent ideal sheaf on X."],
 },
 "lemma-exact":{
   "review_holds":["Source statement only refers to the completion functor by equation label; its full domain, codomain and action must be expanded."],
 },
 "lemma-norm-invertible":{
   "term_explanations":["A norm of degree d is the source-defined multiplicative sheaf map π_*O_X→O_Y with power compatibility and the specified vanishing property."],
 },
 "lemma-norm-ample":{
   "term_explanations":["The phrase norm of degree d uses the conditions spelled out in the Norms section opening; they are not assumed for unrelated lemmas."],
 },
 "lemma-norm-quasi-affine":{
   "term_explanations":["The phrase norm of degree d uses the source's full definition and its vanishing condition."],
 },
 "lemma-finite-locally-free-has-norm":{
   "term_explanations":["The claimed existence of a norm of degree d is a conclusion; it is NOT a hypothesis."],
 },
 "lemma-norm-in-normal-case":{
   "term_explanations":["The existence of a norm is asserted, not assumed; the degree is the generic field extension degree."],
 },
 "lemma-finite-trivialize-invertible-upstairs":{
   "term_explanations":["No norm exists in the hypotheses; this first lemma is independent of later norm assumptions."],
 },
 "lemma-relative-assassin-affine-open":{
   "term_explanations":["Relative assassin is the union over scheme fibres of their associated points as defined in the preceding definition."],
 },
 "lemma-regular-meromorphic-ideal-denominators":{
   "term_explanations":["The source constructs the denominator ideal in the lemma; later named definitions reference this construction."],
 },
}
STRONG_AMBIGUITY=re.compile(
  r"(?is)(?:we may assume|above assumptions|as before|situation\s+\\ref\{"
  r"|assumptions and notation|let \S+ be (?:as above|as in)|following diagram "
  r"|in the above setup|as in the proof of)")
EDITORIAL_REF=r"(?i)(?:see|cf\.|compare)\s+[^.\n]{0,110}?\\ref\{"

def clean_source(tex):
    # Preserve all mathematical quantifiers, multistep clauses and displayed
    # formulae. Strip only formal theorem label and nonmathematical slogans/
    # bibliographic reference blocks, retaining the original verbatim below.
    return normalized(tex)

def source_logical_shape(cleaned,orig,prior_hyp,prior_conc):
    """Split without interpreting proof or spreading a conditional across items."""
    parsed=split_source_enumeration(orig)
    holds=[]
    aux=[]
    items=[]
    if not parsed:
        hyp=list(prior_hyp)
        conc=list(prior_conc)
        shape="plain_source_statement"
    else:
        items=list(parsed["items"])
        intro=parsed["intro"].strip()
        tail=parsed["tail"].strip()
        count_open=orig.count(r"\begin{enumerate}")
        count_close=orig.count(r"\end{enumerate}")
        if count_open!=count_close or count_open!=1:
            holds.append("Nested/multiple enumerations require source-specific quantifier and condition grouping; entire original statement is preserved.")
            shape="nested_or_multi_enumeration_needs_review"
            hyp=[intro] if intro else list(prior_hyp)
            conc=[cleaned]
        elif parsed["shape"]=="equivalent_conditions":
            shape="equivalent_conditions"
            hyp=[intro] if intro else []
            conc=items
            if tail: aux=[tail]
        elif re.search(r"(?i)\b(?:assume|suppose)\s+(?:that\s+)?there\s+exist",intro):
            # Hypotheses for the theorem consist of one quantified witness
            # satisfying *all* listed conditions. Theorem conclusion
            # follows "Then" after the enumeration, not each item.
            shape="shared_existential_witness_hypotheses"
            split=re.split(r"(?i)\bthen\b",tail,maxsplit=1)
            grouped=intro+" "+r"\begin{enumerate}"+" "+" ".join(
                r"\item "+x for x in items)+" "+r"\end{enumerate}"
            if len(split)==2:
                hyp=[grouped+" "+split[0].strip()]
                conc=[split[1].strip()]
            else:
                hyp=[grouped]
                conc=[tail] if tail else [cleaned]
                holds.append("Shared existential premise list has no unambiguous following conclusion.")
            holds.append("Verify the existential premise quantifier and logical scope before mathematical source-equivalence approval.")
        elif re.search(r"(?i)\b(?:assume|suppose|given)\s*(?:that\s*)?$",intro):
            # Source 'Assume [items] Then conclusion' means all listed
            # items are assumptions; NONE becomes a free conclusion.
            shape="listed_premises_then_conclusion"
            hyp=[intro]+items
            split=re.split(r"(?i)\bthen\b",tail,maxsplit=1)
            if len(split)==2:
                if split[0].strip():hyp.append(split[0].strip())
                conc=[split[1].strip()]
            else:
                conc=[tail] if tail else [cleaned]
                if not tail or re.match(r"(?i)\s*(?:let|set|write|denote)\b",tail):
                    holds.append("The text after enumerated premises contains definitions or no explicit consequent; review quantifier split.")
        elif EXISTENTIAL.search(intro):
            # One shared witness with multiple properties; cannot split
            # the listed properties into unrelated existential conclusions.
            shape="shared_existential_witness_properties"
            hyp=list(prior_hyp[:1]) if prior_hyp else [intro]
            conc=[cleaned]
            holds.append("Confirm the joint quantifier binding the listed properties to the same existential witness.")
        elif re.search(r"(?i)\b(?:if|provided that|under one of|under any of)\s*(?:the following|either|one of)\b",intro):
            shape="alternative_conditional_cases"
            hyp=[intro]
            conc=[cleaned]
            holds.append("List items are alternative theorem hypotheses, not independent conclusions; verify their disjunction and any final consequence.")
        elif parsed["shape"]=="listed_premises_then_conclusion":
            shape="listed_premises_then_conclusion"
            hyp=([intro] if intro else [])+items
            conc=[tail] if tail else [cleaned]
            if not tail:holds.append("Listed premises detected but no explicit following conclusion was separated.")
        else:
            # Entire source items, including each item's own if/suppose
            # guard, are conclusions. A prior Pass 2 split is not used to
            # infer unconditional hypotheses from these clauses.
            shape="listed_assertions_with_individual_guards"
            hyp=[intro] if intro else list(prior_hyp[:1])
            conc=items
            if tail:aux=[tail]
            if re.search(r"(?i)\bif\s*$",intro):
                holds.append("List may encode conditional alternatives whose parent antecedent remains in the source introductory phrase.")
    if not hyp:
        # Theorems such as 'Every X has Y' have an implicit universally
        # quantified X, not an absent or inherited extra premise.
        hyp=["Universally quantified objects and hypotheses as explicitly stated in the displayed source statement."]
    if not conc:
        conc=[cleaned]
        holds.append("No independently identified conclusion; source statement was retained without guessed quantifier split.")
    return shape,hyp,conc,items,aux,holds

def main():
    manifest=json.loads((ROOT/"MANIFEST.json").read_text(encoding="utf-8"))
    scope=json.loads((ROOT/"SCOPES_REVIEWED.json").read_text(encoding="utf-8"))
    source_defs=[x for x in hp.read_jsonl(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl")
                 if x["kind"] in ("definition","notation","situation","setup","construction")]
    assert manifest["active_candidate_count"]==300
    assert manifest["sections"]==54
    assert [x["source_filename"] for x in manifest["section_inventory"]][:17]==["coherent.tex"]*17
    assert [x["source_filename"] for x in manifest["section_inventory"]][17:]==["divisors.tex"]*37
    assert len(scope["section_context_leads"])==8
    by_section={x["section"]:x for x in scope["section_context_leads"]}
    allids=set()
    statuses=Counter()
    shape_counts=Counter()
    hold_types=Counter()
    reports=[]
    review_ids=[]
    previous_chapter=None
    for sec in manifest["section_inventory"]:
        key=sec["key"]
        filename=sec["source_filename"]
        chapter_transition=previous_chapter is not None and filename!=previous_chapter
        if chapter_transition:
            assert previous_chapter=="coherent.tex" and filename=="divisors.tex"
        previous_chapter=filename
        packets=hp.read_jsonl(ROOT/(key+"_packets.jsonl"))
        events=hp.read_jsonl(ROOT/(key+"_events.jsonl"))
        frames=local_frames(events)
        rows=[]
        for p in packets:
            ident=p["candidate_id"]
            assert ident not in allids
            allids.add(ident)
            label=p["source_label"]
            old=p["statement_tex"]
            display=clean_source(old)
            patch=SOURCE_LABEL_PATCHES.get(label,{})
            shape,hyp,conc,items,aux,holds=source_logical_shape(
                display,old,p["prior_hypotheses"],p["prior_conclusions"])
            if patch.get("hypotheses"):
                hyp=patch["hypotheses"]
            if patch.get("conclusions"):
                conc=patch["conclusions"]
            holds.extend(patch.get("review_holds",[]))
            local=frames[p["source_statement_line"]]
            assert local["source_end"]>local["source_start"]
            source_refs=[r["reference"] for r in p["explicit_refs"]]
            inline_refs=list(dict.fromkeys(REF.findall(display)))
            if inline_refs:
                holds.append("Source uses named references not yet semantically expanded in the standalone displayed statement: "+
                             ", ".join(inline_refs[:12]))
            if p["statement_truncated"]:
                holds.append("Source statement truncated in staging packet: recover full source before standalone approval.")
            if FOOTNOTE.search(display):
                holds.append("Source footnote may contain a mathematical caveat: review before removing it.")
            if DEICTIC.search(display) or STRONG_AMBIGUITY.search(display):
                holds.append("Source uses contextual or deictic wording; identify exact antecedents and their mathematical scope.")
            if display.count(r"\begin{enumerate}")>1 and not any(
               "Nested/multiple enumerations" in x for x in holds):
                holds.append("Nested source enumeration: preserve full quantifier binding.")
            # A theorem referring to a named 'as above' setting cannot
            # inherit every paragraph or earlier theorem blindly.
            if not p["prior_hypotheses"] and shape=="plain_source_statement":
                holds.append("Pass 2 did not identify hypotheses; check actual universal quantifiers and section context.")
            if not p["prior_conclusions"] and shape=="plain_source_statement":
                holds.append("Pass 2 did not identify conclusion; source statement retained pending semantic extraction.")
            if re.search(r"(?i)\b(?:in the situation|notation as in|assumptions as in)\b",display):
                holds.append("Theorem imports a named external situation; expand before final standalone approval.")
            # Some terms arise in prose rather than a formal Definition env.
            in_scope_defs=[
                q["label"] for q in source_defs
                if q["label"] and (
                    (q["source_filename"]==filename and
                     q["source_end_line"]<p["source_statement_line"])
                    or
                    (filename=="divisors.tex" and q["source_filename"]=="coherent.tex"))
            ]
            prose_concepts=[]
            if filename=="coherent.tex" and (
                sec["section_index"]>=12):
                prose_concepts.append("coherent:s12:Coh(X,I)")
            if filename=="divisors.tex" and sec["section_index"]>=35:
                prose_concepts.append("divisors:s35:norm-degree-d")
            is_under_ambient=False
            # Coherent s01: a stated mathematical fact is a reusable
            # source convention, not a new theorem assumption.
            # Coherent s12: Coh(X,I) is a term that expects X Noetherian,
            # I an ideal sheaf; candidate must quantify these on its own.
            if filename=="coherent.tex" and sec["section_index"]==12 and "Coh" in display:
                if "Noetherian" not in display and "Coh" in display:
                    holds.append("Coherent formal module category needs its Noetherian X and ideal-sheaf parameters from the section opening.")
            term_explanations=patch.get("term_explanations",[])
            all_holds=list(dict.fromkeys(holds))
            status=HOLD if all_holds else READY
            # This is a preparatory editorial classification; even READY
            # has no final semantic source equivalence or proof approval.
            r={
                "schema":"maththm.scale300.standalone-context-draft.v1",
                "candidate_id":ident,
                "source_revision":REV,
                "source_filename":filename,
                "source_statement_line":p["source_statement_line"],
                "source_label":label,
                "source_url":p["source_url"],
                "chapter_order":sec["chapter_order"],
                "section_key":key,
                "section_title":sec["section_title"],
                "section_start_line":sec["section_start_line"],
                "section_end_line":sec["section_end_line"],
                "section_index":sec["section_index"],
                "source_formal_environment":local["environment"],
                "source_formal_environment_start_line":local["source_start"],
                "source_formal_environment_end_line":local["source_end"],
                "original_source_statement_tex":old,
                "standalone_statement_tex":display,
                "draft_hypotheses":hyp,
                "draft_conclusions":conc,
                "additional_conclusions":aux,
                "source_logical_form":shape,
                "source_enumerated_clauses":items,
                "applicable_prior_named_definition_ids":in_scope_defs,
                "available_prose_context_ids":prose_concepts,
                "named_definitions_are_not_ambient_assumptions":True,
                "section_ambient_hypotheses_auto_inherited":[],
                "local_lemma_hypotheses_expire_at_end":True,
                "source_specific_term_explanations":term_explanations,
                "inherited_context_review_decision":(
                    "chapter boundary: chapter-local standing assumptions reset"
                    if chapter_transition else
                    "only identified source definitions and section-specific meanings available"),
                "source_named_reference_labels":source_refs,
                "source_inline_reference_labels":inline_refs,
                "context_resolution_needed":all_holds,
                "context_review_status":status,
                "original_pass2_hypotheses_proposed":p["prior_hypotheses"],
                "original_pass2_conclusions_proposed":p["prior_conclusions"],
                "original_pass2_context_status":p["prior_context_status"],
                "final_mathematical_source_equivalence_approved":False,
                "source_proof_screened":False,
                "pass3_eligible":False,
                "published":False,
                "original_pass1_pass2_unchanged":True,
            }
            rows.append(r)
            statuses[status]+=1
            shape_counts[shape]+=1
            review_ids.append(ident)
            for hold in all_holds:hold_types[hold.split(":")[0][:110]]+=1
        hp.atomic_text(ROOT/(key+"_reviews.jsonl"),
            "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows))
        reports.append({
            "key":key,"chapter":filename,
            "section_title":sec["section_title"],
            "active_candidates":len(rows),
            "draft_ready":sum(x["context_review_status"]==READY for x in rows),
            "context_held":sum(x["context_review_status"]==HOLD for x in rows),
            "source_environment_frames_complete":True,
            "section_complete":True,
        })
    assert len(allids)==len(review_ids)==300
    assert sum(x["active_candidates"] for x in reports)==300
    summary={
        "schema":"maththm.scale300.standalone-draft-manifest.v1",
        "source_revision":REV,
        "source_chapters":manifest["source_chapters"],
        "consecutive_complete_source_sections":54,
        "distinct_active_candidates_with_drafts":300,
        "status_counts":dict(sorted(statuses.items())),
        "logical_forms":dict(sorted(shape_counts.items())),
        "context_hold_categories":dict(hold_types.most_common(25)),
        "section_results":reports,
        "final_mathematical_source_equivalence_approvals":0,
        "proofs_screened":0,
        "pass3_eligible":0,
        "published":0,
        "original_pass1_pass2_unchanged":True,
        "stage":"source_grounded_mathematical_context_drafts_with_conservative_holds_not_proof_verification",
        "quality_note":"A draft-ready status means no mechanically identified source-context blocker, NOT a mathematical verification. Complex references and context-dependent statements have explicit holds. Original source statement is always retained."
    }
    hp.atomic_text(ROOT/"DRAFT_MANIFEST.json",
                   json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"candidate_count":300,
          "status_counts":summary["status_counts"],
          "logical_forms":summary["logical_forms"],
          "held_by_section":[(x["key"],x["context_held"]) for x in reports if x["context_held"]]},
          ensure_ascii=False))
if __name__=="__main__":main()
