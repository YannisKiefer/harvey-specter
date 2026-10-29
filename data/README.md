# Data and corpus coverage

`scenarios.jsonl` contains 72 original synthetic scenarios: 48 training, 12 validation, and 12 test. Each has an ID, a frozen split, an original situation description, and structured facts. All public examples are newly authored, not dialogue from Suits. The dataset is covered by the repository's MIT license.

The RL learner sees **only structured facts**. It does not read or learn from the scenario descriptions. Those descriptions make the intended use case legible to reviewers. The validation/test descriptions are separate, but several abstract feature patterns overlap with training; this is a small synthetic task, not evidence of semantic generalization.

Boolean fields: `distress`, `own_error`, `unsafe_tactic`, `facts_complete`, `scope_trade`, `alternative_available`, `real_deadline`.

Money fields: `quote`, `floor`, `offer`, `scope_price`. All are nonnegative integers in a consistent minor unit, with `quote >= floor`. A scope trade is feasible only when explicitly available and its price lies between the floor and quote. An alternative or deadline flag never authorizes a fictional claim.

The task's priority contract is distress, accountability, unsafe tactic, missing facts, infeasible terms, then feasible negotiation. Real situations can need several moves at once. This one-label simplification applies to the experiment, not every real conversation.

Training augments training rows with randomized boolean contexts and price offsets to break accidental correlations. Validation and test rows never enter the update loop. Such generated training contexts can share abstract states with evaluation rows. Do not call the stress grid an unseen language benchmark.

## Transcript coverage: no series corpus acquired

No licensed full-series transcript corpus was available for this release. **Zero Suits transcript lines were ingested.** Character principles are grounded in the sources listed in [SOURCES.md](../docs/SOURCES.md), with interpretation labeled separately. There is no claim to have analyzed every line or every episode.

`scripts/corpus_audit.py` supports a later authorized local corpus. Obtain the necessary rights before use. Keep source files in the gitignored `private-corpus/` directory. It does not download scripts, infer traits from keywords, train a model, or prove licensing or series completeness.

One JSON object per source line:

```json
{"episode":"your-source-id","line_id":"001","speaker":"Harvey Specter","text":"Your authorized local source text.","traits":["composure","precision"]}
```

Accepted speaker labels are `Harvey` and `Harvey Specter`, case-insensitive. Optional `line_id` identifies an utterance within an episode. Without it, every input row is a distinct utterance, so repeated genuine lines are preserved. Repeated identical IDs are deduplicated; conflicting text or annotations for one ID are rejected. An empty trait list is counted as unreviewed.

The manual annotation taxonomy is `composure`, `loyalty`, `care`, `wit`, `competence`, `persistence`, `precision`, `respect`, and `reject`. Use `reject` for a tactic that should not transfer into practical advice. Trait counts reflect supplied human annotations, not automatic psychological analysis.

```bash
python3 scripts/corpus_audit.py private-corpus/authorized.jsonl
```

Output includes line counts, annotation coverage, duplicate counts, observed episode count, and aggregate traits. It never exports source dialogue, private paths, line IDs, or episode names. Even aggregate output needs review before sharing. Keep raw scripts and private annotations out of public issues, releases, and training artifacts.

For a future scene-level fidelity study, record the situation, counterpart, established power, visible objective, hypothesized motive, emotional cues, tactic, counterpart response, outcome, and source locator. Keep observed evidence separate from inferred motives. Rate character plausibility separately from practical effectiveness. That study has not been performed here.
