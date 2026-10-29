# Contributing

A useful contribution fixes a demonstrated decision failure or makes the evidence easier to reproduce.

For a new case, include a de-identified prompt, the model and harness, the actual response, and the specific fact, calculation, tone, or boundary that failed. Label written examples separately from captured model output. Never include customer information, private conversations, credentials, or copyrighted script excerpts.

Keep skill instructions short. Add reference material only when it changes decisions. Original examples are welcome; memorized dialogue and catchphrase collections are not. Do not turn interpretation into an unsupported claim about the show.

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/strategy_lab.py train
python3 scripts/stress_eval.py
git diff --check
```

For skill changes, exercise a realistic scenario and record the actual result. Automated routing tests do not validate natural-language behavior. Keep training and evaluation inputs distinct; record rejected experiments and any feedback used to improve a candidate. New evaluation cases created after a failure are regression evidence, not a pristine held-out result.

By contributing original material, you agree it is available under this repository's MIT license. Maintainers review changes before merging. Be specific and respectful; do not solicit stars, mass-post issues, or advertise this project in unrelated discussions.
