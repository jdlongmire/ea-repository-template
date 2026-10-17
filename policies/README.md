# Policies

The compiled, machine-checkable form of standards that declare
`enforcement: policy` in their header. The human-readable standard in
its level's standards folder is the source of truth; the `.rego` file
here is its compiled form, and the verifier fails any change that lets
the two fall out of pairing. CI evaluates these policies with Open
Policy Agent against the artifact headers emitted by the verifier.
Interpretation disputes are settled by the standard's prose, at
ratification, never by the compiled form alone.
