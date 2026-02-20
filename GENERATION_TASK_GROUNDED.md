# Data-Grounded Generation Task Design: Hindi Second-Person Honorifics

**Author**: Subagent research (Feb 15, 2026)  
**Status**: Proposal — ready for review

---

## 1. Executive Summary

This document proposes a generation task **grounded in our existing data** — primarily the 7,094 IndicDialogue cloze probes across 23 Hindi films. Rather than fabricating scenarios from scratch, we transform real subtitle dialogue into generation prompts, using the known gold honorific as ground truth. We also identify how the Mukherjee et al. dataset and Hindi Politeness Corpus can complement this approach.

**Key insight**: Our cloze probes already contain the ingredients for a generation task. Each probe has 5 lines of real dialogue context + a target line with a known honorific. We can use the context as a seed and ask models to *generate* the next turn, then check whether the generated honorific tier matches the gold.

---

## 2. What We Actually Have

### 2.1 IndicDialogue Probes (Primary Resource)

**7,094 probes** from 23 Hindi-original films with:
- 5-line dialogue context (real subtitle text)
- A masked line where a 2nd-person pronoun was removed
- The gold pronoun

**Tier distribution**:
| Tier | Count | % |
|------|-------|---|
| आप-tier | 3,303 | 46.6% |
| तुम-tier | 2,669 | 37.6% |
| तू-tier | 1,122 | 15.8% |

**23 films** spanning genres (rom-com, thriller, drama, family). Top contributors: Hero (690), Kick (599), Firaaq (474), Om Jai Jagadish (452), Tu Jhoothi Main Makkaar (377).

**Concrete example from the data**:
```
Context (5 lines):
  क्या हाल है? क्या चल रहा है?
  चलिए चलते हैं। अपनी प्रार्थना समाप्त हो गया? - हाँ।
  इस विशेष समय पर प्रार्थना के लिए किसी भी प्रमुख कारण है?
  हाँ। मेरी मां इस समय प्रार्थना करता है। - क्यूं कर?
  मेरी मां घर वापस इस समय प्रार्थना करता है।

Gold line: "यह है .. यह केवल समय मैं उसके साथ होने के लिए मिलता है, तुम जानते हो?"
Gold pronoun: तुम
```

**Important limitations**:
- Subtitles lack speaker labels — we don't know who's speaking to whom
- These are translated subtitles (sometimes awkward Hindi — e.g., "मेरी मां प्रार्थना करता है" instead of "करती हैं")
- No relationship metadata
- Context is short (5 lines)

### 2.2 Final Validated Pairs (15 pairs)

15 formal↔informal sentence pairs from blog data. All are **greeting/wish patterns** where the formal version adds आपको. Very narrow — only covers one honorific pattern (presence/absence of आपको in greetings). Not suitable as a primary generation resource, but could serve as few-shot examples for style transfer tasks.

### 2.3 Mukherjee et al. Dataset (Available on GitHub)

**Repository**: `github.com/souro/honorific-wiki-llm`

**What it contains**:
- 20,000 annotated Wikipedia articles (10K Hindi, 10K Bengali) with honorific usage labels
- 1,000 culturally balanced entities used for LLM probing
- Controlled generation and translation tasks
- Socio-demographic attributes: gender, age group, fame, cultural origin

**Key methodology**: They asked LLMs to generate biographical text about known entities and checked whether the 3rd-person honorific matched Wikipedia norms. They used GPT-4o as an annotation tool.

**Relevance to our work**: Their entity list with socio-demographic attributes could be repurposed. Instead of generating *about* an entity (3rd person), we could create scenarios where models generate dialogue *addressed to* these entities (2nd person). For example: "Write what a fan would say when meeting [celebrity X]" — checking whether the model uses आप.

**Limitation**: Their focus is 3rd person (he/she → वह/वे). Adapting to 2nd person requires new task framing entirely.

### 2.4 Hindi Politeness Corpus (Kumar, LREC 2014)

**What it is**: ~479,000 Hindi blog posts annotated for politeness features.

