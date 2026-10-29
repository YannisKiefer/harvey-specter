# Evaluation: what ran and what it proves

Release evaluation, October 29, 2026. The skill, learned policy, and deterministic guard are three different artifacts. Their results must not be combined into a personality score.

## Observed results

| Check | Observed result | What it establishes |
| --- | --- | --- |
| Automated unit tests | 13 passed | Reproducibility, split isolation, priority rules, input rejection, duplicate handling, and private-corpus output boundaries. |
| Final RL validation | 12/12; always-negotiate baseline 2/12 | Correct move selection on a small fixed synthetic split. |
| Final RL test | 12/12; always-negotiate baseline 2/12 | Same narrow task, after development feedback was already consumed. Not a pristine post-development holdout. |
| Independent structural grid | Raw policy 1,408/1,408; guard function 1,408/1,408 | 128 Boolean contexts across 11 price regimes, including mixed priorities and numeric edges. This is a regression check of the finite abstraction. |
| Actual predict CLI guard checks | 3/3 | Empty, maliciously biased, and correct policies produce the rule-contract move with a truthful override trace. |
| Independent natural-language review | 12 initial cases and 4 character-engine cases exercised | Recorded prompts, generated responses, and qualitative assessments in one reviewing-agent context. |
| Skill package | Frontmatter validated; local skills-CLI installation succeeded | Structural validity and a real installer path, not universal harness behavior. |

The [recorded strategy run](../evals/strategy-report.json), [behavioral cases](BEHAVIOR.md), and [final independent review](REVIEW.md) contain the evidence and limitations. CI runs the automated checks on the actual published commit.

## The failures that changed the implementation

The first policy-gradient experiment scored 10/12 on validation and test. More training alone did not fix it. A linear value learner then reached 12/12 on those small splits but failed **294 of 1,408** independently constructed stress cases: 150 steady, 80 repair, 44 boundary, and 20 discovery contexts were incorrectly treated as negotiation. Mixed contexts exposed accidental training correlations.

The final implementation uses a tabular learner for the small finite state space, plus explicitly randomized synthetic training environments. It also adds a deterministic guard to the actual `predict` command. The unchanged stress expectations then passed. The prior failures were not removed or reclassified as successes. The initial test and stress feedback informed development, so the final score is a regression result, not evidence of untouched generalization.

## The experiment

```bash
python3 scripts/strategy_lab.py train
python3 scripts/stress_eval.py
```

The seed is 17; the default run has 24,000 one-step episodes. The environment exposes eight actions: six constructive moves, bluff, and capitulate. A deterministic verifier returns +1 for the contract-consistent move and -1 otherwise. With 20% exploration, the learner updates the chosen state's action value toward that reward. Half the episodes randomize training-row flags and price offsets, so the learner sees simulated combinations beyond the original rows.

Only training rows seed updates. A unit test mutates all validation/test facts and confirms the learned values remain identical. A validation gate requires every validation row to pass and a strict improvement over the always-negotiate baseline before selecting the candidate. The baseline is deliberately simple; the hand-written contract itself is perfect by construction. RL is unnecessary for implementing that contract and does not outperform it.

The eight-bit state records distress, accountability, unsafe tactics, missing facts, below-floor offer, feasible scope trade, alternative availability, and real deadline. Several seed train and evaluation rows share these abstract features; generated environments extend the overlap. Scenario text never enters the learner. The independent grid varies all seven input flags across eleven fixed numeric regimes. It verifies the abstraction, not every possible real negotiation.

`predict` always uses the deterministic task contract for its authoritative `move`, and reports `learned_move` plus `guard_override` for comparison. Learned rewards cannot authorize deception or bypass the guard. The natural-language skill does not call this experimental script automatically.

This is a genuine small RL experiment with executable, task-specific verifiable rewards. It does **not** train language-model weights, edit the skill, learn Harvey's voice, process transcripts, measure emotion, or improve itself after installation.

## Natural-language behavior and character fidelity

An independent reviewer generated responses under the skill to original scenarios covering negotiation, arithmetic, grief, apology, deception, vulnerable colleagues, legal uncertainty, hostile messages, prompt injection, German drafting, closing, and absent alternatives. A later pass exercised trusted correction, loyalty versus misconduct, investor framing, and fictional vulnerability. The reviewer did not author the skill.

These are actual generated outputs in one reviewing-agent context, assessed by that same reviewer. They are not blinded human judgments, separate provider trials, multiple samples per case, an A/B improvement estimate, a Claude-platform certification, or proof of market outcomes. Two unsupported commitments in the original worked examples were found and corrected before release; the original report retains those findings.

Character fidelity and practical effectiveness remain qualitative and distinct. No universal 100/100 score is assigned. Compatibility with other agents follows the portable format but has not been behaviorally verified in each harness. A genuine Claude run was unavailable because the local Claude CLI was logged out; no credentials were collected or account settings changed.

## Reproduction limits

Python's seeded standard-library PRNG makes a run reproducible in the same runtime; cross-version identity of every value is not promised. CI verifies the supported runtime. The corpus tool's tests use original sentinel sentences, not show dialogue. No full-series corpus, field negotiation study, repeated-sampling reliability study, or copyright/trademark clearance opinion is included.
