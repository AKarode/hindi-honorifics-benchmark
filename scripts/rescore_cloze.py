#!/usr/bin/env python3
"""
Re-score existing cloze results with the fixed scorer.

Usage:
    python scripts/rescore_cloze.py results/gpt5_mini_mc_500.jsonl
"""

import argparse
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cloze_eval import compute_metrics, print_report, save_results, load_probes, extract_pronoun_from_response


def rescore_results(input_path: str, probes_path: str, output_path: str = None):
    """Re-score existing cloze results with fixed scorer."""
    results = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            results.append(json.loads(line))
    
    probes = load_probes(probes_path)
    
    print(f"Loaded {len(results)} results from {input_path}")
    print(f"Loaded {len(probes)} probes from {probes_path}")
    
    # Re-extract pronouns from verbose responses
    rescored = []
    for r in results:
        predicted = r.get("predicted", "")
        
        # Re-apply extraction if it's not an error
        if not predicted.startswith("ERROR"):
            raw = r.get("raw_response", predicted)
            predicted = extract_pronoun_from_response(raw if raw else predicted)
        
        rescored.append({
            "probe_idx": r["probe_idx"],
            "predicted": predicted,
            "raw_response": r.get("raw_response"),
            "scores": r.get("scores", {}),
        })
    
    # Compute new metrics
    metrics = compute_metrics(probes, rescored)
    
    # Infer model name from input path
    model_name = Path(input_path).stem.replace("_mc_500", "").replace("_", "-")
    metrics["model"] = model_name
    metrics["rescored"] = True
    
    print_report(metrics, f"{model_name} (RESCORED)")
    
    # Save if output path provided
    if output_path:
        save_results(rescored, metrics, output_path)
    
    return rescored, metrics


def main():
    parser = argparse.ArgumentParser(description="Re-score cloze results")
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("--probes", default="probes_stratified_500.csv", help="Probes CSV file")
    parser.add_argument("--output", default=None, help="Output JSONL (optional)")
    args = parser.parse_args()
    
    rescore_results(args.input, args.probes, args.output)


if __name__ == "__main__":
    main()
