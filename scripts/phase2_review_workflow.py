"""Checkpoint explicitly recorded mathematical reviews; never infer approval.

`materialize` copies only independently approved formulations from the explicit
review manifest into downstream overlays. `status` reconciles every canonical
ID, including holds and unprocessed candidates. Neither operation reads proofs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from scripts.phase2_authoritative import REV, content_digest, load_approved, validate_overlay, apply_overlay

BASE = Path('harvest/phase2_calibration_2026-10-29')
MANIFEST = BASE / 'REVIEW_BATCHES.json'
REGISTRY = Path('harvest/PHASE2_AUTHORITATIVE_REGISTRY.json')
OUTPUT = BASE / 'AUTHORITATIVE.jsonl'

def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def formulation_digest(row):
    return content_digest(row)

def atomic_text(path, text):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(text)
    temporary.replace(path)


def unique(items):
    result = {}
    for row in items:
        if row['candidate_id'] in result:
            raise ValueError('Duplicate candidate review: ' + row['candidate_id'])
        result[row['candidate_id']] = row
    return result

def active_ids():
    return {r['candidate_id'] for r in rows('harvest/active_candidate_ids.jsonl')}

def provisional_duplicate_ids():
    return {r['canonical_candidate_id'] for r in rows('harvest/CONSOLIDATED_CANDIDATES.jsonl')}

def review_pairs(manifest=MANIFEST):
    config = json.loads(Path(manifest).read_text())
    if config['source_revision'] != REV:
        raise ValueError('Review manifest revision mismatch')
    seen = set()
    for batch in config['review_batches']:
        reconstruct = unique(rows(batch['reconstructions']))
        validators = unique(rows(batch['independent_validation']))
        if set(reconstruct) != set(validators):
            raise ValueError('Every batch candidate must have an independent recorded state')
        if seen & set(reconstruct):
            raise ValueError('Review batches overlap')
        seen.update(reconstruct)
        for cid, row in reconstruct.items():
            verdict = validators[cid]
            if row['source_revision'] != REV or verdict['source_revision'] != REV:
                raise ValueError('Review source revision mismatch')
            reviewer = verdict.get('reviewer', verdict.get('independent_validator', verdict.get('validator')))
            if not reviewer or reviewer == batch['reconstructor']:
                raise ValueError('Independent reviewer must differ from reconstructor')
            if verdict.get('source_first_review') is not True:
                raise ValueError('Independent source-first review required')
            if row.get('proof_reviewed') is not False or verdict.get('proof_reviewed') is not False:
                raise ValueError('Phase 2 reviews must not assess proofs')
            if verdict.get('formulation_sha256') != formulation_digest(row):
                raise ValueError('Formulation changed since independent mathematical review: ' + cid)
            yield batch, row, verdict

def materialize(manifest=MANIFEST, output=OUTPUT):
    active = active_ids()
    duplicate = provisional_duplicate_ids()
    registry = json.loads(REGISTRY.read_text())
    existing = {}
    for path in registry['overlay_files']:
        if Path(path) == Path(output):
            continue
        for record in rows(path):
            validate_overlay(record)
            if record['candidate_id'] in existing:
                raise ValueError('Duplicate existing authoritative record')
            existing[record['candidate_id']] = record
    from scripts.active_candidate_pool import BATCHES
    raw = {}
    for name in BATCHES:
        raw.update(unique(rows(Path('harvest/batches') / name / 'pass1.jsonl')))
    approved = []
    for batch, row, verdict in review_pairs(manifest):
        if row['candidate_id'] not in active:
            raise ValueError('Review outside active canonical population')
        decision = verdict.get('independent_decision', verdict.get('decision'))
        if decision != 'source_equivalence_approved':
            continue
        if row['candidate_id'] in duplicate:
            raise ValueError('Provisional duplicate requires separate explicit adjudication')
        if row['candidate_id'] in existing:
            raise ValueError('New review overlaps historical approval')
        if not row.get('logical_form'):
            raise ValueError('Reviewer-confirmed logical form required')
        overlay = dict(row)
        overlay.update(schema='maththm.phase2.authoritative-overlay.v1',
                       phase2_validated=True, phase3_eligible=True, duplicate_review_status='clear',
                       original_draft_sha256=digest(row['original_draft']),
                       source_statement_sha256=hashlib.sha256(row['original_source_statement_tex'].encode()).hexdigest(),
                       independent_validation=verdict,
                       reconstruction_artifact=batch['reconstructions'],
                       independent_validation_artifact=batch['independent_validation'],
                       mathematical_review_date='2026-10-29',
                       logical_form=row['logical_form'],
                       structured_cases=row.get('structured_cases', []),
                       equivalence_sides=row.get('equivalence_sides', []))
        overlay['approved_content_sha256'] = content_digest(overlay)
        validate_overlay(overlay)
        apply_overlay({'candidate_id':row['candidate_id']}, overlay, raw=raw[row['candidate_id']])
        approved.append(overlay)
    unique(approved)
    atomic_text(output, ''.join(json.dumps(r, sort_keys=True, ensure_ascii=False)+'\n'
                                   for r in sorted(approved,key=lambda x:x['candidate_id'])))
    if str(output) not in registry['overlay_files']:
        registry['overlay_files'].append(str(output))
        atomic_text(REGISTRY, json.dumps(registry, indent=2)+'\n')
    # The complete union was checked before either atomic replacement.
    load_approved()
    return len(approved)

def population_status(approved=None, pairs=None):
    approved = approved if approved is not None else load_approved()
    active = active_ids()
    states = {cid: 'not_yet_reconstructed' for cid in active}
    registry = json.loads(Path('harvest/SECTION_WALK_COMPLETED_SECTIONS.json').read_text())
    sections = []
    drafted = set()
    for section in registry['sections']:
        candidates = rows(section['artifacts'])
        if len(candidates) != section['active_candidate_count']:
            raise ValueError('Section draft count mismatch')
        ids=[]
        for row in candidates:
            cid=row.get('candidate_id',row.get('source_candidate_id'))
            if cid not in active or cid in drafted:
                raise ValueError('Section registry candidate mismatch')
            ids.append(cid);drafted.add(cid)
            old=row.get('context_review_status',row.get('review_status',row.get('status')))
            states[cid] = ('awaiting_mathematical_validation' if old=='standalone_draft_ready_for_validation'
                           else 'context_reconstruction_required' if old=='context_resolution_pending'
                           else 'earlier_pilot_reconciliation_required')
        sections.append((section,ids))
    for row in rows('harvest/phase2_semantic_gate_2026-10-28/INDIVIDUAL_DECISIONS.jsonl'):
        if row['decision']!='source_equivalence_approved':
            states[row['candidate_id']]='reconstruction_error_requires_correction'
    pending_reconstructed=set()
    config=json.loads(MANIFEST.read_text())
    for batch in config.get('pending_reconstruction_batches', []):
        for row in rows(batch['reconstructions']):
            cid=row['candidate_id']
            if cid not in active:
                raise ValueError('Pending reconstruction outside active population')
            pending_reconstructed.add(cid)
            # Stage A completed; no mathematical approval is inferred.
            if row.get('decision')=='reconstruction_completed_awaiting_independent_validation':
                states[cid]='awaiting_mathematical_validation'
    pairs=list(pairs if pairs is not None else review_pairs())
    reviewed=set()
    for batch,row,verdict in pairs:
        cid=row['candidate_id'];reviewed.add(cid)
        decision=verdict.get('independent_decision',verdict.get('decision'))
        if decision=='source_equivalence_approved':
            states[cid]='awaiting_authoritative_materialization'
        elif decision in ('context_resolution_required','context_resolution_pending','context_hold'):
            states[cid]='context_reconstruction_required'
        else:
            states[cid]='reconstruction_error_requires_correction'
    if not set(approved)<=active:
        raise ValueError('Approved overlay outside active population')
    for cid in approved:
        states[cid]='fully_phase2_validated'
    counts=Counter(states.values())
    if sum(counts.values())!=9675:
        raise ValueError('Active population changed without controlled adjudication')
    section_states=[]
    for section,ids in sections:
        section_states.append(dict(source_file=section['source_file'],
            section_start_line=section['section_start_line'], section_end_line=section['section_end_line'],
            active_candidates=len(ids), recorded_this_run=sum(cid in reviewed for cid in ids),
            all_individually_reviewed=all(cid in reviewed or cid in approved for cid in ids),
            all_phase3_eligible=all(cid in approved for cid in ids)))
    return dict(schema='maththm.phase2.population-checkpoint.v1',date='2026-10-29',source_revision=REV,
                active_candidates=len(active),fully_phase2_validated=len(approved),phase3_eligible=len(approved),
                mutually_exclusive_states=dict(sorted(counts.items())),
                duplicate_review_blockers=len(provisional_duplicate_ids()),
                duplicate_blockers_are_secondary_not_additional_population=True,
                newly_validated_this_run=len(set(approved)-{r['candidate_id'] for r in rows('harvest/phase2_semantic_gate_2026-10-28/PHASE3_ELIGIBLE.jsonl')}),
                calibration_and_followup_candidates_reviewed=len(reviewed),
                additional_stage_a_candidates_awaiting_independent_review=len(pending_reconstructed-reviewed),
                reconstructed_registry_candidates=len(drafted),
                section_checkpoints=section_states,
                proofs_screened_this_run=0,production_corpus_changed=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['materialize','status'])
    args=parser.parse_args()
    if args.action=='materialize':
        print('Materialized independently approved overlays:',materialize())
    else:
        result=population_status()
        (BASE/'STATUS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='section_checkpoints'},indent=2))

if __name__=='__main__':
    main()
