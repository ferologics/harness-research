# AGENTS.md

Research repo comparing Prime Agent's building blocks against objective duals built on Pi. Before proposing anything, read [docs/decisions.md](docs/decisions.md), then [VISION.md](VISION.md) and [TODO.md](TODO.md). A proposal that conflicts with a decision needs explicit agreement to reopen it; record new agreements in `docs/decisions.md` the same day.

## Rules

- **Objective duals only.** Pi arms use only Pi as shipped plus duals built in this repo. Never use third-party Pi packages, and never use the maintainer's personal Pi setup (global settings, installed packages, skills, `AGENTS.md`) as an arm or as a design reference. Experimental Pi runs use a fresh agent directory.
- **Duals mirror Prime Agent.** Same mechanism, same trigger, model-facing text ported from Prime Agent's prompt layers, Prime's defaults, nothing extra. Each dual documents its Prime source (file and commit) and every deliberate difference.
- **Pre-registration is binding.** After a plan records its freeze commit, changes to arms, tasks, metrics, or analysis go under its Deviations section with a reason.
- **Screening and dev runs stay out of the analysis.** Never tune duals or prompts on main-run tasks.
- **Raw results are append-only.** Never edit or delete run outputs; rerun and record instead.
- **Label evidence honestly.** In [docs/literature.md](docs/literature.md), the Read column reflects what was actually read. Unknowns stay `?`. Inferences are marked as such.
- **Measured runs use stock model weights.** No uncensored or otherwise modified variants.
- **No secrets in the repo.** Provider keys come from the environment.

## Conventions

- Python: 4-space indentation; run scripts with `uv run --with <deps>`.
- External repos are read from `~/.cache/checkouts/<host>/<org>/<repo>`; record the commit when citing code.
