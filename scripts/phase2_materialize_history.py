"""Materialize existing mathematical approvals; does not create new approvals.

The four explicit historical corrections are applied to structured fields.
Pinned-source comparisons below check transcription only, not equivalence.
"""
import hashlib
import json
import re
from pathlib import Path
from scripts.phase2_authoritative import REV, content_digest, validate_overlay

BASE = Path("harvest/phase2_semantic_gate_2026-10-28")
OUT = Path("harvest/phase2_authoritative_2026-10-29/APPROVED_OVERLAYS.jsonl")


def rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def build(source_root=Path("upstream/stacks")):
    states = {r["candidate_id"]: r for r in rows(BASE/"ALL_DRAFT_READY_STATES.jsonl")}
    decisions = {r["candidate_id"]: r for r in rows(BASE/"INDIVIDUAL_DECISIONS.jsonl")}
    eligible = rows(BASE/"PHASE3_ELIGIBLE.jsonl")
    overlays = []
    for approval in eligible:
        cid = approval["candidate_id"]
        state, decision = states[cid], decisions[cid]
        assert decision["decision"] == "source_equivalence_approved"
        draft_path = Path(state["original_draft"])
        draft = next(r for r in rows(draft_path) if r.get("candidate_id", r.get("source_candidate_id")) == cid)
        label = approval["source_label"]
        text = (source_root/state["source_file"]).read_text()
        start = text.index("\\label{"+label+"}")
        end = start+re.search(r"\\end\{(?:lemma|theorem|proposition|corollary)\}", text[start:]).start()
        original = text[start:end].strip()
        assert original == draft["original_source_statement_tex"].strip(), label
        h, c = list(draft["draft_hypotheses"]), list(draft["draft_conclusions"])
        statement = draft["standalone_statement_tex"]
        cases, sides = [], []
        # Logical forms here follow the existing candidate-specific review,
        # not keyword detection (an internal iff is not a global equivalence).
        equivalences = {"lemma-qc-open", "lemma-domain-image-dense-set-points-generic-point",
                        "lemma-image-dense-generic-points", "lemma-constructible",
                        "lemma-surjective-finite-morphism-ample", "lemma-ample-on-reduction",
                        "lemma-thickening-quasi-affine", "lemma-locally-nilpotent-unit"}
        guarded = {"lemma-minimal-prime-reduced-ring", "lemma-cohen", "lemma-primes-principal",
                   "lemma-characterize-domain", "lemma-intersection-not-zero", "lemma-Noetherian-power",
                   "lemma-graded-finiteness", "lemma-lift-nth-roots", "lemma-characteristic-polynomial-prime"}
        logical = ("equivalence" if label in equivalences else
                   "independent_guarded_assertions" if label in guarded else "single_implication")
        if label in equivalences and len(c) > 1:
            sides = list(c)
        if label in ("lemma-coherent-on-proj", "lemma-coherent-on-proj-general"):
            h = [re.sub(r"Then \$X\$\s+is a Noetherian scheme\.\s*", "", x) for x in h]
            c = ["$X$ is a Noetherian scheme."]+c
            assert all("Then $X$" not in x for x in h)
        if label == "lemma-Noetherian-permanence":
            h = ["$R$ is a Noetherian commutative ring with identity."]
            c = ["Every finite type $R$-algebra is Noetherian.", "For every multiplicative subset $S$ of $R$, the localization $S^{-1}R$ is Noetherian."]
            cases = [{"hypotheses": [h[0], "$A$ is a finite type $R$-algebra."], "conclusions": ["$A$ is Noetherian."]},
                     {"hypotheses": [h[0], "$S$ is a multiplicative subset of $R$."], "conclusions": ["$S^{-1}R$ is Noetherian."]}]
            logical = "independent_conditional_claims"
            statement = "Let $R$ be a Noetherian commutative ring with identity. Every finite type $R$-algebra is Noetherian. Independently, for every multiplicative subset $S$ of $R$, $S^{-1}R$ is Noetherian."
        if label == "lemma-obvious-Noetherian":
            h = ["First independent case: $k$ is any field and $A$ is any finite type $k$-algebra. Second independent case: $B$ is any finite type $\\mathbf{Z}$-algebra. The cases are not conjoined."]
            c = ["In the first case $A$ is Noetherian.", "Independently, in the second case $B$ is Noetherian."]
            cases = [{"hypotheses": ["$k$ is a field.", "$A$ is a finite type $k$-algebra."], "conclusions": ["$A$ is Noetherian."]},
                     {"hypotheses": ["$B$ is a finite type $\\mathbf{Z}$-algebra."], "conclusions": ["$B$ is Noetherian."]}]
            logical = "independent_conditional_claims"
        r = dict(schema="maththm.phase2.authoritative-overlay.v1", candidate_id=cid,
                 source_revision=REV, source_label=label, source_file=state["source_file"],
                 source_line=state["source_line"], original_source_statement_tex=original,
                 source_statement_sha256=hashlib.sha256(original.encode()).hexdigest(),
                 original_draft=str(draft_path), original_draft_sha256=hashlib.sha256(draft_path.read_bytes()).hexdigest(),
                 statement=statement, hypotheses=h, conclusions=c, logical_form=logical,
                 structured_cases=cases, equivalence_sides=sides,
                 phase2_validated=True, phase3_eligible=True, duplicate_review_status="clear",
                 semantic_review_note=decision["semantic_review_note"],
                 historical_decision_file=str(BASE/"INDIVIDUAL_DECISIONS.jsonl"),
                 historical_eligibility_file=str(BASE/"PHASE3_ELIGIBLE.jsonl"),
                 mathematical_approval_origin="preserved_historical_individual_source_equivalence_review",
                 materialization_date="2026-10-29", corrected_split=approval.get("corrected_split"),
                 proof_reviewed=False, published=False)
        r["approved_content_sha256"] = content_digest(r)
        validate_overlay(r)
        overlays.append(r)
    assert len(overlays) == 68
    return sorted(overlays, key=lambda r: r["candidate_id"])


def main():
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False)+"\n" for r in result))
    print("Materialized", len(result), "existing approvals; no new mathematical approvals")


if __name__ == "__main__":
    main()
