# Differential Graded Algebra (dga) — Stage A handoff

Pinned Stacks source: [dga.tex](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L17) at `a04446e57ec1fbc252a871afcec7752fb2807b14`.
Branch: `work/phase2-stage-a-context-enrichment`. **Chat Stage A source walk completed; independent Codex Stage B has not run.**

## Reconciled scope

- **38/38** physical sections traversed in source order (source lines 17–7210), including all intervening candidate-free sections.
- **103** harvested theorem-like results; **87** canonical active candidates; **16** inactive records excluded by exact candidate ID.
- **80** self-contained Stage A drafts eligible for Codex's independent review; **7** explicitly held as `further_work_needed`.
- **56** chronological source-anchored context events; **38** after-section checkpoints.
- No proof validation, mathematical equivalence certification, independent Stage B approval, or Phase 3 promotion occurred.

## Batch packets

| Sections | Active | Stage B-ready | Further work | Packet |
|---|---:|---:|---:|---|
| 1–13 | 19 | 18 | 1 | [batch_01_sections_01_13](batch_01_sections_01_13/MANIFEST.json) |
| 14–25 | 15 | 15 | 0 | [batch_02_sections_14_25](batch_02_sections_14_25/MANIFEST.json) |
| 26–30 | 23 | 19 | 4 | [batch_03_sections_26_30](batch_03_sections_26_30/MANIFEST.json) |
| 31–38 | 30 | 28 | 2 | [batch_04_sections_31_38](batch_04_sections_31_38/MANIFEST.json) |
| **Total** | **87** | **80** | **7** | |

## Further-work worklist

1. **§9 [lemma-third-isomorphism](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L798)** (L798): The displayed target triangle repeats $(K_1,L_1,C(f_1))$ rather than the data of $f_2:K_2\to L_2$. Reconcile both triangles and the exact target before standalone acceptance. Packet: `harvest/phase2_chat_stage_a/dga/batch_01_sections_01_13/MANIFEST.json`.
2. **§27 [lemma-get-triangle](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L3490)** (L3490): The source only specifies the boundary $z\to x[1]$ by '(see proof)' under axioms (A),(B). Materialize its definition and sign convention independently. Source-deictic/proof-dependent wording remains unmaterialized. Packet: `harvest/phase2_chat_stage_a/dga/batch_03_sections_26_30/MANIFEST.json`.
3. **§27 [lemma-analogue-triangle-independent-splittings](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L3887)** (L3887): The connecting arrow is defined through an earlier source-specific construction. Write down the graded-splitting formula and its sign/choice independence before acceptance. Unexpanded source references: lemma-get-triangle Packet: `harvest/phase2_chat_stage_a/dga/batch_03_sections_26_30/MANIFEST.json`.
4. **§27 [lemma-restate-axiom-c](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L3930)** (L3930): The source says $c(f)$ is 'defined as in Lemma get-triangle', but that lemma constructs a boundary triangle, not the cone prescribed by axiom (C); adjudicate this inconsistent attribution. Unexpanded source references: lemma-get-triangle Packet: `harvest/phase2_chat_stage_a/dga/batch_03_sections_26_30/MANIFEST.json`.
5. **§27 [lemma-analogue-third-isomorphism](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L4043)** (L4043): The target cone triangle repeats $i_1,p_1$ where the target should use the structure maps associated to $f_2$; verify source indexing and types. Packet: `harvest/phase2_chat_stage_a/dga/batch_03_sections_26_30/MANIFEST.json`.
6. **§34 [lemma-compose-tensor-functors-general-algebra](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L5741)** (L5741): The resulting $(A,C)$-bimodule $N''$ is only 'described in the proof'. The actual construction (or a justified replacement with an existential assertion) must be verified. Packet: `harvest/phase2_chat_stage_a/dga/batch_04_sections_31_38/MANIFEST.json`.
7. **§34 [lemma-compose-tensor-functors](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/dga.tex#L5849)** (L5849): This depends on the proof-defined kernel of the preceding composition lemma and its three-algebra derived comparison; expand and type the bimodule $N''$. Packet: `harvest/phase2_chat_stage_a/dga/batch_04_sections_31_38/MANIFEST.json`.

## Context and review boundary

Read sections and candidate statements from the pinned source in chronological order, registering definitions, constructions, conventions, section-specific setup and the actual `situation-ABC` separately. The chapter's convention is that rings are commutative with 1 and its dg sign rules are those of the pinned source. The chapter-specific properties (P) and (I), bimodule-specific property (P), the (A)/(B)/(C) dg-category axioms, source-side tensor/Hom functors and derived comparison arrows were explicitly materialized in the relevant candidate statements. Earlier theorem-local assumptions and proof-local constructions were not inherited. The seven source-level unresolved cases are kept out of Codex's Stage B-ready queue.

For Stage B, use only the four `RECONSTRUCTIONS.jsonl` packets and select exact IDs with `decision == "reconstruction_completed_awaiting_independent_stage_b_validation"`. The `hypotheses` and `conclusions` entries remain Stage A split leads, sometimes conservatively incorporating the entire theorem when the old Pass 2 split referred to missing context. The full materialized `standalone_statement_draft` is the authoritative draft to independently split and validate. Do not process the `further_work_needed` records without additional context recovery. Retain original source attribution, pinned revision, and proof bodies without modification.

Structural checks cover unique active IDs, complete section coverage, no unresolved `\\ref{...}` in ready statements and splits, nonempty hypotheses/conclusions, and no Phase 3 flags. **The repository regression suite has not been executed by this pass.**
