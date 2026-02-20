# Subtitle Quality Audit — 23 Hindi-Original Films (IndicDialogue)

## Summary Table

| Film | Probes | Quality | Grammar | Naturalness | Notes |
|------|--------|---------|---------|-------------|-------|
| Axone | 261 | **HIGH** (5) | 5 | 5 | Excellent natural Delhi/colloquial Hindi. तू/तुम/आप used authentically. |
| Darlings | 116 | **HIGH** (5) | 5 | 5 | Mumbai Hindi, Bambaiya touches. Very natural dialogue. |
| Dhamaka | 255 | **HIGH** (4) | 4 | 4 | Good natural Hindi. Minor subtitle formatting artifacts (`{\an8}`). |
| Emergency | 230 | **LOW** (1) | 2 | 1 | ⚠️ **NOT Hindi-original.** English-original film translated to Hindi. References Princeton, "Kunle", space. Clean grammar but clearly dubbed/translated. |
| Firaaq | 474 | **LOW** (1) | 1 | 1 | ⚠️ **Machine-translated garbage.** Broken sentences, nonsensical Hindi. "ओह, हम सिर्फ था कि यह सेवित" is not Hindi. |
| Ginny Weds Sunny | 266 | **HIGH** (5) | 5 | 5 | Excellent natural Hindi. Colloquial family dialogue, authentic तू/तुम/आप. |
| Good Newwz | 358 | **HIGH** (5) | 5 | 5 | Natural Punjabi-Hindi mix. Authentic family/medical setting dialogue. |
| Guilty | 237 | **HIGH** (4) | 4 | 4 | Natural Hindi. Some formal register mixing but generally authentic. |
| Haseen Dillruba | 133 | **HIGH** (5) | 5 | 5 | Excellent small-town UP Hindi. Very authentic. |
| Hero | 690 | **LOW** (1) | 1 | 1 | ⚠️ **Machine-translated.** Stilted, unnatural constructions. "चलिए मैं आपको कुछ कॉफी देता हूं" with "मेरा यह टी-शर्ट पहनना गलत था" — reads like EN→HI MT. |
| Hit the First Case | 232 | **HIGH** (4) | 4 | 4 | Natural Hindi. Police procedural dialogue feels authentic. Minor `{\an8}` artifacts. |
| Indoo Ki Jawani | 373 | **HIGH** (5) | 5 | 5 | Excellent colloquial Hindi. Noida/Delhi register, very natural. |
| Jaadugar | 252 | **HIGH** (5) | 5 | 5 | Natural small-town Hindi. Sports + family banter, very authentic. |
| Jaane Jaan | 285 | **HIGH** (5) | 5 | 5 | Natural conversational Hindi. Good तू/तुम/आप differentiation. |
| Kick | 599 | **LOW** (1) | 1 | 1 | ⚠️ **Worst quality. Machine-translated gibberish.** English leaking everywhere ("I'I", "Ijust"). Sentences are nonsensical. "आईएफएल मेरी रोगी नहीं पाते हैं" — incomprehensible. |
| Lust Stories 2 | 244 | **HIGH** (5) | 5 | 5 | Natural intimate/conversational Hindi. Authentic register shifts. |
| Madam Chief Minister | 251 | **HIGH** (5) | 5 | 5 | Excellent political/UP Hindi. Very natural power dynamics in language. |
| Om Jai Jagadish | 452 | **LOW** (1) | 1 | 1 | ⚠️ **Machine-translated.** "कृपया जवान आदमी में आते हैं", "मैं तुम से शादी करेंगे" — broken grammar, literal EN→HI translation. |
| Ray Hungama Hai Kyon Barpa | 267 | **LOW** (2) | 2 | 2 | ⚠️ **Translated feel.** "आपको आगे बाधित करने के लिए खेद है, महोदय" — formal calques. Some lines OK, many awkward. |
| Shehzada | 310 | **HIGH** (5) | 5 | 5 | Natural family drama Hindi. Authentic colloquial register. |
| The Great Indian Family | 228 | **HIGH** (5) | 5 | 5 | Natural UP/small-town Hindi. Authentic family dialogue with हम/तुम usage. |
| The White Tiger | 204 | **HIGH** (4) | 4 | 5 | Natural Hindi. Class-conscious register shifts (servant/master). Excellent. |
| Tu Jhoothi Main Makkaar | 377 | **HIGH** (5) | 5 | 5 | Excellent modern urban Hindi. Very natural youth dialogue. Minor `{\an8}` subtitle formatting. |

## Quality Distribution

- **HIGH (4-5):** 17 films — Axone, Darlings, Dhamaka, Ginny Weds Sunny, Good Newwz, Guilty, Haseen Dillruba, Hit the First Case, Indoo Ki Jawani, Jaadugar, Jaane Jaan, Lust Stories 2, Madam Chief Minister, Shehzada, The Great Indian Family, The White Tiger, Tu Jhoothi Main Makkaar
- **MEDIUM (3):** 0 films
- **LOW (1-2):** 6 films — Emergency, Firaaq, Hero, Kick, Om Jai Jagadish, Ray Hungama Hai Kyon Barpa

## ⚠️ Films to EXCLUDE from Benchmark

These 6 films have machine-translated or non-Hindi-original subtitles that would corrupt pronoun evaluation:

