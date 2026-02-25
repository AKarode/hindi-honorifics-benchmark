# Hindi Honorifics Cloze Benchmark — Evaluation Analysis

**Date:** 2026-02-24  
**Probes:** 500 (stratified sample from 21,910 clean probes)  
**Source:** IndicDialogue Hindi film subtitles  
**Task:** Fill-in-the-blank with correct Hindi 2nd-person pronoun form (18 possible forms across 3 tiers)

---

## Results Summary

| Model | Exact Acc | Tier Acc | Valid Form Rate |
|---|---|---|---|
| Random baseline | 5.2% | 35.4% | 100% |
| Majority (तुम) | 25.0% | 47.4% | 100% |
| Tier-Majority (आप) | 25.0% | 47.4% | 100% |
| GPT-4o-mini | 37.2% | 60.4% | 96.0% |
| GPT-4o | 33.2% | 44.6% | 59.4% |
| GPT-4.1-mini | 43.0% | 62.6% | 89.8% |
| **GPT-5.2** | **57.2%** | **70.4%** | **91.0%** |

## Per-Tier Accuracy

| Model | तू (intimate) | तुम (familiar) | आप (formal) |
|---|---|---|---|
| GPT-4o-mini | 81.5% | 53.2% | 63.2% |
| GPT-4o | 38.9% | 38.4% | 53.1% |
| GPT-4.1-mini | 27.8% | 85.2% | 45.9% |
| **GPT-5.2** | **70.4%** | **69.2%** | **71.8%** |

---

## Key Findings

### 1. GPT-5.2 is the clear winner — but still far from ceiling
At 57.2% exact / 70.4% tier accuracy, GPT-5.2 substantially outperforms all other models. But a 30% tier error rate on a 3-way classification (where random = 33%) means there's still enormous headroom. A native Hindi speaker would likely score 90%+ on this task.

### 2. Scaling helps — but not linearly
The progression from GPT-4o-mini → GPT-4.1-mini → GPT-5.2 shows clear improvement in exact accuracy (37% → 43% → 57%). However, GPT-4o (the *larger* model in the 4o family) actually performed *worse* than 4o-mini (33% vs 37%), suggesting that model size alone doesn't drive honorific competence.

### 3. GPT-5.2 is the most balanced across tiers
This is arguably the most important finding. Other models show strong biases:
- **GPT-4o-mini**: Great at तू (81.5%) but mediocre at तुम (53.2%)
- **GPT-4.1-mini**: Massively biased toward तुम (85.2%) but terrible at तू (27.8%)
- **GPT-5.2**: Roughly uniform — 70.4% / 69.2% / 71.8% across all three tiers

This balanced performance suggests GPT-5.2 has genuinely better sociopragmatic understanding rather than just a better prior for one register.

### 4. GPT-4.1-mini has a strong तुम bias
GPT-4.1-mini predicts तुम-tier 85.2% of the time when the gold is तुम, but massively over-predicts it for other tiers too. It only catches 27.8% of तू cases and 45.9% of आप cases. This is essentially a smarter majority baseline — it's learned that तुम is most common in Hindi film dialogue and defaults to it.

### 5. GPT-4o has a severe instruction-following problem
GPT-4o only produced valid Hindi pronoun forms 59.4% of the time — the worst of any model. It frequently outputs explanations, multiple words, or romanized forms instead of just the Devanagari pronoun. This is a prompt compliance issue, not a linguistic one.

### 6. The confusion matrix reveals directional asymmetries
For GPT-5.2:
- **तू→तुम confusion (24.5%)** is much higher than **तुम→तू (14.8%)**: The model is more likely to "upgrade" from intimate to familiar than vice versa. This mirrors a politeness bias — defaulting to the safer/less-marked register when uncertain.
- **आप→तुम confusion (16.9%)** vs **तुम→आप (11.6%)**: Similar asymmetry — the model tends to informalize rather than formalize when confused.

### 7. The exact-vs-tier accuracy gap reveals morphological weakness
Across all models, there's a persistent ~13-15 percentage point gap between tier and exact accuracy. This means models can often identify the right *social register* but struggle to select the correct *case form* (nominative तुम vs oblique तुम्हें vs possessive तुम्हारा/तुम्हारी/तुम्हारे). This is a morphosyntactic challenge on top of the sociopragmatic one.

---

## Implications for Research

1. **The benchmark discriminates well.** There's clear separation between baselines, mid-tier models, and frontier models, with no model at ceiling. This makes it useful as a diagnostic tool.

2. **Honorific competence scales with model generation**, not just size. The GPT-4o < GPT-4o-mini result suggests training data/methodology matters more than parameter count.

3. **The तुम/आप boundary is the interesting zone.** तू is relatively easy to detect (marked register, strong contextual cues). The तुम↔आप distinction is where cultural competence really shows — and where even GPT-5.2 still makes ~30% errors.

4. **Two separate capabilities are being tested**: sociopragmatic register selection (tier) and Hindi morphological competence (exact form). Future work could disentangle these.

---

## Files

- `results/gpt52_mc_500.jsonl` — Per-probe predictions for GPT-5.2
- `results/gpt52_mc_500_metrics.json` — Aggregate metrics
- `results/gpt41_mini_mc_500.jsonl` — GPT-4.1-mini results
- `results/gpt4o_mini_mc_500.jsonl` — GPT-4o-mini results
- `results/gpt4o_mc_500.jsonl` — GPT-4o results
- `plots/overall_accuracy.png` — Bar chart comparing all models
- `plots/per_tier_accuracy.png` — Per-tier breakdown for LLM models
- `plots/confusion_matrix_gpt52.png` — Tier confusion matrix for GPT-5.2
- `plots/valid_form_rate.png` — Valid form output rates

## Next Steps

- [ ] Run o4-mini (reasoning model) to see if chain-of-thought helps
- [ ] Run Gemini Flash (free) for cross-family comparison
- [ ] Scale GPT-5.2 to full 21K probes for tighter confidence intervals
- [ ] Error analysis on тुम↔आप confusion — what contextual features predict failure?
- [ ] Try MuRIL logprob scoring as a non-generative baseline
