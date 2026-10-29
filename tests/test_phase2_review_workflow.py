"""Recorded reviews may be materialized; scripts never infer mathematical approval."""
import copy
import unittest
from scripts import phase2_review_workflow as w
from scripts.phase2_authoritative import load_approved, apply_overlay

class ReviewWorkflowTests(unittest.TestCase):
    def test_every_final_review_bound_to_exact_formulation(self):
        pairs=list(w.review_pairs())
        self.assertEqual(len(pairs),77)
        self.assertEqual(sum(v.get('independent_decision',v.get('decision'))=='source_equivalence_approved'
                             for _,r,v in pairs),76)
        for batch,row,verdict in pairs:
            self.assertEqual(verdict['formulation_sha256'],w.formulation_digest(row))
            changed=copy.deepcopy(row)
            changed['hypotheses']=row['hypotheses']+['An unjustified extra premise']
            self.assertNotEqual(w.formulation_digest(changed),verdict['formulation_sha256'])
            changed=copy.deepcopy(row);changed['logical_form']='incorrect_new_logical_form'
            self.assertNotEqual(w.formulation_digest(changed),verdict['formulation_sha256'])

    def test_population_reconciles_and_pending_is_not_approved(self):
        approved=load_approved();status=w.population_status(approved)
        self.assertEqual(sum(status['mutually_exclusive_states'].values()),9675)
        self.assertEqual(status['fully_phase2_validated'],len(approved))
        self.assertEqual(status['newly_validated_this_run'],76)
        self.assertEqual(status['additional_stage_a_candidates_awaiting_independent_review'],46)
        self.assertFalse(set(approved)&w.provisional_duplicate_ids())
        pending=w.rows(w.BASE/'algebra_next/RECONSTRUCTIONS.jsonl')
        self.assertFalse({r['candidate_id'] for r in pending}&set(approved))

    def test_eight_defects_corrected_but_history_retained(self):
        approved={r['source_label']:r for r in load_approved().values()}
        repairs=w.rows(w.BASE/'defects/RECONSTRUCTIONS.jsonl')
        self.assertEqual(len(repairs),8)
        for r in repairs:
            self.assertEqual(approved[r['source_label']]['statement'],r['statement'])
        subring=approved['lemma-subring-of-local-ring']
        self.assertEqual(subring['logical_form'],'alternative_sufficient_hypotheses')
        self.assertIn('At least one',subring['hypotheses'][1])
        self.assertIn('injective',subring['conclusions'][0])
        basechange=approved['lemma-surjective-spec-radical-ideal']
        self.assertIn('If those equivalent conditions hold',basechange['conclusions'][1])
        cohomology=approved['lemma-invert-s-cohomology']
        self.assertIn('quasi-compact',cohomology['hypotheses'][0])
        self.assertIn('degree-zero',cohomology['statement'])
        general=approved['proposition-coherent-modules-on-proj-general']
        self.assertIn('M_{nd}=0',general['statement'])
        self.assertIn('Serre',general['statement'])

if __name__=='__main__':
    unittest.main()
