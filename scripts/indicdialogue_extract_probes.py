#!/usr/bin/env python3
import argparse
import csv
import json
import re
from typing import Iterable, List, Optional

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
LATIN_RE = re.compile(r"[A-Za-z]")

PRONOUN_TOKENS = [
    "तू",
    "तुम",
    "आप",
    "तुम्हें",
    "तुम्हारा",
    "तुम्हारी",
    "तुम्हारे",
    "तुमसे",
    "तुमको",
    "तुझे",
    "तुझसे",
    "तुझको",
    "आपको",
    "आपका",
    "आपकी",
    "आपके",
    "आपसे",
    "आपने",
]

TOKEN_RE = re.compile(
    r"(?<![\u0900-\u097F])(" + "|".join(map(re.escape, PRONOUN_TOKENS)) + r")(?![\u0900-\u097F])"
)


def is_devanagari_line(text: str, min_chars: int, max_latin_ratio: float) -> bool:
    if not text:
        return False
    dev_chars = len(DEVANAGARI_RE.findall(text))
    if dev_chars < min_chars:
        return False
    latin_chars = len(LATIN_RE.findall(text))
    total_letters = dev_chars + latin_chars
    if total_letters == 0:
        return False
    if latin_chars / total_letters > max_latin_ratio:
        return False
    return True


def find_pronoun(text: str) -> Optional[re.Match]:
    return TOKEN_RE.search(text)


def mask_pronoun(text: str, match: re.Match) -> str:
    return text[: match.start(1)] + "____" + text[match.end(1) :]


def iter_context_lines(dialogs: List[str], idx: int, context_size: int) -> Iterable[str]:
    if context_size <= 0:
        return []
    start = max(0, idx - context_size)
    return dialogs[start:idx]


def write_rows_csv(path: str, rows: List[dict]) -> None:
    if not rows:
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_rows_jsonl(path: str, rows: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract non-synthetic pronoun cloze probes from IndicDialogue Hindi subtitles."
    )
    parser.add_argument(
        "--input",
        default="modules/IndicDialogue/Hindi/Hindi.jsonl",
        help="Path to IndicDialogue Hindi.jsonl",
    )
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument(
        "--format",
        choices=["csv", "jsonl"],
        default="csv",
        help="Output format (csv or jsonl)",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=1,
        help="Number of previous lines to include as context",
    )
    parser.add_argument(
        "--min-devanagari-chars",
        type=int,
        default=3,
        help="Minimum Devanagari characters required for a line to be kept",
    )
    parser.add_argument(
        "--max-latin-ratio",
        type=float,
        default=0.2,
        help="Maximum ratio of Latin letters to total letters",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Max rows to output (0 = no limit)",
    )
    args = parser.parse_args()

    rows: List[dict] = []
    with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                data = json.loads(line)
            except Exception:
                continue
            dialogs = data.get("dialogs", {}).get("hin", [])
            if not dialogs:
                continue
            metadata = data.get("metadata", {})
            for idx, text in enumerate(dialogs):
                if not is_devanagari_line(text, args.min_devanagari_chars, args.max_latin_ratio):
                    continue
                match = find_pronoun(text)
                if not match:
                    continue
                context_lines = list(iter_context_lines(dialogs, idx, args.context))
                context_lines = [
                    c
                    for c in context_lines
                    if is_devanagari_line(c, args.min_devanagari_chars, args.max_latin_ratio)
                ]
                if len(context_lines) < args.context:
                    continue
                masked = mask_pronoun(text, match)
                row = {
                    "source": "IndicDialogue",
                    "movie": metadata.get("MovieName"),
                    "subtitle_id": metadata.get("IDSubtitleFile"),
                    "line_index": idx,
                    "context": "\n".join(context_lines),
                    "masked_line": masked,
                    "gold_line": text,
                    "gold_pronoun": match.group(1),
                }
                rows.append(row)
                if args.max_rows and len(rows) >= args.max_rows:
                    break
            if args.max_rows and len(rows) >= args.max_rows:
                break

    if args.format == "csv":
        write_rows_csv(args.output, rows)
    else:
        write_rows_jsonl(args.output, rows)


if __name__ == "__main__":
    main()

