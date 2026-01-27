# Hindi Honorifics — Exploratory Study

Adit | Prof. Malihe Alikhani | Updated Jan 27, 2026

---

## Project Status: Exploratory Phase

We are **discovering whether a problem exists** before building anything. No benchmark, no metrics, no claims yet.

## What's the question?

Mukherjee et al. (EMNLP 2025) showed LLMs mess up Hindi honorifics in **third-person reference** (formal Wikipedia contexts). They noted: *"honorific dynamics can differ substantially in second-person usage and more casual or spoken communication."*

We're investigating that gap: **Do LLMs handle second-person honorifics (तू/तुम/आप) appropriately in conversational contexts?**

Why it matters: Hindi has 600M+ speakers. Honorifics aren't optional—using तू when you should use आप is genuinely rude. If LLMs are deployed in Hindi conversations, they need to get direct address right.

## What we're looking for

Failure modes (if they exist):
- Over-formality (always आप) or over-informality
- Inconsistency across runs
- Pronoun–verb agreement mismatches (आप with तुम verb forms)
- Avoidance (rephrasing to dodge direct address)
- Bias patterns in pronoun choice

## Current Progress

### Done
- **Probe extraction pipeline**: `scripts/indicdialogue_extract_probes.py` extracts pronoun-cloze probes from IndicDialogue Hindi subtitles
- **Probe dataset**: `probes.csv` — large set of real dialogue lines with masked pronouns, context windows, and gold labels
- **Data validation**: Devanagari filtering, context requirements, multiple pronoun forms (18 forms including oblique cases)

### In Progress
- Sampling strategy for manageable probe set
- Verb agreement tracking (not yet in extraction)

### Not Started
- Running probes on models (GPT-5.2, Claude Opus 4.5, Claude Sonnet 4, Gemini 2.5 Pro)
- Pattern analysis
- Any benchmark or metric work

## Data Sources

| Source | Role | Status |
|--------|------|--------|
| IndicDialogue | Primary probe source (real subtitles) | Extraction complete |
| Hindi Politeness Corpus | Validation/triangulation only | Available |
| Wiki-LLM (Mukherjee) | Prior work reference | Not used for probes |

## Probe Types (from real data only)

1. **Pronoun cloze**: Mask the pronoun, model fills blank given context. Gold = original.
2. **Contextual paraphrase**: Same context, model paraphrases. Compare pronoun/verb choice.
3. **Lexical-cue labeling**: Only lines with explicit relationship markers (sir/जी/maa/papa).

## Constraints

- **Non-synthetic only**: All probes derived from real dialogue, no invented scenarios
- **Devanagari only**: English/romanized lines filtered out
- **Context required**: Isolated utterances dropped

## Limitations

- Subtitles lack speaker/relationship metadata
- Context windows are short (1-2 lines)
- No verb form tracking yet
- Hindi only

## What comes next (in order)

1. Sample probe set for manual validation
2. Add verb agreement extraction to pipeline
3. Run probes on target models
4. Analyze outputs for failure patterns
5. **Then decide**: Is there a problem worth a benchmark?

## Open questions

- What sampling strategy gives representative coverage?
- How to handle ambiguous contexts where multiple pronouns are acceptable?
- Minimum probe count for reliable pattern detection?

## References

- Mukherjee et al. (EMNLP 2025) — third-person honorific bias
- Kumar (LREC 2014) — Hindi Politeness Corpus
- Farhansyah et al. (ACL 2025) — Javanese honorifics

---

## Log

**Jan 27** — Probe extraction complete (`probes.csv`). Pivoting to sampling and model runs.

**Jan 26** — Shifted to non-synthetic probing using IndicDialogue; exploratory focus.
