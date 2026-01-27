# Hindi Honorifics — Exploratory Study

Investigating whether LLMs handle Hindi second-person honorifics (तू/तुम/आप) appropriately in conversational contexts.

**Status**: Exploratory phase — discovering if a problem exists before building any benchmark.

## What's here

| File | Purpose |
|------|---------|
| `charter.md` | Project scope, current progress, next steps |
| `PROBE.MD` | Detailed methodology and research context |
| `probes.csv` | Extracted pronoun-cloze probes from real dialogue |
| `scripts/indicdialogue_extract_probes.py` | Probe extraction pipeline |

## Current Progress

- **Done**: Probe extraction from IndicDialogue subtitles (~100K+ probes with context windows)
- **Next**: Sample, validate, run on models, analyze for failure patterns

## Data

All probes derived from **non-synthetic** sources (IndicDialogue movie subtitles). No invented scenarios.

## Submodules

- `modules/IndicDialogue/` — subtitle dialogues (primary source)
- `modules/hindi-politeness/` — reference corpus
- `modules/honorific-wiki-llm/` — Mukherjee Dataset