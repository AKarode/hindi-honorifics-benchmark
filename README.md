# Hindi Second-Person Honorifics Benchmark

**Do LLMs understand Hindi social dynamics?** This benchmark evaluates how well language models handle Hindi's three-tier second-person pronoun system (तू/तुम/आप) — a core sociopragmatic competence required for respectful Hindi conversation.

Hindi has 600M+ speakers. Using तू when you should use आप is genuinely rude. If LLMs are deployed in Hindi conversations (chatbots, translation, creative writing), they need to get direct address right.

## Why This Matters

Mukherjee et al. (EMNLP 2025) showed LLMs mess up Hindi honorifics in third-person reference. We extend this to **second-person conversational usage** — the harder, more socially consequential case. Our benchmark tests both **comprehension** (cloze task) and **production** (generation task).

---

## Results: Cloze Task (Comprehension)

500 pronoun-cloze probes extracted from real Hindi film dialogue (IndicDialogue). Models fill in the masked pronoun from 18 possible forms across 3 tiers.

| Model | Type | Input $/1M | Exact Acc | Tier Acc | Valid Form |
|---|---|---|---|---|---|
| Random baseline | — | — | 5.2% | 35.4% | 100% |
| Majority (तुम) | — | — | 25.0% | 47.4% | 100% |
| Tier-majority (तुम) | — | — | — | 47.4% | 100% |
| GPT-4.1-nano | Standard | $0.10 | 21.0% | 44.0% | 76.2% |
| GPT-4o | Standard | $2.50 | 33.2% | 44.6% | 59.4% |
| GPT-4o-mini | Standard | $0.15 | 37.2% | 60.4% | 96.0% |
| GPT-4.1-mini | Standard | $0.40 | 43.0% | 62.6% | 89.8% |
| GPT-5.2 | Standard | $1.75 | 57.2% | 70.4% | 91.0% |
| GPT-5-nano | Reasoning | $0.05 | 65.4% | 75.2% | 96.8% |
| o4-mini | Reasoning | $1.10 | 71.8% | 81.2% | 99.4% |
| **GPT-5-mini** | **Reasoning** | **$0.25** | **73.6%** | **81.4%** | **100%** |

### Per-Tier Accuracy

| Model | तू (intimate) | तुम (familiar) | आप (formal) |
|---|---|---|---|
| GPT-4.1-nano | 9.3% | 52.7% | 43.1% |
| GPT-4o | 38.9% | 38.4% | 53.1% |
| GPT-4o-mini | 81.5% | 53.2% | 63.2% |
| GPT-4.1-mini | 27.8% | 85.2% | 45.9% |
| GPT-5.2 | 70.4% | 69.2% | 71.8% |
| GPT-5-nano | 64.8% | 81.9% | 70.3% |
| o4-mini | 75.9% | 82.7% | 80.9% |
| **GPT-5-mini** | **68.5%** | **88.6%** | **76.6%** |

---

## Key Findings

1. **Reasoning models dominate — and they're cheaper.** The top 3 models are all reasoning models. GPT-5-mini ($0.25/1M) is both the best AND cheaper than GPT-5.2 ($1.75/1M). Chain-of-thought helps enormously with sociopragmatic judgments.

2. **GPT-5-nano is the cost-performance king.** At $0.05/1M input tokens, it achieves 75.2% tier accuracy — ideal for cost-sensitive India deployment.

3. **Standard models plateau at ~60-70% tier accuracy.** Even GPT-5.2 (most capable standard model) only reaches 70.4%. There's a ceiling without explicit reasoning.

4. **तू (intimate) is the hardest tier.** Even the best model (o4-mini) only reaches 75.9% on तू. This register is rare (~1.2% of corpus) and highly context-dependent.

5. **Models show "politeness bias."** When uncertain, models default UP the formality hierarchy (तू→तुम, तुम→आप). The #1 error for GPT-5-mini is आप→तुम (44% of errors) — informalization in formal contexts.

6. **~80% tier accuracy may be the LLM ceiling** without deeper cultural grounding. Native speakers with film context would likely score 90%+.

For detailed analysis, see [EVAL_ANALYSIS.md](EVAL_ANALYSIS.md) and [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md).

---

## Tasks

