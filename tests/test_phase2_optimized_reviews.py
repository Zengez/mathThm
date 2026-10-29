"""Regression examples discovered during independent mathematical comparison.

These protect recorded corrections; passing them is not a mathematical verdict.
"""
import json
from pathlib import Path
import unittest
from scripts.phase2_authoritative import content_digest, load_approved

BASE=Path('harvest/phase2_optimized_2026-10-29')
def records(region):
    return [json.loads(s) for s in (BASE/region/'RECONSTRUCTIONS.jsonl').read_text().splitlines()]

class OptimizedMathematicalRegressionTests(unittest.TestCase):
    def test_independent_decisions_bind_all_logical_fields(self):
        for region in ['divisors_a','divisors_b']:
            drafts={r['candidate_id']:r for r in records(region)}
            decisions=[json.loads(s) for s in (BASE/region/'INDEPENDENT_VALIDATION.jsonl').read_text().splitlines()]
            self.assertEqual(len(decisions),len(drafts))
            for verdict in decisions:
                self.assertEqual(verdict['formulation_sha256'],content_digest(drafts[verdict['candidate_id']]))
                self.assertTrue(verdict['source_first_review'])
                self.assertFalse(verdict['proof_reviewed'])

    def test_source_ambiguities_are_not_promoted(self):
        approved=load_approved()
        holds={r['source_label']:r for region in ['divisors_a','divisors_b']
               for r in records(region) if r['decision']=='context_resolution_pending'}
        self.assertIn('lemma-effective-Cartier-divisor-Sk',holds)
        self.assertIn('lemma-Pic-projective-space-UFD',holds)
        for row in holds.values():
            self.assertNotIn(row['candidate_id'],approved)

    def test_internal_equivalences_do_not_swallow_main_assertions(self):
        r={r['source_label']:r for r in records('divisors_a')}
        self.assertEqual(r['lemma-reflexive-torsion-free']['logical_form'],
                         'conditional_assertion_with_internal_equivalence')
        self.assertEqual(r['lemma-zero-scheme']['logical_form'],
                         'conjunctive_assertions_with_internal_equivalences')
        self.assertEqual(r['lemma-codim-1-part']['logical_form'],'independent_conditional_assertions')
        self.assertEqual(r['lemma-fitting-ideal-generate-locally']['logical_form'],'equivalence')

    def test_alternative_hypotheses_and_omitted_corollaries_restored(self):
        r={r['source_label']:r for r in records('divisors_b')}
        ample=r['proposition-push-down-ample']
        self.assertEqual(ample['logical_form'],'alternative_sufficient_hypotheses')
        self.assertEqual(ample['conclusions'],['Y has an ample invertible module.'])
        self.assertIn('prime number',ample['statement'])
        fibre=r['lemma-fibre-Cartier']
        self.assertEqual(len(fibre['conclusions']),5)
        self.assertIn('locally principal',fibre['conclusions'][-1])
        norms=r['lemma-norm-map-invertible']
        self.assertIn('There is an induced map',norms['conclusions'][0])
        self.assertIn('iff',norms['conclusions'][1])
        for label in ['lemma-complement-affine-open-immersion','lemma-complement-affine-open']:
            self.assertNotIn('dim',r[label]['hypotheses'][0])
            self.assertIn('\\leq1',r[label]['conclusions'][0])

    def test_source_typo_corrected_only_in_reviewed_overlay(self):
        r=next(r for r in records('divisors_b') if r['source_label']=='lemma-conormal-algebra-functorial')
        self.assertIn("f^\\sharp : R'",r['original_source_statement_tex'])
        self.assertIn("g^\\sharp : R'",r['statement'])
        self.assertNotIn("f^\\sharp : R'",r['statement'])
        self.assertIn('source_typo_correction',r)
        regular=next(r for r in records('divisors_b') if r['source_label']=='lemma-types-regular-sequences-implications')
        self.assertIn('\\mathcal J=(f_1,\\ldots,f_r)',regular['statement'])

if __name__=='__main__':
    unittest.main()
