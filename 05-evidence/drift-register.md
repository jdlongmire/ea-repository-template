# Drift Register

Drift is a recorded difference between the authorized target state
(the record) and the state the evidence supports, with an owner, a
classification, and a path back to agreement. Each item is a typed
artifact in `drift/` citing the evidence it rests on; this register
is the index.

| ID | Artifact | Classification | Modeled | Observed | Owner | Status |
|----|----------|----------------|---------|----------|-------|--------|
| DRIFT-001 | INT-007 | defect | Provider contract v2 | Provider endpoint still serving v1 in production | enterprise-architecture | open |

DRIFT-001 closes when the phase 3 cutover in RM-002 lands and a fresh
observed-state snapshot confirms v2 in production.
