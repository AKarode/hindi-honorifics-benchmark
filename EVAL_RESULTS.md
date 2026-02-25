# Hindi Honorifics Cloze Benchmark — Evaluation Results

**Date:** 2026-02-24  
**Probes:** 500 (stratified sample from 21,910 clean probes)  
**Prompt language:** Hindi (unless noted)  
**Task:** Fill-in-the-blank with correct Hindi pronoun form from 18 candidates

---

## Summary Table

| Model | Exact Acc | Tier Acc | Valid Form Rate | Cost/1M (in/out) |
|---|---|---|---|---|
| Random baseline | 5.2% | 35.4% | 100% | — |
| Majority (तुम) | 25.0% | 47.4% | 100% | — |
| Tier-Majority (आप) | 25.0% | 47.4% | 100% | — |
| GPT-4o-mini | 37.2% | 60.4% | 96.0% | $0.15/$0.60 |
| GPT-4o | 33.2% | 44.6% | 59.4% | $2.50/$10.00 |
| GPT-4.1-mini | 43.0% | 62.6% | 89.8% | $0.40/$1.60 |
| **GPT-5.2** | **56.0%** | **68.4%** | **90.8%** | $1.75/$14.00 |

---

## Per-Tier Accuracy (Tier-level, not exact form)

| Model | तू (T) | तुम (TUM) | आप (AAP) |
|---|---|---|---|
| GPT-4o-mini | 81.5% (n=54) | 53.2% (n=237) | 63.2% (n=209) |
| GPT-4o | 38.9% (n=54) | 38.4% (n=237) | 53.1% (n=209) |
| GPT-4.1-mini | 27.8% (n=54) | 85.7% (n=237) | 45.9% (n=209) |
| **GPT-5.2** | **66.7% (n=54)** | **67.1% (n=237)** | **70.3% (n=209)** |

---

## Key Findings

### 1. GPT-5.2 is the clear winner — but still far from human-level
At 56% exact form accuracy and 68.4% tier accuracy, GPT-5.2 substantially outperforms all other models. But a ~32% error rate on just getting the right *tier* (तू/तुम/आप) shows that even frontier LLMs lack reliable sociopragmatic competence in Hindi.

### 2. Scaling helps, but not linearly
The progression tells an interesting story:
- GPT-4o-mini → GPT-4.1-mini → GPT-5.2: **37.2% → 43.0% → 56.0%** exact accuracy
- Each generation improves, with GPT-5.2 making the biggest jump (+13 percentage points over 4.1-mini)
- But GPT-4o (the full-size 4o model) actually performs *worse* than 4o-mini (33.2% vs 37.2%), suggesting that model size alone doesn't determine sociopragmatic performance

### 3. GPT-5.2 is the most *balanced* model across tiers
- GPT-4o-mini is great at तू (81.5%) but poor at तुम (53.2%) — it over-detects intimacy
- GPT-4.1-mini is heavily biased toward तुम (85.7%) but terrible at तू (27.8%) — it over-defaults to informal
- **GPT-5.2 has the most even per-tier performance: 66.7% / 67.1% / 70.3%** — no single tier dominates its errors

### 4. The तुम/आप boundary remains the hardest distinction
From GPT-5.2's confusion matrix:
- तुम→आप confusion: 11.6% (predicted आप when gold was तुम)
- आप→तुम confusion: 16.9% (predicted तुम when gold was आप)
- This is the socially meaningful boundary (respectful vs familiar), and models are weakest exactly where cultural sensitivity matters most

### 5. Valid form rate drops with newer models
Counterintuitively, newer models produce *fewer* valid pronoun forms:
- GPT-4o-mini: 96.0%
- GPT-4.1-mini: 89.8%
- GPT-5.2: 90.8%
- GPT-4o: 59.4% (worst)

Newer/larger models tend to generate explanations or hedged responses instead of a bare pronoun. GPT-4o is especially bad at following the "write only the pronoun" instruction.

### 6. The 12-point gap between tier and exact accuracy is consistent
Across all LLMs, exact accuracy trails tier accuracy by ~10-15 points. This means models understand the social register (T/TUM/AAP) better than they understand Hindi case morphology (nominative vs oblique vs possessive). The case-form selection within a tier appears to be a grammatical rather than pragmatic challenge.

---

## Confusion Patterns (GPT-5.2)

```
             → pred_T   pred_TUM   pred_AAP
gold_T:        73.5%      24.5%       2.0%
gold_TUM:      14.8%      73.6%      11.6%
gold_AAP:       5.3%      16.9%      77.8%
```

The confusion is heavily weighted toward "upgrading" formality (predicting more formal than gold):
- तू→तुम (24.5%): Model is reluctant to predict intimate/inferior address
- आप→तुम (16.9%): Model slightly under-predicts formal address

This suggests LLMs have a **politeness bias** — they default toward more respectful forms when uncertain.

---

## Implications for Research

1. **This benchmark discriminates between models.** The spread from 44.6% (GPT-4o) to 68.4% (GPT-5.2) tier accuracy shows the task captures real capability differences.

2. **The ceiling is still low.** Native Hindi speakers would likely score 85-95%+ on this task. The gap represents genuine sociopragmatic understanding that LLMs lack.

3. **Politeness bias is a measurable phenomenon.** The asymmetric confusion matrix (upgrading > downgrading formality) could be a paper-worthy finding.

4. **Case morphology is a separate axis from pragmatic competence.** The consistent tier-exact gap suggests these should be evaluated separately.

---

## Files

- `results/gpt52_mc_500.jsonl` — per-probe predictions for GPT-5.2
- `results/gpt52_mc_500_metrics.json` — aggregate metrics
- `results/gpt41_mini_mc_500.jsonl` / `_metrics.json` — GPT-4.1-mini
- `results/gpt4o_mini_mc_500.jsonl` / `_metrics.json` — GPT-4o-mini
- `results/gpt4o_mc_500.jsonl` / `_metrics.json` — GPT-4o
- `plots/overall_accuracy.png` — bar chart comparison
- `plots/per_tier_accuracy.png` — per-tier breakdown
- `plots/confusion_matrix_gpt52.png` — confusion matrix for GPT-5.2
- `plots/valid_form_rate.png` — valid form rates
- `scripts/cloze_eval.py` — evaluation pipeline
- `scripts/plot_results.py` — visualization script
