#!/usr/bin/env python3
"""Filter probes_hindi_only_ctx5.csv to only the 17 HIGH-quality Hindi-original films."""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 17 films that passed the subtitle quality audit (score 4-5)
CLEAN_FILMS = {
    "Axone",
    "Darlings",
    "Dhamaka",
    "Ginny Weds Sunny",
    "Good Newwz",
    "Guilty",
    "Haseen Dillruba",
    "Hit the First Case",
    "Indoo Ki Jawani",
    "Jaadugar",
    "Jaane Jaan",
    "Lust Stories 2",
    "Madam Chief Minister",
    "Shehzada",
    "The Great Indian Family",
    "The White Tiger",
    "Tu Jhoothi Main Makkaar",
}

def main():
    infile = REPO / "probes_hindi_only_ctx5.csv"
    outfile = REPO / "probes_clean17_ctx5.csv"

    kept = 0
    skipped = 0
    film_counts = {}

    with open(infile, newline="", encoding="utf-8") as fin, \
         open(outfile, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            movie = row["movie"].strip()
            if movie in CLEAN_FILMS:
                writer.writerow(row)
                kept += 1
                film_counts[movie] = film_counts.get(movie, 0) + 1
            else:
                skipped += 1

    print(f"Kept: {kept} probes from {len(film_counts)} films")
    print(f"Skipped: {skipped} probes")
    print(f"\nPer-film breakdown:")
    for film in sorted(film_counts, key=film_counts.get, reverse=True):
        print(f"  {film}: {film_counts[film]}")

    # Verify we got all 17
    missing = CLEAN_FILMS - set(film_counts.keys())
    if missing:
        print(f"\n⚠️  Missing films (no probes found): {missing}")

if __name__ == "__main__":
    main()
