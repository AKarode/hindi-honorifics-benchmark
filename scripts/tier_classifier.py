#!/usr/bin/env python3
"""
Hindi Honorific Tier Classifier

Classifies text into तू / तुम / आप tiers based on:
1. Pronoun detection (primary signal)
2. Verb conjugation patterns (secondary signal)

Returns tier label + confidence markers.
"""

import re
from collections import Counter
from dataclasses import dataclass
from typing import Optional

# === Tier Mappings ===

PRONOUN_TO_TIER = {
    # तू tier (intimate/inferior)
    'तू': 'T', 'तुझे': 'T', 'तुझसे': 'T', 'तुझको': 'T',
    'तेरा': 'T', 'तेरी': 'T', 'तेरे': 'T',
    # तुम tier (informal/familiar)
    'तुम': 'TUM', 'तुम्हें': 'TUM', 'तुमसे': 'TUM', 'तुमको': 'TUM',
    'तुम्हारा': 'TUM', 'तुम्हारी': 'TUM', 'तुम्हारे': 'TUM',
    # आप tier (formal/respectful)
    'आप': 'AAP', 'आपको': 'AAP', 'आपसे': 'AAP',
    'आपका': 'AAP', 'आपकी': 'AAP', 'आपके': 'AAP', 'आपने': 'AAP',
}

TIER_LABELS = {'T': 'तू', 'TUM': 'तुम', 'AAP': 'आप'}

# Pronoun regex — \b doesn't work with Devanagari, use lookbehind/lookahead for non-Devanagari or whitespace/boundary
_DEVA = r'[\u0900-\u097F]'
_NOT_DEVA = rf'(?<![{chr(0x0900)}-{chr(0x097F)}])'
_NOT_DEVA_AFTER = rf'(?![{chr(0x0900)}-{chr(0x097F)}])'
PRONOUN_PATTERN = re.compile(
    _NOT_DEVA + '(' + '|'.join(re.escape(p) for p in sorted(PRONOUN_TO_TIER.keys(), key=len, reverse=True)) + ')' + _NOT_DEVA_AFTER
)

# === Verb Patterns ===
# आप-tier imperatives: -इए, -इये, -ईए (कीजिए, बोलिए, जाइए, बताइए)
AAP_VERB = re.compile(r'(?<!\S)\S+(?:िए|िये|ीए|ईए)(?!\S)')

# तुम-tier imperatives: -ओ ending (करो, बोलो, जाओ, बताओ, देखो)
TUM_VERB = re.compile(r'(?<!\S)\S+ो(?!\S)')

# तू-tier: bare stem imperatives are hard to detect reliably
# but verb+है (करता है, करती है) vs verb+हो (करते हो) vs verb+हैं (करते हैं) helps
TU_AUX = re.compile(r'(?:करता|करती|जाता|जाती|बोलता|बोलती|देता|देती|लेता|लेती|आता|आती)\s+है(?!' + _DEVA[1:-1] + ')')
TUM_AUX = re.compile(r'(?:करते|जाते|बोलते|देते|लेते|आते|करती|जाती)\s+हो(?!' + _DEVA[1:-1] + ')')
AAP_AUX = re.compile(r'(?:करते|जाते|बोलते|देते|लेते|आते|करती|जाती)\s+हैं')


@dataclass
class TierResult:
    tier: Optional[str]          # 'T', 'TUM', 'AAP', or None
    tier_label: Optional[str]    # 'तू', 'तुम', 'आप', or None
    confidence: str              # 'high', 'medium', 'low', 'indeterminate'
    pronoun_counts: dict         # {tier: count}
    verb_counts: dict            # {tier: count}
    pronouns_found: list         # actual pronouns found
    dominant_by_pronoun: Optional[str]
    dominant_by_verb: Optional[str]