**Structure** (from survey literature): Blog posts from Hindi blogosphere, annotated with sociolinguistic variables governing politeness — likely including pronoun choice, verb forms, and discourse markers like जी.

**Availability**: Not confirmed as publicly downloadable. The LREC paper describes the corpus but it may require contacting the author. This is **not yet in hand**.

**Potential use**: If obtainable, blog posts with natural 2nd-person address could provide generation prompts (e.g., advice columns, responses to questions). The large scale (479K posts) means we could filter for posts with तू/तुम/आप usage.

### 2.5 Farhansyah et al. (ACL 2025) — Methodological Reference

Their "Unggah-Ungguh" dataset for Javanese honorifics includes:
1. **Classification task**: Identify the honorific level of a sentence
2. **Machine translation**: Between Javanese honorific levels and Indonesian
3. **Conversation generation**: Generate contextually appropriate Javanese in conversation

**Critical detail**: Their dataset is a "carefully curated dataset" — it appears to be **purpose-built, not extracted from natural conversation**. Their conversation generation task uses social role descriptions to prompt generation. They trained a DistilBERT classifier (95.65% accuracy) to auto-evaluate the honorific level of generated text.

**Takeaway for us**: Their classifier-based auto-evaluation approach is directly applicable. We could train an equivalent Hindi classifier on our 7,094 cloze probes (which already have tier labels).

---

## 3. Proposed Generation Task: Dialogue Continuation with Real Seeds

### 3.1 Core Design

**Transform cloze probes into generation prompts** by using the context as a dialogue seed and asking models to generate the next turn.

**Cloze task** (existing): Given context + masked line → fill in the pronoun  
**Generation task** (new): Given context alone → generate the next dialogue line freely

The gold line from our cloze data serves as a reference for what a native speaker actually said, including which honorific tier they used.

### 3.2 Prompt Template

```
निम्नलिखित बातचीत में अगला संवाद लिखें (1-2 वाक्य):

"{context_line_1}"
"{context_line_2}"
"{context_line_3}"
"{context_line_4}"
"{context_line_5}"

अगला संवाद:
```

**No mention of honorifics, formality, or politeness.** The prompt is purely about dialogue continuation.

### 3.3 Concrete Examples from Our Data

**Example 1 — Gold tier: तुम (from Om Jai Jagadish)**
```
Prompt:
  "क्या हाल है? क्या चल रहा है?"
  "चलिए चलते हैं। अपनी प्रार्थना समाप्त हो गया? - हाँ।"
  "इस विशेष समय पर प्रार्थना के लिए किसी भी प्रमुख कारण है?"
  "हाँ। मेरी मां इस समय प्रार्थना करता है। - क्यूं कर?"
  "मेरी मां घर वापस इस समय प्रार्थना करता है।"

Gold continuation: "यह है .. यह केवल समय मैं उसके साथ होने के लिए मिलता है, तुम जानते हो?"
Gold tier: तुम
```

**Example 2 — Gold tier: आप (from Om Jai Jagadish)**
```
Prompt:
  "मेरी मां घर वापस इस समय प्रार्थना करता है।"
  "यह है .. यह केवल समय मैं उसके साथ होने के लिए मिलता है, तुम जानते हो?"
  "आप इस मिल नहीं होंगे। - क्या?"
  "वाह! 1984 मर्सिडीज, वी 8, 380 एसी, शीर्ष गति।"
  "240 किलोमीटर प्रति घंटे। वह सुंदर है।"

Gold continuation: "वहाँ किसी भी अन्य बात आप कारों के अलावा के बारे में बात कर सकते है?"
Gold tier: आप
```

**Example 3 — Gold tier: तू (from a film with intimate/informal dialogue)**
```
[Would be selected from probes where gold_pronoun ∈ {तू, तुझे, तेरा, तेरी, तेरे}]
```

### 3.4 Sampling Strategy

From 7,094 probes, sample **300 probes** (100 per tier), stratified by:
- **Tier**: 100 तू, 100 तुम, 100 आप
- **Movie**: Spread across films to avoid genre/style confounds
- **Context quality**: Manual filtering to exclude:
  - Contexts with no clear conversational flow
  - Contexts with translation artifacts that make the dialogue incomprehensible
  - Contexts where the gold line doesn't naturally follow (subtitle alignment issues)

