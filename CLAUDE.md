# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Benchmark evaluating LLM competence with Hindi second-person honorifics (तू/तुम/आप) in conversational settings. Two tasks: cloze (comprehension) and dialogue continuation (production). All data is **non-synthetic** — derived from real Hindi film dialogue (IndicDialogue subtitles).

## Key Concepts

**Hindi Honorific System**: Hindi requires explicit formality marking:
- तू (tu) = very informal/intimate
- तुम (tum) = informal/familiar
- आप (aap) = formal/respectful

18 pronoun forms across 3 tiers (nominative, oblique, possessive, dative cases).

**Pronoun-verb agreement** is part of correctness (e.g., आप … हैं vs तुम … हो vs तू … है).

## Repository Structure

- `modules/IndicDialogue/`: subtitle dialogues. `Hindi/Hindi.jsonl` is the primary source.
- `modules/hindi-politeness/`: reference corpus (validation only).
- `modules/honorific-wiki-llm/`: prior work resources (Mukherjee et al.).
- `scripts/`: extraction, sampling, evaluation, and visualization pipeline.
- `probes_clean17_ctx5.csv`: full cleaned probe set (4,271 probes from 17 films).
- `probes_stratified_500.csv`: cloze evaluation sample (stratified by tier and movie).
- `probes_generation_200.csv`: generation evaluation sample (single-tier contexts only).
- `results/`: model evaluation outputs (JSONL + metrics JSON).

## Current Status

- **Done**: Probe extraction, cleaning, deduplication, stratified sampling, cloze and generation pipelines
- **Pending**: Run evaluations on both tasks, cross-family model comparison

## Scripts

- `scripts/indicdialogue_extract_probes.py`: extracts pronoun cloze probes from IndicDialogue.
- `scripts/filter_probes_clean17.py`: filters to 17 high-quality Hindi-original films.
- `scripts/sample_stratified.py`: stratified sampling for cloze task (balanced tier + proportional movie).
- `scripts/sample_generation.py`: filtered sampling for generation task (single-tier contexts only).
- `scripts/cloze_eval.py`: cloze evaluation pipeline (MC via API, logprob, baselines).
- `scripts/generation_eval.py`: generation evaluation (dialogue continuation from real contexts).
- `scripts/tier_classifier.py`: pronoun/tier classification with verb agreement patterns.
- `scripts/plot_results.py`: visualization.

## Known Limitations

- IndicDialogue lacks speaker diarization — mitigated in generation by restricting to single-register contexts.
- TUM_VERB regex in `tier_classifier.py` matches any ो-ending word (false positives). Needs constraining.
