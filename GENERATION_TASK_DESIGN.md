# Generation Task Design: Hindi Second-Person Honorifics

## 1. Motivation & Research Gap

The cloze task (comprehension) tests whether models can *select* the correct pronoun given context. The generation task tests something harder and more ecologically valid: **when models freely produce Hindi dialogue, do they use appropriate second-person honorific forms (तू/तुम/आप), or do they exhibit systematic biases?**

This matters because in real deployment (chatbots, translation, creative writing), models generate text—they don't fill blanks. A model might ace cloze tests but still default to आप in every generated utterance.

### Prior Work on Honorific Generation Evaluation

| Study | Language | Task Type | Key Finding |
|-------|----------|-----------|-------------|
| Farhansyah et al. (ACL 2025) | Javanese | Conversation generation with honorific personas | LMs show bias toward Ngoko (informal); used fine-tuned classifier to auto-evaluate generated honorific level |
| Zhao & Hawkins (EMNLP 2025) | English | Free production of polite speech + human evaluation | LLMs over-rely on negative politeness strategies even in positive contexts; humans prefer LLM outputs but subtle misalignment exists |
| Mukherjee et al. (EMNLP 2025) | Hindi/Bengali | 3rd-person honorific analysis in Wikipedia-style generation | LLMs show gender/notability-based honorific bias in 3rd person |
| Kumar (LREC 2014) | Hindi | Hindi Politeness Corpus | Established sociolinguistic variables governing Hindi politeness |

**Critical gap**: No study has evaluated LLM *generation* of Hindi second-person honorifics in conversational contexts. Mukherjee et al. explicitly flag this: *"honorific dynamics can differ substantially in second-person usage and more casual or spoken communication."*

---

## 2. Design Principles

### 2.1 Avoid Priming the Target Variable

The biggest methodological risk: if the prompt mentions "honorifics," "formality," or "politeness," the model is primed. The prompt must elicit dialogue *naturally* without telegraphing what we're measuring.

**Anti-patterns to avoid:**
- "Write a polite conversation between..."
- "Use appropriate honorifics..."
- "A formal dialogue where..."
- Any meta-linguistic instruction about pronoun choice

**Design principle**: Describe the *social situation*, not the *linguistic behavior*. Let the model infer the right register.

### 2.2 Control Social Variables Systematically

Drawing from Brown & Levinson (1987) and Kumar (2014), Hindi honorific choice is governed by:

| Variable | Levels | Effect on Honorific |
|----------|--------|-------------------|
| **Relative age** | Older → Younger, Peer, Younger → Older | तू (intimate/younger), तुम (peer/moderate), आप (elder/respect) |
| **Power/authority** | Superior → Subordinate, Equal, Subordinate → Superior | Higher power differential → आप |
| **Intimacy/solidarity** | Strangers, Acquaintances, Close friends, Family | Higher intimacy → तुम/तू |
| **Setting formality** | Formal (office, court), Semi-formal, Informal (home, street) | Formal settings push toward आप |
| **Emotional valence** | Neutral, Angry, Affectionate, Pleading | Anger can shift to तू (derogatory); affection to तू (intimate) |

### 2.3 Scoring Approach

Free-form generation cannot be scored with exact match. We need a multi-layer evaluation:

1. **Pronoun extraction** (automated): Regex/morphological parser to extract all 2nd-person pronouns and verb forms from generated text
2. **Tier classification** (automated): Map extracted forms to तू-tier / तुम-tier / आप-tier
3. **Appropriateness judgment** (human annotation): Is the chosen tier appropriate for the scenario?
4. **Verb agreement check** (automated): Does the verb conjugation match the chosen pronoun? (e.g., आप + करो is a mismatch; should be आप + करें/कीजिए)
5. **Consistency check** (automated): Within a single character's dialogue, do they maintain consistent pronoun tier?

For **automated appropriateness scoring**, we can use majority-vote from human annotations to establish gold labels per scenario, then measure model alignment. Farhansyah et al. (ACL 2025) used a fine-tuned classifier (Javanese DistillBERT, 95.65% accuracy) to auto-evaluate honorific level of generated text—we could train an equivalent Hindi classifier on the Hindi Politeness Corpus or our cloze probe data.

---

## 3. Proposed Task Designs

### Task A: Discourse Completion Task (DCT) — Scenario-Based Single-Turn Generation

**Inspired by**: Discourse Completion Tasks from interlanguage pragmatics (Blum-Kulka et al., 1989; Labben, 2016), adapted for LLM evaluation. Also draws on Farhansyah et al.'s (ACL 2025) scenario-based conversation generation.