### 3.5 Why This Works

1. **Grounded in real data**: Every prompt comes from actual Hindi film dialogue
2. **Gold standard exists**: The original subtitle tells us what a native speaker actually said, including their honorific choice
3. **Complements cloze**: Same underlying data, different cognitive demand (production vs. selection)
4. **No priming**: The prompt never mentions honorifics or formality
5. **Natural context**: Film dialogue reflects actual Hindi speech patterns in various social situations

### 3.6 Addressing the Speaker Label Problem

Subtitles lack speaker labels, which means the model doesn't know *who* is speaking. This is actually a **feature, not a bug** for our purposes:

- The context establishes a *register* through the pronouns and verb forms already present in the 5 lines
- A competent Hindi speaker can infer the appropriate register from context alone
- We're testing whether models can do the same — pick up on pragmatic cues and maintain register consistency

**Validation**: For the 300 sampled probes, have 2 native speakers read the context and predict the expected tier. If they agree with the gold tier (κ ≥ 0.70), the probe is valid for generation evaluation. Discard probes where context is insufficient to determine tier.

---

## 4. Complementary Task: Style-Conditioned Rewriting

### 4.1 Design

Take the gold line from our probes and ask models to rewrite it at a different honorific tier.

**Prompt**:
```
निम्नलिखित वाक्य को फिर से लिखें, जैसे कोई अपने {relation} से बात कर रहा हो:

मूल: "{gold_line}"

नया वाक्य:
```

Where `{relation}` implicitly signals the tier:
- "बॉस" / "ससुर जी" → आप tier expected
- "दोस्त" / "भाई" → तुम tier expected  
- "छोटा भाई" / "बचपन का यार" → तू tier expected

### 4.2 Example from Our Data

```
Original (तुम-tier): "जय, तुम देर से कर रहे हैं!"
Prompt: Rewrite as if speaking to your "बॉस"
Expected: "जय सर, आप देर से कर रहे हैं!" (or similar आप-tier reformulation)
```

### 4.3 Scoring

- **Tier accuracy**: Did the rewritten sentence use the expected tier?
- **Meaning preservation**: Does the rewrite preserve the semantic content?
- **Verb agreement**: Does the verb form match the pronoun?
- **Naturalness**: Does it sound like natural Hindi? (human-rated subset)

### 4.4 Grounding

Every stimulus comes from our real data. We're not inventing sentences — we're asking models to transform real dialogue between registers.

---

## 5. Third Task: Entity-Grounded Address Generation (Using Mukherjee Data)

### 5.1 Design

Leverage the 1,000 culturally balanced entities from Mukherjee et al.'s dataset (with gender, age, fame, cultural origin attributes). Create 2nd-person address scenarios:

```
{entity_name} एक {entity_description} हैं। 
एक {speaker_role} {entity_name} से मिलता है। {speaker_role} क्या कहेगा?

केवल {speaker_role} का संवाद लिखें (1-2 वाक्य)।
```

**Example**:
```
सचिन तेंदुलकर एक प्रसिद्ध क्रिकेटर हैं।
एक युवा प्रशंसक सचिन तेंदुलकर से मिलता है। प्रशंसक क्या कहेगा?

Expected: आप-tier (addressing a famous elder)
```

### 5.2 Why It's Grounded

- Entities come from a published, peer-reviewed dataset with established socio-demographic attributes
- The expected tier can be derived from the attributes (age, fame, status) using sociolinguistic principles from Kumar (2014)
- We can compare 2nd-person honorific patterns against the 3rd-person patterns Mukherjee et al. already documented — do the same biases (gender, fame) manifest in direct address?

### 5.3 Scale

~200 scenarios from the 1,000 entities, sampling across demographic categories. Each entity gets one scenario (one speaker role). Speaker roles vary to create different power dynamics.

---

## 6. Scoring Methodology (All Tasks)

### 6.1 Automated Tier Extraction

