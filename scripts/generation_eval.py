#!/usr/bin/env python3
"""
Hindi Honorifics Generation Evaluation — Task A: Discourse Completion Task (DCT)

Presents social scenarios in Hindi, asks the model to produce dialogue,
then extracts and scores the honorific tier of generated pronouns.

Usage:
  python generation_eval.py --model gpt-5-mini --output results/gen_gpt5_mini.jsonl
  python generation_eval.py --model gpt-4o-mini --limit 10 --output results/gen_test.jsonl
"""

import argparse
import asyncio
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tier_classifier import (
    PRONOUN_TO_TIER, TIER_LABELS, PRONOUN_PATTERN,
    AAP_VERB, TUM_VERB, TU_AUX, TUM_AUX, AAP_AUX,
    classify_tier,
)

# === Prompt Template (Hindi, no honorific priming) ===

PROMPT_TEMPLATE = """स्थिति: {situation}

{speaker} {addressee} से {action}। {speaker} क्या {verb}?

केवल {speaker} का संवाद लिखें (1-3 वाक्य)।"""


def gender_verb(gender: str) -> str:
    """Return appropriate verb form based on speaker gender."""
    if gender == "F":
        return "कहेगी"
    return "कहेगा"


def build_prompt(scenario: dict) -> str:
    return PROMPT_TEMPLATE.format(
        situation=scenario["situation"],
        speaker=scenario["speaker"],
        addressee=scenario["addressee"],
        action=scenario["action"],
        verb=gender_verb(scenario.get("gender", "M")),
    )


# === Scoring ===

TIER_MAP = {"T": "T", "TUM": "TUM", "AAP": "AAP"}

def extract_pronouns(text: str) -> list[dict]:
    """Extract all 2nd-person pronouns from text with their tiers."""
    hits = PRONOUN_PATTERN.findall(text)
    return [{"form": h, "tier": PRONOUN_TO_TIER.get(h)} for h in hits]


