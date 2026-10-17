# 00 Meta-Model

The constitution of this repository. It defines what an artifact is,
which types exist, and what every artifact must declare, and it holds
the machinery that keeps the rest of the tree honest.

- `schemas.json`: the artifact types, their required fields, the legal
  levels and statuses, and the id pattern. Machine-readable on purpose:
  this file is data, not documentation about data.
- `verify.py`: the verifier. Checks layout, artifact headers against
  `schemas.json`, cross-references between artifacts, and pairing
  between policy-enforced standards and their compiled form in
  `policies/`. Run it before proposing any change:

      python3 00-meta-model/verify.py

  With `--emit-json artifacts.json` it also writes every artifact
  header as JSON, which is what CI feeds to the policy engine.

- `decisions/`: decisions about the repository itself.

Artifact headers are a flat subset of YAML front matter (scalars and
inline lists). That subset is all a typed header needs and it parses
with the Python standard library alone, so the verifier runs anywhere
Python 3 does, with no packages to install.