```python
TU = {'तू','तुझे','तुझसे','तुझको','तुझमें','तेरा','तेरी','तेरे'}
TUM = {'तुम','तुम्हें','तुम्हारा','तुम्हारी','तुम्हारे','तुमसे','तुमको','तुमने'}
AAP = {'आप','आपको','आपका','आपकी','आपके','आपसे','आपने','आपमें'}
```

Already validated — these are the exact forms from our probe extraction pipeline.

### 6.2 Trained Classifier (Farhansyah-inspired)

Train a Hindi honorific tier classifier on our 7,094 probes:
- Input: sentence text
- Output: तू / तुम / आप tier
- Architecture: fine-tuned IndicBERT or MuRIL
- Training data: our gold lines with tier labels

This handles cases where the model generates an honorific form not in our regex lists (e.g., dialectal forms, verb-only tier markers like कीजिए without an explicit pronoun).

### 6.3 Metrics

| Metric | Description | Tasks |
|--------|-------------|-------|
| **Tier accuracy** | % of outputs matching expected tier | All |
| **Tier distribution** | Distribution of तू/तुम/आप across outputs | All |
| **Formality bias** | P(आप) / expected P(आप) — ratio > 1 = over-formal | Continuation |
| **Avoidance rate** | % of outputs with no 2nd-person pronoun at all | All |
| **Verb agreement** | % of outputs where verb form matches pronoun tier | All |
| **Cross-tier accuracy** | Confusion matrix: which tiers get confused? | All |
| **Register maintenance** | In continuation: does generated tier match the tier established in context? | Continuation |

### 6.4 Human Evaluation (30% subset)

For ~90 outputs (30 per tier):
1. **Appropriateness** (1-5): Is the honorific tier fitting for the context?
2. **Naturalness** (1-5): Does it sound like natural Hindi dialogue?
3. **Semantic relevance** (1-3): Does the continuation logically follow the context?

---

## 7. What We Need But Don't Have (Gaps)

### 7.1 Hindi Politeness Corpus (Kumar, LREC 2014)
- **Status**: Not confirmed as publicly downloadable
- **What it would give us**: ~479K blog posts with politeness annotations — potential source of generation prompts with natural 2nd-person address
- **Action**: Contact author or search ELRA/LDC catalogue
- **Workaround if unavailable**: Our IndicDialogue data is sufficient for the primary task

### 7.2 Speaker Labels for IndicDialogue
- **Status**: Not available in subtitle data
- **What it would give us**: Ability to track per-character honorific consistency
- **Partial workaround**: Use film scripts (if available) or manual annotation of a subset to add speaker labels
- **Alternative**: Frame the task as register maintenance (does the model continue the *established* register?) rather than character-specific address

### 7.3 Relationship Metadata
- **Status**: Not available
- **What it would give us**: Ground truth for *why* a particular tier is used
- **Partial workaround**: The 300-probe annotation pass can include annotator judgment of relationship type (parent-child, friends, strangers, etc.)

---

## 8. Other Hindi Dialogue Corpora (Research Findings)

| Corpus | Description | Relevance |
|--------|-------------|-----------|
| **HDRS Corpus** (Malviya et al.) | Hindi Dialogue Restaurant Search — task-oriented dialogue | Low: task-oriented, likely all formal register |
| **Hindi Speech Recognition Dataset** (HuggingFace, ud-nlp) | 760 hours, 1000+ speakers, telephone dialogues | Medium: natural conversation with potential formality variation, but audio-only |
| **FutureBee Hindi Conversation** | Real-world unscripted conversations with metadata | Medium: has speaker metadata, but commercial dataset |
| **IndicDialogue** (our source) | 23 Hindi films, subtitles | Already using |
| **DIWALI** (Sahoo et al., EMNLP 2025) | Cultural text adaptation for India | Low: not dialogue-focused |

**Bottom line**: No publicly available Hindi dialogue corpus with speaker metadata AND formality/honorific annotations exists. This is itself a contribution — our annotated probe set would be the first such resource.

---

## 9. Comparison: Our Approach vs. Alternatives

