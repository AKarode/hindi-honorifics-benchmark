#!/usr/bin/env python3
"""
Sample probes suitable for the corpus-grounded generation task.

Filters for probes where:
  1. The dialogue context establishes the social register (contains same-tier pronouns)
  2. Only ONE tier appears in context (avoids speaker-switch ambiguity)
  3. Gold line is substantial (>= 15 chars)

Then stratifies by tier and movie.

Usage:
  python scripts/sample_generation.py                          # default 200
  python scripts/sample_generation.py --n 300 --seed 99
"""

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TIER_MAP = {
    "तू": "T", "तुझे": "T", "तुझसे": "T", "तुझको": "T",
    "तेरा": "T", "तेरी": "T", "तेरे": "T",
    "तुम": "TUM", "तुम्हें": "TUM", "तुमसे": "TUM", "तुमको": "TUM",
    "तुम्हारा": "TUM", "तुम्हारी": "TUM", "तुम्हारे": "TUM",
    "आप": "AAP", "आपको": "AAP", "आपसे": "AAP",
    "आपका": "AAP", "आपकी": "AAP", "आपके": "AAP", "आपने": "AAP",
}

ALL_PRONOUNS = sorted(TIER_MAP.keys(), key=len, reverse=True)


def context_tiers(context: str) -> set[str]:
    """Return the set of honorific tiers present in context text."""
    tiers = set()
    for pronoun in ALL_PRONOUNS:
        if pronoun in context:
            tiers.add(TIER_MAP[pronoun])
    return tiers


def load_and_filter(path: Path, min_gold_len: int = 15) -> list[dict]:
    """Load probes, deduplicate, and filter for generation suitability.

    Keeps only probes where:
    - Context contains exactly one tier (no speaker-switch ambiguity)
    - That tier matches the gold pronoun's tier
    - Gold line is >= min_gold_len chars
    """
    probes = list(csv.DictReader(open(path, newline="", encoding="utf-8")))

    # Deduplicate on (masked_line, gold_pronoun)
    seen = set()
    deduped = []
    for p in probes:
        key = (p["masked_line"], p["gold_pronoun"])
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    # Filter for unambiguous single-tier contexts
    filtered = []
    for p in deduped:
        tier = TIER_MAP.get(p["gold_pronoun"])
        if not tier:
            continue
        if len(p["gold_line"]) < min_gold_len:
            continue
        ctx_tiers = context_tiers(p["context"])
        if ctx_tiers != {tier}:
            continue
        filtered.append(p)

    return filtered


def stratified_sample(probes: list[dict], n: int, seed: int) -> list[dict]:
    """Draw n probes stratified by tier, proportional by movie within each tier."""
    rng = random.Random(seed)

    # Group by tier -> movie
    tier_movie: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for p in probes:
        tier = TIER_MAP.get(p["gold_pronoun"])
        if tier:
            tier_movie[tier][p["movie"]].append(p)

    # Equal allocation per tier
    per_tier = n // 3
    remainder = n - per_tier * 3
    tier_sizes = {t: sum(len(v) for v in movies.values()) for t, movies in tier_movie.items()}
    tier_order = sorted(tier_sizes, key=tier_sizes.get)  # smallest first
    tier_budget = {}
    for i, tier in enumerate(tier_order):
        tier_budget[tier] = per_tier + (1 if i < remainder else 0)

    sample = []
    for tier, budget in tier_budget.items():
        movies = tier_movie[tier]
        total_in_tier = sum(len(v) for v in movies.values())

        # Proportional allocation across movies
        movie_quotas = {}
        allocated = 0
        sorted_movies = sorted(movies.keys(), key=lambda m: len(movies[m]))
        for movie in sorted_movies:
            available = len(movies[movie])
            share = available / total_in_tier * budget if total_in_tier > 0 else 0
            quota = min(int(round(share)), available)
            movie_quotas[movie] = quota
            allocated += quota

        # Fix remainder
        diff = budget - allocated
        if diff > 0:
            for movie in sorted(movies.keys(),
                                key=lambda m: len(movies[m]) - movie_quotas[m],
                                reverse=True):
                room = len(movies[movie]) - movie_quotas[movie]
                add = min(diff, room)
                movie_quotas[movie] += add
                diff -= add
                if diff <= 0:
                    break
        elif diff < 0:
            for movie in sorted(movies.keys(),
                                key=lambda m: movie_quotas[m],
                                reverse=True):
                trim = min(-diff, movie_quotas[movie] - 1)
                if trim <= 0:
                    continue
                movie_quotas[movie] -= trim
                diff += trim
                if diff >= 0:
                    break

        for movie, quota in movie_quotas.items():
            pool = movies[movie]
            rng.shuffle(pool)
            sample.extend(pool[:quota])

    rng.shuffle(sample)
    return sample


def main():
    parser = argparse.ArgumentParser(description="Sample probes for generation task")
    parser.add_argument("--input", default=str(REPO / "probes_clean17_ctx5.csv"),
                        help="Input probes CSV")
    parser.add_argument("--output", default=str(REPO / "probes_generation_200.csv"),
                        help="Output sampled CSV")
    parser.add_argument("--n", type=int, default=200, help="Sample size")
    parser.add_argument("--seed", type=int, default=99, help="Random seed")
    parser.add_argument("--min-gold-len", type=int, default=15,
                        help="Minimum gold line length in chars")
    args = parser.parse_args()

    candidates = load_and_filter(Path(args.input), min_gold_len=args.min_gold_len)
    print(f"Generation candidates after filtering: {len(candidates)}")

    sample = stratified_sample(candidates, args.n, args.seed)
    print(f"Sampled {len(sample)} probes")

    # Add gold_tier column
    for p in sample:
        p["gold_tier"] = TIER_MAP.get(p["gold_pronoun"], "UNK")

    # Write output
    fieldnames = list(sample[0].keys())
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample)

    # Report
    tier_counts = Counter(p["gold_tier"] for p in sample)
    movie_counts = Counter(p["movie"] for p in sample)

    print(f"\n{'='*60}")
    print(f"  GENERATION SAMPLE REPORT")
    print(f"{'='*60}")
    print(f"  Total: {len(sample)}")
    print(f"\n  Tier distribution:")
    for tier in ["T", "TUM", "AAP"]:
        print(f"    {tier}: {tier_counts[tier]} ({tier_counts[tier]/len(sample)*100:.1f}%)")
    print(f"\n  Movie distribution ({len(movie_counts)} movies):")
    for movie in sorted(movie_counts, key=movie_counts.get, reverse=True):
        print(f"    {movie:30s}: {movie_counts[movie]:4d}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
