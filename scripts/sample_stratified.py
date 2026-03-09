#!/usr/bin/env python3
"""
Stratified sampling of cloze probes for evaluation.

Produces a deduplicated, stratified sample balanced by tier and movie.
Strategy:
  1. Deduplicate on (masked_line, gold_pronoun)
  2. Stratify by tier (T / TUM / AAP) — equal counts per tier
  3. Within each tier, sample proportionally across all 17 movies
  4. Shuffle the final sample

Usage:
  python scripts/sample_stratified.py                          # default 500
  python scripts/sample_stratified.py --n 1000 --seed 123
"""

import argparse
import csv
import random
from collections import defaultdict
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


def load_and_dedup(path: Path) -> list[dict]:
    """Load probes and deduplicate on (masked_line, gold_pronoun)."""
    probes = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    seen = set()
    deduped = []
    for p in probes:
        key = (p["masked_line"], p["gold_pronoun"])
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


def stratified_sample(probes: list[dict], n: int, seed: int) -> list[dict]:
    """
    Draw n probes stratified by tier, then proportional by movie within each tier.

    Each tier gets n // 3 probes (remainder goes to smallest tier first).
    Within a tier, movies are sampled proportionally to their share of that tier.
    """
    rng = random.Random(seed)

    # Group by tier -> movie
    tier_movie: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for p in probes:
        tier = TIER_MAP.get(p["gold_pronoun"])
        if tier:
            tier_movie[tier][p["movie"]].append(p)

    # Allocate per-tier counts — give extra to the smallest tiers
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
        for i, movie in enumerate(sorted_movies):
            available = len(movies[movie])
            # Proportional share, but cap at available
            if total_in_tier > 0:
                share = available / total_in_tier * budget
            else:
                share = 0
            quota = min(int(round(share)), available)
            movie_quotas[movie] = quota
            allocated += quota

        # Distribute remainder/shortfall across movies with room
        diff = budget - allocated
        if diff > 0:
            # Need more — add to movies with most remaining capacity
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
            # Over-allocated — trim from movies with largest quotas
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

        # Sample from each movie
        for movie, quota in movie_quotas.items():
            pool = movies[movie]
            rng.shuffle(pool)
            sample.extend(pool[:quota])

    rng.shuffle(sample)
    return sample


def main():
    parser = argparse.ArgumentParser(description="Stratified probe sampling")
    parser.add_argument("--input", default=str(REPO / "probes_clean17_ctx5.csv"),
                        help="Input probes CSV")
    parser.add_argument("--output", default=str(REPO / "probes_stratified_500.csv"),
                        help="Output sampled CSV")
    parser.add_argument("--n", type=int, default=500, help="Sample size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    probes = load_and_dedup(Path(args.input))
    print(f"Loaded {len(probes)} probes after deduplication")

    sample = stratified_sample(probes, args.n, args.seed)
    print(f"Sampled {len(sample)} probes")

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(sample[0].keys()))
        writer.writeheader()
        writer.writerows(sample)

    # Report stats
    from collections import Counter
    tier_counts = Counter(TIER_MAP.get(p["gold_pronoun"], "UNK") for p in sample)
    movie_counts = Counter(p["movie"] for p in sample)
    pronoun_counts = Counter(p["gold_pronoun"] for p in sample)

    print(f"\n{'='*60}")
    print(f"  STRATIFIED SAMPLE REPORT")
    print(f"{'='*60}")
    print(f"  Total: {len(sample)}")
    print(f"\n  Tier distribution:")
    for tier in ["T", "TUM", "AAP"]:
        print(f"    {tier}: {tier_counts[tier]} ({tier_counts[tier]/len(sample)*100:.1f}%)")
    print(f"\n  Movie distribution ({len(movie_counts)} movies):")
    for movie in sorted(movie_counts, key=movie_counts.get, reverse=True):
        print(f"    {movie:30s}: {movie_counts[movie]:4d}")
    print(f"\n  Pronoun form distribution:")
    for pronoun, count in pronoun_counts.most_common():
        print(f"    {pronoun}: {count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
