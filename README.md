# The Architecture Repository (Template)

One Git repository that holds an enterprise architecture practice:
Strategy, Architecture, Roadmaps, and Standards at the enterprise,
systems, and solutions levels, as typed, versioned artifacts that
humans ratify and agents can operate.

This is the reference structure from the Thinx-Tank series
[Agentic Enterprise Architecture](https://blog.thinxai.net/posts/agentic-enterprise-architecture/),
[The Architecture Repository](https://blog.thinxai.net/posts/the-architecture-repository/),
and [Own the Core. Synthesize the Rest.](https://blog.thinxai.net/posts/own-the-core-synthesize-the-rest/),
made literal. Use it as a GitHub template to start an architecture
repository of your own.

## Structure

| Path | Holds |
|------|-------|
| `00-meta-model/` | Artifact schemas, the element-and-relation catalog, the view register, the renderer, the verifier, decisions about the repository itself |
| `01-enterprise/` | Enterprise level: `1.1-strategy`, `1.2-architecture`, `1.3-roadmaps`, `1.4-standards` |
| `02-systems/` | One folder per system, each with the same four focus areas (`2.1` to `2.4`) |
| `03-solutions/` | One folder per solution, each with the same four focus areas (`3.1` to `3.4`) |
| `04-work-packages/` | Bounded units of architecture work, worked as pull requests |
| `05-evidence/` | Evidence artifacts with provenance (declared, observed, inferred), the drift register, generated view evidence |
| `06-operations/` | Runbooks: reconciliation cadence, admission, agent access |
| `policies/` | Standards compiled to policy-as-code (Open Policy Agent) |
| `CODEOWNERS` | The ratification map: who approves changes to what |
| `AGENTS.md` | The governed-execution contract for agents working the repository |

## How change works

Propose (pull request) -> validate (CI: layout, headers, references,
compiled policies, catalog, generated views) -> ratify (CODEOWNERS
review, branch protection) -> merge (the change becomes the record)
-> reconcile (observed state is diffed against the model; drift is
filed in `05-evidence/` as a defect and opens the next proposal).

Diagrams are not drawn here. The catalog (00-meta-model/catalog.toml)
is the model of record; views are registered in
00-meta-model/views.toml and generated into `05-evidence/views/` by
00-meta-model/render_views.py. A view shows exactly its registered
elements and the catalogued relations between them, and CI fails on a
stale or unregistered drawing.

## Quickstart

1. Click "Use this template" and create your repository.
2. Replace the handle in `CODEOWNERS` with your architecture board's
   reviewers, and enable branch protection on `main` requiring
   CODEOWNERS review and the `verify` check.
3. Run `python3 00-meta-model/verify.py`. It should pass on the
   template as shipped, worked example included.
4. Delete or replace the worked example (claims processing) as your
   own artifacts land, one ratified pull request at a time.

## The worked example

A claims processing platform is threaded through all three levels so
every mechanism fires at least once: an enterprise capability
(CAP-001), a target system (SYS-014) binding two interfaces and two
standards, one standard compiled to a working OPA policy
(STD-DATA-002), an architecture decision (ADR-001), a closed work
package (WP-001), and an open drift item (DRIFT-001) showing the
reconciliation loop with a defect in it, on purpose. The same example
populates the catalog (15 elements, 15 relations) and all six
registered views, including a standards register view (VW-003) and a
requirements realization view (VW-005) generated from the catalog.

## License

MIT. Take the structure, keep the discipline.

Human-Curated, AI-Enabled (HCAE)
