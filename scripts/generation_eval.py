#!/usr/bin/env python3
"""
Hindi Honorifics Generation Evaluation — Corpus-Grounded Dialogue Continuation

Presents real film dialogue context, asks the model to produce the next line,
then extracts and scores the honorific tier of generated pronouns.

All stimuli are derived from IndicDialogue subtitles (non-synthetic).

Usage:
  python scripts/generation_eval.py --model gpt-5-mini --probes probes_generation_200.csv
  python scripts/generation_eval.py --model gpt-4o-mini --probes probes_generation_200.csv --limit 10
"""

import argparse
import asyncio
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tier_classifier import (
    PRONOUN_TO_TIER, TIER_LABELS, PRONOUN_PATTERN,
    AAP_VERB, TUM_VERB, TU_AUX, TUM_AUX, AAP_AUX,
    _AAP_VERB_EXCLUSIONS, _TUM_VERB_EXCLUSIONS,
    classify_tier,
)

# === Refusal Detection ===
REFUSAL_MARKERS = [
    'माफ़ कीजिए', 'माफ कीजिए', 'माफ़ कीजिये', 'माफ कीजिये',
    'कॉपीराइट', 'उद्धृत नहीं', 'जारी नहीं कर सकता', 'आगे नहीं बढ़ा सकता',
    'I cannot', "I can't", 'I am unable', 'as an AI',
    'मैं यह नहीं कर सकता', 'मैं ऐसा नहीं कर सकता',
]

def is_refusal(text: str) -> bool:
    """Detect if a response is a model refusal/safety response."""
    text_lower = text.lower()
    return any(marker.lower() in text_lower for marker in REFUSAL_MARKERS)

# === Prompt Template ===
# Hindi prompt, no mention of honorifics or pronouns to avoid priming.

PROMPT_TEMPLATE = """यह एक हिंदी फ़िल्म के संवाद का अंश है:

{context}

इस संवाद को जारी रखते हुए अगला एक वाक्य लिखें।
केवल संवाद लिखें, कोई व्याख्या नहीं:"""


def build_prompt(probe: dict) -> str:
    """Build a dialogue continuation prompt from a probe's context."""
    return PROMPT_TEMPLATE.format(context=probe["context"].strip())


# === Scoring ===

def extract_pronouns(text: str) -> list[dict]:
    """Extract all 2nd-person pronouns from text with their tiers."""
    hits = PRONOUN_PATTERN.findall(text)
    return [{"form": h, "tier": PRONOUN_TO_TIER.get(h)} for h in hits]


def check_verb_agreement(text: str, dominant_tier: str) -> dict:
    """Check if verb conjugations match the dominant pronoun tier.
    
    Uses exclusion filtering to avoid false positives from common words.
    """
    tum_matches = [m for m in TUM_VERB.findall(text) if m not in _TUM_VERB_EXCLUSIONS]
    aap_matches = [m for m in AAP_VERB.findall(text) if m not in _AAP_VERB_EXCLUSIONS]
    
    verb_counts = {
        "T": len(TU_AUX.findall(text)),
        "TUM": len(tum_matches) + len(TUM_AUX.findall(text)),
        "AAP": len(aap_matches) + len(AAP_AUX.findall(text)),
    }
    total_verbs = sum(verb_counts.values())
    if total_verbs == 0:
        return {"match": None, "verb_counts": verb_counts, "total": 0}
    matching = verb_counts.get(dominant_tier, 0)
    return {
        "match": matching / total_verbs if total_verbs > 0 else None,
        "verb_counts": verb_counts,
        "total": total_verbs,
    }


