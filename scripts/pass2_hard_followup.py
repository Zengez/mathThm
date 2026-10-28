#!/usr/bin/env python3
"""Second bounded follow-up on unresolved Pass 2 mathematical statements.

Targets only the 194 candidates deferred by pass2_hard_structures.py;
handles explicit equivalences + additional consequences, simple universal
assertions and alternate sufficient-condition cases. No proof is read.
Existing resolved statements are left intact except per-case search repairs.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from collections import Counter

try:
    from . import harvest_pipeline as pipe
    from .pass2_hard_structures import (
        EQUIV, AMBIGUOUS, CROSS_CONTEXT, INTRO, enum_blocks, list_items,
        split_equivalence, predicate_assertion, logical_item,
    )
except ImportError:
    import harvest_pipeline as pipe
    from pass2_hard_structures import (
        EQUIV, AMBIGUOUS, CROSS_CONTEXT, INTRO, enum_blocks, list_items,
        split_equivalence, predicate_assertion, logical_item,
    )

TAIL_START = re.compile(r"^(?:Moreover|In\s+particular|In\s+other\s+words|"
                        r"Furthermore|Also|Consequently|In\s+addition)\b",re.I)
ALTERNATE = re.compile(
    r"\bIn\s+each\s+of\s+the\s+following\s+cases\b"
    r"|\b(?:provided|if)\s+(?:in\s+addition\s+to\s+"
    r"(?:the\s+)?conditions\s+above\s+)?"
    r"(?:at\s+least\s+)?one\s+of\s+the\s+following\s+"
    r"(?:conditions\s+)?(?:holds|is\s+satisfied)\b",re.I)
PRE_TITLE = re.compile(
    r"^(?:Elementary\s+properties|Permanence\s+properties|"
    r"Sections\s+of\s+[^\n]+|Exactness\s+and\s+[^\n]+)\.\s*",re.I)


def outline(s):
    blocks=enum_blocks(s)
    if blocks is None or len(blocks)>2:
        return None
    return blocks


def repack(base, *, hypothesis, conclusion, form, cases=None, eq=None, why):
    h=[x for x in hypothesis if x and x.strip()]
    c=[x for x in conclusion if x and x.strip()]
    if not h or not c:
        return None
    return {**base,"hypotheses":h,"conclusions":c,"logical_form":form,
            "equivalence_sides":eq or [],
            "structured_cases":cases or [],
            "split_confidence":"bounded_semantic_structure_unverified",
            "context_status":"resolved","context_note":"",
            "review_method":"editorial",
            "statement_editorial_notes":why+" Source statement preserved; proof not consulted.",
           }


def interpret_followup(old):
    text=old["statement"].strip()
    if not text or AMBIGUOUS.search(text):
        return None,"Source may be unfinished or text is empty"
    if CROSS_CONTEXT.search(text):
        return None,"Inherited setting requires external statement context"
    blocks=outline(text)
    if blocks is None:
        return None,"Malformed or too many source enumerations"

    # Nested premises followed by an explicit equivalence list:
    # Let X; Assume [P,Q]; For T, the following are equivalent: [A,B].
    if len(blocks)==2:
        a1,b1=blocks[0];a2,b2=blocks[1]
        pre=text[:a1].strip()
        mid=text[b1:a2].strip()
        tail=text[b2:].strip()
        if (INTRO.match(pre) and re.search(r"\b(?:assume|suppose|has\s+the\s+following|"
                 r"following\s+properties)\s*:?\s*$",pre,re.I)
                and EQUIV.search(mid) and not tail):
            assumption_items=list_items(text,blocks[0])
            equivalent_items=list_items(text,blocks[1])
            if assumption_items and equivalent_items and len(equivalent_items)>=2:
                ctx=pre+"\n"+text[a1:b1]+"\n"+mid[:EQUIV.search(mid).start()]
                return repack(old,hypothesis=[ctx]+equivalent_items,
                       conclusion=equivalent_items,form="equivalence_with_enumerated_premises",
                       eq=[[x] for x in equivalent_items],
                       why="Explicit common assumptions with mutually equivalent conditions"),None

    if len(blocks)==1:
        a,b=blocks[0]
        before=text[:a].strip()
        after=text[b:].strip()
        items=list_items(text,blocks[0])
        if not items:
            return None,"List items need editorial interpretation"
        m=EQUIV.search(before)
        if m and len(items)>=2:
            if AMBIGUOUS.search(after):
                return None,"Extra clause contains unresolved editorial text"
            head=before[:m.start()].strip()
            if before[m.end():].strip(" :.\n\t"):
                return None,"Unparsed content between equivalence header and list"
            if not after or TAIL_START.match(after):
                # Tail stays as a scoped consequence, NEVER a new equivalent
                # condition unless it explicitly asserts equivalence.
                if after and len(after)>900:
                    return None,"Consequence following equivalence too complex"
                eq=[[x] for x in items]
                h=([head] if head else [])+items
                c=items+([after] if after else [])
                cases=[{"logical_form":"equivalence",
                         "hypotheses":items,"conclusions":items,
                         "equivalence_sides":items,
                         "source_clause":text[a:b]}]
                if after:
                    cases.append({"logical_form":"scoped_additional_assertion",
                                  "hypotheses":[head] if head else [],
                                  "conclusions":[after],
                                  "source_clause":after,
                                  "scope_note":"Additional conclusion attached to equivalence; do not treat as equivalence side"})
                return repack(old,hypothesis=h,conclusion=c,
                              form="equivalence_with_additional_assertion" if after else "equivalence",
                              eq=eq,cases=cases,why="Equivalence sides searchable in both columns; additional assertions preserve scope"),None

        # Conditional results stated as 'under any of the following cases'
        if ALTERNATE.search(before) and not after and len(items)<=12:
            m=ALTERNATE.search(before)
            common=before[:m.start()].strip(" :\n")
            if not common:
                return None,"No stated conclusion or shared ambient assumptions for alternative cases"
            # In 'In each following cases, RESULT:' retain RESULT as
            # conclusion, with source-context prefix as the shared setup.
            result_prefix=common
            if re.search(r"In\s+each\s+of\s+the\s+following\s+cases",m.group(),re.I):
                # The assertion is AFTER 'cases' but BEFORE the list, so
                # this pattern is intentionally deferred rather than guessed.
                return None,"Result follows the alternate-case introducer"
            if INTRO.match(common) and re.search(r"\b(?:Then|the\s+group|the\s+map|is\s+defined)\b",common,re.I):
                # The text before 'provided ...' contains the precise result.
                cases=[{"hypotheses":[item],
                        "conclusions":[common],
                        "logical_form":"sufficient_condition",
                        "source_clause":item} for item in items]
                return repack(old,hypothesis=items,conclusion=[common],
                              form="alternative_sufficient_conditions",
                              cases=cases,why="Any single listed assumption suffices for preceding asserted result"),None

        # Source titles followed by independent theorem clauses.
        if not after and not EQUIV.search(before) and len(items)<=12:
            bare=PRE_TITLE.sub("",before).strip()
            if not bare:
                cases=[]
                for item in items:
                    unit=predicate_assertion(item.strip(" ,\n"))
                    if not unit:
                        break
                    h,c=unit
                    cases.append({"hypotheses":[h],"conclusions":[c],
                                  "logical_form":"universal_property",
                                  "source_clause":item})
                if len(cases)==len(items):
                    return repack(old,hypothesis=[z for case in cases for z in case["hypotheses"]],
                                  conclusion=[z for case in cases for z in case["conclusions"]],
                                  form="collection_of_unconditional_results",cases=cases,
                                  why="Independent source-listed assertions under an editorial heading"),None

    if not blocks:
        # A plain source equivalence: any iff condition is both searchable
        # sides without creating duplicate theorem records.
        if re.search(r"\bif\s+and\s+only\s+if\b",text,re.I) and len(text)<750:
            m=re.search(r"\bif\s+and\s+only\s+if\b",text,re.I)
            left,right=text[:m.start()].strip(),text[m.end():].strip()
            if left and right and not re.search(r"\bif\s+and\s+only\s+if\b",right,re.I):
                return repack(old,hypothesis=[left,right],conclusion=[left,right],
                      form="equivalence",eq=[[left],[right]],
                      why="Explicit biconditional conditions appear in both search fields"),None
        # A short unconditional theorem (a predicate over a source subject).
        parsed=predicate_assertion(text)
        if parsed:
            h,c=parsed
            return repack(old,hypothesis=[h],conclusion=[c],
                     form="source_universal_predicate",
                     why="Subject identified; conclusion retains full original assertion"),None

        # Source-native Let/Assume setup followed by a simple 'there is' or
        # 'we can' existential sentence, possibly without a period.
        if INTRO.match(text) and len(text)<900:
            m=re.search(r"\b(?:there\s+(?:exists?|is|are)|"
                        r"we\s+(?:can|obtain|find)|"
                        r"the\s+(?:functor|map|morphism|diagram)\s+)"
                        r".{0,25}?\b(?:exists?|is|are|has|admits)\b",text,re.I)
            if m and m.start()>20:
                h=text[:m.start()].strip()
                c=text[m.start():].strip()
                if h and c and not re.search(r"\bthe\s+following\s+(?:are|is)\b",h,re.I):
                    return repack(old,hypothesis=[h],conclusion=[c],
                           form="existential_with_source_setup",
                           why="Source setup followed by explicitly asserted existential result"),None
    return None,"Requires detailed semantic interpretation; retain for higher effort"


def repair_existing_cases(old):
    """Repair flattened source conditionals without changing canonical statement."""
    if old.get("logical_form")!="conjunction_of_source_clauses":
        return None
    cases=old.get("structured_cases",[])
    if not cases:
        return None
    # Old pipeline stored whole conditional clause as conclusion; rebuild
    # condition→result within each case while retaining original sources.
    if all(x.get("source_clause") for x in cases):
        return None
    setup=old["hypotheses"][0]
    new=[logical_item(x["conclusions"][0],setup) for x in cases]
    h=[setup]
    c=[]
    for case in new:
        h.extend(v for v in case["hypotheses"][1:] if v not in h)
        c.extend(case["conclusions"])
    return {**old,"hypotheses":h,"conclusions":c,"structured_cases":new,
            "split_confidence":"source_structure_interpretation_unverified",
            "statement_editorial_notes":"Repaired enumerated conditional/equivalence cases for search. Exact original statement and per-case source text retained. No proof read."}


def run(args):
    w=Path(args.workdir)
    current=pipe.load_rows(w/"pass2.jsonl","candidate_id")
    pending=pipe.load_rows(w/"pass2_higher_thinking_remaining.jsonl","candidate_id")
    raw=pipe.load_rows(w/"pass1.jsonl","candidate_id")
    revisions=[]
    still=[]
    forms=Counter()
    for ident,q in sorted(pending.items()):
        original=current.get(ident)
        if not original or original["context_status"]!="needs_structure":
            continue
        interpretation,reason=interpret_followup(original)
        if interpretation:
            revisions.append(interpretation)
            forms[interpretation["logical_form"]]+=1
        else:
            still.append({**q,"higher_thinking_reason":reason,"queue":"pass2_requires_editorial_reasoning"})
    repairs=[]
    for ident,old in sorted(current.items()):
        revised=repair_existing_cases(old)
        if revised:
            repairs.append(revised)
    all_updates=revisions+repairs
    if all_updates:
        f=w/"pass2_hard_followup_decisions.jsonl"
        pipe.atomic_text(f,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in all_updates))
        pipe.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(f),replace=True))
    pipe.atomic_text(w/"pass2_higher_thinking_remaining_v2.jsonl",
       "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in still))
    after=pipe.load_rows(w/"pass2.jsonl","candidate_id")
    summary={
      "stage":"pass2_hard_followup",
      "target":len(pending),"newly_resolved":len(revisions),
      "remaining_higher_thinking":len(still),
      "previous_structured_case_reannotations":len(repairs),
      "new_logical_forms":dict(sorted(forms.items())),
      "current_statuses":dict(sorted(Counter(x["context_status"] for x in after.values()).items())),
      "proofs_read":False,"mathematical_validity_assessed":False,
      "source":"Stacks original statement texts and existing Pass 2 records",
    }
    assert len(pending)==len(still)+len(revisions)
    pipe.atomic_text(w/"pass2_hard_followup_summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir",required=True)
    run(p.parse_args())