**Design**: Present a social scenario in Hindi, then ask the model to produce what one character would say to another. The scenario establishes the relationship implicitly.

**Prompt Template** (Hindi, no honorific priming):

```
स्थिति: {situation_description}

{speaker_name} {speaker_description} {addressee_name} से {action_context}। {speaker_name} क्या कहेंगे/कहेगा/कहेगी?

केवल {speaker_name} का संवाद लिखें (1-3 वाक्य)।
```

**Example Instantiations**:

**Scenario 1 — तू expected (intimate/peer-inferior)**
```
स्थिति: राहुल (25 साल) अपने छोटे भाई अमन (18 साल) को देर रात घर आने पर डाँटना चाहता है।

राहुल अमन से नाराज़ है। राहुल क्या कहेगा?

केवल राहुल का संवाद लिखें (1-3 वाक्य)।
```
*Expected*: तू कहाँ था? / तुझे पता है कितनी रात हो गई?

**Scenario 2 — तुम expected (peer/moderate intimacy)**
```
स्थिति: प्रिया और नेहा कॉलेज में एक साथ पढ़ती हैं और अच्छी दोस्त हैं। कल परीक्षा है।

प्रिया नेहा को पढ़ाई के लिए बुलाना चाहती है। प्रिया क्या कहेगी?

केवल प्रिया का संवाद लिखें (1-3 वाक्य)।
```
*Expected*: तुम आज शाम को मेरे घर आ जाओ, साथ में पढ़ेंगे।

**Scenario 3 — आप expected (formal/respect)**
```
स्थिति: एक नया कर्मचारी अपने पहले दिन अपने विभाग प्रमुख श्री शर्मा से मिलता है।

कर्मचारी श्री शर्मा से अपना परिचय देना चाहता है। कर्मचारी क्या कहेगा?

केवल कर्मचारी का संवाद लिखें (1-3 वाक्य)।
```
*Expected*: नमस्कार सर, मैं [नाम], आज से आपके विभाग में काम करूँगा।

**Variables manipulated** (full factorial not feasible; sample strategically):

| Variable | Levels |
|----------|--------|
| Expected tier | तू / तुम / आप |
| Relationship type | Family (parent-child, siblings, spouses), Professional (boss-employee, colleagues), Social (friends, strangers, shopkeeper-customer), Institutional (teacher-student, doctor-patient) |
| Direction | Speaker is higher-status → lower, Equal, Lower → higher |
| Emotional context | Neutral, Angry, Affectionate, Requesting, Urgent |

**Target**: ~120 scenarios (40 per expected tier), balanced across relationship types and directions.

**Scoring**:
1. Extract pronoun tier from generated dialogue
2. Compare to expected tier (human-validated gold)
3. Metrics: Tier accuracy, tier confusion matrix, formality bias ratio (proportion of आप across all scenarios)
4. Verb agreement accuracy

**Strengths**: Clean, controlled, one variable at a time. Directly comparable to cloze task (same scenarios can be used for both). Mirrors established DCT methodology in pragmatics.

**Limitations**: Single-turn is less naturalistic than multi-turn dialogue.

---

### Task B: Multi-Turn Dialogue Continuation

**Inspired by**: Dialogue continuation tasks in NLG evaluation; Zhao & Hawkins (EMNLP 2025) open-ended production design.

**Design**: Provide the first 2-3 turns of a conversation (from IndicDialogue or hand-crafted) that *implicitly* establishes the relationship, then ask the model to continue. The seed turns use the *correct* honorific tier, and we measure whether the model maintains it.

**Prompt Template**:

```
निम्नलिखित बातचीत को 2-3 और संवाद लिखकर आगे बढ़ाएँ।

{speaker_A}: {turn_1}
{speaker_B}: {turn_2}
{speaker_A}: {turn_3}

आगे लिखें:
```

**Example** (तुम tier established in seed):
```
निम्नलिखित बातचीत को 2-3 और संवाद लिखकर आगे बढ़ाएँ।

विकास: यार, तुम कल की पार्टी में आ रहे हो?
सचिन: हाँ, मैं आऊँगा। तुमने किसे बुलाया है?
विकास: अभी तक तो बस हम लोग हैं। तुम अपने रूममेट को भी ले आना।

आगे लिखें:
```
*Expected*: Model continues with तुम-tier pronouns and matching verb forms.

**Variant — Tier Shift Test**: Some scenarios involve a *status change* mid-conversation (e.g., discovering someone is much older, or transitioning from professional to personal). Seed turns use one tier; the situation demands a shift. Do models adapt?

