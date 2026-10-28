# mathThm — mathematical theorems and proven results

**Current status (2026-10-23): the 20-result theorem prototype, search interface, proof links, mathDef snapshot consumer and GitHub Actions workflow are implemented.** Automated prototype build/tests passed; the consumer has now been upgraded to mathDef's canonical v2 merged snapshot. **GitHub Pages is enabled and deployed successfully**, with the initial live URL at https://zengez.github.io/mathThm/ . See [PROTOTYPE_IMPLEMENTATION.md](PROTOTYPE_IMPLEMENTATION.md) for testing and current limitations. Mathematical statements/proofs are NOT rigorously verified.

mathThm is a companion to [mathDef](https://github.com/Zengez/mathDef). Its goal is a searchable, source-attributed collection of mathematical results, with separate searches for hypotheses and conclusions and contextual, expandable definitions provided by mathDef.

## Read these before doing any work

1. **[PROJECT_PLAN.md](PROJECT_PLAN.md)** — authoritative consolidated design, requirements, phased workflow, acceptance criteria, and decisions from the October 23, 2026 discussions. Read this first.
2. **[WORK_CHECKPOINT.md](WORK_CHECKPOINT.md)** — current implementation state, next authorized action, and restart instructions. Update it whenever work begins, pauses, or completes a major stage.
3. **[PROTOTYPE_IMPLEMENTATION.md](PROTOTYPE_IMPLEMENTATION.md)** — what has actually been built, what passed, manual GitHub Pages setup, and remaining limitations.
4. **[FUTURE_FEATURES.md](FUTURE_FEATURES.md)** — explicitly postponed ideas, with particular care not to mistake these for prototype requirements.

## Coordination with mathDef

mathDef is the canonical owner of mathematical definitions, term aliases, and definition content. mathThm should consume mathDef's versioned public definition snapshot; it should never autonomously insert terms into mathDef.

**Updated October 28, 2026:** mathThm consumes mathDef's published **complete cleaned v2** feed, including its independent-research additions, canonical meanings, alternate formulations, official Subjects and historical ID redirects. It verifies the v2 content-hash manifest and refreshes the bundled definitions during every main-branch Pages build and nightly schedule. The v1 original-only feed is no longer consumed. See [the mathDef v2 consumer](https://github.com/Zengez/mathDef/blob/main/examples/consume_mathdef_v2.py) and [WORK_CHECKPOINT.md](WORK_CHECKPOINT.md).

The projects are to share a recognizable visual identity, but mathThm will require its own theorem-specific search and display behavior.

## Current implementation / next decision gate

The user subsequently explicitly authorized building the prototype. The present code, dataset, workflow and checks are described in [PROTOTYPE_IMPLEMENTATION.md](PROTOTYPE_IMPLEMENTATION.md). GitHub Pages setup is complete and publication succeeded (workflow run 39978765020); the next step is to review the live interface. Bulk theorem collection and deep proof auditing remain deferred until the user approves proceeding.
