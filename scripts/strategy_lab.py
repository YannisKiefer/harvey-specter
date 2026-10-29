#!/usr/bin/env python3
"""A dependency-free contextual bandit. Trains move selection, not an LLM."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = ("steady", "repair", "boundary", "discover", "walk", "negotiate", "bluff", "capitulate")
FLAGS = ("distress", "own_error", "unsafe_tactic", "facts_complete", "scope_trade", "alternative_available", "real_deadline")


def validate(facts):
    if not isinstance(facts, dict) or set(facts) != set(FLAGS) | {"quote", "floor", "offer", "scope_price"}:
        raise ValueError("facts must contain exactly the documented fields")
    if any(type(facts[k]) is not bool for k in FLAGS):
        raise ValueError("flags must be JSON booleans")
    if any(type(facts[k]) is not int or not 0 <= facts[k] <= 10**9 for k in ("quote", "floor", "offer", "scope_price")):
        raise ValueError("prices must be nonnegative integer minor units, at most 1e9")
    if facts["quote"] < facts["floor"]:
        raise ValueError("quote cannot be below floor")
    return facts


def feasible_trade(facts):
    return facts["scope_trade"] and facts["floor"] <= facts["scope_price"] <= facts["quote"]


def required_move(facts):
    """Published synthetic task contract; not a real-world moral oracle."""
    validate(facts)
    if facts["distress"]:
        return "steady"
    if facts["own_error"]:
        return "repair"
    if facts["unsafe_tactic"]:
        return "boundary"
    if not facts["facts_complete"]:
        return "discover"
    if facts["offer"] < facts["floor"] and not feasible_trade(facts):
        return "walk"
    return "negotiate"


def features(facts):
    validate(facts)
    return [1.0, float(facts["distress"]), float(facts["own_error"]),
            float(facts["unsafe_tactic"]), float(not facts["facts_complete"]),
            float(facts["offer"] < facts["floor"]), float(feasible_trade(facts)),
            float(facts["alternative_available"]), float(facts["real_deadline"])]


def reward(facts, action):
    return 1.0 if action == required_move(facts) else -1.0


def state_key(facts):
    return "".join(str(int(value)) for value in features(facts)[1:])


def choose(policy, facts):
    scores = policy.get(state_key(facts))
    if scores is None:
        return "discover"
    return ACTIONS[max(range(len(ACTIONS)), key=lambda i: scores[i])]


def load_dataset(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    seen = set()
    for row in rows:
        if row["id"] in seen or row["split"] not in ("train", "validation", "test"):
            raise ValueError("duplicate id or invalid split")
        seen.add(row["id"])
        validate(row["facts"])
    if not all(any(r["split"] == split for r in rows) for split in ("train", "validation", "test")):
        raise ValueError("all three splits are required")
    return rows


def train(rows, seed=17, episodes=24000):
    # Tabular one-step Q learning. No validation/test rows enter the update loop.
    rng = random.Random(seed)
    pool = [row for row in rows if row["split"] == "train"]
    policy = {}
    for step in range(episodes):
        facts = dict(rng.choice(pool)["facts"])
        # Simulated training environments break incidental correlations in the seed rows.
        if step % 2:
            for key in FLAGS:
                facts[key] = bool(rng.randrange(2))
            facts["offer"] = max(0, facts["floor"] + rng.choice((-20000, 0, 20000)))
            facts["scope_price"] = max(0, facts["floor"] + rng.choice((-5000, 5000, 50000)))
        scores = policy.setdefault(state_key(facts), [0.0] * len(ACTIONS))
        action = rng.randrange(len(ACTIONS)) if rng.random() < 0.2 else max(range(len(ACTIONS)), key=lambda i: scores[i])
        result = reward(facts, ACTIONS[action])
        error = result - scores[action]
        scores[action] += 0.2 * error
    return policy


def evaluate(rows, weights, split):
    cases = []
    for row in rows:
        if row["split"] != split:
            continue
        predicted = choose(weights, row["facts"])
        expected = required_move(row["facts"])
        cases.append({"id": row["id"], "expected": expected, "actual": predicted,
                      "passed": predicted == expected})
    return {"passed": sum(c["passed"] for c in cases), "total": len(cases), "cases": cases}


def experiment(dataset_path, seed=17, episodes=24000):
    rows = load_dataset(dataset_path)
    baseline = {state_key(row["facts"]): [0.0] * len(ACTIONS) for row in rows}
    for values in baseline.values():
        values[ACTIONS.index("negotiate")] = 1.0
    candidate = train(rows, seed, episodes)
    base_val = evaluate(rows, baseline, "validation")
    candidate_val = evaluate(rows, candidate, "validation")
    accepted = candidate_val["passed"] == candidate_val["total"] and candidate_val["passed"] > base_val["passed"]
    selected = candidate if accepted else baseline
    # Test is reported only after the validation gate has selected the policy.
    report = {"method": "epsilon-greedy tabular contextual bandit with deterministic task rewards",
              "scope": "structured move selection only; no language-model training or style score",
              "training_environments": "48 seed rows plus randomized synthetic contexts; not natural-language learning",
              "seed": seed, "episodes": episodes,
              "dataset_sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
              "accepted": accepted, "baseline_validation": base_val,
              "candidate_validation": candidate_val,
              "baseline_test": evaluate(rows, baseline, "test"),
              "selected_test": evaluate(rows, selected, "test")}
    return selected, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("train")
    run.add_argument("--data", type=Path, default=ROOT / "data/scenarios.jsonl")
    run.add_argument("--output", type=Path, default=ROOT / "local-results")
    run.add_argument("--seed", type=int, default=17)
    run.add_argument("--episodes", type=int, default=24000)
    predict = sub.add_parser("predict")
    predict.add_argument("--policy", type=Path, required=True)
    predict.add_argument("--facts", required=True, help="JSON facts object; see data/scenarios.jsonl")
    args = parser.parse_args()
    try:
        if args.command == "train":
            if not 1 <= args.episodes <= 1000000:
                raise ValueError("episodes must be between 1 and 1000000")
            weights, report = experiment(args.data, args.seed, args.episodes)
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / "policy.json").write_text(json.dumps({"actions": ACTIONS, "values": weights}, indent=2, sort_keys=True) + "\n")
            (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps({k: v for k, v in report.items() if k not in ("baseline_validation", "candidate_validation", "baseline_test", "selected_test")}, indent=2))
            for key in ("baseline_validation", "candidate_validation", "baseline_test", "selected_test"):
                print(f'{key}: {report[key]["passed"]}/{report[key]["total"]}')
            return 0 if report["accepted"] else 1
        policy = json.loads(args.policy.read_text())
        values = policy["values"]
        if policy["actions"] != list(ACTIONS) or not isinstance(values, dict):
            raise ValueError("invalid policy format or action order")
        for key, row in values.items():
            if len(key) != 8 or set(key) - {"0", "1"} or not isinstance(row, list) or len(row) != len(ACTIONS):
                raise ValueError("invalid state key or action values")
            if any(type(w) not in (int, float) or not math.isfinite(w) for w in row):
                raise ValueError("action values must be finite numbers")
        facts = json.loads(args.facts)
        learned = choose(values, facts)
        guarded = required_move(facts)
        print(json.dumps({"move": guarded, "learned_move": learned, "guard_override": learned != guarded}))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
