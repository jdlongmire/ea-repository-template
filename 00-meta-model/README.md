# 00 Meta-Model

The constitution of this repository. It defines what an artifact is,
which types exist, and what every artifact must declare, and it holds
the machinery that keeps the rest of the tree honest.

- `schemas.json`: the artifact types, their required fields, the legal
  levels and statuses, and the id pattern. Machine-readable on purpose:
  this file is data, not documentation about data.
- `catalog.toml`: the model of record. Architecture elements and
  their typed relations. Every element is a typed artifact in this
  repository; the verifier binds the two together (same id, type,
  name, and level), so the catalog and the artifacts are two
  projections of one record, not two records that can drift apart.
  The relation vocabulary is fixed in `schemas.json`.
- `views.toml`: the view register. Every view names its viewpoint and
  concern, its level and focus area (Strategy, Architecture,
  Roadmaps, Standards, or cross-level traceability), the elements it
  shows, and two completeness flags: whether its element list is the
  whole of its scope, and whether it draws every catalogued relation
  between the elements it shows.
- `render_views.py`: generates each registered view into
  `05-evidence/views/` as Mermaid source and a rendered SVG. Views
  are generated, never drawn or edited by hand.

      python3 00-meta-model/render_views.py

- `verify.py`: the verifier. Checks layout, artifact headers against
  `schemas.json`, cross-references between artifacts, pairing between
  policy-enforced standards and their compiled form in `policies/`,
  the catalog against the artifacts, the generated views against
  the catalog (a stale or unregistered drawing fails), and the
  evidence model: state kinds, provenance fields, drift
  classifications, and evidence citations (DEC-003). Run it before
  proposing any change:

      python3 00-meta-model/verify.py

  With `--emit-json artifacts.json` it also writes every artifact
  header as JSON, which is what CI feeds to the policy engine.

- `decisions/`: decisions about the repository itself.

Artifact headers are a flat subset of YAML front matter (scalars and
inline lists). That subset is all a typed header needs and it parses
with the Python standard library alone, so the verifier runs anywhere
Python 3 does, with no packages to install.
