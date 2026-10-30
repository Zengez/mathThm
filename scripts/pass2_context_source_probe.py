"""Pinned Stacks same-source label indexing for tested Pass 2 parsers.

Historical report-generation CLI removed; keep only shared primitives.
"""
import re
from bisect import bisect_right

BATCHES=("stacks-bulk-2026-10-28","stacks-second-2026-10-28","stacks-remaining-2026-10-28")
LABEL=re.compile(r"\\label\{([^}]+)\}")
SOURCE_STATEMENTS = re.compile(
    r"\\begin\{(situation|notation|setup|lemma|definition|remark|construction|convention|theorem|proposition|corollary)\}"
    r"(?:\[[^\]\n]*\])?([\s\S]*?)\\end\{\1\}", re.I
)

def get_index(root,files):
    index={}
    for filename in files:
        path=root/filename
        if not path.exists():continue
        s=path.read_text(encoding="utf-8")
        # One newline scan per file: avoid repeatedly recounting the prefix
        # of a potentially large source for every matched environment.
        newlines = [match.start() for match in re.finditer("\\n", s)]
        for m in SOURCE_STATEMENTS.finditer(s):
            inside=m.group(2)
            k=LABEL.search(inside[:350])
            if not k:continue
            label=k.group(1)
            index[(filename,label)]={"kind":m.group(1),"text":LABEL.sub("",inside).strip(),
                                     "file":filename,"line":bisect_right(newlines, m.start()) + 1}
    return index

