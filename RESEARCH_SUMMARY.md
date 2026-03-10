# Hindi Second-Person Honorifics Benchmark
## Evaluating LLM Sociopragmatic Competence in Conversational Hindi

**Adit Karode** | March 2026

---

## Research Question

Do large language models handle Hindi's three-tier second-person pronoun system (T/TUM/AAP) appropriately in conversational settings?

Hindi has 600M+ speakers. Using T (intimate) when AAP (formal) is expected is genuinely offensive. As LLMs are deployed in Hindi chatbots, translation, and creative writing, this sociopragmatic competence is critical.

> **The Three Tiers:** T (intimate/rude), TUM (familiar/neutral), AAP (formal/respectful)

## Methodology

### Data Source: IndicDialogue

All evaluation data is derived from **IndicDialogue**, a corpus of real Hindi film subtitles. No synthetic scenarios or researcher-authored stimuli are used. This ensures ecological validity—we test on dialogue patterns that exist in actual Hindi media.

**Pipeline:**
1. Extracted ~21K pronoun occurrences from Hindi film subtitles
2. Filtered to 17 high-quality Hindi-original films (4,271 probes)
3. Stratified sampling balanced by honorific tier and proportional by movie

### Two Complementary Tasks

| | **Cloze (Comprehension)** | **Generation (Production)** |
|---|---|---|
| **Input** | Dialogue context + masked line with `____` | Dialogue context only |
| **Task** | Select correct pronoun from 18 forms | Generate the next dialogue line |
| **Gold** | Original pronoun from subtitle | Tier of original next line |
| **Sample** | 500 probes (167 T / 167 TUM / 166 AAP) | 200 probes (67 T / 67 TUM / 66 AAP) |
| **Tests** | Recognition / selection | Production / pragmatic inference |

### Models Evaluated

- **OpenAI**: gpt-5-mini, o4-mini, gpt-5-nano, gpt-5.2, gpt-4.1-mini, gpt-4o-mini, gpt-4o
- **Anthropic**: Claude Sonnet 4.5
- **Google**: Gemini 2.5 Flash
- **Sarvam AI** (India-first): Sarvam-M

---

## Key Findings

### 1. Comprehension Significantly Exceeds Production

![Cloze vs Generation Accuracy](plots/cloze_vs_gen.png)

Models achieve 55-81% tier accuracy on cloze (comprehension) but only 27-57% on generation (production). This ~25-40 percentage point gap indicates models can *recognize* correct honorifics but struggle to *produce* them in free dialogue.

### 2. Reasoning Models Refuse Hindi Film Dialogue

| Model | Refusal Rate |
|-------|-------------|
| gpt-5-mini | **47.5%** |
| Claude Sonnet | 17.5% |
| gpt-5.2 | 2.0% |
| Others | 0% |

GPT-5-mini refused nearly half of all generation prompts, citing copyright concerns about film dialogue. This safety behavior significantly impacts usability for Hindi creative applications.

### 3. Cross-Family Performance Comparison

![Model Family Comparison](plots/family_comparison.png)

| Family | Best Cloze | Best Generation |
|--------|-----------|-----------------|
| OpenAI | 81.4% (gpt-5-mini) | 57.5% (gpt-4o-mini) |
| Anthropic | 75.8% | 41.2% |
| Google | 55.0% | 39.0% |
| Sarvam | 52.7% | 27.6% |

OpenAI models lead both tasks. Notably, the India-focused Sarvam-M underperforms despite being trained specifically on Indian languages.

### 4. Avoidance is a Common Strategy

Models frequently avoid second-person pronouns entirely in generation (36-68% avoidance rate), using passive constructions or dropping subjects. This masks true honorific competence.

### 5. Per-Tier Breakdown

![Per-Tier Accuracy](plots/tier_breakdown.png)

The intimate tier (T) is hardest to generate correctly—models default toward the safer TUM (familiar) or AAP (formal) registers.

---

## Conclusion

This benchmark reveals a significant gap between LLM comprehension and production of Hindi honorifics. While top models achieve >80% on recognition tasks, production accuracy drops to ~40-57%, with high avoidance and refusal rates. Cross-family evaluation shows OpenAI models currently lead, while India-focused alternatives underperform expectations.

**Implications:** LLMs deployed in Hindi conversational settings may produce socially inappropriate or overly formal language, particularly in intimate/informal contexts where T-tier usage is expected.

---

## References

- Mukherjee et al. (EMNLP 2025) — Third-person honorific bias in Hindi/Bengali LLMs
- Farhansyah et al. (ACL 2025) — Javanese honorific evaluation
- IndicDialogue corpus — Hindi film subtitle dataset