def score_generation(text: str, expected_tier: str) -> dict:
    """Score a single generated response.
    
    Key logic:
    - Refusals are flagged separately and excluded from tier accuracy
    - 'avoided' means no pronouns were found (regardless of verb patterns)
    - 'generated_tier' only trusts pronoun-based classification when no pronouns found
    - Verb agreement is only computed when tier was determined by pronouns (not circular)
    """
    refusal = is_refusal(text)
    pronouns = extract_pronouns(text)
    tier_result = classify_tier(text)

    tier_counts = Counter(p["tier"] for p in pronouns if p["tier"])
    has_pronouns = len(pronouns) > 0
    
    # Only trust generated_tier if it came from pronouns (not verb-only classification)
    # This fixes the avoided vs generated_tier contradiction
    if has_pronouns:
        generated_tier = tier_result.tier
    else:
        # No pronouns found - don't trust verb-only tier classification
        generated_tier = None
    
    avoided = not has_pronouns
    tier_correct = generated_tier == expected_tier if generated_tier else False

    # Only compute verb agreement when tier was determined by pronouns (avoids circularity)
    verb_check = (check_verb_agreement(text, generated_tier)
                  if generated_tier and has_pronouns
                  else {"match": None, "verb_counts": {}, "total": 0})

    return {
        "generated_tier": generated_tier,
        "expected_tier": expected_tier,
        "tier_correct": tier_correct,
        "avoided": avoided,
        "is_refusal": refusal,
        "pronoun_counts": dict(tier_counts),
        "pronouns_found": [p["form"] for p in pronouns],
        "verb_agreement": verb_check["match"],
        "verb_counts": verb_check["verb_counts"],
        "confidence": tier_result.confidence if has_pronouns else "indeterminate",
    }


# === API Backends ===

async def call_openai(prompt: str, model: str, semaphore: asyncio.Semaphore) -> str:
    """Call OpenAI API."""
    import aiohttp
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not api_key:
        raise ValueError("Set OPENAI_API_KEY env var")

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    is_reasoning = any(k in model for k in ["o3", "o4", "gpt-5-nano", "gpt-5-mini", "gpt-5."])
    use_new_param = any(model.startswith(p) for p in ["gpt-4.1", "gpt-5", "o3", "o4"])
    token_key = "max_completion_tokens" if use_new_param else "max_tokens"
    token_budget = 8000 if is_reasoning else 300

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        token_key: token_budget,
    }
    if not is_reasoning:
        payload["temperature"] = 0.0

    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                try:
                    return data["choices"][0]["message"]["content"].strip()
                except (KeyError, IndexError):
                    return f"ERROR: {json.dumps(data)[:300]}"
        await asyncio.sleep(0.3)


async def call_gemini(prompt: str, model: str, semaphore: asyncio.Semaphore) -> str:
    """Call Gemini API (free tier)."""
    import aiohttp
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY or GOOGLE_API_KEY env var")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.0,
        }
    }
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError):
                    return f"ERROR: {json.dumps(data)[:300]}"
        await asyncio.sleep(0.3)


async def call_groq(prompt: str, model: str, semaphore: asyncio.Semaphore) -> str:
    """Call Groq API (free tier for Llama/Qwen)."""
    import aiohttp
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Set GROQ_API_KEY env var")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.0,
    }
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                try:
                    return data["choices"][0]["message"]["content"].strip()
                except (KeyError, IndexError):
                    return f"ERROR: {json.dumps(data)[:300]}"
        await asyncio.sleep(0.3)


async def call_sarvam(prompt: str, model: str, semaphore: asyncio.Semaphore) -> str:
    """Call Sarvam AI API (India-first models).
    
    Models: sarvam-m (free), sarvam-105b (paid)
    """
    import aiohttp
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("Set SARVAM_API_KEY env var")

    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.0,
    }
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                try:
                    return data["choices"][0]["message"]["content"].strip()
                except (KeyError, IndexError):
                    return f"ERROR: {json.dumps(data)[:300]}"
        await asyncio.sleep(0.3)


async def call_anthropic(prompt: str, model: str, semaphore: asyncio.Semaphore) -> str:
    """Call Anthropic Claude API.
    
    Models: claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5
    """
    import aiohttp
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY env var")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}],
    }
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                try:
                    return data["content"][0]["text"].strip()
                except (KeyError, IndexError):
                    return f"ERROR: {json.dumps(data)[:300]}"
        await asyncio.sleep(0.3)


# === Main Pipeline ===

BACKEND_FUNCTIONS = {
    'openai': call_openai,
    'gemini': call_gemini,
    'groq': call_groq,
    'sarvam': call_sarvam,
    'anthropic': call_anthropic,
}