def check_verb_agreement(text: str, dominant_tier: str) -> dict:
    """Check if verb conjugations match the dominant pronoun tier."""
    verb_counts = {
        "T": len(TU_AUX.findall(text)),
        "TUM": len(TUM_VERB.findall(text)) + len(TUM_AUX.findall(text)),
        "AAP": len(AAP_VERB.findall(text)) + len(AAP_AUX.findall(text)),
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
    """Score a single generated response."""
    pronouns = extract_pronouns(text)
    tier_result = classify_tier(text)
    
    # Pronoun tier counts
    tier_counts = Counter(p["tier"] for p in pronouns if p["tier"])
    
    # Determine generated tier
    generated_tier = tier_result.tier  # from classify_tier composite
    
    # Tier accuracy
    tier_correct = generated_tier == expected_tier if generated_tier else False
    
    # Avoidance: no 2nd person pronouns at all
    avoided = len(pronouns) == 0
    
    # Verb agreement
    verb_check = check_verb_agreement(text, generated_tier) if generated_tier else {"match": None, "verb_counts": {}, "total": 0}
    
    return {
        "generated_tier": generated_tier,
        "expected_tier": expected_tier,
        "tier_correct": tier_correct,
        "avoided": avoided,
        "pronoun_counts": dict(tier_counts),
        "pronouns_found": [p["form"] for p in pronouns],
        "verb_agreement": verb_check["match"],
        "verb_counts": verb_check["verb_counts"],
        "confidence": tier_result.confidence,
    }


# === API Backend ===

async def call_openai(prompt: str, model: str, semaphore: asyncio.Semaphore) -> str:
    """Call OpenAI API."""
    import aiohttp
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not api_key:
        raise ValueError("Set OPENAI_API_KEY env var")

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Reasoning models: no temperature, large token budget
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


# === Main Pipeline ===

async def run_eval(scenarios: list[dict], model: str, max_concurrent: int = 5,
                   limit: int = None) -> list[dict]:
    """Run generation evaluation on all scenarios."""
    if limit:
        scenarios = scenarios[:limit]

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def eval_one(scenario):
        prompt = build_prompt(scenario)
        response = await call_openai(prompt, model, semaphore)
        score = score_generation(response, scenario["expected_tier"])
        return {
            "id": scenario["id"],
            "expected_tier": scenario["expected_tier"],
            "category": scenario["category"],
            "speaker": scenario["speaker"],
            "addressee": scenario["addressee"],
            "prompt": prompt,
            "response": response,
            **score,
        }

    tasks = [eval_one(s) for s in scenarios]
    
    # Process in batches for progress reporting
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
    """Compute aggregate metrics from generation results."""
    valid = [r for r in results if "error" not in r]
    total = len(valid)
    if total == 0:
        return {"total": 0, "error": "no valid results"}

    # Tier accuracy
    tier_correct = sum(1 for r in valid if r["tier_correct"])
    
    # Avoidance rate
    avoided = sum(1 for r in valid if r["avoided"])
    
    # Formality bias: proportion of AAP across all outputs
    all_tier_counts = Counter()
    for r in valid:
        for tier, count in r.get("pronoun_counts", {}).items():
            all_tier_counts[tier] += count
    total_pronouns = sum(all_tier_counts.values())
    
    # Verb agreement (among those with verbs)
    verb_scores = [r["verb_agreement"] for r in valid if r["verb_agreement"] is not None]
    
    metrics = {
        "total": total,
        "model": valid[0].get("model", "unknown") if valid else "unknown",
        "tier_accuracy": round(tier_correct / total, 4),
        "avoidance_rate": round(avoided / total, 4),
        "formality_bias_ratio": round(all_tier_counts.get("AAP", 0) / total_pronouns, 4) if total_pronouns > 0 else None,
        "pronoun_distribution": {TIER_LABELS.get(k, k): v for k, v in all_tier_counts.items()},
        "total_pronouns_generated": total_pronouns,
        "verb_agreement_mean": round(sum(verb_scores) / len(verb_scores), 4) if verb_scores else None,
        "verb_agreement_n": len(verb_scores),
    }

    # Per-tier breakdown
    for tier_code, tier_label in TIER_LABELS.items():
        tier_results = [r for r in valid if r["expected_tier"] == tier_code]
        if tier_results:
            correct = sum(1 for r in tier_results if r["tier_correct"])
            avoided_t = sum(1 for r in tier_results if r["avoided"])
            metrics[f"tier_accuracy_{tier_label}"] = round(correct / len(tier_results), 4)
            metrics[f"avoidance_rate_{tier_label}"] = round(avoided_t / len(tier_results), 4)
            metrics[f"count_{tier_label}"] = len(tier_results)

    # Tier confusion matrix
    confusion = Counter()
    for r in valid:
        if r["generated_tier"] and r["expected_tier"]:
            confusion[(r["expected_tier"], r["generated_tier"])] += 1
        elif r["avoided"]:
            confusion[(r["expected_tier"], "NONE")] += 1
    metrics["tier_confusion"] = {f"{g}->{p}": c for (g, p), c in sorted(confusion.items())}

    # Per-category breakdown
    categories = set(r.get("category", "") for r in valid)
    for cat in sorted(categories):
        cat_results = [r for r in valid if r.get("category") == cat]
        if cat_results:
            correct = sum(1 for r in cat_results if r["tier_correct"])
            metrics[f"accuracy_{cat}"] = round(correct / len(cat_results), 4)

    return metrics


def print_report(metrics: dict, model: str):
    """Print formatted report."""
    print(f"\n{'='*60}")
    print(f"  GENERATION EVAL REPORT — {model}")
    print(f"{'='*60}")
    print(f"  Total scenarios:     {metrics['total']}")
    print(f"  Tier accuracy:       {metrics['tier_accuracy']:.1%}")
    print(f"  Avoidance rate:      {metrics['avoidance_rate']:.1%}")
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
    print(f"    {'':>8} → T     TUM    AAP    NONE")
    for gold in ["T", "TUM", "AAP"]:
        row = []
        for pred in ["T", "TUM", "AAP", "NONE"]:
            row.append(metrics.get("tier_confusion", {}).get(f"{gold}->{pred}", 0))
        print(f"    {gold:>5}: {row[0]:>5}  {row[1]:>5}  {row[2]:>5}  {row[3]:>5}")

    print()
    print("  Per-category accuracy:")
    for key in sorted(metrics.keys()):
        if key.startswith("accuracy_"):
            cat = key.replace("accuracy_", "")
            print(f"    {cat}: {metrics[key]:.1%}")
    
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
    parser = argparse.ArgumentParser(description="Hindi Honorifics Generation Evaluation (DCT)")
    parser.add_argument("--model", default="gpt-5-mini", help="OpenAI model name")
    parser.add_argument("--output", default="results/gen_eval.jsonl", help="Output JSONL path")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of scenarios")
    parser.add_argument("--concurrent", type=int, default=5, help="Max concurrent API calls")
    parser.add_argument("--scenarios", default=None,
                       help="Path to scenarios JSON (default: scripts/generation_scenarios.json)")

    args = parser.parse_args()

    # Load scenarios
    scenarios_path = args.scenarios or str(Path(__file__).parent / "generation_scenarios.json")
    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print(f"Loaded {len(scenarios)} scenarios")
    print(f"Model: {args.model}")
    print(f"Concurrent: {args.concurrent}")
    if args.limit:
        print(f"Limit: {args.limit}")

    results = await run_eval(scenarios, args.model, 
                             max_concurrent=args.concurrent, limit=args.limit)

    metrics = compute_metrics(results)
    metrics["model"] = args.model
    
    print_report(metrics, args.model)
    save_results(results, metrics, args.output)


if __name__ == "__main__":
    asyncio.run(main())
