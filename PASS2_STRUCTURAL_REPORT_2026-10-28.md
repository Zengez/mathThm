# Second Pass 2 structural attempt — October 28, 2026

The user requested another *light* Pass 2 effort specifically on the **1,231** candidates classified as `needs_structure` across two Stacks Project batches, and asked to flag candidates needing substantial reasoning for a later higher-thinking Pass 2. No new Pass 1 candidates, inherited-context items, Pass 3 proofs, or published catalog records are included.

## Outcomes

| Classification | First batch | Second batch | Total |
| --- | ---: | ---: | ---: |
| Previously `needs_structure` | 408 | 823 | **1,231** |
| Additional explicit structural splits recorded | 113 | 291 | **404** |
| Held for higher-thinking Pass 2 | 295 | 532 | **827** |
| Previously resolved Pass 2 (all methods) | 587 | 987 | 1,574 |
| Now resolved Pass 2 (all methods) | 700 | 1,278 | **1,978** |
| Still `needs_context` (unchanged) | 105 | 212 | **317** |
| Total needing more Pass 2 work | 400 | 744 | **1,144** |
| Pass 3 | 0 | 0 | **0** |

**Important:** These 404 additional splits are **mechanical, source-faithful, explicitly tagged `structural_syntax_only`**. They preserve the wording of the original source and are *not* equivalent to an editorial mathematical interpretation. A later review should especially scrutinize nested conclusions and apparent bidirectional claims. Cases demanding a semantic determination remain queued.

The new `scripts/pass2_structural_light.py` tries to identify clear top-level *then* boundaries even in statements containing LaTeX lists and diagrams. It also recognizes limited conclusion enumerations and subsequent assertions after introductory hypotheses. It deliberately defers unbounded local notation, ambiguous equivalences, nested or internally conflicting lists, and anything without a clear boundary. No proof text is consulted.

Every one of the **827** deferred records is saved in its respective `harvest/batches/<batch>/pass2_higher_thinking.jsonl` with the full preserved statement, candidate ID, original source URL, and a reason. There are still **317** unrelated `needs_context` records in the preexisting investigation queue; these were intentionally not processed in this request.

**Run and validation:** [GitHub Actions 40726195072](https://github.com/Zengez/mathThm/actions/runs/40726195072) succeeded, including the Python regression suite and separate persisted outputs. The original 1,231 targets partition exactly into 404 splits and 827 deferred cases.

**Next:** A genuine higher-thinking Pass 2 interpretation of the 827 queued entries, in bounded batches. The 404 syntax-split records remain provisional and can be audited independently. Pass 3 and any public theorem publication remain on hold.
