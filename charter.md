# Hindi Honorific Evaluation Benchmark Charter

**Project Title:** Hindi Honorific Evaluation Benchmark (working title: "HonorificEval")

**Author:** Adit

**Advisor:** Professor Malihe Alikhani

**Last Updated:** 2026-01-20

**Status:** In Progress

---

## 1. Problem Statement

### 1.1 The Gap
[What problem exists that this benchmark solves?]

- Mukherjee et al. (EMNLP 2025) showed LLMs struggle with Hindi honorifics, but only did descriptive analysis
- No automatic evaluation tool exists for Hindi honorific appropriateness
- Existing metrics (BERTScore, etc.) measure semantic similarity, not pragmatic appropriateness

### 1.2 Why It Matters
[Why should anyone care?]

- Hindi has 600M+ speakers
- Honorifics are obligatory, not optional — wrong usage is socially significant
- LLMs deployed in Hindi contexts need pragmatic competence
- [Add more...]

---

## 2. Research Questions

### Primary Question
> [Main question your benchmark answers]
> 
> e.g., "Can we automatically evaluate whether LLM-generated Hindi text uses contextually appropriate honorifics?"

### Secondary Questions
- [ ] Do LLMs show systematic bias in honorific usage across social categories (caste, gender, religion)?
- [ ] Which models perform best at Hindi pragmatic competence?
- [ ] [Add more...]

---

## 3. Scope

### 3.1 In Scope
- [ ] Hindi language (Devanagari script)
- [ ] Three-level honorific system (tu/tum/aap)
- [ ] Pronoun forms
- [ ] Verb morphology agreement
- [ ] Social categories: [list which — caste, gender, religion, age?]
- [ ] [Add more...]

### 3.2 Out of Scope (for this paper)
- [ ] Other Indic languages (Bengali, Marathi, etc.)
- [ ] Code-mixed Hindi-English
- [ ] Spoken/prosodic honorific cues
- [ ] [Add more...]

### 3.3 Open Scope Decisions
- [ ] Include only second-person (tu/tum/aap) or also third-person honorifics?
- [ ] Focus on generation only, or also comprehension?
- [ ] [Add more...]

---

## 4. Data Sources

### 4.1 Primary Data

