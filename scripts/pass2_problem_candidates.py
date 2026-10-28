"""Backward-compatible entry point for the unified deferred problem-candidate registry.

Both inherited-context and structural Pass 2 difficulties are grouped together.
Run `python -m scripts.pass2_problem_candidates` after each Pass 2 continuation.
"""
from scripts.pass2_problem_candidates_unified import main

if __name__ == "__main__":
    main()
