"""Offline tests for Wikipedia Stage A catalog matching. No mathematical audit."""
import unittest
from scripts.match_wikipedia_prepared_to_existing import (
    decision, combined_ranking, normalize_text, strict_key, terms,
)


def t(id, statement, hypotheses, conclusions):
    return {"id":id,"title":id,"statement":statement,"hypotheses":hypotheses,"conclusions":conclusions}


class WikipediaMatchTests(unittest.TestCase):
    def test_exact_split_is_unique(self):
        c=t("wiki", "Assume X is compact. Then every cover admits a finite subcover.",
             ["X is compact"],["Every cover admits a finite subcover."])
        e=t("thm", c["statement"],c["hypotheses"],c["conclusions"])
        self.assertTrue(decision(c,[e],(1,0,1,1,1),None)[0])

    def test_changed_hypothesis_not_automatic(self):
        c=t("wiki", "Every finite group has a representation.",["G is finite group"],["G has representation"])
        e=t("thm", c["statement"],["G is an infinite group"],c["conclusions"])
        self.assertFalse(decision(c,[e],(.6,0,.25,1,.8),None)[0])

    def test_ambiguous_duplicates_not_automerge(self):
        c=t("wiki","Every finite graph has finitely many vertices",
             ["G is a finite graph"],["G has finite vertex set"])
        e=t("thm",c["statement"],c["hypotheses"],c["conclusions"])
        self.assertFalse(decision(c,[e,e],(1,0,1,1,1),(.99,1,1,1,1))[0])

    def test_vector_ranking_with_distinct_formulations(self):
        candidates=[t("wiki","Let G be a finite abelian group. Then G decomposes as a product of cyclic groups.",
                      ["G is a finite abelian group"],["G decomposes as a product of cyclic groups"])]
        existing=[t("yes",candidates[0]["statement"],candidates[0]["hypotheses"],candidates[0]["conclusions"]),
                  t("no","Every topological space admits a neighborhood basis.",
                    ["X is a topological space"],["X admits a neighborhood basis"])]
        ranks=combined_ranking(candidates,existing)[0]
        self.assertEqual(ranks[0][1],0)
        self.assertGreater(ranks[0][0], .95)

    def test_strict_math_key(self):
        self.assertEqual(strict_key(["$A$ is compact."]),strict_key(["A  is compact"]))
        self.assertNotEqual(strict_key(["A is compact"]),strict_key(["A is not compact"]))


if __name__=="__main__":
    unittest.main()