| Dataset | Size | What It Provides | Link | Status |
|---------|------|------------------|------|--------|
| Hindi Politeness Corpus | ~30K posts | Honorific annotations (pronouns, verbs) | [GitHub](https://github.com/kmi-linguistics/hindi-politeness) | [ ] Downloaded [ ] Explored |
| Mukherjee Wikipedia Data | 10K articles | Honorific usage + socio-demographic attributes | [GitHub](https://github.com/souro/honorific-wiki-llm) | [ ] Downloaded [ ] Explored |

### 4.2 Supplementary Data (if needed)

| Dataset | Potential Use | Link | Status |
|---------|---------------|------|--------|
| IndiBias | Social category names/terms | [GitHub](https://github.com/niharr/IndiBias) | [ ] To explore |
| IndicCorp | Pretraining / additional examples | [AI4Bharat](https://ai4bharat.org/) | [ ] To explore |

### 4.3 Data Questions to Resolve
- [ ] Is Hindi Politeness Corpus sufficient for training pairs?
- [ ] What format is the data in?
- [ ] Any licensing restrictions?
- [ ] [Add more...]

---

## 5. Methodology

### 5.1 High-Level Approach
```
[Diagram or description of overall pipeline]

Training Data (Hindi Politeness Corpus)
         ↓
    Pair Generation (rule-based transformation)
         ↓
    Contrastive Encoder Training
         ↓
    Evaluation Metric
         ↓
    LLM Evaluation
```

### 5.2 Training Pair Creation

**Approach:** [Rule-based transformation / Other]

**Transformation Rules:**
| From | To | Pronoun Change | Verb Change Example |
|------|-----|----------------|---------------------|
| Formal | Familiar | आप → तुम | बैठिए → बैठो |
| Formal | Intimate | आप → तू | बैठिए → बैठ |
| Familiar | Intimate | तुम → तू | बैठो → बैठ |

**Tools Needed:**
- [ ] Hindi morphological analyzer — Options: [Indic NLP Library](https://github.com/anoopkunchukuttan/indic_nlp_library), [Stanza](https://stanfordnlp.github.io/stanza/)
- [ ] [Other tools...]

**Open Questions:**
- [ ] Can transformations be fully automated or need manual verification?
- [ ] How to handle irregular verbs?
- [ ] [Add more...]

### 5.3 Contrastive Encoder

**Base Model Options:**
- [ ] [ai4bharat/indic-bert](https://huggingface.co/ai4bharat/indic-bert)
- [ ] [google/muril-base-cased](https://huggingface.co/google/muril-base-cased)
- [ ] [Other options...]

**Training Setup:**
- Loss function: Triplet Loss / InfoNCE / [Other]
- Pair structure: (anchor, positive, negative)
  - Anchor: original sentence
  - Positive: same register, similar meaning
  - Negative: same meaning, wrong register

**Hyperparameters (to tune):**
- Learning rate: [TBD]
- Batch size: [TBD]
- Epochs: [TBD]
- Margin (for triplet loss): [TBD]

### 5.4 Evaluation Metric Design

**Input:** 
- Context (social situation)
- Reference (appropriate response)
- Candidate (LLM output)

**Output:** 
- Score (0-1) indicating honorific appropriateness

**Scoring Method:**
```
score = cosine_similarity(encode(reference), encode(candidate))
```

**Validation:**
- [ ] Correlate with human judgments
- [ ] Test on held-out examples
- [ ] [Other validation...]

---

## 6. Evaluation Tasks

### 6.1 LLM Evaluation Tasks

| Task | Description | Input | Expected Output |
|------|-------------|-------|-----------------|
| Honorific Generation | Given context, generate appropriate response | Social context + prompt | Hindi text with correct honorifics |
| Honorific Selection | Choose appropriate form | Context + options | Correct option |
| [Add more...] | | | |

### 6.2 Models to Evaluate

| Model | Type | Why Include |
|-------|------|-------------|
| GPT-4 | Proprietary multilingual | SOTA baseline |
| Llama 3 | Open multilingual | Open-source baseline |
| OpenHathi | Hindi-optimized | Hindi-specific comparison |
| Sarvam | Hindi-optimized | Hindi-specific comparison |
| [Add more...] | | |

### 6.3 Evaluation Dimensions

- [ ] Overall honorific accuracy
- [ ] By social category (caste, gender, religion, age)
- [ ] By formality level (formal vs informal contexts)
- [ ] [Add more...]

---

## 7. Success Metrics

### 7.1 For the Evaluation Model
- [ ] Separation in embedding space between appropriate/inappropriate (measured by: [metric])
- [ ] Correlation with human judgments (target: r > [X])
- [ ] [Add more...]

### 7.2 For LLM Evaluation
- [ ] Clear differentiation between models
- [ ] Interpretable results (can explain why model X scores higher/lower)
- [ ] [Add more...]

---

## 8. Limitations & Future Work

### 8.1 Known Limitations
- [ ] Only covers Hindi (not other Indic languages)
- [ ] Relies on rule-based transformations (may miss edge cases)
- [ ] [Add more...]

### 8.2 Future Work (Paper 2+)
- [ ] Extend to Bengali, Marathi, etc.
- [ ] Fine-tune LLM to improve honorific competence
- [ ] [Add more...]

---

## 9. Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| 1 | Download data, explore structure, document transformation rules | Data exploration notes |
| 2 | Build pair generation pipeline, create initial pairs | 100+ validated pairs |
| 3 | Train contrastive encoder, iterate | Trained model |
| 4 | Build evaluation metric, validate | Working metric |
| 5 | Evaluate LLMs, analyze results | Results tables |
| 6 | Write paper | Draft |

---

## 10. Open Questions & Decisions

### Blocking Questions (need answer to proceed)
- [ ] [Question 1]
- [ ] [Question 2]

### Questions for Professor
- [ ] Is rule-based transformation acceptable methodology?
- [ ] Any recommended Hindi morphological analyzers?
- [ ] Target venue: ISCLS 2026? ACL workshop? Other?

### Decisions Made
| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| [Example: Base model] | [indic-bert] | [Most Hindi data in pretraining] | [Date] |

---

## 11. Resources & References

### Key Papers
- Mukherjee et al. (EMNLP 2025) - Hindi/Bengali honorifics in LLMs — https://arxiv.org/abs/2501.03479
- Kumar (LREC 2014) - Hindi Politeness Corpus — https://github.com/kmi-linguistics/hindi-politeness
- Gao et al. (EMNLP 2021) - SimCSE — https://arxiv.org/abs/2104.08821
- Zhang et al. (ICLR 2020) - BERTScore — https://arxiv.org/abs/1904.09675
- Farhansyah et al. (ACL 2025) - Javanese honorifics — [TBD link]

### Tools
- Indic NLP Library — https://github.com/anoopkunchukuttan/indic_nlp_library
- Stanza (Hindi pipeline) — https://stanfordnlp.github.io/stanza/

### Code Repositories
- Hindi Politeness: https://github.com/kmi-linguistics/hindi-politeness
- Mukherjee data: https://github.com/souro/honorific-wiki-llm

---

## 12. Log / Notes

### 2026-01-20
- Updated charter with current links and dates

### [Date]
- [Notes...]

---

*This is a living document. Update as the project evolves.*