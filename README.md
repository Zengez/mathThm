# mathThm — mathematical theorems and proven results

**Status (2026-10-23): planning documentation only.** No prototype, theorem collection, scripts, deployment, or user interface has been implemented in this repository. Do not treat any design document as evidence that features have been built.

mathThm is a companion to [mathDef](https://github.com/Zengez/mathDef). Its goal is a searchable, source-attributed collection of mathematical results, with separate searches for hypotheses and conclusions and contextual, expandable definitions provided by mathDef.

## Read these before doing any work

1. **[PROJECT_PLAN.md](PROJECT_PLAN.md)** — authoritative consolidated design, requirements, phased workflow, acceptance criteria, and decisions from the October 23, 2026 discussions. Read this first.
2. **[WORK_CHECKPOINT.md](WORK_CHECKPOINT.md)** — current implementation state, next authorized action, and restart instructions. Update it whenever work begins, pauses, or completes a major stage.
3. **[FUTURE_FEATURES.md](FUTURE_FEATURES.md)** — explicitly postponed ideas, with particular care not to mistake these for prototype requirements.

## Coordination with mathDef

mathDef is the canonical owner of mathematical definitions, term aliases, and definition content. mathThm should consume mathDef's versioned public definition snapshot; it should never autonomously insert terms into mathDef.

As of October 23, 2026, mathDef has committed the production export implementation and GitHub's publication and audit workflows passed. See [mathDef's export documentation](https://github.com/Zengez/mathDef/blob/main/DEFINITION_EXPORT.md). Independent mathDef Wave 2 research remains separately managed; the production feed does **not** silently include it.

The projects are to share a recognizable visual identity, but mathThm will require its own theorem-specific search and display behavior.

## Immediate constraint

The user explicitly requested **documentation only** at this stage. No theorem ingestion, implementation, prototype creation, or changes to mathDef are authorized by this documentation request. When explicitly instructed to begin, follow the sequence and guardrails in PROJECT_PLAN.md.
