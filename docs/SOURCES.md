# Sources and interpretation

Sources were checked on October 29, 2026. No episode transcripts, show stills, actor photographs, or third-party dialogue are redistributed.

| Source | What supports this project | Boundary |
| --- | --- | --- |
| [USA Network: Aaron Korsh on Harvey's seven admirable qualities](https://pro-serv-tp.s3.amazonaws.com/Suits/www.usanetwork.com/suits/blog/harvey-specters-7-best-qualities.html), February 6, 2017 | Loyalty, care, wit, competence, persistence, deliberate wording, and equal human worth. The creator explains the preparation behind seemingly instant responses. | Character commentary, not a transcript corpus or evidence that every fictional tactic is effective. |
| [Netflix Tudum: Suits character guide](https://www.netflix.com/tudum/articles/suits-cast-characters), July 1, 2024 | Character identities and the credentials deception at the center of the story. | Supports separating mentorship and loyalty from concealment or invented authority. |
| Contributor-provided personality blueprint | The twelve-trait interpretation, confidence as armor, relational changes, pride versus judgment, and separate fidelity/effectiveness assessment. | A design input, not independently validated clinical or episode-wide research. The release adapts its useful concepts and supplies all references it actually links. |
| [Agent Skills specification](https://agentskills.io/specification) | `SKILL.md` with metadata and progressively loaded supporting references. | Format compatibility alone does not prove behavior in every harness. |
| [Vercel skills CLI](https://github.com/vercel-labs/skills) and [command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) | Repository discovery and installation. | Directory listing and ranking are independently controlled; installation is not evidence of popularity. |

The character engine is an original operational interpretation. Its relationship examples, pressure model, and tension pairs are not episode-specific findings. It makes no unsupported claim about exact season boundaries or psychological diagnoses. No claim from an unlinked favicon or an unspecified interview is treated as established fact.

## Learning terminology

The local experiment uses a **contextual bandit**, a one-step reinforcement-learning setting. An epsilon-greedy learner samples an action, receives a deterministic positive or negative reward from the task contract, and updates that state's action value. For this finite toy environment, tabular action values are simpler and more reliable than the first linear model.

The reward is verifiable relative to the **published synthetic contract**. This is a small RL-with-verifiable-rewards demonstration, not a GRPO run, an LLM fine-tune, a scientific validation of negotiation ethics, or training on the show. Model weights, natural-language skill text, and character fidelity are unchanged by running it.

Do not use "RL-trained Harvey," "every line analyzed," "100% character fidelity," or "beats other agents" to describe this release.
