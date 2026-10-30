"""Pinned Stacks same-source label indexing for tested Pass 2 parsers.

Historical report-generation CLI removed; keep only shared primitives.
"""
import re

BATCHES=("stacks-bulk-2026-10-28","stacks-second-2026-10-28","stacks-remaining-2026-10-28")
LABEL=re.compile(r"\\label\{([^}]+)\}")

def get_index(root,files):
    index={}
    for filename in files:
        path=root/filename
        if not path.exists():continue
        s=path.read_text(encoding="utf-8")
        # A bounded grammar only reads statement environments; no proof
        # environment is selected or returned.
        pat=re.compile(r"\\begin\{(situation|notation|setup|lemma|definition|remark|construction|convention|theorem|proposition|corollary)\}(?:\[[^\]\n]*\])?([\s\S]*?)\\end\{\1\}",re.I)
        for m in pat.finditer(s):
            inside=m.group(2)
            k=LABEL.search(inside[:350])
            if not k:continue
            label=k.group(1)
            index[(filename,label)]={"kind":m.group(1),"text":LABEL.sub("",inside).strip(),
                                     "file":filename,"line":s.count("\n",0,m.start())+1}
    return index