def classify_tier(text: str) -> TierResult:
    """Classify a Hindi text's honorific tier."""
    # 1. Count pronoun hits
    pronoun_hits = PRONOUN_PATTERN.findall(text)
    pronoun_tier_counts = Counter()
    for p in pronoun_hits:
        tier = PRONOUN_TO_TIER.get(p)
        if tier:
            pronoun_tier_counts[tier] += 1

    # 2. Count verb pattern hits
    verb_tier_counts = Counter()
    verb_tier_counts['AAP'] = len(AAP_VERB.findall(text))
    verb_tier_counts['TUM'] = len(TUM_VERB.findall(text))
    # Auxiliary patterns
    verb_tier_counts['T'] += len(TU_AUX.findall(text))
    verb_tier_counts['TUM'] += len(TUM_AUX.findall(text))
    verb_tier_counts['AAP'] += len(AAP_AUX.findall(text))

    # 3. Composite scoring (pronouns weight 2x, verbs weight 1x)
    composite = Counter()
    for tier in ['T', 'TUM', 'AAP']:
        composite[tier] = pronoun_tier_counts.get(tier, 0) * 2 + verb_tier_counts.get(tier, 0)

    # 4. Determine dominant tier
    dominant_pronoun = pronoun_tier_counts.most_common(1)[0][0] if pronoun_tier_counts else None
    dominant_verb = verb_tier_counts.most_common(1)[0][0] if any(verb_tier_counts.values()) else None

    total = sum(composite.values())
    if total == 0:
        return TierResult(
            tier=None, tier_label=None, confidence='indeterminate',
            pronoun_counts=dict(pronoun_tier_counts), verb_counts=dict(verb_tier_counts),
            pronouns_found=pronoun_hits, dominant_by_pronoun=dominant_pronoun,
            dominant_by_verb=dominant_verb,
        )

    top_tier, top_count = composite.most_common(1)[0]
    second_count = composite.most_common(2)[1][1] if len(composite.most_common(2)) > 1 else 0

    # Confidence: high if dominant tier has >66% of composite score, medium if >50%, low otherwise
    ratio = top_count / total
    if ratio > 0.66 and top_count >= 2:
        confidence = 'high'
    elif ratio > 0.50:
        confidence = 'medium'
    else:
        confidence = 'low'

    return TierResult(
        tier=top_tier, tier_label=TIER_LABELS.get(top_tier),
        confidence=confidence,
        pronoun_counts=dict(pronoun_tier_counts), verb_counts=dict(verb_tier_counts),
        pronouns_found=pronoun_hits, dominant_by_pronoun=dominant_pronoun,
        dominant_by_verb=dominant_verb,
    )


def gold_to_tier(gold_pronoun: str) -> Optional[str]:
    """Map a gold pronoun to its tier code."""
    return PRONOUN_TO_TIER.get(gold_pronoun.strip())


# === Scoring Utilities ===

def score_prediction(predicted: str, gold: str) -> dict:
    """Score a single cloze prediction against gold."""
    predicted = predicted.strip()
    gold = gold.strip()

    pred_tier = PRONOUN_TO_TIER.get(predicted)
    gold_tier = PRONOUN_TO_TIER.get(gold)

    return {
        'exact_match': int(predicted == gold),
        'tier_match': int(pred_tier == gold_tier) if (pred_tier and gold_tier) else 0,
        'valid_form': int(predicted in PRONOUN_TO_TIER),
        'pred_tier': pred_tier,
        'gold_tier': gold_tier,
        'predicted': predicted,
        'gold': gold,
    }


if __name__ == '__main__':
    # Quick demo
    examples = [
        "तू जल्दी खाना खा ले, तेरी माँ बुला रही है।",
        "तुम कल कहाँ थे? तुम्हें बहुत ढूँढा।",
        "आप कृपया बैठिए, मैं आपके लिए चाय लाता हूँ।",
        "ठीक है, कल मिलते हैं।",  # indeterminate
    ]
    for ex in examples:
        result = classify_tier(ex)
        print(f"Text: {ex[:50]}...")
        print(f"  Tier: {result.tier_label} ({result.confidence})")
        print(f"  Pronouns: {result.pronoun_counts}")
        print(f"  Verbs: {result.verb_counts}")
        print()
