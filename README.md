# Hindi Second-Person Honorifics Benchmark

**Do LLMs understand Hindi social dynamics?** This benchmark evaluates how well language models handle Hindi's three-tier second-person pronoun system (तू/तुम/आप) — a core sociopragmatic competence required for respectful Hindi conversation.

Hindi has 600M+ speakers. Using तू when you should use आप is genuinely rude. If LLMs are deployed in Hindi conversations (chatbots, translation, creative writing), they need to get direct address right.

## Why This Matters

Mukherjee et al. (EMNLP 2025) showed LLMs mess up Hindi honorifics in third-person reference. We extend this to **second-person conversational usage** — the harder, more socially consequential case. Our benchmark tests both **comprehension** (cloze task) and **production** (generation task) using only real dialogue data.

---

## Data

All evaluation data is derived from **IndicDialogue** — a corpus of real Hindi film subtitles. No synthetic scenarios or researcher-authored stimuli are used.

**Pipeline:**
1. Extract pronoun-cloze probes from 17 high-quality Hindi-original films (`indicdialogue_extract_probes.py` → `filter_probes_clean17.py`)
2. Deduplicate on (masked_line, gold_pronoun) — 4,382 → 4,271 unique probes
3. Stratified sampling balanced by tier (T/TUM/AAP) and proportional by movie (`sample_stratified.py`, `sample_generation.py`)

**Known limitation:** IndicDialogue lacks speaker diarization. For the generation task, we mitigate this by restricting to single-register contexts (where only one honorific tier appears in the dialogue context).

---

## Tasks

### Task 1: Cloze (Comprehension)
Fill-in-the-blank with the correct Hindi 2nd-person pronoun. 500 probes stratified by tier (167 T / 167 TUM / 166 AAP) and proportional by movie across all 17 films. 18 possible pronoun forms across 3 tiers.

- **Data source**: IndicDialogue film subtitles (non-synthetic)
- **Sample**: `probes_stratified_500.csv` (from `sample_stratified.py`)

### Task 2: Generation — Dialogue Continuation (Production)
Given real film dialogue context, generate the next line. Tests whether models produce appropriate honorific forms in free generation — the harder, more ecologically valid task.

- **Data source**: IndicDialogue film subtitles (non-synthetic)
- **Sample**: `probes_generation_200.csv` (from `sample_generation.py`)
- **Filtering**: Only probes where context contains a single honorific tier (no speaker-switch ambiguity) and gold line is substantial (>= 15 chars)
- **Sample size**: 200 probes (67 T / 67 TUM / 66 AAP), all 17 movies

| | Cloze Task | Generation Task |
|---|---|---|
| Input | Context + masked line | Context only |
| Model does | Selects a pronoun | Generates free-form dialogue |
| Gold | The exact pronoun | The tier of the original line |
| Tests | Recognition/selection | Production/pragmatic inference |
| Data source | IndicDialogue (real) | IndicDialogue (real) |

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
  --probes probes_stratified_500.csv --output results/gpt5_mini_mc.jsonl

# Baselines
python scripts/cloze_eval.py --method baseline-majority --probes probes_stratified_500.csv \
  --output results/baseline_majority.jsonl
python scripts/cloze_eval.py --method baseline-random --probes probes_stratified_500.csv \
  --output results/baseline_random.jsonl
```

### Generation Evaluation (Dialogue Continuation)
```bash
# Run generation eval
python scripts/generation_eval.py --model gpt-5-mini \
  --probes probes_generation_200.csv --output results/gen_gpt5_mini.jsonl

# With limits for testing
python scripts/generation_eval.py --model gpt-4o-mini \
  --probes probes_generation_200.csv --limit 10 --output results/gen_test.jsonl
```

### Sampling (regenerate samples)
```bash
# Cloze sample: 500 probes, stratified by tier and movie
python scripts/sample_stratified.py --n 500 --seed 42

# Generation sample: 200 probes, single-tier contexts only
python scripts/sample_generation.py --n 200 --seed 99
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
├── PROBE.md                           # Probe methodology and design
├── probes_clean17_ctx5.csv            # Full cleaned probes (4,271 after dedup)
├── probes_stratified_500.csv          # Cloze evaluation sample (stratified)
├── probes_generation_200.csv          # Generation evaluation sample
├── scripts/
│   ├── cloze_eval.py                  # Cloze evaluation pipeline
│   ├── generation_eval.py             # Generation (dialogue continuation) pipeline
│   ├── tier_classifier.py             # Pronoun/tier classification
│   ├── sample_stratified.py           # Stratified sampling for cloze task
│   ├── sample_generation.py           # Filtered sampling for generation task
│   ├── plot_results.py                # Visualization
│   ├── indicdialogue_extract_probes.py # Probe extraction from IndicDialogue
│   └── filter_probes_clean17.py       # Probe filtering to 17 clean films
├── results/                           # Evaluation results (JSONL + metrics JSON)
├── plots/                             # Generated visualizations
└── modules/                           # Git submodules
    ├── IndicDialogue/                 # Hindi film subtitle dialogues
    ├── hindi-politeness/              # Reference corpus
    └── honorific-wiki-llm/           # Mukherjee et al. dataset
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
