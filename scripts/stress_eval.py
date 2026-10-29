#!/usr/bin/env python3
"""Independent synthetic audit, frozen before any experimental output was read."""
import copy
from collections import Counter
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def expected(f):
    # Independent task specification. No use of the implementation's reward/oracle.
    priorities = ((f["distress"], "steady"), (f["own_error"], "repair"),
                  (f["unsafe_tactic"], "boundary"), (not f["facts_complete"], "discover"))
    for applies, move in priorities:
        if applies:
            return move
    valid_trade = f["scope_trade"] and f["scope_price"] >= f["floor"] and f["scope_price"] <= f["quote"]
    return "walk" if f["offer"] < f["floor"] and not valid_trade else "negotiate"


def run():
    lab, corpus = module("strategy_lab"), module("corpus_audit")
    rows = lab.load_dataset(ROOT / "data/scenarios.jsonl")
    # No held-out rows supplied to the learner. Seed/episodes fixed in advance.
    train_rows = [r for r in rows if r["split"] == "train"]
    weights = lab.train(train_rows, seed=17, episodes=24000)
    flags = ("distress", "own_error", "unsafe_tactic", "facts_complete", "scope_trade", "alternative_available", "real_deadline")
    # Quote, minimum, offer, smaller-scope price. Edge cases fixed before execution.
    regimes = ((0, 0, 0, 0), (150, 100, 0, 100), (150, 100, 99, 100),
               (150, 100, 100, 100), (150, 100, 101, 100), (150, 100, 150, 100),
               (150, 100, 151, 100), (150, 100, 99, 99), (150, 100, 99, 151),
               (150, 100, 99, 150), (10**9, 10**9, 10**9 - 1, 10**9))
    failures, oracle_failures = [], []
    expected_counts, failed_by_pair = Counter(), Counter()
    total = 0
    for bits in itertools.product((False, True), repeat=len(flags)):
        for quote, floor, offer, scope_price in regimes:
            f = dict(zip(flags, bits), quote=quote, floor=floor, offer=offer, scope_price=scope_price)
            wanted = expected(f)
            expected_counts[wanted] += 1
            total += 1
            actual = lab.choose(weights, f)
            if actual != wanted:
                failures.append({"facts": f, "expected": wanted, "actual": actual})
                failed_by_pair[f"{wanted}->{actual}"] += 1
            oracle = lab.required_move(f)
            if oracle != wanted:
                oracle_failures.append({"facts": f, "expected": wanted, "actual": oracle})
    # Changing held-out facts must not affect training weights.
    mutated = copy.deepcopy(rows)
    for r in mutated:
        if r["split"] != "train":
            r["facts"] = copy.deepcopy(train_rows[0]["facts"])
    contamination = lab.train(rows, 17, 24000) == lab.train(mutated, 17, 24000) == weights
    signatures = {split: {tuple(lab.features(r["facts"])) for r in rows if r["split"] == split}
                  for split in ("train", "validation", "test")}
    overlap = {split: len(signatures["train"] & signatures[split]) for split in ("validation", "test")}

    validation = []
    base = copy.deepcopy(train_rows[0]["facts"])
    invalid = [{}, [], {**base, "distress": 1}, {**base, "offer": True},
               {**base, "offer": -1}, {**base, "offer": 1.5}, {**base, "offer": float("nan")},
               {**base, "quote": 0, "floor": 1}, {**base, "quote": 10**9 + 1},
               {**base, "extra": "must reject"}]
    for item in invalid:
        try:
            lab.validate(item)
            validation.append(False)
        except ValueError:
            validation.append(True)

    corpus_checks = {}
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        path = temp / "private.jsonl"
        marker = "PRIVATE_DIALOGUE_SENTINEL_DO_NOT_EXPORT"
        entry = {"episode": "PRIVATE_EPISODE_SENTINEL", "speaker": "Harvey Specter", "text": marker, "line_id": "1", "traits": ["care", "care"]}
        repeated = {**entry, "line_id": "2"}
        path.write_text("\n".join(json.dumps(e) for e in (entry, repeated, entry)) + "\n")
        report = corpus.audit(path)
        corpus_checks["repeated_genuine_utterances_counted"] = report["speaker_lines"] == 2
        corpus_checks["same_id_exact_duplicates_skipped"] = report["duplicate_lines_skipped"] == 1
        corpus_checks["repeated_tags_count_once_per_line"] = report["trait_counts"] == {"care": 2}
        corpus_checks["dialogue_and_episode_not_exported"] = marker not in json.dumps(report) and "PRIVATE_EPISODE_SENTINEL" not in json.dumps(report)
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/corpus_audit.py"), str(path)], capture_output=True, text=True)
        corpus_checks["cli_success_private"] = proc.returncode == 0 and marker not in proc.stdout + proc.stderr
        conflicts = {**entry, "text": marker + " conflicting"}
        path.write_text(json.dumps(entry) + "\n" + json.dumps(conflicts) + "\n")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/corpus_audit.py"), str(path)], capture_output=True, text=True)
        corpus_checks["conflicting_id_rejected_private"] = proc.returncode == 2 and marker not in proc.stdout + proc.stderr and str(path) not in proc.stdout + proc.stderr
        malformed = ["not json " + marker, json.dumps([]), json.dumps({**entry, "traits": ["unknown"]}),
                     json.dumps({**entry, "text": ""}), json.dumps({**entry, "line_id": True})]
        for i, content in enumerate(malformed):
            path.write_text(content)
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/corpus_audit.py"), str(path)], capture_output=True, text=True)
            corpus_checks[f"malformed_{i}_rejected_private"] = proc.returncode == 2 and marker not in proc.stdout + proc.stderr and str(path) not in proc.stdout + proc.stderr
        missing = temp / "nonexistent-private-path"
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/corpus_audit.py"), str(missing)], capture_output=True, text=True)
        corpus_checks["missing_input_private_error"] = proc.returncode == 2 and str(missing) not in proc.stdout + proc.stderr
        path.write_bytes(b"\xff\xfe")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/corpus_audit.py"), str(path)], capture_output=True, text=True)
        corpus_checks["invalid_unicode_private_error"] = proc.returncode == 2 and str(path) not in proc.stdout + proc.stderr
        # Neither policy schema errors nor unusable output directories should traceback.
        schema_cases = ({"actions": list(lab.ACTIONS), "values": {"00000000": [0] * 7}},
                        {"actions": list(lab.ACTIONS), "values": {"00000000": [float("nan")] * 8}},
                        [], {"actions": [], "values": {}})
        policy_checks = []
        for policy in schema_cases:
            path.write_text(json.dumps(policy))
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/strategy_lab.py"), "predict", "--policy", str(path), "--facts", json.dumps(base)], capture_output=True, text=True)
            policy_checks.append(proc.returncode == 2 and "Traceback" not in proc.stderr)
        blocked_output = temp / "not-a-directory"
        blocked_output.write_text("preserve me")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/strategy_lab.py"), "train", "--episodes", "1", "--output", str(blocked_output)], capture_output=True, text=True)
        output_error_ok = proc.returncode == 2 and "Traceback" not in proc.stderr and blocked_output.read_text() == "preserve me"
    result = {"scope": "structured synthetic policy generalization, not natural language or style", "seed": 17, "episodes": 24000,
              "trained_on": dict(Counter(r["split"] for r in train_rows)), "stress_total": total,
              "stress_passed": total - len(failures), "stress_failed": len(failures),
              "expected_counts": dict(expected_counts), "failure_pairs": dict(failed_by_pair),
              "first_failures": failures[:16], "oracle_contract_failures": len(oracle_failures),
              "train_heldout_independence": contamination,
              "unique_contexts": {k: len(v) for k, v in signatures.items()}, "train_context_overlap": overlap,
              "invalid_fact_checks_passed": sum(validation), "invalid_fact_checks_total": len(validation),
              "corpus_checks": corpus_checks, "invalid_policy_checks_passed": sum(policy_checks),
              "invalid_policy_checks_total": len(policy_checks), "output_error_safe": output_error_ok}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    result = run()
    passed = (result["stress_failed"] == 0 and result["oracle_contract_failures"] == 0
              and result["train_heldout_independence"]
              and result["invalid_fact_checks_passed"] == result["invalid_fact_checks_total"]
              and all(result["corpus_checks"].values())
              and result["invalid_policy_checks_passed"] == result["invalid_policy_checks_total"]
              and result["output_error_safe"])
    raise SystemExit(0 if passed else 1)
