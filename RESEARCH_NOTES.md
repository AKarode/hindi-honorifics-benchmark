# Research Notes — Hindi Honorifics Benchmark

## Competitive Assessment (2026-02-20)

### Overall Verdict
Methodology is **ACL-competitive**. Closest published comp: Farhansyah et al. (ACL 2025) on Javanese honorifics — our design is arguably more sophisticated, especially the style transfer component.

---

### Strengths

1. **Novel 3-task ladder** (cloze → generation → style transfer) — comprehension → production → adaptation maps to Bloom's taxonomy. Most benchmarks test a single capability; this is a deliberate, theoretically motivated contribution.

2. **Ecological indirection is the biggest methodological contribution** — situational vignettes instead of explicit register labels for style transfer has **no direct precedent** in the literature. Standard benchmarks (GYAFC, XFORMAL) always name the target formality level.

3. **Corpus size is competitive** — 4,382 probes from 17 films is on par with XFORMAL (~2.5K/language) and Farhansyah (~4K instances).

4. **Clear literature gap** — no Hindi honorific LLM benchmark exists. Hindi has a 3-tier system (तू/तुम/आप) with rich morphological agreement, making it more complex than binary formal/informal benchmarks.

5. **Mitigation ablation** (zero-shot → system prompt → few-shot → fine-tune) is systematic and publishable.

---

### Reviewer Concerns to Address

| Concern | Severity | Mitigation |
|---------|----------|------------|
| **Inter-annotator agreement (IAA)** | HIGH | Need IAA numbers on probe gold labels. At minimum, have 2-3 native speakers independently label a subset. |
| **Human evaluation** | HIGH | At least a subset of generation + style transfer tasks needs human judges, not just automatic metrics. |
| **Scripted vs. naturalistic data** | MEDIUM | Preempt by arguing film dialogue encodes sociolinguistic norms native speakers recognize. Cite sociolinguistic film corpus work. |
| **Pretraining contamination** | MEDIUM | Models may have seen these scripts. Run a contamination check (e.g., verbatim recall test). |
| **Content preservation metric** | MEDIUM | Operationalize with BERTScore or chrF, not just vague "semantic similarity." |
| **Error analysis** | MEDIUM | ACL expects qualitative error analysis beyond aggregate metrics. |
| **Statistical significance** | LOW-MEDIUM | Pairwise comparisons across ablation ladder need significance tests (bootstrap or paired permutation). |

---

### Missing Baselines to Add

- **Majority class baseline** — most frequent honorific form
- **Random baseline**
- **Rule-based baseline** — using explicit social metadata (age, power, relationship)
- **Monolingual Hindi models** — IndicBERT, MuRIL alongside GPT-class / multilingual models

### Missing Evaluation Metrics

- **Confusion matrices** across तू/तुम/आप (not just aggregate accuracy)
- **Per-film and per-relationship-type breakdowns** (parent-child, boss-employee, romantic, strangers)
- **Calibration analysis** — do models know when they're uncertain about register?
- **BERTScore or chrF** for content preservation in style transfer
- **Human evaluation** on a representative subset

---

### Closest Comparable Papers

| Paper | Venue | Similarity | Key Difference |
|-------|-------|-----------|----------------|
| Farhansyah et al. 2025 | ACL 2025 | Honorific system evaluation for LLMs, multi-task, similar corpus size | Javanese not Hindi; classification + translation, not cloze + generation + transfer |
| Briakou et al. 2021 (XFORMAL) | NAACL 2021 | Multilingual formality style transfer benchmark | Binary formal/informal, no honorific morphology, no situational inference |
| Rao & Tetreault 2018 (GYAFC) | NAACL 2018 | Formality style transfer benchmark | English only, larger corpus, simpler register distinction |
| Kumar 2014 | LREC 2014 | Hindi politeness corpus with honorific annotations | Blog data, classification only, no LLM evaluation |
| Pragmatics survey (ACL 2025) | ACL 2025 | Comprehensive survey of LLM pragmatic competence | Survey; identifies honorifics as understudied |
| IndicGenBench (Singh et al. 2024) | arXiv | Hindi LLM evaluation | General NLU/NLG, no sociolinguistic focus |

### Key Citations

- Farhansyah et al. (2025) — Javanese honorifics: https://aclanthology.org/2025.acl-long.1296/
- Kumar (2014) — Hindi politeness corpus: https://aclanthology.org/L14-1480/
- GYAFC — Rao & Tetreault (2018): https://arxiv.org/abs/1803.06535
- XFORMAL — Briakou et al. (2021): https://aclanthology.org/2021.naacl-main.256/
- IndicGenBench (2024): https://arxiv.org/abs/2404.16816
- LLM Politeness Strategies (EMNLP 2025): https://aclanthology.org/2025.emnlp-main.820
- Pragmatics survey (ACL 2025): https://aclanthology.org/2025.acl-long.425
- Hindi Politeness GitHub (Kumar): https://github.com/kmi-linguistics/hindi-politeness

---

### Project Status (2026-02-20)

- ✅ 17 clean Hindi films, 4,382 probes with 5-line context
- ✅ Cloze task ready
- ✅ Generation task designed (dialogue continuation)
- 📦 Style transfer task designed but deferred to future work (archived)
- ✅ Probe filtering script (`scripts/filter_probes_clean17.py`)
- ✅ Filtered output (`probes_clean17_ctx5.csv`)
- 🔲 IAA validation on probe subset
- 🔲 Build sampling + evaluation pipeline
- 🔲 Decide mitigation strategy (few-shot / fine-tune / system prompt / all as ablations)
- 🔲 Add baselines (majority, random, rule-based, monolingual Hindi models)
- 🔲 Human evaluation protocol
- 🔲 Contamination check
