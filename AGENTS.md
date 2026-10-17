# Agent Contract for This Repository

Agents (AI assistants) may work in this repository under governed
execution. The terms:

- Propose, never merge. All agent work arrives as a pull request.
  Ratification belongs to the humans named in CODEOWNERS, enforced by
  branch protection.
- Run `python3 00-meta-model/verify.py` before proposing. A proposal
  that fails verification is withdrawn, not argued with.
- Stay inside the structure. New artifact types, new top-level areas,
  and schema changes are decisions for 00-meta-model/decisions/ and
  require human authorship.
- Leave records. Every proposal states its purpose, the artifacts it
  touches, and its validation output in the pull request body.
- Reconciliation is in scope. An agent may file observed-state
  snapshots and drift entries in 05-evidence/ as pull requests, under
  the same ratification rule as any other change.
- Views are generated. Never hand-edit files in 05-evidence/views/.
  To change a drawing, change 00-meta-model/catalog.toml or
  00-meta-model/views.toml and run 00-meta-model/render_views.py.

An agent that cannot meet a term says so in the pull request rather
than working around it.
