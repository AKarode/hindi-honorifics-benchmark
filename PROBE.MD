# Hindi Honorifics — Probe Methodology

## Research Goal

Evaluate whether LLMs handle Hindi second-person honorifics (तू/तुम/आप) appropriately in conversational settings. Extending Mukherjee et al. (EMNLP 2025), who showed failures in third-person usage, to the harder second-person case.

**Explicit gap (Mukherjee et al., Section 5):**
> "Our study focused exclusively on third-person usage in formal Wikipedia contexts. However, honorific dynamics can differ substantially in second-person usage and more casual or spoken communication."

---

## Data Source

All probes are derived from **IndicDialogue** — a corpus of real Hindi film subtitles. No synthetic data is used.

**What IndicDialogue provides:**
- Subtitle lines from Hindi films with `movie`, `subtitle_id`, and dialogue text
- Mixed-quality lines (English, romanized, and Devanagari Hindi)

**What IndicDialogue lacks:**
- Speaker labels / diarization
- Relationship metadata between characters
- Scene or emotional context annotations

---

## Probe Extraction Pipeline

### Step 1: Raw extraction (`indicdialogue_extract_probes.py`)
- Scan all subtitle lines for 18 second-person pronoun forms across 3 tiers
- For each hit: mask the pronoun, capture surrounding context (5-line window)
- Filter to Devanagari-only lines
- Output: `probes.csv` (~21K raw probes)

### Step 2: Film quality filter (`filter_probes_clean17.py`)
- Restrict to 17 films that passed a subtitle quality audit (score 4-5)
- These are Hindi-original films with high-quality Devanagari subtitles
- Output: `probes_clean17_ctx5.csv` (4,382 probes)

### Step 3: Deduplication
- Deduplicate on (masked_line, gold_pronoun) key
- 111 duplicates removed → 4,271 unique probes

### Step 4: Task-specific sampling

**Cloze sample** (`sample_stratified.py` → `probes_stratified_500.csv`):
- 500 probes, stratified by tier (167 T / 167 TUM / 166 AAP)
- Proportional by movie within each tier (all 17 films represented)
- Fixed seed (42) for reproducibility

**Generation sample** (`sample_generation.py` → `probes_generation_200.csv`):
- Filtered to probes where context contains exactly ONE honorific tier (no speaker-switch ambiguity)
- Gold line >= 15 characters (substantial dialogue)
- 200 probes (67 T / 67 TUM / 66 AAP), all 17 films
- Fixed seed (99) for reproducibility

---

## Task Designs

### Task 1: Cloze (Comprehension)
- **Input**: Dialogue context + masked line with `____` replacing the pronoun
- **Model task**: Select the correct pronoun from 18 forms
- **Gold**: The original pronoun from the subtitle
- **Metrics**: Exact accuracy, tier accuracy, valid form rate, tier confusion matrix

### Task 2: Dialogue Continuation (Production)
- **Input**: Dialogue context only (5 lines, single-tier register)
- **Model task**: Generate the next line of dialogue
- **Gold**: The tier of the original next line
- **Metrics**: Tier accuracy, avoidance rate, formality bias ratio, verb agreement
- **Prompt**: Hindi, no mention of honorifics or pronouns (avoids priming)

### Complementarity

| Dimension | Cloze | Generation |
|-----------|-------|------------|
| Tests | Recognition / selection | Production / pragmatic inference |
| Input | Context + masked line | Context only |
| Scoring | Exact match + tier match | Tier classification of generated text |
| Failure mode | "Doesn't know the right answer" | "Knows but doesn't produce" or "defaults to one tier" |

---

## Known Limitations

1. **No speaker diarization**: Cannot attribute lines to specific characters. Mitigated in generation by single-tier filtering.
2. **First-occurrence bias**: Extraction uses `TOKEN_RE.search()` which returns the first pronoun match per line. Lines with multiple pronouns are represented by their first occurrence only.
3. **No human validation**: Gold labels come directly from the subtitle text. Some may be contextually inappropriate (e.g., code-switching scenes).
4. **Film dialogue bias**: Subtitles represent scripted, performed dialogue — not natural conversation. Register may be exaggerated for dramatic effect.

---

## Pronoun Forms (18 total)

| Tier | Forms |
|------|-------|
| तू (T) — intimate/inferior | तू, तुझे, तुझसे, तुझको, तेरा, तेरी, तेरे |
| तुम (TUM) — familiar | तुम, तुम्हें, तुमसे, तुमको, तुम्हारा, तुम्हारी, तुम्हारे |
| आप (AAP) — formal/respectful | आप, आपको, आपसे, आपका, आपकी, आपके, आपने |

---

## Key Resources

- **Mukherjee et al. (EMNLP 2025)**: 3rd-person honorific bias in Hindi/Bengali LLMs
- **Farhansyah et al. (ACL 2025)**: Javanese honorific evaluation — methodological template
- **Zhao & Hawkins (EMNLP 2025)**: LLM politeness strategies in free production
- **Kumar (LREC 2014)**: Hindi Politeness Corpus — sociolinguistic variables
- **Brown & Levinson (1987)**: Politeness theory (power, distance, imposition)
