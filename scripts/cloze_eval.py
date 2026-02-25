#!/usr/bin/env python3
"""
Hindi Honorifics Cloze Evaluation Pipeline

Supports:
1. Forced-choice MC via API (Gemini, OpenAI, Groq/Llama)
2. Log-probability scoring via HuggingFace (MuRIL, Llama local)
3. Scoring at both tier-level and exact-form level

Usage:
  # MC evaluation with Gemini
  python cloze_eval.py --method mc --model gemini --probes probes_clean17_ctx5.csv --output results/gemini_mc.jsonl

  # Logprob evaluation with MuRIL
  python cloze_eval.py --method logprob --model muril --probes probes_clean17_ctx5.csv --output results/muril_logprob.jsonl

  # Baselines
  python cloze_eval.py --method baseline-majority --probes probes_clean17_ctx5.csv --output results/baseline_majority.jsonl
  python cloze_eval.py --method baseline-random --probes probes_clean17_ctx5.csv --output results/baseline_random.jsonl
"""

import argparse
import asyncio
import csv
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).parent))
from tier_classifier import PRONOUN_TO_TIER, TIER_LABELS, score_prediction, gold_to_tier

# === All 18 candidate forms ===
ALL_FORMS = sorted(PRONOUN_TO_TIER.keys())

# === Prompt Templates ===

PROMPT_MC_HINDI = """निम्नलिखित संवाद में ____ की जगह सही सर्वनाम भरें।

संवाद:
{context}

{masked_line}

विकल्प: {options}

केवल एक सही सर्वनाम लिखें, कोई और शब्द नहीं:"""

PROMPT_MC_ENGLISH = """Fill in the blank (____) with the correct Hindi pronoun.

Dialogue:
{context}

{masked_line}

Options: {options}

Write only the correct pronoun, nothing else:"""

PROMPT_FREE_HINDI = """निम्नलिखित संवाद में ____ की जगह सही शब्द भरें।

संवाद:
{context}

{masked_line}

केवल एक शब्द लिखें:"""


def format_mc_prompt(probe: dict, lang: str = 'hindi', shuffle: bool = True) -> str:
    """Format a forced-choice MC prompt for a single probe."""
    forms = ALL_FORMS.copy()
    if shuffle:
        random.shuffle(forms)
    options = ', '.join(forms)

    template = PROMPT_MC_HINDI if lang == 'hindi' else PROMPT_MC_ENGLISH
    return template.format(
        context=probe['context'],
        masked_line=probe['masked_line'],
        options=options,
    )


def format_free_prompt(probe: dict) -> str:
    """Format a free-generation prompt."""
    return PROMPT_FREE_HINDI.format(
        context=probe['context'],
        masked_line=probe['masked_line'],
    )


# === API Backends ===

async def call_gemini(prompt: str, model: str = 'gemini-2.0-flash') -> str:
    """Call Gemini API (free tier)."""
    import aiohttp
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY or GOOGLE_API_KEY env var")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 20,
            "temperature": 0.0,
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            try:
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except (KeyError, IndexError):
                return f"ERROR: {json.dumps(data)[:200]}"


async def call_openai(prompt: str, model: str = 'gpt-4o-mini') -> str:
    """Call OpenAI-compatible API."""
    import aiohttp
    api_key = os.environ.get('OPENAI_API_KEY')
    base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    if not api_key:
        raise ValueError("Set OPENAI_API_KEY env var")

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    # Newer models (gpt-4.1+, gpt-5+, o3, o4) require max_completion_tokens
    use_new_param = any(model.startswith(p) for p in ['gpt-4.1', 'gpt-5', 'o3', 'o4'])
    token_key = "max_completion_tokens" if use_new_param else "max_tokens"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        token_key: 20,
        "temperature": 0.0,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            try:
                return data['choices'][0]['message']['content'].strip()
            except (KeyError, IndexError):
                return f"ERROR: {json.dumps(data)[:200]}"


async def call_groq(prompt: str, model: str = 'llama-3.1-8b-instant') -> str:
    """Call Groq API (free tier for Llama)."""
    import aiohttp
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError("Set GROQ_API_KEY env var")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 20,
        "temperature": 0.0,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            try:
                return data['choices'][0]['message']['content'].strip()
            except (KeyError, IndexError):
                return f"ERROR: {json.dumps(data)[:200]}"