async def run_eval(probes: list[dict], model: str, backend: str = 'openai',
                   max_concurrent: int = 5, limit: int = None) -> list[dict]:
    """Run generation evaluation on all probes."""
    if limit:
        probes = probes[:limit]
    
    call_fn = BACKEND_FUNCTIONS[backend]
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def eval_one(probe):
        prompt = build_prompt(probe)
        response = await call_fn(prompt, model, semaphore)
        expected_tier = PRONOUN_TO_TIER.get(probe["gold_pronoun"], probe.get("gold_tier"))
        score = score_generation(response, expected_tier)
        return {
            "movie": probe["movie"],
            "gold_pronoun": probe["gold_pronoun"],
            "expected_tier": expected_tier,
            "gold_line": probe["gold_line"],
            "context": probe["context"],
            "prompt": prompt,
            "response": response,
            **score,
        }

    tasks = [eval_one(p) for p in probes]

    for i in range(0, len(tasks), 20):
        batch = tasks[i:i+20]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        for r in batch_results:
            if isinstance(r, Exception):
                results.append({"error": str(r)})
            else:
                results.append(r)
        print(f"  Progress: {min(i+20, len(tasks))}/{len(tasks)}")

    return results


def compute_metrics(results: list[dict]) -> dict:
    """Compute aggregate metrics from generation results.
    
    Refusals are counted separately and excluded from tier accuracy calculations.
    """
    valid = [r for r in results if "error" not in r]
    total = len(valid)
    if total == 0:
        return {"total": 0, "error": "no valid results"}

    # Separate refusals from genuine responses
    refusals = [r for r in valid if r.get("is_refusal", False)]
    non_refusals = [r for r in valid if not r.get("is_refusal", False)]
    
    # Compute tier accuracy only on non-refusal responses
    tier_correct = sum(1 for r in non_refusals if r["tier_correct"])
    avoided = sum(1 for r in non_refusals if r["avoided"])

    # Count pronouns from non-refusal responses only
    all_tier_counts = Counter()
    for r in non_refusals:
        for tier, count in r.get("pronoun_counts", {}).items():
            all_tier_counts[tier] += count
    total_pronouns = sum(all_tier_counts.values())

    verb_scores = [r["verb_agreement"] for r in non_refusals if r["verb_agreement"] is not None]
    
    # Denominator for accuracy is non-refusals, not total
    non_refusal_count = len(non_refusals)

    metrics = {
        "total": total,
        "total_non_refusals": non_refusal_count,
        "refusal_count": len(refusals),
        "refusal_rate": round(len(refusals) / total, 4) if total > 0 else 0,
        "tier_accuracy": round(tier_correct / non_refusal_count, 4) if non_refusal_count > 0 else None,
        "avoidance_rate": round(avoided / non_refusal_count, 4) if non_refusal_count > 0 else None,
        "formality_bias_ratio": round(all_tier_counts.get("AAP", 0) / total_pronouns, 4) if total_pronouns > 0 else None,
        "pronoun_distribution": {TIER_LABELS.get(k, k): v for k, v in all_tier_counts.items()},
        "total_pronouns_generated": total_pronouns,
        "verb_agreement_mean": round(sum(verb_scores) / len(verb_scores), 4) if verb_scores else None,
        "verb_agreement_n": len(verb_scores),
    }

    # Per-tier breakdown (using non-refusals only)
    for tier_code, tier_label in TIER_LABELS.items():
        tier_results = [r for r in non_refusals if r["expected_tier"] == tier_code]
        if tier_results:
            correct = sum(1 for r in tier_results if r["tier_correct"])
            avoided_t = sum(1 for r in tier_results if r["avoided"])
            metrics[f"tier_accuracy_{tier_label}"] = round(correct / len(tier_results), 4)
            metrics[f"avoidance_rate_{tier_label}"] = round(avoided_t / len(tier_results), 4)
            metrics[f"count_{tier_label}"] = len(tier_results)

    # Tier confusion matrix (using non-refusals only)
    confusion = Counter()
    for r in non_refusals:
        if r["generated_tier"] and r["expected_tier"]:
            confusion[(r["expected_tier"], r["generated_tier"])] += 1
        elif r["avoided"]:
            confusion[(r["expected_tier"], "NONE")] += 1
    metrics["tier_confusion"] = {f"{g}->{p}": c for (g, p), c in sorted(confusion.items())}

    # Per-movie breakdown (using non-refusals only)
    movies = set(r.get("movie", "") for r in non_refusals)
    for movie in sorted(movies):
        movie_results = [r for r in non_refusals if r.get("movie") == movie]
        if movie_results:
            correct = sum(1 for r in movie_results if r["tier_correct"])
            metrics[f"accuracy_{movie}"] = round(correct / len(movie_results), 4)

    return metrics


