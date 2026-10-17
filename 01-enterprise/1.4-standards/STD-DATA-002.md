---
id: STD-DATA-002
type: standard
name: Data Classification and Handling
level: enterprise
owner: enterprise-architecture
status: ratified
enforcement: policy
---

# Data Classification and Handling

Every system declares a data classification (public, internal,
confidential, restricted) in its artifact header. Handling rules tighten
with classification: restricted data is encrypted in transit and at rest,
access is logged, and retention follows the records schedule.

Two rules of this standard are mechanical and are compiled to
`policies/std-data-002.rego`:

1. A target-state system binds at least one standard.
2. A system that binds this standard declares a data classification.

CI evaluates the compiled form against every artifact header on every
proposed change. The prose above governs interpretation; the compiled
form governs the build.