### Task 1: Cloze (Comprehension)
Fill-in-the-blank with the correct Hindi 2nd-person pronoun. 500 probes from real film dialogue (IndicDialogue), 18 possible pronoun forms across 3 tiers.

### Task 2: Generation — Discourse Completion Task (Production)
Given a social scenario in Hindi, generate what a character would say. Tests whether models produce appropriate honorific forms in free generation — the harder, more ecologically valid task.

120 scenarios (40 per tier) covering family, professional, social, and institutional relationships with varied age gaps, power dynamics, and emotional contexts. See [GENERATION_TASK_DESIGN.md](GENERATION_TASK_DESIGN.md).

---

## How to Run

### Prerequisites
```bash
pip install aiohttp
export OPENAI_API_KEY=your_key_here
```

### Cloze Evaluation
```bash
# Run with any OpenAI model
python scripts/cloze_eval.py --method mc --backend openai --model gpt-5-mini \
  --probes probes_clean17_ctx5.csv --output results/gpt5_mini_mc.jsonl

# Baselines
python scripts/cloze_eval.py --method baseline-majority --probes probes_clean17_ctx5.csv \
  --output results/baseline_majority.jsonl
python scripts/cloze_eval.py --method baseline-random --probes probes_clean17_ctx5.csv \
  --output results/baseline_random.jsonl
```

### Generation Evaluation (DCT)
```bash
# Run generation eval
python scripts/generation_eval.py --model gpt-5-mini --output results/gen_gpt5_mini.jsonl

# With limits for testing
python scripts/generation_eval.py --model gpt-4o-mini --limit 10 --output results/gen_test.jsonl

# Control concurrency
python scripts/generation_eval.py --model gpt-5.2 --concurrent 3 --output results/gen_gpt52.jsonl
```

### Visualization
```bash
python scripts/plot_results.py
```

---

## File Structure

```
├── README.md                          # This file
├── charter.md                         # Project scope and status
├── GENERATION_TASK_DESIGN.md          # Full generation task design doc
├── EVAL_ANALYSIS.md                   # Detailed cloze evaluation analysis
├── ERROR_ANALYSIS.md                  # Error analysis for GPT-5-mini
├── PROBE.md                           # Probe methodology
├── probes.csv                         # Full probe set (~21K)
├── probes_clean17_ctx5.csv            # Cleaned probes for evaluation
├── scripts/
│   ├── cloze_eval.py                  # Cloze evaluation pipeline
│   ├── generation_eval.py             # Generation (DCT) evaluation pipeline
│   ├── generation_scenarios.json      # 120 DCT scenarios (40 per tier)
│   ├── tier_classifier.py             # Pronoun/tier classification
│   ├── plot_results.py                # Visualization
│   ├── indicdialogue_extract_probes.py # Probe extraction from IndicDialogue
│   └── filter_probes_clean17.py       # Probe filtering/cleaning
├── results/                           # Evaluation results (JSONL + metrics JSON)
├── plots/                             # Generated visualizations
└── modules/                           # Git submodules
    ├── IndicDialogue/                 # Hindi film subtitle dialogues
    ├── hindi-politeness/              # Reference corpus
    └── honorific-wiki-llm/            # Mukherjee et al. dataset
```

---

## References

- Mukherjee, S., Mehta, A., & Saha, S. (2025). Women, Infamous, and Exotic Beings: Honorific Usages in Wikipedia and LLMs for Bengali and Hindi. *EMNLP 2025*.
- Farhansyah, M. R. et al. (2025). Do Language Models Understand Honorific Systems in Javanese? *ACL 2025*.
- Zhao, H. & Hawkins, R. D. (2025). Comparing human and LLM politeness strategies in free production. *EMNLP 2025*.
- Kumar, R. (2014). Politeness in Hindi: A Corpus-Based Study. *LREC 2014*.
- Brown, P. & Levinson, S. (1987). *Politeness: Some universals in language usage*. Cambridge University Press.

---

## Citation

```bibtex
@misc{karode2026hindihonorificsbenchmark,
  title={Hindi Second-Person Honorifics Benchmark: Evaluating LLM Sociopragmatic Competence},
  author={Karode, Adit},
  year={2026},
  url={https://github.com/AKarode/hindi-honorifics-benchmark}
}
```

---

## License

Research use. See individual data sources for their respective licenses.
