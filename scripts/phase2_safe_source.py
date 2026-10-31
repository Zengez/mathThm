"""Conservative, line-preserving Stacks source view for proof-free Phase 2 review.

Never present raw Stacks chapter slices to a Stage B reviewer. This viewer
only exposes explicitly delimited statement/context environments. Everything
else, including remarks and informal proof discussion outside formal proof
environments, is hidden. If necessary context is hidden, HOLD rather than infer.
This module does not perform Phase 3 proof screening.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

# Restrict source-first review to mathematical statement/context declarations.
STATEMENT_ENVS = frozenset({
    "theorem", "lemma", "proposition", "corollary", "definition",
    "assumption", "hypothesis", "notation", "convention",
    "axiom",
})
# Situations may mix setup with explanatory arguments (dualizing incident,
# 2026-10-31). Keep the whole environment hidden, even when context is needed.
# Formatting and enumerations *inside* a permitted statement.
NESTED_ENVS = frozenset({
    "enumerate", "itemize", "description", "reference", "equation",
    "equation*", "align", "align*", "gather", "gather*",
    "multline", "multline*", "displaymath", "array", "cases",
    "matrix", "pmatrix", "bmatrix", "CD", "tikzcd", "tikzpicture",
})
TOKEN = re.compile(r"\\(begin|end)\{([A-Za-z*]+)\}")


class UnsafeSourceView(ValueError):
    """A malformed environment boundary prevents safe rendering."""


def _without_comments(line: str) -> str:
    """Remove unescaped TeX comments, including their contents."""
    for index, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        j = index - 1
        while j >= 0 and line[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return line[:index] + ("\n" if line.endswith("\n") else "")
    return line


def mask_source(source: str) -> str:
    """Return a source view preserving lines, with unsafe material blanked.

    Only top-level approved mathematical environments and whitelisted nested
    types are visible. A remark, proof, or any unknown nested environment is
    hidden. This is intentionally stricter than omitting \\begin{proof}.
    """
    stack: list[str] = []
    lines: list[str] = []

    def effective(state: list[str]) -> list[str]:
        # Stacks .tex chapters have a document wrapper around every theorem.
        # This wrapper is inert: it does NOT make outside prose visible.
        return state[1:] if state and state[0] == "document" else state

    def permitted(state: list[str]) -> bool:
        scope = effective(state)
        return bool(scope) and scope[0] in STATEMENT_ENVS and all(
            item in NESTED_ENVS or item in STATEMENT_ENVS
            for item in scope[1:]
        )

    def neutral(state: list[str]) -> bool:
        return not effective(state)

    for number, raw in enumerate(source.splitlines(keepends=True), start=1):
        code = _without_comments(raw)
        tokens = list(TOKEN.finditer(code))
        before = stack.copy()
        after = stack.copy()
        for tok in tokens:
            op, env = tok.groups()
            if op == "begin":
                after.append(env)
            elif not after or after[-1] != env:
                raise UnsafeSourceView(
                    f"Unmatched environment at source line {number}: {env}"
                )
            else:
                after.pop()

        # A transition through any disallowed environment masks the whole
        # line, even if it starts/ends in an approved statement.
        intermediate = before.copy()
        states = [intermediate.copy()]
        for tok in tokens:
            op, env = tok.groups()
            if op == "begin":
                intermediate.append(env)
            else:
                intermediate.pop()
            states.append(intermediate.copy())
        allowed = (permitted(before) or permitted(after)) and all(
            neutral(state) or permitted(state) for state in states
        )
        # Avoid leaking prose before a statement opens or after it closes.
        if allowed and tokens and neutral(before):
            allowed = not code[:tokens[0].start()].strip()
        if allowed and tokens and neutral(after):
            allowed = not code[tokens[-1].end():].strip()
        if re.search(r"\\(?:input|include)\s*\{", code):
            allowed = False
        lines.append(code if allowed else ("\n" if raw.endswith("\n") else ""))
        stack = after

    if stack:
        raise UnsafeSourceView("Unclosed source environment: " + stack[-1])
    return "".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_file", type=Path)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=None)
    args = parser.parse_args()
    if args.start < 1 or (args.end is not None and args.end < args.start):
        parser.error("Invalid source line interval")
    visible = mask_source(args.source_file.read_text(encoding="utf-8"))
    lines = visible.splitlines(keepends=True)
    print("".join(lines[args.start - 1:args.end]), end="")


if __name__ == "__main__":
    main()
