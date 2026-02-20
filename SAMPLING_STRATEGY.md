# Sampling & Validation Strategy

## Goal

Select a manageable, representative subset of probes from `probes.csv` for manual validation and subsequent model evaluation. We need enough coverage to detect failure patterns without making annotation infeasible.

---

## Phase 1: Stratified Sampling (~500 probes)

### Why 500?
- Large enough for statistical signal across 3 pronoun tiers (तू/तुम/आप + oblique forms)
- Small enough for one person to manually validate in ~3–4 hours
- Enough per-stratum count (~50+) to measure model accuracy per pronoun class

### Stratification axes

| Axis | Strata | Rationale |
|------|--------|-----------|
| **Pronoun tier** | तू-forms (तू, तुझे, तुझसे, तुझको) / तुम-forms (तुम, तुम्हें, तुम्हारा/ी/े, तुमसे, तुमको) / आप-forms (आप, आपको, आपका/की/के, आपसे, आपने) | Core variable — formality level |
| **Context length** | 1-line context vs. 2-line context | Tests whether models benefit from more context |
| **Line length** | Short (<30 chars) / Medium (30–80) / Long (>80) | Longer lines may have more disambiguation cues |

### Sampling procedure

1. Group probes by **pronoun tier** (तू / तुम / आप)
2. Within each tier, sample proportionally to natural distribution but with a **floor of 80 probes** per tier (oversample rare tiers)
3. Within each tier, ensure mix of context lengths and line lengths
4. Deduplicate by movie to avoid leaking same-film style

---

## Phase 2: Manual Validation (~2 hours)

### What we're validating

For each sampled probe, a Hindi-literate annotator answers:

1. **Is the gold pronoun unambiguous?** (Yes / No / Ambiguous)
   - "Unambiguous" = only one pronoun tier is appropriate given context
   - "Ambiguous" = multiple tiers could work (e.g., between friends, तुम or तू both fine)

2. **Are there lexical cues?** (Yes / No)
   - Relationship markers: sir, जी, maa, papa, boss, beta, bhai, etc.
   - These make the "correct" tier more deterministic

3. **Is the context sufficient?** (Yes / No)
   - Can a human pick the right pronoun from the context alone?
   - If No → mark as "insufficient context" (still useful for model evaluation — tests if models default-guess)

### Annotation output

```csv
probe_id, gold_pronoun, annotator_label, ambiguity, has_lexical_cue, context_sufficient, notes
```

### Quality check
- 50 probes double-annotated (by Adit + one other Hindi speaker) for inter-annotator agreement
- Target: Cohen's κ ≥ 0.7 on the ambiguity judgment

---

## Phase 3: Probe Set Construction

After validation, construct the final probe set:

### Set A: "Clear" probes (~300–350 expected)
- Unambiguous gold label
- Sufficient context
- These are the high-confidence probes for measuring model accuracy

### Set B: "Ambiguous" probes (~100–150 expected)
- Multiple valid pronoun tiers
- Interesting for a different question: do models show **bias** toward one tier?
- Measure: distribution of model outputs vs. natural distribution

### Set C: "Cue-rich" probes (subset of A, ~80–120 expected)
- Has explicit lexical cues (जी, sir, etc.)
- Tests: can models use obvious signals?
- If models fail even here, that's a strong finding

---

## Phase 4: Model Evaluation Protocol

### Models
- GPT-5.2 (OpenAI)
- Claude Opus 4.5 (Anthropic)
- Claude Sonnet 4 (Anthropic)
- Gemini 2.5 Pro (Google)

### Prompt template (cloze)

```
निम्नलिखित संवाद में रिक्त स्थान (____) में सही सर्वनाम भरें।

संदर्भ:
{context}

वाक्य: {masked_line}

केवल सर्वनाम लिखें, कोई व्याख्या नहीं।
```

### Runs per probe
- 5 runs at temperature=0.0 (determinism check)
- 5 runs at temperature=0.7 (consistency check)

### Metrics

| Metric | What it measures |
|--------|-----------------|
| **Tier accuracy** | Does model pick the correct formality tier? (ignoring oblique case) |
| **Exact match** | Does model pick the exact pronoun form? |
| **Formality bias** | Distribution of आप vs. तुम vs. तू across ambiguous probes |
| **Consistency** | Agreement across 5 runs (same probe, same temp) |
| **Cue sensitivity** | Accuracy on Set C (cue-rich) vs. Set A overall |
| **Verb agreement** | (Future: does the model conjugate correctly for its chosen pronoun?) |

---

## Timeline

| Step | Time estimate | Dependency |
|------|--------------|------------|
| Extract probes | ✅ Done (this session) | IndicDialogue data |
| Stratified sampling script | ~1 hour | probes.csv |
| Manual validation | ~3–4 hours | Adit + Hindi speaker |
| Probe set construction | ~30 min | Validation output |
| Model runs (4 models × 500 probes × 10 runs) | ~2–3 hours API time | Probe set + API keys |
| Analysis + write-up | ~1 day | Model outputs |

---

## Open Design Decisions

1. **Should we include romanized/Hinglish lines?** Currently filtered out. Could be a separate study.
2. **Verb agreement tracking**: Not yet in extraction pipeline. Add before or after model runs?
3. **Paraphrase probes**: Charter mentions "contextual paraphrase" as probe type 2. Build this now or after cloze results?
4. **How many movies to cap per stratum?** Avoid one chatty film dominating a tier.

---

## Next Immediate Steps

1. ✅ Download IndicDialogue Hindi.jsonl
2. ✅ Run extraction → probes.csv
3. [ ] Analyze probe distribution (pronoun counts, movie coverage, line lengths)
4. [ ] Write `scripts/sample_probes.py` — stratified sampler
5. [ ] Manual validation pass (Adit)
6. [ ] Construct final probe sets A/B/C
