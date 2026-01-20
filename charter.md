# Hindi Honorific Evaluation Benchmark

**Author:** Adit
**Advisor:** Professor Malihe Alikhani
**Last Updated:** 2026-01-20
**Status:** Data exploration done, starting work on training pairs

## Problem

Mukherjee et al. (EMNLP 2025) showed LLMs don't handle Hindi honorifics well, but they only analyzed the problem—there's no automatic way to evaluate it.

Why this matters:
- Hindi has 600M+ speakers. Honorifics are mandatory (not optional like English titles).
- Using the wrong honorific is socially wrong and models deployed in Hindi need to get this right.
- Existing metrics like BERTScore and COMET only check semantic similarity, not whether something is pragmatically appropriate.
- Even frontier models (GPT-5.2, Gemini 3) only score ~35% on OpenAI's culture-aware benchmark (IndQA), suggesting pragmatic understanding is a weak spot.

## Main Question

Can we build a metric that automatically scores whether an LLM-generated sentence uses the right honorific (formal आप vs informal तुम/तू)?

Sub-questions:
- Do different models have biases (e.g., always using informal)?
- Do models perform differently based on who they're talking about (by gender, age, fame)?
- Does a metric trained on embeddings correlate with what humans think is appropriate?

## Scope

**In:**
- Hindi, Devanagari script
- Binary classification: आप (formal) vs informal (तुम/तू)
- Pronouns and verb forms
- Second-person address only

**Out (for now):**
- Other Indic languages
- Code-mixed Hindi-English
- Spoken/prosodic honorifics
- Third-person honorifics
- Three-way distinction (तू vs तुम—our datasets don't distinguish these)

**Why binary?** Both the Hindi Politeness Corpus and Wiki-LLM only mark formal/informal, not the three-level system.

## Data

**Hindi Politeness Corpus v0.2:** 56K examples, has an `ap` column (1=formal, 0=informal). From social media (blogs, Twitter). Mix of Devanagari and Romanized text. Will use ~45K for training.

**Wiki-LLM:** 10K Hindi Wikipedia articles + 1K entities with socio-demographic metadata (age, gender, fame, role). Also marks honorifics as binary. Good for understanding bias patterns.

Both are open-licensed and have binary labels (formal/informal only).

## Approach

1. **Create training pairs** by transforming formal sentences to informal:
   - Pronoun: आप → तुम/तू
   - Verb: बैठिए → बैठो
   - Remove honorific suffix जी
   - Need to manually validate 10-20 pairs first to check feasibility

2. **Train a contrastive encoder** on these pairs
   - Use Hindi-specific base model (indic-bert or google/muril)
   - Framework: sentence-transformers
   - Loss: TripletLoss
   - Goal: same-meaning sentences with different registers should be far apart in embedding space

3. **Build the metric:**
   ```
   honorific_score = cosine_similarity(reference_embedding, candidate_embedding)
   ```
   Score ranges 0-1. Higher = more appropriate honorific choice.

**Tools:** Indic NLP Library, Stanza Hindi, or iNLTK for morphological analysis if needed

## Evaluation

**Prompts:** Will use Wiki-LLM entities to create contexts: "Describe [person]", "Write about [historical figure]", etc. Then score whether the model's response uses appropriate honorifics for that person (age, fame, role, etc.).

**Models to test:**

Frontier models (2026):
- GPT-5.2 (Dec 2025) — top performer on culture-aware benchmarks, scores 34.9% on IndQA
- Claude Opus 4.5 (Nov 2025) — leads on multilingual benchmarks
- Gemini 3 Pro (2026) — shows high variance in cultural alignment
- Llama 3.1/4 (open-source baseline)

Hindi-specific models:
- OpenHathi (Sarvam AI)
- Airavata (AI4Bharat)

**Why frontier models?** They score ~35% on culture-aware benchmarks despite being SOTA. Testing if honorifics is where they're weak.

## Success Criteria

**For the metric:**
- Formal and informal versions of the same sentence score far apart
- Correlates with human judgment (target r > 0.6)
- Can distinguish good honorific choices from bad ones

**For model evaluation:**
- Clear ranking of models (frontier vs Hindi-specific)
- Identify if models have systematic biases (always informal, or biased by gender/age/fame)
- See if frontier models that score ~35% on culture benchmarks also do poorly on honorifics

## Limitations

- **Binary only** — our data doesn't distinguish तू from तुम, so that's a limitation
- Rule-based transformations might miss irregular verbs
- Social media domain (where we get training data) might not match formal writing
- Hindi only (other Indic languages for later)

## Next Steps

1. Manually create 10-20 training pairs to validate the transformation rules
2. Build automated pair generation from the corpus
3. Train the contrastive encoder
4. Build the metric and validate with human ratings
5. Evaluate models and write up results

## Open Questions

- Rule-based transformation acceptable for the paper?
- Best Hindi morphological analyzer to use?
- Target venue for publishing?

## References

**Key papers:**
- Mukherjee et al. (EMNLP 2025) — Hindi/Bengali honorifics in LLMs
- Kumar (LREC 2014) — Hindi Politeness Corpus
- Gao et al. (EMNLP 2021) — SimCSE (contrastive learning method)
- Farhansyah et al. (ACL 2025) — Javanese honorifics (parallel work on honorific systems)

**Benchmarks:**
- OpenAI IndQA (2025) — Shows frontier models only score ~35% on culture-aware questions

**Data:**
- Hindi Politeness Corpus: https://github.com/kmi-linguistics/hindi-politeness
- Mukherjee Wiki-LLM: https://github.com/souro/honorific-wiki-llm

## Notes

**2026-01-20 Data Exploration**
- Explored both datasets. Both are binary (formal/informal). Neither distinguishes तू from तुम.
- Hindi Politeness has `ap` column (1=formal, 0=informal)
- Wiki-LLM has "Honorific" / "Non-Honorific" labels
- Both open-licensed with 45K+ examples available

**2026-01-20 Frontier Model Analysis**
- Checked OpenAI's IndQA benchmark (culture-aware, 12 Indian languages)
- Frontier models score ~35% despite being SOTA:
  - GPT-5.2: 34.9%
  - Gemini 2.5 Pro: 34.3%
  - Grok 4: 28.5%
  - (vs GPT-4 Turbo: 12.1%)
- This validates that pragmatic understanding is weak in LLMs, even frontier models
- Updated model list to test GPT-5.2, Claude Opus 4.5, Gemini 3 Pro
