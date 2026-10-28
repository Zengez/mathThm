import argparse,json
from pathlib import Path
from collections import Counter
try:
    from scripts import harvest_pipeline as p
except ImportError:
    import harvest_pipeline as p

def run():
    review=json.loads(Path('harvest/pass2_manual_statement_review_2026-10-28.json').read_text())['decisions']
    pending={d['candidate_id']:d for d in review}
    assert len(pending)==len(review)
    for batch in ('stacks-bulk-2026-10-28','stacks-second-2026-10-28'):
        w=Path('harvest/batches')/batch
        existing=p.load_rows(w/'pass2.jsonl','candidate_id')
        unresolved=p.load_rows(w/'pass2_higher_thinking_remaining_v2.jsonl','candidate_id')
        changes=[]
        for ident,d in list(pending.items()):
            if ident not in existing: continue
            old=existing[ident]
            if ident not in unresolved or old['context_status']!='needs_structure' or not old['statement'].startswith(d['expect_prefix']):
                raise ValueError('Statement or status mismatch: '+ident)
            h,c=d['hypotheses'],d['conclusions']
            if not all(isinstance(x,str) and x.strip() for x in h+c): raise ValueError(ident)
            if d['logical_form']=='equivalence' and h!=c: raise ValueError('Equivalence search mismatch: '+ident)
            cases=[]
            if d['logical_form']=='collection_of_implications':
                if len(c)==1: pairs=[(x,c[0]) for x in h]
                elif len(h)==len(c): pairs=list(zip(h,c))
                else: raise ValueError('case mapping: '+ident)
                cases=[{'hypotheses':[x],'conclusions':[y],'logical_form':'implication_subcase'} for x,y in pairs]
            changes.append({**old,'hypotheses':h,'conclusions':c,
               'logical_form':d['logical_form'],
               'equivalence_sides':[[x] for x in h] if d['logical_form']=='equivalence' else [],
               'structured_cases':cases,'context_status':'resolved','context_note':'',
               'review_method':'editorial','split_confidence':'bounded_editorial_statement_only',
               'statement_editorial_notes':'Source-statement-only editorial split; no mathematical/proof verification.'})
            del pending[ident]
        if changes:
            path=w/'pass2_manual_decisions.jsonl'
            p.atomic_text(path,''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in changes))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        ids={x['candidate_id'] for x in changes}
        residual=[x for k,x in sorted(unresolved.items()) if k not in ids]
        p.atomic_text(w/'pass2_higher_thinking_remaining_v3.jsonl',
            ''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in residual))
        statuses=Counter(x['context_status'] for x in p.load_rows(w/'pass2.jsonl','candidate_id').values())
        summary={'new_editorial_splits':len(changes),'higher_thinking_remaining':len(residual),
                 'statuses':dict(statuses),'proofs_read':False}
        p.atomic_text(w/'pass2_manual_summary.json',json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print(batch,summary)
    if pending: raise ValueError('Unmatched editorial IDs: '+str(sorted(pending)))

if __name__=='__main__': run()
