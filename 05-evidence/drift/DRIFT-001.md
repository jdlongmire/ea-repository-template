---
id: DRIFT-001
type: drift
name: Payment Disbursement API Version Lag
level: systems
owner: enterprise-architecture
status: current
subject: INT-007
classification: defect
evidence: [OBS-001, OBS-002]
---

# DRIFT-001: Payment Disbursement API Version Lag

Modeled (authorized target): INT-007 at provider contract v2, per
SYS-014's target state.

Declared (OBS-002): the provider registry declares v2 active.
Observed (OBS-001): the production endpoint still serves v1.

Classification: **defect**. The estate does not match the authorized
target. The classification rests on weighing the evidence by method
and confidence: direct inspection of the deployed endpoint (high)
against a vendor self-report (medium). It is not a model error; the
target stands. It is not a sensor error; the observation method is
the strongest available. Had the only evidence been the registry
declaration, this item would sit at **undetermined**, not defect.

Closes when the phase 3 cutover in RM-002 lands and a fresh observed
snapshot confirms v2 in production.