# === Logprob Backend (HuggingFace) ===

def logprob_muril(probes: list[dict]) -> list[dict]:
    """Score probes using MuRIL's native MLM head."""
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    import torch

    print("Loading MuRIL model...")
    model_name = "google/muril-base-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name)
    model.eval()

    # Pre-tokenize all candidate forms
    candidate_token_ids = {}
    for form in ALL_FORMS:
        tokens = tokenizer.encode(form, add_special_tokens=False)
        candidate_token_ids[form] = tokens

    results = []
    for i, probe in enumerate(probes):
        if i % 100 == 0:
            print(f"  MuRIL: {i}/{len(probes)}")

        # Replace ____ with [MASK]
        text = probe['context'] + '\n' + probe['masked_line'].replace('____', tokenizer.mask_token)
        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)

        # Find [MASK] position
        mask_positions = (inputs.input_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)
        if len(mask_positions[1]) == 0:
            results.append({'probe_idx': i, 'predicted': 'ERROR_NO_MASK', 'scores': {}})
            continue

        mask_idx = mask_positions[1][0].item()

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0, mask_idx]
            log_probs = torch.log_softmax(logits, dim=-1)

        # Score each candidate (use first token if multi-token)
        scores = {}
        for form, token_ids in candidate_token_ids.items():
            if token_ids:
                scores[form] = log_probs[token_ids[0]].item()

        predicted = max(scores, key=scores.get) if scores else 'ERROR'
        results.append({
            'probe_idx': i,
            'predicted': predicted,
            'scores': {k: round(v, 4) for k, v in sorted(scores.items(), key=lambda x: -x[1])[:5]},
        })

    return results


def logprob_hf_causal(probes: list[dict], model_name: str = 'meta-llama/Llama-3.1-8B') -> list[dict]:
    """Score probes using a causal LM's log-probabilities."""
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map='auto')
    model.eval()

    results = []
    for i, probe in enumerate(probes):
        if i % 50 == 0:
            print(f"  Causal LM: {i}/{len(probes)}")

        context_text = probe['context'] + '\n'
        scores = {}

        for form in ALL_FORMS:
            # Fill in the form and compute total log-prob of the completed sentence
            filled = probe['masked_line'].replace('____', form)
            full_text = context_text + filled
            inputs = tokenizer(full_text, return_tensors='pt', truncation=True, max_length=512).to(model.device)

            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits

            # Sum log-probs of tokens corresponding to the filled form
            log_probs = torch.log_softmax(logits[0, :-1], dim=-1)
            target_ids = inputs.input_ids[0, 1:]
            token_log_probs = log_probs.gather(1, target_ids.unsqueeze(1)).squeeze()

            # Get log-prob of just the candidate tokens
            form_tokens = tokenizer.encode(form, add_special_tokens=False)
            # Find where form appears in the target sequence
            context_len = len(tokenizer.encode(context_text, add_special_tokens=False))
            form_start = context_len  # approximate
            form_end = form_start + len(form_tokens)
            form_log_prob = token_log_probs[form_start:form_end].sum().item()
            scores[form] = form_log_prob

        predicted = max(scores, key=scores.get) if scores else 'ERROR'
        results.append({
            'probe_idx': i,
            'predicted': predicted,
            'scores': {k: round(v, 4) for k, v in sorted(scores.items(), key=lambda x: -x[1])[:5]},
        })

    return results


# === Baselines ===

def baseline_majority(probes: list[dict]) -> list[dict]:
    """Always predict the most frequent gold pronoun."""
    counts = Counter(p['gold_pronoun'] for p in probes)
    majority = counts.most_common(1)[0][0]
    return [{'probe_idx': i, 'predicted': majority, 'scores': {}} for i in range(len(probes))]


def baseline_random(probes: list[dict], seed: int = 42) -> list[dict]:
    """Random prediction from all 18 forms."""
    rng = random.Random(seed)
    return [{'probe_idx': i, 'predicted': rng.choice(ALL_FORMS), 'scores': {}} for i in range(len(probes))]