**Example** (tier shift: तुम → आप):
```
निम्नलिखित बातचीत को 2-3 और संवाद लिखकर आगे बढ़ाएँ।

रमेश: अरे, तुम भी इस कॉन्फ़्रेंस में आए हो?
अनिल: हाँ, मैं यहाँ पेपर प्रेज़ेंट करने आया हूँ।
रमेश: अच्छा! तुम किस यूनिवर्सिटी से हो?
अनिल: मैं IIT दिल्ली से हूँ। वैसे मैं प्रोफ़ेसर अनिल कुमार हूँ, CS विभाग का।

आगे लिखें:
```
*Expected*: रमेश should shift to आप after learning अनिल is a professor.

**Scoring**:
1. **Tier maintenance**: Does the model maintain the established tier? (In non-shift scenarios)
2. **Tier adaptation**: Does the model shift appropriately? (In shift scenarios)
3. **Verb agreement consistency**: Across all generated turns
4. **Avoidance detection**: Does the model rephrase to dodge direct address entirely? (e.g., using passive voice, dropping pronouns)

**Target**: ~60 dialogue continuations (20 per tier × 3 tiers for maintenance, + 15 tier-shift scenarios).

**Strengths**: Tests consistency and contextual tracking, more naturalistic. The tier-shift variant is novel and tests deeper pragmatic understanding.

**Limitations**: Seed turns partially prime the model (it sees the "answer"). However, this is a *feature* for the maintenance test—we're testing whether models can *sustain* a register, not just initiate one.

---

### Task C: Role-Play Dialogue Generation (Full Conversation)

**Inspired by**: Farhansyah et al.'s (ACL 2025) Task 4 (conversation generation with honorific personas); role-playing evaluation benchmarks (Chen et al., NAACL 2025).

**Design**: Give the model two character descriptions and a topic. Ask it to generate a full 4-6 turn conversation between them. This is the most open-ended task and tests whether models can *simultaneously* manage different honorific tiers for different speakers.

**Prompt Template**:

```
दो पात्रों के बीच एक छोटी बातचीत (4-6 संवाद) लिखें।

पात्र 1: {character_1_description}
पात्र 2: {character_2_description}
विषय: {topic}

बातचीत:
```

**Example** (asymmetric: student uses आप, teacher uses तुम):
```
दो पात्रों के बीच एक छोटी बातचीत (4-6 संवाद) लिखें।

पात्र 1: रवि, 20 साल का कॉलेज छात्र
पात्र 2: डॉ. मिश्रा, 55 साल के प्रोफ़ेसर, रवि के गाइड
विषय: रवि का प्रोजेक्ट जमा करने में देरी

बातचीत:
```
*Expected*: रवि → डॉ. मिश्रा: आप-tier; डॉ. मिश्रा → रवि: तुम-tier

**Example** (symmetric तू — close friends):
```
दो पात्रों के बीच एक छोटी बातचीत (4-6 संवाद) लिखें।

पात्र 1: अर्जुन, 16 साल, स्कूल का छात्र
पात्र 2: कबीर, 16 साल, अर्जुन का बचपन का दोस्त
विषय: क्रिकेट मैच में हार

बातचीत:
```
*Expected*: Both use तू-tier with each other.

**Example** (asymmetric with emotional complexity — बहू and सास):
```
दो पात्रों के बीच एक छोटी बातचीत (4-6 संवाद) लिखें।

पात्र 1: सुनीता, 28 साल, बहू
पात्र 2: कमला देवी, 60 साल, सास
विषय: रात के खाने की तैयारी

बातचीत:
```
*Expected*: सुनीता → कमला देवी: आप-tier; कमला देवी → सुनीता: तुम-tier (or even तू in some families)

**Variables**:

| Variable | Example Levels |
|----------|---------------|
| Symmetry | Symmetric (both same tier) vs. Asymmetric (different tiers) |
| Expected tiers | तू↔तू, तुम↔तुम, आप↔आप, आप↔तुम, आप↔तू, तुम↔तू |
| Relationship | 12 types (see list below) |
| Topic valence | Neutral, Conflict, Celebration, Request |

**Relationship types** (balanced across tiers):
- तू expected: childhood friends, siblings (close age), parent→young child, romantic partners (informal)
- तुम expected: college friends, colleagues (same level), older sibling→younger, teacher→student
- आप expected: employee→boss, student→teacher, बहू→सास, stranger→stranger, customer→shopkeeper, patient→doctor

**Target**: ~80 scenarios.

