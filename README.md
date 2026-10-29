<div align="center">

<img src="assets/banner.png" alt="SPECTER. Composure is a skill. A Harvey Specter-inspired skill for AI agents." width="100%">

**A closer's judgment. In your agent.**

Prepare the leverage. Read the room. Make the next move count.

[![Checks](https://github.com/YannisKiefer/harvey-specter/actions/workflows/checks.yml/badge.svg)](https://github.com/YannisKiefer/harvey-specter/actions/workflows/checks.yml)
[![MIT](https://img.shields.io/badge/license-MIT-b7eb83)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/format-SKILL.md-1c1e1b)](https://agentskills.io/specification)

[Install](#install) · [Try it](#try-it) · [The method](#the-method) · [Evidence](docs/EVALUATION.md) · [Brand assets](assets/brand/README.md)

</div>

## Meet SPECTER

A Harvey Specter-inspired skill for negotiation, difficult conversations, leadership, and composure under pressure. It gives your agent a way to decide what matters before choosing what to say.

Confident with an investor. Demanding with a promising junior. Accountable after a mistake. Present when a friend is hurting. The relationship changes the response.

The default is a mature interpretation of Harvey: prepared, incisive, loyal, and willing to change his mind. Explicit fictional roleplay can explore the contradictions behind the confidence.

## Install

```bash
npx skills add YannisKiefer/harvey-specter --skill harvey-specter
```

Choose your agent when prompted. The skill itself is plain Markdown; it needs no API key, Python, server, or account. You can also open [SKILL.md](skills/harvey-specter/SKILL.md) and provide it to an agent as instructions, along with a relevant reference when needed. Follow your agent's skill-loading instructions for automatic discovery.

The repository includes optional Python experiments. They are separate from installation and require Python 3.10+ with no third-party dependencies.

## Try it

```text
Use the harvey-specter skill.

A client offered 8,000 for a 12,000 project. Our minimum is 10,000.
We can remove reporting and one review round to make 10,000 work.
There's no other buyer. Draft the reply and explain the next move.
```

An original worked example:

> For the full scope, the price is 12,000. We can bring it to 10,000 by removing the reporting package and moving to one review round. Which version fits your priorities?

The useful move is a feasible trade. Keep the floor private. Don't invent a competing offer. Don't accidentally promise a 20% discount: that would land at 9,600, below the minimum.

More prompts:

- "The investor wants twice the equity. Help me identify the real issue before I counter."
- "I missed a deadline. Write an apology that takes responsibility without inventing a recovery date."
- "A talented junior challenged my plan. Help me demand evidence while staying open to being wrong."
- "My friend just lost their job. Drop the boardroom voice and help me show up."
- "Roleplay an original scene where a trusted partner calls out your pride. Keep it fictional."

[Read the worked playbook →](skills/harvey-specter/references/playbook.md)

## The method

SPECTER asks what the situation needs, then adapts the voice.

| The moment | The move |
| --- | --- |
| Someone is overwhelmed | Steady them. Make the next step manageable. |
| You caused the problem | Own it. Repair what you can. Promise only what you control. |
| The tactic requires deception or intimidation | Hold the line. Find an honest route to the goal. |
| A decisive fact is missing | Investigate before committing. |
| Terms breach a genuine minimum | Walk warm, or change the scope. |
| An agreement is feasible | Negotiate with evidence and trade-offs. |

For harder situations, the [character engine](skills/harvey-specter/references/character-engine.md) adds twelve interacting traits, incentive analysis, relationship dynamics, pressure, and the tension between pride and judgment. It keeps two questions separate: would this fit the character, and would it be good advice?

The agent should anticipate a plausible reply, examine the assumption setting the terms, and prepare a fallback. It should never claim to know someone's hidden motives.

## Built to be challenged

The repository includes:

- **72 original structured scenarios**, split into training, validation, and test rows.
- **A real local RL experiment**: a small contextual bandit learns move selection from deterministic rewards. It trains a lookup policy, not a language model or the skill's prose.
- **A separate behavioral review** with original prompts and observed agent responses.
- **A private-corpus audit tool** for authorized, locally supplied transcript annotations. It exports aggregate counts, never dialogue.
- **Automated tests and an independent stress evaluator**, including mixed priorities and arithmetic boundaries.

```bash
git clone https://github.com/YannisKiefer/harvey-specter.git
cd harvey-specter
python3 -m unittest discover -s tests -v
python3 scripts/strategy_lab.py train
python3 scripts/stress_eval.py
```

Read the [evaluation report](docs/EVALUATION.md) before interpreting any score. The original linear learner failed mixed-context tests; those failures led to a finite-state learner and a deterministic guard. Synthetic routing success does not measure personality fidelity, prose quality, or real negotiation outcomes. The natural-language skill does not invoke the experimental policy automatically.

## What this release can claim

The character foundation comes from [creator commentary and official character material](docs/SOURCES.md), plus an openly labeled interpretive blueprint. The examples and public dataset are original.

This release does **not** claim a complete analysis of every Suits line, licensed access to a full transcript corpus, language-model fine-tuning, perfect imitation, or a guaranteed business result. [Corpus coverage and data provenance](data/README.md) explain what exists and what is missing.

SPECTER is an independent fan-inspired project. It is not affiliated with Suits, NBCUniversal, USA Network, Netflix, Gabriel Macht, or the show's creators. Character names remain the property of their respective owners. MIT covers this project's original code, instructions, and examples; it grants no rights to third-party scripts or characters. Generated artwork depicts an original still life, not an actor or a show frame.

## Build the next case

Bring a situation where the response was too theatrical, too timid, or wrong about the facts. Include the prompt, model/harness, actual answer, and what should have changed. Remove private details first.

[Contributing](CONTRIBUTING.md) · [Open a case](https://github.com/YannisKiefer/harvey-specter/issues/new) · [Launch research](docs/LAUNCH.md)

MIT. Built by [Yannis Kiefer](https://github.com/YannisKiefer).
