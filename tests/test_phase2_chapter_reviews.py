"""Protect explicit logical repairs in the chapter-sized review campaign."""
import json
from pathlib import Path
import unittest
from scripts.phase2_authoritative import content_digest
BASE=Path('harvest/phase2_chapters_2026-10-29')

class ChapterReviewRegressionTests(unittest.TestCase):
    def test_algebra_tail_separate_guards_and_equivalences(self):
        rows={r['source_label']:r for r in map(json.loads,(BASE/'algebra_tail/RECONSTRUCTIONS.jsonl').read_text().splitlines())}
        self.assertEqual(len(rows),13)
        composition=rows['lemma-going-up-down-composition']
        self.assertEqual(composition['logical_form'],'independent_conditional_claims')
        self.assertNotIn('going down',' '.join(composition['hypotheses']))
        self.assertIn('going up',composition['conclusions'][1])
        closed=rows['lemma-going-up-closed']
        self.assertEqual(closed['logical_form'],'equivalence')
        self.assertIn('if and only if',closed['conclusions'][0])
        fppf=rows['proposition-fppf-open']
        self.assertNotIn('flat',' '.join(fppf['hypotheses']))
        self.assertEqual(len(fppf['structured_cases']),2)
        self.assertIn('going down',fppf['structured_cases'][1]['hypotheses'][0])
        separable=rows['lemma-subextensions-are-separable']
        self.assertIn('every finitely generated intermediate',separable['statement'])
        self.assertEqual(rows['lemma-generating-finitely-generated-separable-field-extensions']['logical_form'],'joint_existential_conclusion')

    def test_final_chapter_reviews_bound_to_exact_formulations(self):
        manifest=json.loads(Path('harvest/phase2_calibration_2026-10-29/REVIEW_BATCHES.json').read_text())
        paths=[Path(b['independent_validation']) for b in manifest['review_batches']
               if Path(b['independent_validation']).is_relative_to(BASE)]
        for path in paths:
            drafts={r['candidate_id']:r for r in map(json.loads,path.with_name('RECONSTRUCTIONS.jsonl').read_text().splitlines())}
            decisions=[json.loads(s) for s in path.read_text().splitlines()]
            self.assertEqual(set(drafts),{v['candidate_id'] for v in decisions})
            for v in decisions:
                self.assertEqual(v['formulation_sha256'],content_digest(drafts[v['candidate_id']]))
                self.assertTrue(v['source_first_review'])
                self.assertFalse(v['proof_reviewed'])

    def test_varieties_first_batch_review_corrections(self):
        path=BASE/'varieties_a/RECONSTRUCTIONS.jsonl'
        rows={r['source_label']:r for r in map(json.loads,path.read_text().splitlines())}
        self.assertIn('as $k$-fields',' '.join(rows['lemma-birational-varieties']['conclusions']))
        tangent=rows['lemma-tangent-space-rational-point']
        self.assertNotIn('\\kappa', ' '.join(tangent['hypotheses']))
        self.assertEqual(len(tangent['conclusions']),2)
        self.assertIn('separable algebraic',tangent['conclusions'][1])
        diagram=rows['lemma-geometric-structure-unramified']
        self.assertNotIn('Y & & V',' '.join(diagram['conclusions']))
        self.assertIn('S & & V',' '.join(diagram['conclusions']))

    def test_varieties_source_ambiguities_stay_out_of_authority(self):
        from scripts.phase2_authoritative import load_approved
        approved=load_approved()
        rows={r['source_label']:r for r in map(json.loads,(BASE/'varieties_a/RECONSTRUCTIONS.jsonl').read_text().splitlines())}
        for label in ['theorem-varieties-rational-maps','lemma-geometrically-irreducible-local','lemma-units-variety']:
            self.assertEqual(rows[label]['decision'],'context_resolution_pending')
            self.assertNotIn(rows[label]['candidate_id'],approved)

    def test_varieties_degree_scope_holds_are_not_silently_repaired(self):
        from scripts.phase2_authoritative import load_approved
        approved=load_approved()
        rows={r['source_label']:r for r in map(json.loads,(BASE/'varieties_b/RECONSTRUCTIONS.jsonl').read_text().splitlines())}
        for label in ['lemma-divisible','lemma-intersection-numbers-and-degrees-on-curves']:
            self.assertEqual(rows[label]['decision'],'context_resolution_pending')
            self.assertNotIn(rows[label]['candidate_id'],approved)

    def test_varieties_coverage_includes_zero_active_sections(self):
        coverage=json.loads((BASE/'VARIETIES_COVERAGE.json').read_text())
        self.assertEqual(coverage['active_canonical_candidates'],237)
        self.assertEqual(coverage['complete_source_sections'],48)
        self.assertEqual(sum(s['active_candidate_count'] for s in coverage['sections']),237)
        self.assertTrue(coverage['all_active_ids_equal_registered_drafts'])
        self.assertEqual(coverage['provisional_duplicate_candidate_ids'],[])
        self.assertEqual(sum(b['candidates'] for b in coverage['internal_batches']),237)
        for left,right in zip(coverage['sections'],coverage['sections'][1:]):
            self.assertEqual(left['section_end_line']+1,right['section_start_line'])

if __name__=='__main__':
    unittest.main()