def baseline_tier_majority(probes: list[dict]) -> list[dict]:
    """Always predict the most frequent tier's nominative form."""
    tier_counts = Counter(gold_to_tier(p['gold_pronoun']) for p in probes)
    majority_tier = tier_counts.most_common(1)[0][0]
    # Map back to nominative form
    tier_to_nom = {'T': 'तू', 'TUM': 'तुम', 'AAP': 'आप'}
    majority_form = tier_to_nom[majority_tier]
    return [{'probe_idx': i, 'predicted': majority_form, 'scores': {}} for i in range(len(probes))]


# === MC Evaluation Runner ===

async def run_mc_eval(probes: list[dict], backend: str, model: str,
                      lang: str = 'hindi', max_concurrent: int = 5,
                      limit: int = None) -> list[dict]:
    """Run MC evaluation across all probes using an API backend."""
    call_fn = {'gemini': call_gemini, 'openai': call_openai, 'groq': call_groq}[backend]

    if limit:
        probes = probes[:limit]

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def eval_one(i, probe):
        async with semaphore:
            prompt = format_mc_prompt(probe, lang=lang)
            try:
                response = await call_fn(prompt, model=model)
                # Clean response — extract just the pronoun
                response = response.strip().split('\n')[0].strip()
                # Remove any surrounding quotes or punctuation
                response = response.strip('"\'।,.!? ')
            except Exception as e:
                response = f"ERROR: {e}"

            # Rate limiting
            await asyncio.sleep(0.5)  # conservative, adjust per API

            return {
                'probe_idx': i,
                'predicted': response,
                'scores': {},
            }

    tasks = [eval_one(i, p) for i, p in enumerate(probes)]

    # Process with progress
    for j in range(0, len(tasks), 50):
        batch = tasks[j:j+50]
        batch_results = await asyncio.gather(*batch)
        results.extend(batch_results)
        print(f"  MC eval: {min(j+50, len(tasks))}/{len(tasks)}")

    return results


# === Aggregate Scoring ===

def compute_metrics(probes: list[dict], results: list[dict]) -> dict:
    """Compute aggregate metrics from evaluation results."""
    exact_matches = 0
    tier_matches = 0
    valid_forms = 0
    total = len(results)

    tier_confusion = Counter()  # (gold_tier, pred_tier) -> count
    form_distribution = Counter()  # predicted form -> count

    for res in results:
        idx = res['probe_idx']
        probe = probes[idx]
        score = score_prediction(res['predicted'], probe['gold_pronoun'])

        exact_matches += score['exact_match']
        tier_matches += score['tier_match']
        valid_forms += score['valid_form']

        if score['gold_tier'] and score['pred_tier']:
            tier_confusion[(score['gold_tier'], score['pred_tier'])] += 1
        form_distribution[res['predicted']] += 1

    metrics = {
        'total': total,
        'exact_accuracy': round(exact_matches / total, 4) if total else 0,
        'tier_accuracy': round(tier_matches / total, 4) if total else 0,
        'valid_form_rate': round(valid_forms / total, 4) if total else 0,
        'tier_confusion': {f"{g}->{p}": c for (g, p), c in sorted(tier_confusion.items())},
        'top_predictions': dict(form_distribution.most_common(10)),
    }

    # Per-tier accuracy
    for tier in ['T', 'TUM', 'AAP']:
        tier_probes = [(probes[r['probe_idx']], r) for r in results
                       if gold_to_tier(probes[r['probe_idx']]['gold_pronoun']) == tier]
        if tier_probes:
            tier_correct = sum(1 for p, r in tier_probes
                             if PRONOUN_TO_TIER.get(r['predicted'].strip()) == tier)
            metrics[f'tier_accuracy_{TIER_LABELS[tier]}'] = round(tier_correct / len(tier_probes), 4)
            metrics[f'tier_count_{TIER_LABELS[tier]}'] = len(tier_probes)

    return metrics


