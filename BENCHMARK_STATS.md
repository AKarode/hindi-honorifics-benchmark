# Hindi Honorifics Benchmark — Corpus Statistics

## Overview

| Metric | Value |
|--------|-------|
| Total probes | 4,382 |
| Source films | 17 (Hindi-original, quality-audited) |
| Honorific tiers | 3 (तू / तुम / आप) |
| Pronoun forms covered | 18 (nominative, oblique, possessive, postpositional) |
| Context window | 5 preceding subtitle lines per probe |
| Data source | IndicDialogue corpus (Netflix Hindi subtitles) |

## Honorific Tier Distribution

| Tier | Count | % | Description |
|------|-------|---|-------------|
| तू (tū) | 1,116 | 25.5% | Intimate / inferior |
| तुम (tum) | 1,577 | 36.0% | Informal / familiar |
| आप (āp) | 1,689 | 38.5% | Formal / respectful |

**Near-balanced three-way split** — no single tier dominates, enabling fair evaluation without class imbalance corrections.

## Pronoun Form Distribution

| Form | Tier | Count | % |
|------|------|-------|---|
| तुम | तुम | 839 | 19.1% |
| आप | आप | 828 | 18.9% |
| तू | तू | 798 | 18.2% |
| तुम्हें | तुम | 297 | 6.8% |
| आपको | आप | 278 | 6.3% |
| तुझे | तू | 272 | 6.2% |
| आपके | आप | 173 | 3.9% |
| तुम्हारे | तुम | 166 | 3.8% |
| आपने | आप | 121 | 2.8% |
| आपकी | आप | 120 | 2.7% |
| आपका | आप | 115 | 2.6% |
| तुम्हारी | तुम | 112 | 2.6% |
| तुम्हारा | तुम | 96 | 2.2% |
| आपसे | आप | 54 | 1.2% |
| तुमसे | तुम | 43 | 1.0% |
| तुझसे | तू | 37 | 0.8% |
| तुमको | तुम | 24 | 0.5% |
| तुझको | तू | 9 | 0.2% |

## Per-Film Probe Counts

| Film | Year | Probes | Quality Score |
|------|------|--------|---------------|
| Tu Jhoothi Main Makkaar | 2023 | 377 | 5/5 |
| Indoo Ki Jawani | 2020 | 373 | 5/5 |
| Good Newwz | 2019 | 358 | 5/5 |
| Shehzada | 2023 | 310 | 5/5 |
| Jaane Jaan | 2023 | 285 | 5/5 |
| Ginny Weds Sunny | 2020 | 266 | 5/5 |
| Axone | 2019 | 261 | 5/5 |
| Dhamaka | 2021 | 255 | 4/5 |
| Jaadugar | 2022 | 252 | 5/5 |
| Madam Chief Minister | 2021 | 251 | 5/5 |
| Lust Stories 2 | 2023 | 244 | 5/5 |
| Guilty | 2020 | 237 | 4/5 |
| Hit the First Case | 2022 | 232 | 4/5 |
| The Great Indian Family | 2023 | 228 | 5/5 |
| The White Tiger | 2021 | 204 | 4/5 |
| Haseen Dillruba | 2021 | 133 | 5/5 |
| Darlings | 2022 | 116 | 5/5 |

**Mean:** 258 probes/film | **Min:** 116 (Darlings) | **Max:** 377 (Tu Jhoothi Main Makkaar)

## Quality Assurance

- **23 initial films** from IndicDialogue corpus identified as Hindi-original
- **6 excluded** after manual subtitle quality audit (machine-translated or non-Hindi-original)
- **17 retained** with quality scores of 4/5 or 5/5
- Quality criteria: grammatical correctness, natural Hindi dialogue, authentic honorific usage, no English fragment leakage

## Evaluation Tasks

### Task 1: Cloze (Comprehension)
- Mask honorific pronoun in each probe
- Model fills in the blank given 5-line context
- Tests: Does the model recognize which tier fits the social context?

### Task 2: Dialogue Continuation (Production)
- Provide social context + dialogue opening
- Model generates next turn with appropriate honorifics
- Tests: Can the model produce correct register in free generation?

### Task 3: Style Transfer (Adaptation)
- **(A) Situation-Anchored Rewrite** — source sentence + situational vignette → model rewrites at inferred register
- **(B) Consistency Repair** — wrong-register sentence inserted into dialogue → model corrects it
- Tests: Can the model transform between registers based on social inference?

### Planned Ablation: Mitigation Strategies
- Zero-shot baseline (no guidance)
- System prompt (instructions about Hindi honorifics)
- Few-shot (2, 4, 8 examples)
- *(Fine-tuning deferred to future work)*

## Comparison with Related Benchmarks

| Benchmark | Language | Probes/Items | Tiers | Tasks |
|-----------|----------|-------------|-------|-------|
| **This work** | **Hindi** | **4,382** | **3 (तू/तुम/आप)** | **Cloze + Generation + Style Transfer** |
| Farhansyah et al. (ACL 2025) | Javanese | ~4,000 | 3 (Ngoko/Krama/Krama Alus) | Classification + Translation + Generation |
| XFORMAL (NAACL 2021) | PT/FR/IT | ~2,500/lang | 2 (formal/informal) | Style Transfer |
| GYAFC (NAACL 2018) | English | ~110,000 | 2 (formal/informal) | Style Transfer |
| Kumar (LREC 2014) | Hindi | 479,000+ | 3 (polite/neutral/impolite) | Classification |
