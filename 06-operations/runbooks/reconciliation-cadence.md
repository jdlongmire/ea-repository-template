# Runbook: Reconciliation Cadence

Weekly, an automated job (or an agent under AGENTS.md) snapshots the
observed state of modeled interfaces and systems into
`05-evidence/snapshots/` and diffs it against the merged model.
Differences are entered in `05-evidence/drift-register.md` with an
owner. A drift item closes only when a later snapshot confirms the
modeled and observed states agree.
