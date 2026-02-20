# Hindi Honorifics — Exploratory Study

Investigating whether LLMs handle Hindi second-person honorifics (तू/तुम/आप) appropriately in conversational contexts.

**Status**: Exploratory phase — validating if Mukherjee's findings on 3rd person are applicative to 2nd person. 

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


1. General sentence motivation of the problem, what tghe problem is how im stufdying at and these are the results i got. generation problem, bias problem, context problem. better at processing the context. make sure it has a timeline. find a venue to submit for. 
