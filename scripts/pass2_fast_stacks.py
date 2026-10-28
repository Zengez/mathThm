#!/usr/bin/env python3
"""Fast, CONSERVATIVE Pass 2 syntax triage for Stacks theorem candidates.

Checks whether a source entry appears to state a mathematical result, then
splits hypotheses/conclusions ONLY for safely recognizable surface grammar.
A syntax-only split is NOT mathematically or editorially certified.
No proof is opened or used by this script. All other entries are queued for
bounded human/model statement review; nothing is silently thrown away.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

try:
    from . import harvest_pipeline as pipeline
except ImportError:
    import harvest_pipeline as pipeline

LABEL = re.compile(r"\\label\{[^{}]*\}")
SLOGAN = re.compile(r"\\begin\{slogan\}[\s\S]*?\\end\{slogan\}", re.I)
INDEX = re.compile(r"\\index\{[^{}]*\}")
BEGIN_COMPLEX = re.compile(
    r"\\(?:begin|end)\{(?:enumerate|itemize|description|diagram|xymatrix|equation|align|cases|commdiagram|matrix|array|tabular)\}"
    r"|\\(?:xymatrix|xymatrix@|begin\{equation\*?\})", re.I)
CONTEXT_DEPENDENCY = re.compile(
    r"\b(?:defined|constructed|introduced|described|discussed|chosen|fixed|given)\s+(?:just\s+)?(?:above|earlier|previously|before)\b"
    r"|\b(?:with|using|under|in)\s+(?:the\s+)?(?:notation|assumptions|setup|hypotheses|situation|setting)\s+(?:of|from|as\s+in|above|below|introduced|established)\b"
    r"|\b(?:the|this|these|those)\s+(?:above|preceding|previous|following)\s+(?:lemma|proposition|construction|setup|notation|assumptions|definition|diagram)\b"
    r"|\b(?:as\s+in|as\s+above|from\s+the\s+previous)\b", re.I)
INTRO = re.compile(r"^(?:Let|Suppose|Assume|Fix|Given|Consider|Write|Take)\b", re.I)
THEN = re.compile(r"\bthen\b", re.I)
# A sentence starting after an explicit 'Let/Assume/...' introduction,
# not an arbitrary mathematical proposition.
NEXT_RESULT = re.compile(
    r"\.\s+(?=(?:Then|There|The|This|It|We|Any|Every|Each|For|An|A|One|"
    r"If|Hence)\b|\$(?:\\[A-Za-z]+|[A-Za-z]))", re.I)
QUESTION = re.compile(r"\b(?:open\s+question|conjecture|problem\s+for\s+the\s+reader|"
                      r"exercise\s+for\s+the\s+reader)\b", re.I)
MATH_SIGNAL = re.compile(r"\$|\\[A-Za-z]+|\b(?:category|ring|module|scheme|morphism|"
                         r"topological|space|set|group|field|functor|complex|sheaf|"
                         r"equivalent|isomorphic|finite|continuous|subset|map)\b", re.I)

SUBJECTS = {
    "algebra.tex": "Algebra", "more-algebra.tex": "Algebra",
    "fields.tex": "Field theory", "groups.tex": "Group theory",
    "topology.tex": "Topology", "spaces.tex": "Topology",
    "categories.tex": "Category theory", "sets.tex": "Set theory",
    "modules.tex": "Module theory", "schemes.tex": "Algebraic geometry",
    "comm-algebra.tex": "Commutative algebra", "sheaves.tex": "Sheaf theory",
    "limits.tex": "Algebraic geometry", "groupoids.tex": "Groupoids",
    "derived.tex": "Derived categories", "homology.tex": "Homological algebra",
    "cohomology.tex": "Cohomology", "varieties.tex": "Algebraic geometry",
    "curves.tex": "Algebraic geometry", "divisors.tex": "Algebraic geometry",
    "sites.tex": "Sites and sheaves", "simplicial.tex": "Simplicial methods",
    "descent.tex": "Descent theory", "etale.tex": "Étale theory",
    "number-theory.tex": "Number theory", "homotopy.tex": "Homotopy theory",
}


def clean_statement(raw: str) -> str:
    """Remove metadata commands, not mathematical content or quantifiers."""
    text = SLOGAN.sub("", raw)
    text = LABEL.sub("", text)
    text = INDEX.sub("", text)
    return text.strip()


def gentle_trim(s: str) -> str:
    return s.strip().strip("\n").strip()


def grammatical_split(text: str):
    """Return two source-faithful text spans or None; never invent hypotheses.

    A label-free text is enough: preserve original logical punctuation and
    LaTeX, not a speculative mathematical paraphrase.
    """
    if BEGIN_COMPLEX.search(text):
        return None, "Multi-item or diagram-based statement needs clause-level attention"
    if text.count("$$") % 2 != 0 or text.count("$") % 2 != 0:
        return None, "Unbalanced mathematical delimiters in extracted statement"
    if len(text) > 1250:
        return None, "Long statement; syntax-only extraction is not sufficiently reliable"
    # Avoid splitting on 'then' inside a math region.
    spans = [(m.start(), m.end()) for m in re.finditer(r"(?<!\\)\$[^$]*\$", text, re.S)]
    def outside_math(index):
        return not any(a <= index < b for a,b in spans)
    for m in THEN.finditer(text):
        if not outside_math(m.start()):
            continue
        before = gentle_trim(text[:m.start()])
        after = gentle_trim(text[m.end():])
        if (before and after and
                (INTRO.match(before) or re.search(r"\b(?:If|Suppose|Assume|When|Whenever|Provided)\b", before, re.I))):
            return (before, after), "Explicit then-clause boundary"
    if INTRO.match(text):
        # Seek a safe sentence break between an introduction and the asserted
        # conclusion. 'Let X. Let Y. Then Z' must keep both Let sentences.
        breaks=list(NEXT_RESULT.finditer(text))
        for m in breaks:
            left=gentle_trim(text[:m.start()+1])
            right=gentle_trim(text[m.end():])
            if right and not INTRO.match(right) and not right.lower().startswith("if "):
                return (left,right), "Introductory assumptions separated from assertion"
    return None, "No safely identifiable hypothesis/conclusion boundary"


def classify(row: dict) -> dict:
    ident=row["candidate_id"]
    source=row["source"]
    text=clean_statement(row["statement_tex"])
    area=SUBJECTS.get(source["filename"],"Unclassified")
    refs=row.get("detected_local_references",[])
    decision={
        "candidate_id":ident,
        "result_classification":"mathematical_result",
        "review_method":"mechanical_syntax",
        "split_confidence":"syntax_only",
        "context_status":"needs_structure",
        "context_note":"",
        "statement":text,
        "hypotheses":[], "conclusions":[],
        "hypothesis_tags":[],"conclusion_tags":[],
        "area":area,
        "title":None,
        "statement_editorial_notes":"Syntax-only Pass 2 segmentation. Original raw Stacks text preserved in Pass 1. No proof review or mathematical verification.",
        "local_context_used":[],
    }
    if not source.get("label") or row.get("entry_type") not in ("theorem","lemma","proposition","corollary"):
        decision.update(result_classification="uncertain",context_status="needs_classification",
                        context_note="Missing named result label or unexpected environment")
        return decision
    if not text or len(text)<15 or not MATH_SIGNAL.search(text):
        decision.update(result_classification="uncertain",context_status="needs_classification",
                        context_note="Extracted text lacks readily identifiable mathematical content")
        return decision
    if QUESTION.search(text):
        decision.update(result_classification="uncertain",context_status="needs_classification",
                        context_note="Statement contains an exercise/conjecture/problem term; check context")
        return decision
    if CONTEXT_DEPENDENCY.search(text):
        decision.update(context_status="needs_context",
                        context_note="Statement explicitly inherits construction, assumptions or notation; expand locally in editorial review")
        return decision
    parts,reason=grammatical_split(text)
    if parts is None:
        decision.update(context_status="needs_structure",context_note=reason)
        return decision
    decision.update(context_status="resolved",hypotheses=[parts[0]],
                    conclusions=[parts[1]],context_note="",split_confidence="syntax_only")
    return decision


def run(args):
    w=Path(args.workdir)
    raw=pipeline.load_rows(w/"pass1.jsonl","candidate_id")
    if not raw:
        raise ValueError(f"no Pass 1 candidates at {w}")
    decisions=[classify(row) for _,row in sorted(raw.items())]
    # Cache the exact editable decisions as well as applied normalized output.
    decisions_file=w/"pass2_syntax_decisions.jsonl"
    pipeline.atomic_text(decisions_file,
        "".join(json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n" for d in decisions))
    pipeline.apply_pass2(argparse.Namespace(workdir=str(w),
        decisions=str(decisions_file), replace=args.replace))
    counts=Counter(d["context_status"] for d in decisions)
    classes=Counter(d["result_classification"] for d in decisions)
    stats={
        "stage":"pass2_syntax_triage",
        "total":len(raw),
        "context_status":dict(sorted(counts.items())),
        "result_classification":dict(sorted(classes.items())),
        "mathematical_validity_assessed":False,
        "proofs_read":False,
        "review_method":"mechanical_syntax",
        "split_confidence":"syntax_only; requires editorial QA before treating as final",
        "source_files":dict(sorted(Counter(r["source"]["filename"] for r in raw.values()).items())),
    }
    pipeline.atomic_text(w/"pass2_summary.json",
        json.dumps(stats,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps(stats,ensure_ascii=False,sort_keys=True))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir",required=True)
    p.add_argument("--replace",action="store_true",
                   help="Replace prior Pass 2 decisions intentionally")
    run(p.parse_args())


if __name__=="__main__":
    main()
