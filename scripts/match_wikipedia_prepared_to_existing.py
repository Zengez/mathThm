#!/usr/bin/env python3
"""Fast, conservative overlap scan: prepared Wikipedia statements vs published mathThm.

Use lexical statement, hypothesis and conclusion similarity to propose matches.
Only mechanically exact/near-identical unique pairs can be accepted automatically.
No mathematical equivalence or proof correctness is inferred from a similarity score.
For accepted overlaps, verify the Wikipedia proof-section anchor before adding an
unverified external proof link to the durable overlay. Retain all other candidates.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import json
import math
from pathlib import Path
import re
import unicodedata

from scripts.wiki_obvious_matches import find_section

RUN_DATE = "2026-11-04"
ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "work/wikipedia-stage-a/20261103/reconciled/prepared_statements.jsonl"
CATALOG = ROOT / "data/theorems.json"
PRIOR_LINKS = ROOT / "data/wikipedia_proof_links.json"
OUT = ROOT / "work/wikipedia-existing-match/20261104"

TOKEN_RE = re.compile(r"\\[a-z]+|[a-z]+|\d+|[=<>≤≥≠∈⊆⊂↔→]", re.I)
TRIVIAL = set("""a an the and or is are be to of in on for from by with that this
those these it its at as such then if let assume suppose there where which
every any all some exists has have had can may will does do not theorem
lemma proposition result proof formula claim given follows following
one two three we they this their respectively namely shows shown called
being under over such both each a b x y z n m p q r s t""".split())


def normalize_text(value: str) -> str:
    s = unicodedata.normalize("NFKD", str(value or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\\\\", "\\").replace("–", "-").replace("—", "-")
    for left, right in (
        ("\\left", ""), ("\\right", ""), ("\\displaystyle", ""),
        ("\\textstyle", ""), ("\\mathrm", ""), ("\\operatorname", ""),
        ("\\mathcal", ""), ("\\mathbf", ""), ("\\mathbb", ""),
        ("\\quad", " "), ("\\qquad", " "), ("\\,", " "),
        ("\\;", " "), ("\\!", ""), ("$", " ")):
        s = s.replace(left, right)
    return " ".join(s.split())


def strict_key(value) -> str:
    if isinstance(value, list):
        return " | ".join(strict_key(x) for x in value)
    s = normalize_text(str(value or ""))
    return re.sub(r"\s+", "", re.sub(r"[,.!?;:]+$", "", s))


def terms(value: str) -> Counter:
    t = [x.lower().lstrip("\\") for x in TOKEN_RE.findall(normalize_text(value))]
    t = [x for x in t if x not in TRIVIAL and len(x) > 1 or (x in ("=", "<", ">", "≤", "≥", "≠", "↔", "→"))]
    # Word pairs retain mathematical context. Avoid overly repetitive terms.
    t = t[:320]
    bag = Counter("w:" + x for x in t)
    bag.update("b:" + a + " " + b for a, b in zip(t, t[1:]) if len(a) > 2 or len(b) > 2)
    return bag


def vectorize(candidates: list[dict], existing: list[dict], field: str):
    """TF-IDF normalized sparse bags; index existing docs only."""
    field_text = {
        "hyp": lambda r: " ".join(r.get("hypotheses", [])),
        "con": lambda r: " ".join(r.get("conclusions", [])),
        "stmt": lambda r: r.get("statement", ""),
    }[field]
    docs = [terms(field_text(r)) for r in existing]
    queries = [terms(field_text(r)) for r in candidates]
    df = Counter()
    for bag in docs + queries:
        df.update(bag.keys())
    n = len(docs) + len(queries)
    idf = {t: math.log((n+1)/(freq+1))+1 for t,freq in df.items() if freq <= n*0.32}
    def make_vec(bag):
        d = {t: (1 + math.log(count)) * idf[t] for t,count in bag.items() if t in idf}
        norm = math.sqrt(sum(x*x for x in d.values()))
        return {t: x/norm for t,x in d.items()} if norm else {}
    indexed = defaultdict(list)
    for i, bag in enumerate(docs):
        for t,w in make_vec(bag).items():
            indexed[t].append((i, w))
    similarities = []
    for bag in queries:
        matches = defaultdict(float)
        for t,w in make_vec(bag).items():
            for i,x in indexed.get(t,()):
                matches[i] += w*x
        similarities.append(matches)
    return similarities


def combined_ranking(candidates: list[dict], existing: list[dict]):
    sims = {field: vectorize(candidates, existing, field) for field in ("hyp","con","stmt")}
    data = []
    for i, candidate in enumerate(candidates):
        options = set(sims["hyp"][i]) | set(sims["con"][i]) | set(sims["stmt"][i])
        top = []
        for j in options:
            h=sims["hyp"][i].get(j, 0.)
            c=sims["con"][i].get(j, 0.)
            s=sims["stmt"][i].get(j, 0.)
            # Emphasize the logical result. Generic topic/terminology alone
            # must not dominate and produce a mistaken theorem equivalence.
            score=0.28*h+0.43*c+0.29*s
            if (h<0.1 and c<0.1) or c<0.12:
                continue
            top.append((score,j,h,c,s))
        top.sort(key=lambda x:(-x[0],x[1]))
        data.append(top[:5])
    return data


def decision(candidate, existing, best, nextbest):
    """Return a *mechanical* acceptance, not a semantic equivalence judgment."""
    if not best:
        return False, "no_textual_overlap"
    score,j,h,c,s = best
    e = existing[j]
    c_con, e_con = strict_key(candidate["conclusions"]), strict_key(e["conclusions"])
    c_hyp, e_hyp = strict_key(candidate["hypotheses"]), strict_key(e["hypotheses"])
    c_stmt, e_stmt = strict_key(candidate["statement"]), strict_key(e["statement"])
    second = nextbest[0] if nextbest else 0
    unique = score-second >= 0.10
    # Strong exact-claim evidence, including same logical assumptions.
    if (c_hyp and c_con and c_hyp==e_hyp and c_con==e_con and unique):
        return True,"exact_hypotheses_and_conclusions"
    if (c_stmt and len(c_stmt)>=95 and c_stmt==e_stmt and unique):
        return True,"exact_full_statement"
    # Typographic/LaTeX variations in an otherwise nearly identical claim.
    # All three components and a uniqueness margin are required.
    if h >= .94 and c >= .96 and s >= .96 and unique:
        return True,"near_identical_all_three_texts"
    return False,"requires_mathematical_equivalence_judgment"


def dump_lines(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")


def run(source: Path, catalog: Path, previous: Path, output: Path, no_network=False):
    candidates=[json.loads(s) for s in source.read_text(encoding="utf-8").splitlines() if s.strip()]
    existing=json.loads(catalog.read_text(encoding="utf-8"))["records"]
    overlay=json.loads(previous.read_text(encoding="utf-8"))
    if len(candidates)!=984 or len(existing)<3963 or overlay["schema"]!="maththm.wikipedia-proof-links.v1":
        raise ValueError("Unexpected candidate or published catalog input")
    ids=[c["candidate_id"] for c in candidates]
    if len(set(ids))!=len(ids) or any(c["status"]!="standalone_prepared" for c in candidates):
        raise ValueError("Candidate ID/status inconsistency")
    rankings=combined_ranking(candidates,existing)
    matches=[]; unmatched=[]; suggestions=[]; no_link=[]
    existing_urls={p["source_article"] for links in overlay["links_by_theorem_id"].values() for p in links}
    for i, candidate in enumerate(candidates):
        ranks=rankings[i]
        item={"candidate_id":candidate["candidate_id"],"url":candidate["url"],
              "title":candidate["title"],"status":"not_merged"}
        pairs=[]
        for score,j,h,c,s in ranks:
            theorem=existing[j]
            pairs.append({"theorem_id":theorem["id"],"theorem_title":theorem.get("title"),
                          "score":round(score,4),"hyp_similarity":round(h,4),
                          "con_similarity":round(c,4),"stmt_similarity":round(s,4),
                          "theorem_statement":theorem["statement"][:2000],
                          "theorem_hypotheses":theorem["hypotheses"],
                          "theorem_conclusions":theorem["conclusions"]})
        item["top_match"]=pairs[0] if pairs else None
        item["runner_up_score"]=pairs[1]["score"] if len(pairs)>1 else 0
        accepted, basis=decision(candidate,existing,ranks[0] if ranks else None,
                                 ranks[1] if len(ranks)>1 else None)
        item["decision_basis"]=basis
        if accepted and candidate["url"] in existing_urls:
            accepted=False; item["decision_basis"]="already_linked_article"
        if accepted:
            link,method=(None,"not_checked") if no_network else find_section(candidate["url"],.07)
            if link:
                selected=pairs[0]
                item.update(status="matched_existing",theorem_id=selected["theorem_id"],
                            proof_url=link,proof_section_method=method)
                target=overlay["links_by_theorem_id"].setdefault(selected["theorem_id"],[])
                if not any(l["url"]==link for l in target):
                    target.append({"url":link,"label":"Link to proof (Wikipedia)",
                                   "source_article":candidate["url"],
                                   "match_basis":basis,
                                   "proof_review":"link_only_not_mathematically_audited",
                                   "found_on":RUN_DATE})
                matches.append(item)
            else:
                item["decision_basis"]="unique_text_match_but_no_confirmed_proof_heading"
                no_link.append(item)
        if item["status"]!="matched_existing":
            unmatched.append(candidate)
            if pairs and (pairs[0]["score"]>=.47 or
                (pairs[0]["con_similarity"]>=.67 and
                 pairs[0]["hyp_similarity"]>=.37)):
                suggestions.append({"candidate_id":candidate["candidate_id"],
                                    "title":candidate["title"],"url":candidate["url"],
                                    "statement":candidate["statement"],
                                    "hypotheses":candidate["hypotheses"],
                                    "conclusions":candidate["conclusions"],
                                    "possible_matches":pairs[:3],
                                    "note":"Not an accepted duplicate. Compare only if clear."})
    suggestions.sort(key=lambda r:-r["possible_matches"][0]["score"])
    output.mkdir(parents=True,exist_ok=True)
    dump_lines(output/"matched_existing.jsonl",matches)
    dump_lines(output/"unmatched_prepared.jsonl",unmatched)
    dump_lines(output/"review_shortlist.jsonl",suggestions)
    dump_lines(output/"unlinked_text_matches.jsonl",no_link)
    dump_lines(output/"all_match_decisions.jsonl",matches+[{
        "candidate_id":c["candidate_id"],"url":c["url"],"status":"not_merged"
    } for c in unmatched])
    (output/"unmatched_prepared_urls.txt").write_text(
        "\n".join(c["url"] for c in unmatched)+"\n",encoding="utf-8")
    # Overlay preserves existing Wikipedia links. Site builder reuses by stable theorem ID.
    (output/"wikipedia_proof_links.json").write_text(
        json.dumps(overlay,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    report={"schema":"maththm.wikipedia-existing-overlap.v1",
            "prepared_compared":len(candidates),"published_theorems_compared":len(existing),
            "matched_existing":len(matches),"unmatched_prepared":len(unmatched),
            "candidate_shortlist":len(suggestions),
            "text_matches_missing_proof_anchor":len(no_link),
            "held_untouched":137,"previous_wikipedia_links_preserved":len(existing_urls),
            "new_wikipedia_links":len(matches),
            "scope":"one-pass high precision; uncertain matches remain candidates",
            "proof_validation":"not_performed","mathematical_equivalence_audit":"not_performed"}
    (output/"REPORT.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--catalog",type=Path,default=CATALOG)
    parser.add_argument("--previous",type=Path,default=PRIOR_LINKS)
    parser.add_argument("--output",type=Path,default=OUT)
    parser.add_argument("--no-network",action="store_true")
    args=parser.parse_args()
    run(args.source,args.catalog,args.previous,args.output,args.no_network)


if __name__=="__main__":
    main()
