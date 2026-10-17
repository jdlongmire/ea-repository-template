# 05 Evidence

The return path: statements about the real estate, validation
results, and the drift register.

Statements about the estate are evidence artifacts, not facts. Each
one (in `snapshots/`) declares its kind and its provenance:

- **declared**: what a system or vendor says about itself.
- **observed**: what was directly measured or inspected.
- **inferred**: what was derived from other evidence.

The fourth state, the **authorized target**, is not here. It is the
record itself, in the numbered baselines.

Drift items (in `drift/`) record where evidence and the authorized
target disagree, classify the mismatch (defect, model-error,
sensor-error, or undetermined), and cite the evidence they rest on.
The model is specified in 00-meta-model/decisions/DEC-003.md.
