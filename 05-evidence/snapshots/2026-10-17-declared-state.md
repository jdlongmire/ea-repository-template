---
id: OBS-002
type: evidence
name: Declared State from Provider Registry 2026-10-17
level: systems
owner: enterprise-architecture
status: current
state_kind: declared
subject: INT-007
source: payment provider contract registry
method: vendor self-report (registry entry)
observed_at: 2026-10-17
confidence: medium
---

# Declared State, Payment Provider Registry, 2026-10-17

The provider's contract registry declares INT-007 at provider
contract v2, active for the disbursement endpoint.

This declaration conflicts with OBS-001, which observes the
production endpoint still serving v1. The conflict is recorded, not
resolved by preference: DRIFT-001 weighs the two by method and
confidence (direct inspection, high, against vendor self-report,
medium) and classifies the mismatch as a defect in the estate.
