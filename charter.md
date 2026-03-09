# Hindi Honorifics Benchmark — Project Charter

Adit Karode | Prof. Malihe Alikhani | Updated Mar 9, 2026

---

## Project Status: Active Development

The project has a **fully corpus-grounded evaluation pipeline with two tasks**. All data is derived from real Hindi film dialogue (IndicDialogue) — no synthetic scenarios. Evaluation samples are ready; model runs are pending.

## Research Question

**Do LLMs handle second-person honorifics (तू/तुम/आप) appropriately in conversational Hindi?**

Extending Mukherjee et al. (EMNLP 2025), who showed LLM failures in third-person Hindi honorifics, to the harder and more socially consequential second-person case.

## Why It Matters

Hindi has 600M+ speakers. Honorifics aren't optional — using तू when you should use आप is genuinely rude. As LLMs are deployed in Hindi-speaking contexts (chatbots, translation, creative writing), they must handle direct address correctly.

## Benchmark Design

### Task 1: Cloze (Comprehension) — PIPELINE READY
- **Data**: 500 pronoun-cloze probes from real Hindi film dialogue (IndicDialogue), stratified by tier (167 T / 167 TUM / 166 AAP) and proportional by movie across all 17 films
- **Method**: Fill-in-the-blank with correct pronoun (18 forms, 3 tiers)
- **Baselines**: Random, majority, tier-majority
- **Status**: Pipeline and sample ready, model runs pending

### Task 2: Generation — Dialogue Continuation — PIPELINE READY
- **Data**: 200 probes from IndicDialogue, filtered to single-tier contexts (no speaker-switch ambiguity), stratified by tier (67 T / 67 TUM / 66 AAP) across 17 movies
- **Method**: Present real dialogue context, model generates the next line, extract and score pronoun tier
- **Metrics**: Tier accuracy, formality bias ratio, verb agreement, avoidance rate
- **Status**: Pipeline and sample ready, model runs pending

## Completed Work

1. Probe extraction pipeline from IndicDialogue (~21K raw probes)
2. Probe filtering to 17 high-quality Hindi-original films (4,382 probes)
3. Deduplication on (masked_line, gold_pronoun) — 4,271 unique probes
4. Stratified sampling for cloze task (balanced tier + proportional movie)
5. Filtered sampling for generation task (single-tier contexts, >= 15 char gold lines)
6. Tier classifier (pronoun detection + verb agreement patterns)
7. Cloze evaluation pipeline (MC via API + logprob backends + 3 baselines)
8. Visualization pipeline (plots/)
9. Generation eval pipeline (corpus-grounded dialogue continuation)

## Data Sources

| Source | Role | Status |
|--------|------|--------|
| IndicDialogue | Primary probe source (real Hindi film subtitles) | Extraction complete |
| Hindi Politeness Corpus (Kumar 2014) | Reference/validation | Available |
| Mukherjee et al. (EMNLP 2025) | Prior work reference | Reference only |

## Known Limitations

- **No speaker diarization**: IndicDialogue subtitles lack speaker labels. Mitigated in generation by filtering to single-register contexts.
- **No human validation**: Gold labels come directly from subtitle text. No human annotator verification of probe quality.
- **TUM_VERB regex**: The verb pattern in `tier_classifier.py` for TUM-tier matches any ो-ending word, producing false positives.

## Next Steps

- [ ] Run cloze evaluation across models (`probes_stratified_500.csv`)
- [ ] Run generation evaluation across models (`probes_generation_200.csv`)
- [ ] Cross-family comparison (Gemini, Claude, Llama via free APIs)
- [ ] Fix TUM_VERB regex false positives in tier_classifier.py
- [ ] Error analysis on outputs
- [ ] Write paper for submission

## References

- Mukherjee et al. (EMNLP 2025) — 3rd-person honorific bias
- Farhansyah et al. (ACL 2025) — Javanese honorifics
- Zhao & Hawkins (EMNLP 2025) — LLM politeness strategies
- Kumar (LREC 2014) — Hindi Politeness Corpus
- Brown & Levinson (1987) — Politeness theory

---

## Log

**Mar 9** — Replaced synthetic DCT generation task with corpus-grounded dialogue continuation. Filtered to single-tier contexts to address speaker diarization gap. Cleaned all repo documentation. Removed stale analysis docs based on invalid sample.
**Mar 8** — Fixed stratified sampling (old sample was first 500 rows = 2 movies). Deduplicated full probe set (111 duplicates removed). Researched generation task alternatives.
**Feb 25** — Generation eval pipeline built (initial DCT approach, later replaced).
**Feb 24** — Cloze eval pipeline complete. Initial model runs on non-stratified sample.
**Feb 23** — Cloze eval pipeline working. First model runs.
**Jan 27** — Probe extraction complete. Pivoted to sampling and model runs.
**Jan 26** — Shifted to non-synthetic probing using IndicDialogue; exploratory focus.