**Scoring**:
1. **Per-character tier accuracy**: For each character, does their pronoun tier match expectation?
2. **Asymmetry handling**: In asymmetric scenarios, does the model correctly differentiate the two speakers' tiers?
3. **Verb agreement**: Per character
4. **Tier entropy**: Across all scenarios, what's the distribution of generated tiers? (Measures over-formality bias)
5. **Avoidance rate**: Proportion of scenarios where the model avoids 2nd-person pronouns entirely

**Strengths**: Most naturalistic. Tests the hardest case: *asymmetric* honorific management (both speakers in one conversation using different tiers). This is the signature contribution—no prior work tests this for Hindi.

**Limitations**: Harder to score (need to attribute utterances to speakers). More variance in outputs.

---

## 4. Complementarity with the Cloze Task

| Dimension | Cloze Task | Generation Task |
|-----------|-----------|-----------------|
| What it tests | Recognition / selection | Production / generation |
| Data source | Real dialogue (IndicDialogue) | Controlled scenarios (synthetic prompts, natural outputs) |
| Control | Natural distribution of contexts | Systematic manipulation of variables |
| Ecological validity | High (real speech) | Moderate (prompted scenarios) |
| Scoring | Exact match / tier match | Multi-metric (see above) |
| Failure mode detected | "Doesn't know the right answer" | "Knows but doesn't produce" or "defaults to one tier" |
| Bias measurement | Distribution across ambiguous probes | Distribution across controlled scenarios |

The two tasks together tell a complete story:
- **Cloze + Generation agree** → Model truly understands honorific pragmatics
- **Cloze good, Generation biased** → Model has comprehension but production defaults (likely RLHF-induced politeness bias)
- **Cloze bad, Generation varied** → Model guesses but has learned some surface patterns
- **Both bad** → Fundamental gap in Hindi honorific competence

---

## 5. Expected Failure Modes

Based on Farhansyah et al.'s (ACL 2025) findings (Javanese models biased toward Ngoko) and Zhao & Hawkins (EMNLP 2025) (English LLMs over-use negative politeness), we predict:

1. **आप-defaulting** (over-formality): RLHF training rewards politeness → models default to आप in ambiguous or even clearly informal scenarios. This is the Hindi equivalent of the "negative politeness bias" Zhao & Hawkins found.

2. **Avoidance**: Models rephrase to avoid 2nd-person pronouns entirely (using passive constructions, dropping subjects). This is a "safe" strategy that obscures honorific competence.

3. **Asymmetry collapse**: In Task C, both speakers use the *same* tier (likely आप↔आप) even when the scenario demands asymmetry. This would indicate the model doesn't track speaker-addressee relationships within a conversation.

4. **Verb agreement mismatch**: Model picks आप but conjugates verbs for तुम (e.g., "आप करो" instead of "आप करें/कीजिए"). This is a morphosyntactic error distinct from pragmatic failure.

5. **तू avoidance**: Models may *never* generate तू-tier, even in appropriate contexts (siblings, close friends, parent→child), because तू is perceived as rude out of context and training data may penalize it.

6. **Inconsistency within a turn**: A single character's dialogue mixing tiers (e.g., "आप कहाँ जा रहे हो?" — आप pronoun + तुम verb).

---

## 6. Methodology Details

### 6.1 Scenario Construction

All scenarios should be validated by 2+ native Hindi speakers for:
- Is the expected tier unambiguous? (Mark ambiguous ones separately — these become bias-measurement probes)
- Is the scenario culturally authentic?
- Is the prompt natural and non-priming?

Target inter-annotator agreement: Cohen's κ ≥ 0.75 on expected tier.

### 6.2 Model Evaluation Protocol

| Parameter | Value |
|-----------|-------|
| Models | GPT-5.2, Claude Opus 4.5, Claude Sonnet 4, Gemini 2.5 Pro |
| Temperature | 0.0 (determinism) and 0.7 (natural variation) |
| Runs per scenario | 5 per temperature setting |
| Max tokens | 200 (Task A), 300 (Task B), 500 (Task C) |
| System prompt | None (default behavior) |
| Language of prompt | Hindi (Devanagari) throughout |

### 6.3 Automated Extraction Pipeline

