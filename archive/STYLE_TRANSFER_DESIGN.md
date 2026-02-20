# Style/Register Transfer Task Design: Hindi Honorifics

## 1. The Priming Problem

Standard style transfer prompts telegraph the answer:
- "Rewrite this as if talking to your boss" → model knows to use आप
- "Make this more formal" → same problem
- "Use तुम instead of तू" → directly names the target form

Any prompt that mentions formality, respect, politeness, or a named relationship with obvious power dynamics **primes** the model toward the expected honorific tier. This makes it impossible to distinguish genuine sociolinguistic competence from simple instruction-following.

### What We Actually Want to Test

**Productive register control**: Given implicit social context, can a model independently select the appropriate honorific tier (तू/तुम/आप) and transform all agreement morphology, verb forms, and lexical choices accordingly?

This is harder than the generation task (GENERATION_TASK_DESIGN.md) because here we provide a *source sentence* and expect the model to produce a *target sentence* at a different register—without being told which register.

---

## 2. Literature & Precedent

### 2.1 Unggah-Ungguh (Farhansyah et al., ACL 2025)

The closest precedent. Their **Task 2: Honorific Style Translation** directly translates between Javanese honorific levels (Ngoko ↔ Krama ↔ Krama Alus). However, their task **explicitly names the target level** (e.g., "Translate this Ngoko sentence to Krama Alus"), which is exactly the priming we want to avoid. Their Task 4 (Conversation Generation with Honorific Persona) is closer to our needs—they provide a social role/persona and ask the model to generate conversation, then use a fine-tuned classifier to evaluate the honorific level of the output.

**Key finding**: LLMs exhibit strong bias toward Ngoko (informal), even when the persona demands Krama. This parallels expected आप-bias in Hindi LLMs.

### 2.2 Hindi Politeness Corpus (Kumar, LREC 2014; kmi-linguistics/hindi-politeness)

Annotated Hindi corpus with three classes (Neutral, Polite, Impolite) and fine-grained annotations of honorific verb forms, honorific pronouns, etc. Useful as a **source of natural Hindi sentences at known register levels**, but not designed for transfer tasks.

### 2.3 Mukherjee et al. (EMNLP 2025)

Analyzed 3rd-person honorific bias in Hindi/Bengali Wikipedia-style generation. Showed gender and notability biases. They explicitly note that 2nd-person honorific dynamics in conversational settings remain unstudied—our gap.

### 2.4 Sociolinguistic Accommodation Theory

Communication Accommodation Theory (Giles et al.) predicts speakers adjust register to match interlocutors. This gives us a design lever: provide **dialogue history at a specific register** and see if the model accommodates. No explicit instruction needed—the model should naturally match the established register.

### 2.5 Formality Transfer Literature (GYAFC, XFORMAL)

English/multilingual formality transfer benchmarks (Rao & Tetreault 2018, Briakou et al. 2021) always explicitly label source/target formality. No precedent for implicit elicitation. The "Evaluating the Evaluation Metrics for Style Transfer" (EMNLP 2021) paper notes that human evaluation of style transfer is itself biased when evaluators know the target style.

---

## 3. Proposed Designs

### Design A: Situation-Anchored Rewrite (Recommended — Primary)

**Core idea**: Present a Hindi sentence and a vivid situational vignette. The model must rewrite the sentence *as it would be said in that situation*. The situation implies a register shift without naming it.

**Why it works**: The model must perform social inference (situation → social relationship → register) before linguistic transformation. This tests both sociopragmatic knowledge and morphosyntactic competence.

**Template**:
```
मूल वाक्य: [source sentence at known tier]

स्थिति: [situational vignette]

इस स्थिति में यही बात कैसे कही जाएगी? वाक्य लिखिए।
```

**Example prompts**:

**तुम → आप (upward shift)**
```
मूल वाक्य: "तुम कल कहाँ थे? मैंने तुम्हें बहुत ढूँढा।"

स्थिति: ये बात एक नया कर्मचारी अपने विभाग के निदेशक से पूछ रहा है, जिनसे वो पहली बार मिल रहा है, एक सरकारी दफ़्तर में।

इस स्थिति में यही बात कैसे कही जाएगी? वाक्य लिखिए।
```
Expected: "आप कल कहाँ थे? मैंने आपको बहुत ढूँढा।"

**आप → तू (downward shift)**
```
मूल वाक्य: "आप ये काम क्यों नहीं कर रहे हैं? आपसे कितनी बार कहा है।"

स्थिति: एक माँ अपने छोटे बच्चे (8 साल) से नाराज़ होकर बोल रही है कि उसने होमवर्क नहीं किया।

इस स्थिति में यही बात कैसे कही जाएगी? वाक्य लिखिए।
```
Expected: "तू ये काम क्यों नहीं कर रहा है? तुझसे कितनी बार कहा है।"