def print_report(metrics: dict, model: str):
    """Print formatted report."""
    print(f"\n{'='*60}")
    print(f"  GENERATION EVAL (DIALOGUE CONTINUATION) — {model}")
    print(f"{'='*60}")
    print(f"  Total probes:        {metrics['total']}")
    print(f"  Refusals:            {metrics.get('refusal_count', 0)} ({metrics.get('refusal_rate', 0):.1%})")
    print(f"  Non-refusal probes:  {metrics.get('total_non_refusals', metrics['total'])}")
    tier_acc = metrics.get('tier_accuracy')
    avoid_rate = metrics.get('avoidance_rate')
    print(f"  Tier accuracy:       {tier_acc:.1%}" if tier_acc is not None else "  Tier accuracy:       N/A")
    print(f"  Avoidance rate:      {avoid_rate:.1%}" if avoid_rate is not None else "  Avoidance rate:      N/A")
    print(f"  Formality bias (AAP ratio): {metrics.get('formality_bias_ratio', 'N/A')}")
    if metrics.get("verb_agreement_mean") is not None:
        print(f"  Verb agreement:      {metrics['verb_agreement_mean']:.1%} (n={metrics['verb_agreement_n']})")
    print()
    print("  Per-tier accuracy:")
    for tier in ["तू", "तुम", "आप"]:
        acc = metrics.get(f"tier_accuracy_{tier}", "N/A")
        count = metrics.get(f"count_{tier}", 0)
        avoid = metrics.get(f"avoidance_rate_{tier}", "N/A")
        if isinstance(acc, float):
            print(f"    {tier}: {acc:.1%}  (n={count}, avoided={avoid:.1%})")
        else:
            print(f"    {tier}: {acc}  (n={count})")

    print()
    print("  Tier confusion:")
    print(f"    {'':>8} -> T     TUM    AAP    NONE")
    for gold in ["T", "TUM", "AAP"]:
        row = []
        for pred in ["T", "TUM", "AAP", "NONE"]:
            row.append(metrics.get("tier_confusion", {}).get(f"{gold}->{pred}", 0))
        print(f"    {gold:>5}: {row[0]:>5}  {row[1]:>5}  {row[2]:>5}  {row[3]:>5}")

    print(f"{'='*60}\n")


def save_results(results: list[dict], metrics: dict, path: str):
    """Save results as JSONL + metrics JSON."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    metrics_path = path.replace(".jsonl", "_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Saved results to {path}")
    print(f"Saved metrics to {metrics_path}")


async def main():
    parser = argparse.ArgumentParser(
        description="Hindi Honorifics Generation Evaluation (Dialogue Continuation)")
    parser.add_argument("--model", default=None, help="Model name (defaults per backend)")
    parser.add_argument("--backend", default="openai",
                        choices=["openai", "gemini", "groq", "sarvam", "anthropic"],
                        help="API backend")
    parser.add_argument("--probes", required=True,
                        help="Path to generation probes CSV (from sample_generation.py)")
    parser.add_argument("--output", default="results/gen_eval.jsonl", help="Output JSONL path")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of probes")
    parser.add_argument("--concurrent", type=int, default=5, help="Max concurrent API calls")

    args = parser.parse_args()

    # Default models per backend
    default_models = {
        'openai': 'gpt-5-mini',
        'gemini': 'gemini-2.5-flash',
        'groq': 'qwen/qwen3-32b',
        'sarvam': 'sarvam-m',
        'anthropic': 'claude-sonnet-4-5',
    }
    model = args.model or default_models[args.backend]

    # Load probes from CSV
    with open(args.probes, newline="", encoding="utf-8") as f:
        probes = list(csv.DictReader(f))

    print(f"Loaded {len(probes)} generation probes from {args.probes}")
    print(f"Model: {model} via {args.backend}")
    if args.limit:
        print(f"Limit: {args.limit}")

    results = await run_eval(probes, model, backend=args.backend,
                             max_concurrent=args.concurrent, limit=args.limit)

    metrics = compute_metrics(results)
    metrics["model"] = model
    metrics["backend"] = args.backend

    print_report(metrics, model)
    save_results(results, metrics, args.output)


if __name__ == "__main__":
    asyncio.run(main())
