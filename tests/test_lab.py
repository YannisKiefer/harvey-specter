import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corpus_audit as corpus
import strategy_lab as lab


class StrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = lab.load_dataset(ROOT / "data/scenarios.jsonl")
        cls.weights = lab.train(cls.rows)

    def test_held_out_moves(self):
        result = lab.evaluate(self.rows, self.weights, "test")
        self.assertEqual(result["passed"], result["total"], result["cases"])

    def test_holdouts_never_enter_training(self):
        altered = copy.deepcopy(self.rows)
        for row in altered:
            if row["split"] != "train":
                row["facts"]["distress"] = not row["facts"]["distress"]
        self.assertEqual(self.weights, lab.train(altered))

    def test_reproducible_training(self):
        self.assertEqual(self.weights, lab.train(self.rows))

    def test_distress_overrides_competitive_move(self):
        facts = dict(self.rows[-1]["facts"], distress=True, unsafe_tactic=True)
        self.assertEqual(lab.required_move(facts), "steady")

    def test_invalid_reduced_scope_still_needs_boundary(self):
        facts = dict(self.rows[-1]["facts"], scope_trade=True, scope_price=1, offer=1)
        self.assertEqual(lab.required_move(facts), "walk")

    def test_private_alternative_not_a_license_to_bluff(self):
        for row in self.rows:
            facts = dict(row["facts"], alternative_available=False)
            self.assertEqual(lab.reward(facts, "bluff"), -1)

    def test_invalid_numeric_and_boolean_inputs(self):
        for field, value in (("offer", True), ("floor", -1), ("quote", float("nan")), ("distress", "false")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                lab.validate(dict(self.rows[0]["facts"], **{field: value}))

    def test_cli_rejects_invalid_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            policy = Path(temp) / "policy.json"
            policy.write_text(json.dumps({"actions": lab.ACTIONS, "values": {"00000000": [float("nan")] * 8}}))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/strategy_lab.py"), "predict", "--policy", str(policy), "--facts", json.dumps(self.rows[0]["facts"])], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)


class CorpusTests(unittest.TestCase):
    def run_audit(self, rows):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "corpus.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            return corpus.audit(path)

    def test_filters_speaker_and_never_exports_dialogue(self):
        result = self.run_audit([
            {"episode": "original-example", "speaker": "Harvey Specter", "text": "Original synthetic sentence.", "traits": ["care", "care"]},
            {"episode": "original-example", "speaker": "Other", "text": "Another original sentence."}])
        self.assertEqual(result["speaker_lines"], 1)
        self.assertEqual(result["trait_counts"], {"care": 1})
        self.assertNotIn("sentence", json.dumps(result))
        self.assertFalse(result["dialogue_exported"])

    def test_repeated_utterances_are_not_silently_discarded(self):
        row = {"episode": "original-example", "speaker": "harvey", "text": "Original repeated sentence."}
        self.assertEqual(self.run_audit([row, row])["speaker_lines"], 2)
        identified = dict(row, line_id="line-1")
        result = self.run_audit([identified, identified])
        self.assertEqual(result["speaker_lines"], 1)
        self.assertEqual(result["duplicate_lines_skipped"], 1)

    def test_conflicting_ids_fail(self):
        row = {"episode": "original-example", "speaker": "harvey", "text": "Original.", "line_id": 1}
        with self.assertRaises(ValueError):
            self.run_audit([row, dict(row, text="Conflicting.")])

    def test_bad_annotation_does_not_echo_source(self):
        row = {"episode": "original-example", "speaker": "Harvey", "text": "PRIVATE SOURCE PLACEHOLDER", "traits": ["not-a-trait"]}
        with self.assertRaises(ValueError) as caught:
            self.run_audit([row])
        self.assertNotIn("PRIVATE SOURCE", str(caught.exception))

    def test_malformed_shapes_fail_cleanly(self):
        for row in ([], {}, {"speaker": "Harvey", "episode": "example", "text": "example", "traits": [None]}):
            with self.subTest(row=row), self.assertRaises(ValueError):
                self.run_audit([row])


if __name__ == "__main__":
    unittest.main()