**तू → तुम (lateral shift)**
```
मूल वाक्य: "तू आज शाम को आ जा, हम साथ में खाना बनाएँगे।"

स्थिति: कॉलेज का एक छात्र अपने हॉस्टल के नए रूममेट से बात कर रहा है, जिससे उसकी अभी दो दिन पहले ही मुलाक़ात हुई है।

इस स्थिति में यही बात कैसे कही जाएगी? वाक्य लिखिए।
```
Expected: "तुम आज शाम को आ जाओ, हम साथ में खाना बनाएँगे।"

**Priming analysis**: The prompt never mentions formality, respect, honorifics, or register. The relationship is embedded in a concrete scenario. However, there's **residual priming**—describing a "निदेशक" (director) may still cue the model to use आप through association rather than genuine inference. This is partially unavoidable but is much weaker than "be formal."

**Mitigation**: Include **ambiguous** situations where the "correct" register is debatable (e.g., same-age colleagues who just met—तुम or आप?). These serve as probes for the model's default assumptions rather than strict right/wrong items.

---

### Design B: Dialogue Continuation with Register Anchor

**Core idea**: Present a multi-turn dialogue that establishes a specific register. Then present the same content framed as a new dialogue with different participants (described only by the dialogue's opening turn, which sets a register). The model must rewrite a key utterance to fit the new dialogue's established register.

**Why it works**: Uses sociolinguistic accommodation—the model should match the register of the preceding dialogue turns. No explicit instruction about formality needed.

**Template**:
```
नीचे एक बातचीत दी गई है। इसमें [speaker] की आखिरी बात को बातचीत के हिसाब से फिर से लिखिए।

[Interlocutor A]: [turn establishing register via pronoun/verb form]
[Interlocutor B]: [response maintaining register]
[Interlocutor A]: [SENTENCE TO REWRITE — given in a *different* register]

ऊपर की बातचीत के लहजे में [A] की आखिरी बात को सही करके लिखिए।
```

**Example**:

**Register anchor = तुम, source sentence in आप**
```
नीचे एक बातचीत दी गई है। इसमें रवि की आखिरी बात बातचीत के लहजे में सही नहीं लग रही। इसे ठीक करके लिखिए।

अमित: यार रवि, तुम आज कहाँ थे? क्लास में नहीं दिखे।
रवि: मैं बीमार था, इसलिए नहीं आ पाया।
अमित: अच्छा, तुम्हारी तबीयत अब कैसी है?
रवि: "क्या आप मुझे आज के नोट्स भेज सकते हैं?"

रवि की आखिरी बात बातचीत के हिसाब से फिर से लिखिए।
```
Expected: "क्या तुम मुझे आज के नोट्स भेज सकते हो?"

**Priming analysis**: Very low priming. The instruction is about *consistency* ("बातचीत के हिसाब से"), not formality. The model must read the register from the dialogue context. However, this primarily tests **register recognition + adaptation** rather than situation-to-register mapping.

**Limitation**: Somewhat overlaps with a cloze/consistency task. The model could pattern-match pronouns without understanding the social dynamics. Best used in combination with Design A.

---

### Design C: Film Character Recontextualization

**Core idea**: Use actual Bollywood film dialogue. Present a line from a film and ask: "If [Character X] said this same thing to [Character Y] in this film, how would they say it?" The model must know (or infer from provided context) the relationship between the characters to select the right register.

**Why it works**: Leverages narrative context rather than explicit social labels. Characters have known relationships (father-son, friends, boss-employee) that the model must infer from character descriptions or film knowledge.

**Template**:
```
फ़िल्म "[film name]" में [Character A] ये बात [Character B] से कहते हैं:
"[original dialogue]"

अगर यही बात [Character C] [Character D] से कहें, तो वो कैसे कहेंगे?
```

**Example**:

**Source: friend-to-friend (तू), Target: student-to-teacher (आप)**
Using a hypothetical from *3 Idiots*:
```
फ़िल्म "3 Idiots" में राजू अपने दोस्त फ़रहान से कहता है:
"तू चिंता मत कर, सब ठीक हो जाएगा।"

अगर यही बात राजू अपने प्रोफ़ेसर वीरू सहस्रबुद्धे से कहे, तो वो कैसे कहेगा?
```
Expected: "आप चिंता मत कीजिए, सब ठीक हो जाएगा।"

**Priming analysis**: Moderate. Naming "प्रोफ़ेसर" implies a power dynamic, but this is inherent to the character—you can't name the target without some social information leaking. The priming is **ecological** (it's how humans think about register shifts—in terms of specific people, not abstract formality levels).