### 1. Kick (599 probes) — EXCLUDE
**Problem:** Machine-translated gibberish. English text leaking into Hindi.
- Example 1: *"आईएफएल मेरी रोगी नहीं पाते हैं, | 'इल आप में से किसी को भी नहीं निकाल"* — Nonsensical, English fragments ("I'Il")
- Example 2: *"मैं अपने खुलेपन की तरह। मेरी तरफ आप शादी करने के लिए से यह ठीक है"* — Broken grammar, literal word-by-word translation
- Example 3: *"उन्होंने मुझे आपत्ति की तरह तुम अब किया मैं उन्हें टुकड़ों में काट।"* — Incomprehensible

### 2. Om Jai Jagadish (452 probes) — EXCLUDE
**Problem:** Machine-translated. Grammar is broken throughout.
- Example 1: *"कृपया जवान आदमी में आते हैं।"* — "Please young man come in" literally translated
- Example 2: *"मैं तुम से शादी करेंगे"* — Wrong verb conjugation (करेंगे with मैं)
- Example 3: *"आपका जीवन दुख के माध्यम से कोई यात्रा है"* — Calque of "Your life is no journey through sorrow"

### 3. Firaaq (474 probes) — EXCLUDE
**Problem:** Machine-translated. Many sentences are not valid Hindi at all.
- Example 1: *"ओह, हम सिर्फ था कि यह सेवित"* — Not Hindi. Word salad.
- Example 2: *"करें ... यह तुम कौन तेज कर रहे थे"* — Incomprehensible
- Example 3: *"वामो आप सुनने के लिए सीखना ..."* — Broken, literal translation

### 4. Hero (690 probes) — EXCLUDE
**Problem:** Machine-translated. Stilted, formal constructions that no Hindi speaker would use.
- Example 1: *"मेरे चश्मों को देखते हुए क्या आपको नहीं लगा कि मैं दूल्हा हो सकता हूं?"* — Unnatural calque
- Example 2: *"जब आपकी कार पंक्चर हो गई तो आपको कैब लेनी चाहिए थी।"* — Overly formal, translated
- Example 3: *"जब आप क्रोधित होते हैं, तो आपकी सुंदरता होती है"* — Awkward calque of "when you're angry, you have beauty"

### 5. Emergency (230 probes) — EXCLUDE
**Problem:** Not a Hindi-original film. English-original with Hindi translation. References Princeton, character named "Kunle", space themes.
- Example 1: *"उसे बताया तुम्हें प्रिंस्टन में दाखिला मिला"* — Princeton reference
- Example 2: *"तुम्हें जो करना है, तुम वह करोगे। कून्ले को इसमें मत घसीटो।"* — "Kunle" is not a Hindi name
- Example 3: *"तुम्हें अंतरिक्ष पसंद है?"* — Space theme, foreign setting

### 6. Ray Hungama Hai Kyon Barpa (267 probes) — EXCLUDE (borderline)
**Problem:** Partially translated feel. Mix of natural and awkward lines.
- Example 1: *"आपको आगे बाधित करने के लिए खेद है, महोदय।"* — "Sorry to interrupt you further, sir" — direct calque
- Example 2: *"मैंने सोचा था कि आप गर्भपात के बारे में अपना विचार बदल देंगी।"* — Overly formal, translated feel
- Example 3: *"इंतज़ार नही। तुम मुझ पर जाँच कर रहे हो, है ना?"* — "checking on me" calque

## HIGH Quality Film Examples

### Axone (Score: 5/5)
- *"जंगली चूहे की तरह भागता फिरेगा तू"* — Natural colloquial threat
- *"पापा जी, यह बिल्डिंग तो आपकी है भी नहीं। नानी की है!"* — Authentic family argument
- *"और तुम ए सड़े हुए कॉकरोचों!"* — Natural angry register

### Darlings (Score: 5/5)
- *"बदरू मेरे को बोली… तू सात साल में खाली एक कहानी लिखा करके।"* — Perfect Mumbai Hindi
- *"अरे झुमरू, तू क्या कर रहा है इधर?"* — Natural colloquial
- *"और बेटा, तुम दोनों के पास टिकट नहीं है।"* — Authentic register shift

### Tu Jhoothi Main Makkaar (Score: 5/5)
- *"रुक! आठ महीने टॉर्चर झेल के इसलिए नहीं पैदा किया तुझे"* — Natural maternal scolding
- *"वरना तुम जैसी लड़की इस जैसे गधे को सात जनम में नहीं मिलनी थी।"* — Authentic conversational
- *"अमीर बाप की औलाद है तू, बिगड़ी हुई।"* — Natural tease

## Impact on Benchmark

| Category | Films | Probes | % of Total |
|----------|-------|--------|------------|
| HIGH quality (keep) | 17 | 4,531 | 63.7% |
| LOW quality (exclude) | 6 | 2,712 | 36.3% |
| **Total** | **23** | **7,243** | **100%** |

**Recommendation:** Exclude the 6 LOW-quality films. They have 2,712 probes (36.3%) with broken/translated Hindi where pronoun choices are unreliable as gold labels. The remaining 17 films with 4,531 probes provide a clean, natural-Hindi benchmark.

**Devanagari consistency:** No romanized word leakage in HIGH-quality films (English loanwords like "birthday", "profile" are appropriately used as Hindi speakers would). LOW-quality films have English fragments leaking (especially Kick).
