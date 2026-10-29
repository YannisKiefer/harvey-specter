#!/usr/bin/env python3
"""Audit a locally supplied, authorized JSONL corpus without exporting dialogue."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

TRAITS = {"composure", "loyalty", "care", "wit", "competence", "persistence", "precision", "respect", "reject"}
SPEAKERS = {"harvey", "harvey specter"}


def audit(path):
    episodes, tags = Counter(), Counter()
    lines, reviewed, duplicates, seen = 0, 0, 0, {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip() for k in ("episode", "speaker", "text")):
                raise ValueError("episode, speaker, and text must be nonempty strings")
            if row["speaker"].strip().casefold() not in SPEAKERS:
                continue
            annotations = row.get("traits", [])
            if not isinstance(annotations, list) or any(not isinstance(t, str) or t not in TRAITS for t in annotations):
                raise ValueError("traits must be a list from the documented taxonomy")
            line_id = row.get("line_id", number)
            if type(line_id) not in (str, int) or not str(line_id).strip():
                raise ValueError("line_id must be a nonempty string or integer")
            identity = (row["episode"].strip(), str(line_id))
            digest = hashlib.sha256(json.dumps([row["text"], sorted(set(annotations))]).encode()).hexdigest()
            if identity in seen:
                if seen[identity] != digest:
                    raise ValueError("conflicting entries for the same episode and line_id")
                duplicates += 1
                continue
            seen[identity] = digest
            lines += 1
            episodes[identity[0]] += 1
            if annotations:
                reviewed += 1
                tags.update(set(annotations))
        except (ValueError, TypeError) as error:
            # Do not echo source text, JSON decoder excerpts, or private paths.
            raise ValueError(f"invalid corpus row {number}; check schema and taxonomy") from None
    return {"speaker_lines": lines, "annotated_lines": reviewed, "unannotated_lines": lines - reviewed,
            "duplicate_lines_skipped": duplicates, "episodes_observed": len(episodes),
            "trait_counts": dict(sorted(tags.items())),
            "scope": "supplied rows only; neither complete-series coverage nor automatic trait inference",
            "dialogue_exported": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.input), indent=2))
    except (ValueError, OSError, UnicodeError):
        parser.exit(2, "error: corpus unreadable or invalid; no dialogue exported\n")


if __name__ == "__main__":
    main()