| Approach | Data Source | Grounded? | Pros | Cons |
|----------|-----------|-----------|------|------|
| **Dialogue continuation** (proposed) | IndicDialogue probes | ✅ Real data | Natural, complementary to cloze, gold exists | Translation artifacts, no speaker labels |
| **Style-conditioned rewriting** (proposed) | IndicDialogue gold lines | ✅ Real data | Tests productive transformation, clear scoring | Partially synthetic (relation prompt is invented) |
| **Entity-grounded address** (proposed) | Mukherjee et al. entities | ✅ Published data | Links to prior work, tests socio-demographic biases | Scenarios are synthetic, entities are 3rd→2nd person adaptation |
| **Pure DCT scenarios** (GENERATION_TASK_DESIGN.md) | Invented scenarios | ❌ Synthetic | Clean control, systematic variables | Not grounded in real data, may not reflect actual usage patterns |
| **Farhansyah-style conversation** | Social role descriptions | ❌ Synthetic | Directly comparable to Javanese work | Same as above |

---

## 10. Recommended Implementation Plan

### Phase 1: Dialogue Continuation (Weeks 1-2)
1. Sample 300 probes (100/tier) from IndicDialogue data
2. Manual quality filter: remove probes with bad context or translation artifacts
3. Have 2 annotators validate expected tier from context alone (κ ≥ 0.70)
4. Run on target models (GPT-5.2, Claude Opus 4.5, Claude Sonnet 4, Gemini 2.5 Pro)
5. Extract tiers, compute metrics

### Phase 2: Style-Conditioned Rewriting (Week 3)
1. Select 90 gold lines (30/tier) with clear, natural Hindi
2. Create 3 rewrite prompts per line (one for each target tier) = 270 total
3. Run and evaluate

### Phase 3: Entity-Grounded Address (Week 3-4, if Mukherjee data is cloned)
1. Clone `souro/honorific-wiki-llm`, extract entity list with attributes
2. Create 200 address scenarios
3. Run and evaluate

### Phase 4: Train Hindi Tier Classifier (Parallel)
1. Fine-tune MuRIL on our 7,094 gold lines with tier labels
2. Validate on held-out set
3. Use as automated evaluator for generation outputs

---

## 11. How This Complements the Cloze Task

| Dimension | Cloze Task | Dialogue Continuation | Style Rewriting | Entity Address |
|-----------|-----------|----------------------|-----------------|----------------|
| Tests | Recognition | Production + register tracking | Productive transformation | Socio-pragmatic inference |
| Data source | IndicDialogue (same probes) | IndicDialogue (same probes) | IndicDialogue gold lines | Mukherjee entities |
| Grounded | ✅ | ✅ | ✅ | ✅ (published data) |
| Priming risk | Low (fill-in-blank) | None (pure continuation) | Medium (relation mentioned) | Medium (entity description) |
| Failure mode caught | Wrong tier selection | Over-formality default, avoidance | Can't transform between registers | Socio-demographic bias |

**The complete story**: A model that aces cloze but fails continuation has comprehension without production. A model that can continue but can't rewrite lacks productive control. A model biased on entities reveals socio-pragmatic blindness.

---

## 12. References

- Farhansyah, M. R. et al. (2025). Do Language Models Understand Honorific Systems in Javanese? *ACL 2025*. — Classifier-based evaluation approach; curated (not natural) dataset
- Kumar, R. (2014). Politeness in Hindi: A Corpus-Based Study. *LREC 2014*. — 479K blog posts; sociolinguistic variables for Hindi politeness
- Mukherjee, S. et al. (2025). Women, Infamous, and Exotic Beings. *EMNLP 2025*. — 3rd-person honorifics; entity data at `github.com/souro/honorific-wiki-llm`
- Zhao, H. & Hawkins, R. D. (2025). Comparing human and LLM politeness strategies in free production. *EMNLP 2025*. — Over-formality bias in LLMs
- Blum-Kulka, S. et al. (1989). *Cross-Cultural Pragmatics*. — DCT methodology
- Brown, P. & Levinson, S. (1987). *Politeness*. — Power, distance, imposition framework