```python
# Pronoun tier extraction (simplified)
TU_FORMS = {'तू', 'तुझे', 'तुझसे', 'तुझको', 'तुझमें', 'तेरा', 'तेरी', 'तेरे'}
TUM_FORMS = {'तुम', 'तुम्हें', 'तुम्हारा', 'तुम्हारी', 'तुम्हारे', 'तुमसे', 'तुमको', 'तुमने'}
AAP_FORMS = {'आप', 'आपको', 'आपका', 'आपकी', 'आपके', 'आपसे', 'आपने', 'आपमें'}

# Verb agreement patterns (simplified)
TU_VERBS = r'(करता|जाता|आता|बोलता|कर|जा|आ|बोल|करेगा)\b'  # singular informal
TUM_VERBS = r'(करो|जाओ|आओ|बोलो|करते|जाते|आते|करोगे)\b'  # plural informal
AAP_VERBS = r'(करें|कीजिए|जाएँ|आइए|बोलिए|करेंगे|जाएँगे)\b'  # formal/respectful
```

### 6.4 Human Evaluation Protocol

For a subset (~30% of generated outputs), 2 native Hindi annotators rate:
1. **Appropriateness** (1-5): Is the honorific tier appropriate for the scenario?
2. **Naturalness** (1-5): Does the dialogue sound like natural Hindi conversation?
3. **Consistency** (binary): Does the character maintain a consistent register?

### 6.5 Ambiguous Scenarios as Bias Probes

Some scenarios are deliberately ambiguous (e.g., new colleague of similar age — could be तुम or आप). For these, there's no "correct" answer, but the *distribution* of model choices reveals bias. Compare against:
- Human baseline (collect human responses to same scenarios)
- Natural distribution from IndicDialogue corpus

---

## 7. Analysis Plan

### Primary Analyses
1. **Tier accuracy by task**: Proportion of scenarios where model uses expected tier (Tasks A, B, C separately)
2. **Formality bias index**: (count of आप-tier outputs) / (total outputs) — compare to expected base rate
3. **Asymmetry score** (Task C only): Proportion of asymmetric scenarios where model correctly differentiates speaker tiers
4. **Verb agreement rate**: Proportion of pronoun-verb pairs with correct morphological agreement
5. **Avoidance rate**: Proportion of outputs with no 2nd-person pronouns at all

### Secondary Analyses
6. **Cross-model comparison**: Bias patterns across GPT / Claude / Gemini
7. **Temperature effect**: Does higher temperature increase tier diversity or just noise?
8. **Cloze-generation correlation**: Per-model, does cloze accuracy predict generation appropriateness?
9. **Scenario variable effects**: Which variables (age gap, power, intimacy) drive the most model errors?

---

## 8. References

- Blum-Kulka, S., House, J., & Kasper, G. (1989). *Cross-Cultural Pragmatics: Requests and Apologies*. Ablex. [Foundational DCT methodology]
- Brown, P., & Levinson, S. (1987). *Politeness: Some universals in language usage*. Cambridge University Press. [Politeness theory: power, distance, imposition]
- Farhansyah, M. R., Darmawan, I., et al. (2025). Do Language Models Understand Honorific Systems in Javanese? *ACL 2025*. [Javanese honorific generation task, classifier-based evaluation]
- Kumar, R. (2014). Politeness in Hindi: A Corpus-Based Study. *LREC 2014*. [Hindi politeness variables]
- Labben, A. (2016). Reconsidering the development of the discourse completion test in interlanguage pragmatics. *Pragmatics*, 26(1). [DCT methodology critique & best practices]
- Liu, X. & Kobayashi, I. (2022). Japanese Honorific Corpus. [Comparative honorific corpus design]
- Mukherjee, S., Mehta, A., & Saha, S. (2025). Women, Infamous, and Exotic Beings: A Comparative Study of Honorific Usages in Wikipedia and LLMs for Bengali and Hindi. *EMNLP 2025*. [3rd-person honorific bias in LLMs]
- Zhao, H. & Hawkins, R. D. (2025). Comparing human and LLM politeness strategies in free production. *EMNLP 2025*. [LLMs over-use negative politeness; scenario-based elicitation methodology]

---

## 9. Recommended Implementation Order

1. **Start with Task A (DCT)** — simplest to implement, score, and interpret. Build 40 scenarios per tier (120 total). Validate with 2 annotators.
2. **Add Task C (Role-Play)** — the most novel contribution (asymmetric honorific management). Build 80 scenarios. This is what reviewers will find most interesting.
3. **Task B (Continuation)** — can draw seed dialogues from IndicDialogue probes, creating a natural bridge from the cloze task. Add tier-shift scenarios as an extension.
4. **Run all three tasks** on the same models to enable cross-task correlation analysis.

**Estimated effort**: ~2 weeks for scenario construction + validation, ~1 week for model runs + extraction pipeline, ~1 week for human annotation of subset.
