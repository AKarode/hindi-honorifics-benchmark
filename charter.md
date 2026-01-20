# Hindi Honorific Evaluation Benchmark

Adit | Prof. Malihe Alikhani | Updated Jan 20, 2026

---

## What's the problem?

Mukherjee et al. (EMNLP 2025) showed that LLMs mess up Hindi honorifics, but they just described the problem—no one's built a way to automatically measure it. That's what this project does.

Why it matters: Hindi has 600M+ speakers and honorifics aren't optional like English "sir/ma'am." Using तू when you should use आप is genuinely rude. If we're deploying LLMs in Hindi, they need to get this right.

Existing metrics (BERTScore, COMET) measure semantic similarity, not social appropriateness. We need something new.

## Research question

Can we build a metric that scores whether LLM-generated Hindi uses the right honorific level?

Also want to know:
- Do models have biases (e.g., always defaulting to informal)?
- Do they treat different social groups differently (gender, age)?
- Is there a gap between what models can *recognize* as correct vs what they actually *produce*?

## Scope

Focusing on binary: आप (formal) vs तुम/तू (informal). Both our datasets only mark this distinction—they don't separate तू from तुम, so we can't either. That's a limitation we'll note.

Second-person only. Hindi text in Devanagari. No code-mixing for now.

## Data

**Hindi Politeness Corpus (v0.2):** ~56K examples from social media. Has an `ap` column where 1=formal (uses आप), 0=informal. Also has columns for other politeness markers (जी, verb forms, etc.).

**Wiki-LLM (Mukherjee et al.):** 10K Hindi Wikipedia articles with metadata—gender, age, fame, role, etc.

Both explored, both binary, both open-licensed.

## Approach

1. Take formal sentences (ap=1) and transform them to informal versions
   - Change pronouns: आप → तुम
   - Change verbs: बैठिए → बैठो
   - Drop honorific जी

2. Train a contrastive encoder so same-meaning sentences with different registers end up far apart in embedding space

3. Use cosine similarity as the metric—compare LLM output to an appropriate reference

Need to manually do 10-20 transformations first to make sure the rules work before automating.

## Two evaluation tasks

**Recognition:** Show the model two options (formal/informal) with a social context. Ask which is appropriate. Simple accuracy measure. Tests whether the model *knows* the right answer.

**Production:** Give context, ask model to generate a response. Score it with our metric. Tests whether the model can actually *produce* the right form.

Comparing these tells us if there's a comprehension-production gap—models might know the answer but fail to generate it.

## What we'll analyze

- Overall scores on both tasks
- Breakdown by social category (gender, age, fame) using Wiki-LLM metadata
- Error types: pronoun wrong? verb wrong? both?
- Error direction: do models skew informal or formal?

## Models to test

Frontier: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Llama 4
Hindi-specific: OpenHathi, Airavata

Curious if Hindi-specific models do better despite being smaller.

## Limitations

- Binary only (can't distinguish तू from तुम)
- Training data is social media, might not generalize to formal writing
- Rule-based transformations might miss edge cases
- Hindi only for now

## Next steps

1. ~~Explore data~~ done
2. **Manually create 10-20 training pairs** ← current
3. Build pair generation pipeline
4. Create recognition items (300-500 MCQ)
5. Create production prompts
6. Train encoder
7. Validate metric against human judgments
8. Run evaluation
9. Write paper

## Open questions for professor

- Is rule-based transformation okay or should we do something else?
- Any Hindi morphological analyzer recommendations?
- Target venue?

## References

- Mukherjee et al. (EMNLP 2025) — the paper showing the problem exists
- Kumar (LREC 2014) — Hindi Politeness Corpus
- Gao et al. (EMNLP 2021) — SimCSE, the contrastive learning method we're adapting
- Farhansyah et al. (ACL 2025) — similar work on Javanese honorifics

Data: [hindi-politeness](https://github.com/kmi-linguistics/hindi-politeness) | [wiki-llm](https://github.com/souro/honorific-wiki-llm)

---

## Notes

**Jan 20** — Explored both datasets. Both are binary. Hindi Politeness uses `ap` column (1/0). Wiki-LLM uses "Honorific"/"Non-Honorific" labels. Neither distinguishes तू from तुम so we're stuck with binary. Added two-task design (recognition + production) to measure comprehension-production gap.
