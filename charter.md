# Hindi Honorifics Benchmark — Project Charter

Adit Karode | Prof. Malihe Alikhani | Updated Feb 25, 2026

---

## Project Status: Active Development

The project has progressed from exploratory investigation to a **working benchmark with results across 8 models and 3 baselines**. We've confirmed that LLMs exhibit systematic failures in Hindi second-person honorific usage, and reasoning models significantly outperform standard models.

## Research Question

**Do LLMs handle second-person honorifics (तू/तुम/आप) appropriately in conversational Hindi?**

Extending Mukherjee et al. (EMNLP 2025), who showed LLM failures in third-person Hindi honorifics, to the harder and more socially consequential second-person case.

## Why It Matters

Hindi has 600M+ speakers. Honorifics aren't optional — using तू when you should use आप is genuinely rude. As LLMs are deployed in Hindi-speaking contexts (chatbots, translation, creative writing), they must handle direct address correctly.

## Benchmark Design

### Task 1: Cloze (Comprehension) — COMPLETE ✅
- **Data**: 500 pronoun-cloze probes from real Hindi film dialogue (IndicDialogue)
- **Method**: Fill-in-the-blank with correct pronoun (18 forms, 3 tiers)
- **Models evaluated**: GPT-4o, GPT-4o-mini, GPT-4.1-nano, GPT-4.1-mini, GPT-5.2, GPT-5-nano, GPT-5-mini, o4-mini
- **Baselines**: Random, majority, tier-majority
- **Key result**: Reasoning models dominate (GPT-5-mini 81.4% tier accuracy), standard models plateau at ~70%

### Task 2: Generation — Discourse Completion Task (DCT) — BUILT ✅
- **Design**: 120 scenarios (40 per tier) across family, professional, social, institutional contexts
- **Method**: Present social situation in Hindi, model generates dialogue, extract and score pronoun tier
- **Metrics**: Tier accuracy, formality bias ratio, verb agreement, avoidance rate
- **Status**: Pipeline built, scenarios created, ready to run

### Task 3: Multi-Turn Dialogue / Role-Play — PLANNED
- Dialogue continuation and full conversation generation
- Tests consistency, asymmetric honorific management
- See GENERATION_TASK_DESIGN.md for full design

## Completed Work

1. ✅ Probe extraction pipeline from IndicDialogue (~21K probes)
2. ✅ Probe filtering and cleaning (500 stratified sample)
3. ✅ Tier classifier (pronoun + verb agreement patterns)
4. ✅ Cloze evaluation pipeline (MC via API + logprob backends)
5. ✅ Full cloze evaluation across 8 models + 3 baselines
6. ✅ Detailed analysis (EVAL_ANALYSIS.md, ERROR_ANALYSIS.md)
7. ✅ Visualization pipeline (plots/)
8. ✅ Generation task design document
9. ✅ Generation eval pipeline (120 DCT scenarios)

## Key Findings (Cloze Task)

- Reasoning models (GPT-5-mini, o4-mini, GPT-5-nano) dominate at 75-81% tier accuracy
- Standard models plateau at ~60-70% tier accuracy
- GPT-5-nano ($0.05/1M) is the best cost-performance option for India deployment
- Models show "politeness bias" — defaulting up the formality hierarchy when uncertain
- तू (intimate) is the hardest tier; तुम (familiar) is easiest
- ~80% tier accuracy may be the LLM ceiling without cultural grounding

## Data Sources

| Source | Role | Status |
|--------|------|--------|
| IndicDialogue | Primary probe source (real Hindi film subtitles) | ✅ Extraction complete |
| Hindi Politeness Corpus (Kumar 2014) | Reference/validation | Available |
| Mukherjee et al. (EMNLP 2025) | Prior work reference | Reference only |

## Next Steps

- [ ] Run generation eval (DCT) across all models
- [ ] Cross-family comparison (Gemini, Claude, Llama)
- [ ] Scale cloze eval to full 21K probes for GPT-5-mini
- [ ] Error analysis on generation outputs
- [ ] Human annotation subset for generation validation
- [ ] Implement Task B (multi-turn) and Task C (role-play)
- [ ] Write paper for submission

## References

- Mukherjee et al. (EMNLP 2025) — 3rd-person honorific bias
- Farhansyah et al. (ACL 2025) — Javanese honorifics
- Zhao & Hawkins (EMNLP 2025) — LLM politeness strategies
- Kumar (LREC 2014) — Hindi Politeness Corpus
- Brown & Levinson (1987) — Politeness theory

---

## Log

**Feb 25** — Generation eval pipeline built (120 DCT scenarios). README and charter updated.
**Feb 24** — Full cloze evaluation complete across 8 models. Error analysis done.
**Feb 23** — Cloze eval pipeline working. First model runs (GPT-4o-mini, GPT-5-mini).
**Jan 27** — Probe extraction complete. Pivoted to sampling and model runs.
**Jan 26** — Shifted to non-synthetic probing using IndicDialogue; exploratory focus.
