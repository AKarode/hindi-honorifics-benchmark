# Error Analysis — GPT-5-mini on Hindi Honorifics Cloze (n=500)

**Total tier errors: 93 / 500 (18.6% error rate)**

---

## Error Type Distribution

| Gold → Predicted | Count | % of errors | Description |
|---|---|---|---|
| **आप → तुम** | **41** | **44%** | Formalizing down — model informalizes |
| तुम → आप | 15 | 16% | Informalizing up — model over-formalizes |
| तू → तुम | 15 | 16% | Missing intimate register |
| तुम → तू | 12 | 13% | False intimate prediction |
| आप → तू | 8 | 9% | Formal → intimate (rare, severe) |
| तू → आप | 2 | 2% | Intimate → formal (very rare) |

### The #1 error: आप → तुम (44% of all errors)

The model's biggest failure mode is predicting तुम when the correct answer is आप. This is the "informalization bias" — the model defaults to the more casual register.

**Key finding: 51% of these errors occur in contexts with formal markers (सर, मैडम, जी, साहब) present.** The model sees the formal cues but still predicts informal. This suggests the model recognizes formality but sometimes treats it as background context rather than a signal for pronoun choice.

**54% of these errors have informal markers (यार, बे, अबे) in the surrounding context.** This is revealing — the dialogue contains code-switching or mixed-register scenes where characters use both formal and informal language. The model picks up the informal cues and defaults to तुम, missing that the specific blank requires आप.

### तू → तुम (16% of errors)

The model misses the intimate/inferior register 15 times. Among these:
- **40% have anger cues** (चुप, बंद, हट, गधा, !)
- **27% have intimacy cues** (प्यार, जान, बेबी)
- **33% are ambiguous** — no clear emotional markers

The ambiguous cases are the hardest — तू used casually between friends/family without strong emotional coloring.

---

## Accuracy by Pronoun Form

| Form | N | Exact Acc | Tier Acc | Notes |
|---|---|---|---|---|
| तुम | 125 | 91.2% | 94.4% | Easiest — default register |
| तुम्हें | 53 | 75.5% | 84.9% | Oblique तुम well-handled |
| आपके | 32 | 68.8% | 84.4% | |
| तुम्हारे | 24 | 75.0% | 83.3% | |
| आप | 98 | 68.4% | 72.4% | Nominative आप surprisingly hard |
| तू | 45 | 60.0% | 73.3% | |
| तुझे | 9 | 44.4% | 44.4% | **Hardest form** — oblique तू |

**Key insight:** तुझे is the worst-performing form at 44.4%. The model fails at both tier AND form level — it can't even identify this as T-tier. This is likely because तुझे is rare in the corpus (~1.2% तू distribution overall) and appears in emotionally charged contexts that are hard to parse.

Nominative तुम (91.2% exact) vs nominative आप (68.4% exact) shows the model's default bias clearly — it's much better at predicting the common form.

---

## Contextual Patterns

### Code-switching scenes are the hardest
Many errors occur in scenes where characters switch registers mid-conversation. For example, a character might use आप with a doctor but तुम with their spouse in the same dialogue — the model picks up the informal register and applies it to the formal blank.

### The verb-form mismatch trap
Hindi has a quirk: आप can take informal verb forms in colloquial speech (e.g., "आप कहते हो" instead of strictly formal "आप कहते हैं"). This grammatical ambiguity between आप+informal-verb and तुम+informal-verb makes the task harder when verb forms are present.

### Movie-level variation
| Movie | Probes | Tier Acc |
|---|---|---|
| Guilty | 142 | 84.5% |
| Good Newwz | 358 | 80.2% |

Good Newwz has more errors — it's a comedy with frequent code-switching, mixed-formality scenes, and rapid register shifts. Guilty (a drama) has clearer social hierarchies.

**Note:** The first 500 probes only cover 2 movies. A full 21K evaluation would cover ~2,700 movies and give much more diverse error patterns.

---

## Form-Level Errors (39 cases: right tier, wrong case)

When the model gets the social register right but picks the wrong grammatical form:

| Confusion | Count | Issue |
|---|---|---|
| तुम → तुम्हारे | 3 | Nom → possessive |
| आपके → आप | 2 | Possessive → nominative |
| आपको → आप | 2 | Dative → nominative |
| तू → तुझे | 2 | Nom → oblique |
| आपका → आपको | 2 | Possessive → dative |

The model tends to default to nominative forms (तुम, आप, तू) when unsure, missing oblique/possessive/dative forms. This is a morphosyntactic weakness separate from the sociopragmatic one.

---

## Recommendations for Improvement

1. **Add explicit social relationship metadata** to probes (speaker role, age gap, professional context) — this would help diagnose whether the model fails on *recognizing* social context or *applying* it.

2. **Stratify by movie genre** — comedy vs drama vs thriller may have different register patterns and error profiles.

3. **Scale to full 21K probes** — 500 probes from 2 movies is not representative. The full set covers 2,700+ movies.

4. **Test register-switching detection** — can the model identify when a character switches from आप to तुम mid-scene?

5. **Fine-tune prompt** — adding "consider the social relationship between speakers" might improve reasoning models' performance on the आप/तुम boundary.