**Advantage**: Directly integrates with the film-pair data already in our benchmark (final_validated_pairs.csv). Can reuse the same film contexts across tasks.

**Limitation**: Requires the model to have cultural knowledge of Hindi films, or we must provide sufficient character context in the prompt—which adds more potential priming surface.

---

## 4. Comparative Analysis

| Dimension | Design A (Situation) | Design B (Dialogue Continuation) | Design C (Film Character) |
|-----------|---------------------|----------------------------------|--------------------------|
| **Priming level** | Low-Medium | Very Low | Medium |
| **What it tests** | Situation → register inference + morphosyntactic transfer | Register recognition + accommodation | Character relationship inference + transfer |
| **Ecological validity** | High (real-world scenarios) | High (natural dialogue) | High (cultural grounding) |
| **Scoring clarity** | Clear (situation has expected tier) | Clear (dialogue establishes tier) | Clear (character relationships known) |
| **Risk of gaming** | Model associates keywords (निदेशक→आप) | Model pattern-matches pronouns | Model uses film knowledge shortcuts |
| **Integration with benchmark** | New scenarios needed | Can reuse probe sentences | Leverages existing film pairs |
| **Complexity** | Medium | Low | High (needs character context) |

---

## 5. Recommended Hybrid Approach

Use **Design A as the primary task** with **Design B as a secondary validation**:

1. **Design A (60% of items)**: 30 situation-anchored rewrite items
   - 10 per target tier (तू, तुम, आप)
   - Source sentences drawn from the Hindi Politeness Corpus or our existing probes
   - Situations span the social variable space (age, power, intimacy, setting, emotion)
   - Include 5 ambiguous items for bias analysis

2. **Design B (30% of items)**: 15 dialogue continuation items
   - 5 per target tier
   - Acts as a consistency check—if a model gets Design A right via keyword association but fails Design B, it suggests shallow competence

3. **Design C (10% of items)**: 5 film character items
   - Bonus items using our existing film data
   - Provides cultural grounding and public-facing appeal

### Evaluation

For all designs, score using:
1. **Pronoun accuracy**: Does the output use the expected tier's pronoun (तू/तुम/आप)?
2. **Verb agreement**: Are verb forms correctly conjugated for the tier (करो/करिए/कर, etc.)?
3. **Lexical consistency**: Are possessives (तेरा/तुम्हारा/आपका) and oblique forms (तुझे/तुम्हें/आपको) correct?
4. **Content preservation**: Does the rewrite retain the original meaning (measured via semantic similarity)?

Use the fine-grained morphological checker from our existing pipeline to automate 1-3.

---

## 6. Addressing Residual Priming

Even Design A has some priming—describing a "निदेशक" implies formality. We can't fully eliminate this because **some social context is necessary to motivate a register shift**. The question is whether we're testing:

- (a) "Can the model follow an instruction to change register?" → priming is fine
- (b) "Does the model understand which register fits which situation?" → need situation, some priming inevitable
- (c) "Can the model execute the morphosyntactic transformation?" → priming irrelevant, just test the mechanics

Our task primarily targets **(b) + (c)**. Design A tests (b) with minimal priming; Design B isolates (c) by providing the register directly via dialogue context.

**The honest conclusion**: Perfect non-priming is impossible for a *transfer* task. If you want zero priming, use the **generation task** (GENERATION_TASK_DESIGN.md) where the model freely produces dialogue. The transfer task inherently requires communicating *what to transfer to*, and any such communication carries information. Our designs minimize this by using **ecological indirection** (situations and dialogue context) rather than **metalinguistic instruction** (naming registers or relationships directly).

---

## 7. Data Sources

- **Source sentences**: Hindi Politeness Corpus (kmi-linguistics/hindi-politeness) — provides naturally occurring Hindi at known politeness levels with annotated honorific markers
- **Situations**: Hand-crafted based on Kumar (2014) sociolinguistic variables; validated by native speakers
- **Film items**: Drawn from final_validated_pairs.csv in this benchmark
- **Dialogue contexts**: Constructed to establish clear register via 2-3 preceding turns

## 8. Open Questions

1. **Should we include English-to-Hindi transfer?** E.g., "Translate this English sentence into Hindi as [situation]" — tests whether the model can map from a language without T-V distinction to one with three tiers.
2. **How to handle तुम vs. आप ambiguity?** Many real situations permit either. Should we score both as correct, or use native speaker agreement as ground truth?
3. **Should situations name professions/roles at all?** Even "student" and "professor" prime. Alternative: describe only age, familiarity duration, and setting without role labels. But this feels unnatural.