def print_report(metrics: dict, label: str = ''):
    """Print a formatted evaluation report."""
    print(f"\n{'='*60}")
    print(f"  CLOZE EVALUATION REPORT{f' — {label}' if label else ''}")
    print(f"{'='*60}")
    print(f"  Total probes:      {metrics['total']}")
    print(f"  Exact accuracy:    {metrics['exact_accuracy']:.1%}")
    print(f"  Tier accuracy:     {metrics['tier_accuracy']:.1%}")
    print(f"  Valid form rate:   {metrics['valid_form_rate']:.1%}")
    print()
    print("  Per-tier accuracy:")
    for tier in ['तू', 'तुम', 'आप']:
        acc = metrics.get(f'tier_accuracy_{tier}', 'N/A')
        count = metrics.get(f'tier_count_{tier}', 0)
        if isinstance(acc, float):
            print(f"    {tier}: {acc:.1%}  (n={count})")
        else:
            print(f"    {tier}: {acc}  (n={count})")

    print()
    print("  Tier confusion matrix:")
    print(f"    {'':>8} → pred_T  pred_TUM  pred_AAP")
    for gold in ['T', 'TUM', 'AAP']:
        row = []
        for pred in ['T', 'TUM', 'AAP']:
            row.append(metrics['tier_confusion'].get(f'{gold}->{pred}', 0))
        print(f"    gold_{gold:>3}: {row[0]:>7}  {row[1]:>8}  {row[2]:>8}")

    print()
    print("  Top 5 predicted forms:")
    for form, count in list(metrics['top_predictions'].items())[:5]:
        print(f"    {form}: {count}")
    print(f"{'='*60}\n")


# === Main ===

def load_probes(path: str) -> list[dict]:
    """Load probes from CSV."""
    probes = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            probes.append(row)
    return probes


def save_results(results: list[dict], metrics: dict, path: str):
    """Save results and metrics to JSONL + JSON."""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    metrics_path = path.replace('.jsonl', '_metrics.json')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Saved results to {path}")
    print(f"Saved metrics to {metrics_path}")


async def main():
    parser = argparse.ArgumentParser(description='Hindi Honorifics Cloze Evaluation')
    parser.add_argument('--method', required=True,
                       choices=['mc', 'logprob-muril', 'logprob-causal',
                               'baseline-majority', 'baseline-random', 'baseline-tier-majority'],
                       help='Evaluation method')
    parser.add_argument('--model', default=None, help='Model name/identifier')
    parser.add_argument('--backend', default='gemini', choices=['gemini', 'openai', 'groq'],
                       help='API backend for MC method')
    parser.add_argument('--probes', required=True, help='Path to probes CSV')
    parser.add_argument('--output', required=True, help='Output JSONL path')
    parser.add_argument('--lang', default='hindi', choices=['hindi', 'english'],
                       help='Prompt language')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of probes (for testing)')
    parser.add_argument('--concurrent', type=int, default=5, help='Max concurrent API calls')

    args = parser.parse_args()
    probes = load_probes(args.probes)

    if args.limit:
        probes = probes[:args.limit]
        print(f"Limited to {args.limit} probes")

    print(f"Loaded {len(probes)} probes")
    print(f"Method: {args.method}")

    if args.method == 'mc':
        model = args.model or {'gemini': 'gemini-2.0-flash', 'openai': 'gpt-4o-mini', 'groq': 'llama-3.1-8b-instant'}[args.backend]
        print(f"Model: {model} via {args.backend}")
        results = await run_mc_eval(probes, args.backend, model,
                                    lang=args.lang, max_concurrent=args.concurrent,
                                    limit=args.limit)
    elif args.method == 'logprob-muril':
        results = logprob_muril(probes)
    elif args.method == 'logprob-causal':
        model = args.model or 'meta-llama/Llama-3.1-8B'
        results = logprob_hf_causal(probes, model_name=model)
    elif args.method == 'baseline-majority':
        results = baseline_majority(probes)
    elif args.method == 'baseline-random':
        results = baseline_random(probes)
    elif args.method == 'baseline-tier-majority':
        results = baseline_tier_majority(probes)

    metrics = compute_metrics(probes, results)
    label = f"{args.method} / {args.model or args.backend}"
    print_report(metrics, label=label)
    save_results(results, metrics, args.output)


if __name__ == '__main__':
    asyncio.run(main())
