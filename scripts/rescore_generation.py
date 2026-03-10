#!/usr/bin/env python3
"""
Re-score existing generation results with the fixed tier classifier.

Usage:
    python scripts/rescore_generation.py results/gen_gpt5_mini.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generation_eval import score_generation, compute_metrics, print_report, save_results
from tier_classifier import PRONOUN_TO_TIER


def rescore_results(input_path: str, output_path: str = None):
    """Re-score existing generation results with fixed classifier."""
    results = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            results.append(json.loads(line))
    
    print(f"Loaded {len(results)} results from {input_path}")
    
    # Re-score each result
    rescored = []
    for r in results:
        if "error" in r:
            rescored.append(r)
            continue
        
        response = r.get("response", "")
        expected_tier = r.get("expected_tier") or PRONOUN_TO_TIER.get(r.get("gold_pronoun"))
        
        new_score = score_generation(response, expected_tier)
        
        # Merge new scores with original result (keeping metadata)
        new_result = {
            "movie": r.get("movie"),
            "gold_pronoun": r.get("gold_pronoun"),
            "expected_tier": expected_tier,
            "gold_line": r.get("gold_line"),
            "context": r.get("context"),
            "prompt": r.get("prompt"),
            "response": response,
            **new_score,
        }
        rescored.append(new_result)
    
    # Compute new metrics
    metrics = compute_metrics(rescored)
    
    # Infer model name from input path
    model_name = Path(input_path).stem.replace("gen_", "").replace("_", "-")
    metrics["model"] = model_name
    metrics["rescored"] = True
    
    print_report(metrics, f"{model_name} (RESCORED)")
    
    # Save if output path provided
    if output_path:
        save_results(rescored, metrics, output_path)
    else:
        # Overwrite original
        output_path = input_path
        save_results(rescored, metrics, output_path)
    
    return rescored, metrics


def main():
    parser = argparse.ArgumentParser(description="Re-score generation results")
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("--output", default=None, help="Output JSONL (default: overwrite input)")
    args = parser.parse_args()
    
    rescore_results(args.input, args.output)


if __name__ == "__main__":
    main()
