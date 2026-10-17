#!/usr/bin/env python3
"""Verify the architecture repository: layout, artifact headers, references.

Usage:
    python3 00-meta-model/verify.py [--emit-json artifacts.json]

Checks, in order:
  1. Layout: required numbered areas exist; no unexpected top-level entries;
     every folder under 02-systems/ and 03-solutions/ carries its four
     focus-area subfolders.
  2. Headers: every artifact (Markdown outside README.md, under the numbered
     areas) opens with front matter satisfying 00-meta-model/schemas.json.
  3. References: system interface/standard ids and solution system ids
     resolve to artifacts present in the repository.
  4. Policy pairing: a standard with enforcement: policy has a compiled
     policy at policies/<id-lowercase>.rego, and every policy file pairs
     back to such a standard.
  5. Catalog: 00-meta-model/catalog.toml parses; every element is a
     typed artifact in this repository (same id, type, name, level);
     every relation endpoint exists and its verb is in the vocabulary
     fixed in schemas.json.
  6. Views: 00-meta-model/views.toml parses; every registered view
     names a valid level and focus area, shows only catalogued
     elements, and carries consistent completeness flags; the
     generated outputs in 05-evidence/views/ are exactly what
     render_views.py produces from the catalog (no stale drawings, no
     unregistered ones).
  7. Evidence: artifacts under 05-evidence/snapshots/ and
     05-evidence/drift/ carry the evidence model: a state kind
     (declared, observed, inferred), provenance (source, method,
     observed_at, confidence), and a subject that resolves. Drift
     items classify the mismatch (defect, model-error, sensor-error,
     undetermined) and cite evidence artifacts that resolve.

Front matter is a flat subset of YAML: `key: value` lines and inline lists
`key: [A, B]`. That subset is deliberate: it is all a typed header needs,
and it parses with the standard library only. No third-party packages.

Exit code 0 means every check passed. Failures print one per line.
"""
import importlib.util
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = json.loads((ROOT / "00-meta-model" / "schemas.json").read_text())

REQUIRED_DIRS = [
    "00-meta-model", "01-enterprise", "02-systems", "03-solutions",
    "04-work-packages", "05-evidence", "06-operations", "policies",
    "01-enterprise/1.1-strategy", "01-enterprise/1.2-architecture",
    "01-enterprise/1.3-roadmaps", "01-enterprise/1.4-standards",
]
TOP_LEVEL_ALLOWLIST = set(REQUIRED_DIRS[:8]) | {
    ".github", "README.md", "AGENTS.md", "CODEOWNERS", "LICENSE", ".gitignore",
}
LEVEL_SUBFOLDERS = {
    "02-systems": ["2.1-strategy", "2.2-architecture", "2.3-roadmaps", "2.4-standards"],
    "03-solutions": ["3.1-strategy", "3.2-architecture", "3.3-roadmaps", "3.4-standards"],
}
ARTIFACT_AREAS = ["01-enterprise", "02-systems", "03-solutions", "04-work-packages"]
EVIDENCE_AREAS = ["05-evidence/snapshots", "05-evidence/drift"]

errors = []


def parse_front_matter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fields[key] = [v.strip() for v in inner.split(",")] if inner else []
        else:
            fields[key] = value
    return fields


def check_layout():
    for d in REQUIRED_DIRS:
        if not (ROOT / d).is_dir():
            errors.append(f"layout: missing required directory {d}")
    for entry in ROOT.iterdir():
        if entry.name.startswith(".git") and entry.name != ".github":
            continue
        if entry.name not in TOP_LEVEL_ALLOWLIST:
            errors.append(f"layout: unexpected top-level entry {entry.name}")
    for area, subs in LEVEL_SUBFOLDERS.items():
        base = ROOT / area
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir():
                for sub in subs:
                    if not (child / sub).is_dir():
                        errors.append(f"layout: {child.relative_to(ROOT)} missing {sub}")


def collect_artifacts():
    artifacts = {}
    for area in ARTIFACT_AREAS + EVIDENCE_AREAS:
        base = ROOT / area
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            if md.name == "README.md":
                continue
            fields = parse_front_matter(md.read_text())
            rel = md.relative_to(ROOT)
            if fields is None:
                errors.append(f"header: {rel} has no front matter")
                continue
            artifacts.setdefault(fields.get("id", f"<no-id {rel}>"), (rel, fields))
    return artifacts


def check_headers(artifacts):
    pattern = re.compile(SCHEMAS["id_pattern"])
    seen = {}
    for aid, (rel, f) in artifacts.items():
        if not pattern.match(aid):
            errors.append(f"header: {rel} id '{aid}' does not match the id pattern")
        if aid in seen:
            errors.append(f"header: duplicate id {aid} in {rel} and {seen[aid]}")
        seen[aid] = rel
        for req in SCHEMAS["common_required"]:
            if req not in f:
                errors.append(f"header: {rel} missing required field '{req}'")
        t = f.get("type")
        if t not in SCHEMAS["types"]:
            errors.append(f"header: {rel} unknown type '{t}'")
            continue
        spec = SCHEMAS["types"][t]
        for req in spec.get("extra_required", []):
            if req not in f:
                errors.append(f"header: {rel} type {t} missing field '{req}'")
        if "enforcement_values" in spec and f.get("enforcement") not in spec["enforcement_values"]:
            errors.append(f"header: {rel} enforcement must be one of {spec['enforcement_values']}")
        for field, values in spec.get("field_values", {}).items():
            if f.get(field) not in values:
                errors.append(f"header: {rel} {field} must be one of {values}")
        if f.get("level") not in SCHEMAS["levels"]:
            errors.append(f"header: {rel} level '{f.get('level')}' not in {SCHEMAS['levels']}")
        if f.get("status") not in SCHEMAS["statuses"]:
            errors.append(f"header: {rel} status '{f.get('status')}' not in {SCHEMAS['statuses']}")
    return artifacts


def check_references(artifacts):
    ids = set(artifacts)
    for aid, (rel, f) in artifacts.items():
        if f.get("type") == "system":
            for ref in f.get("interfaces", []) + f.get("standards", []):
                if ref not in ids:
                    errors.append(f"reference: {rel} references unknown id {ref}")
        if f.get("type") == "solution" and f.get("system") not in ids:
            errors.append(f"reference: {rel} references unknown system {f.get('system')}")
        if f.get("type") == "evidence" and f.get("subject") not in ids:
            errors.append(f"reference: {rel} evidence subject {f.get('subject')} does not resolve to an artifact")
        if f.get("type") == "drift":
            if f.get("subject") not in ids:
                errors.append(f"reference: {rel} drift subject {f.get('subject')} does not resolve to an artifact")
            for ref in f.get("evidence", []):
                if ref not in ids:
                    errors.append(f"reference: {rel} cites unknown evidence {ref}")
                elif artifacts[ref][1].get("type") != "evidence":
                    errors.append(f"reference: {rel} cites {ref}, which is not an evidence artifact")


def check_policy_pairing(artifacts):
    policy_files = {p.stem for p in (ROOT / "policies").glob("*.rego")}
    declared = set()
    for aid, (rel, f) in artifacts.items():
        if f.get("type") == "standard" and f.get("enforcement") == "policy":
            declared.add(aid.lower())
            if aid.lower() not in policy_files:
                errors.append(f"policy: standard {aid} declares enforcement: policy but policies/{aid.lower()}.rego is missing")
    for stem in policy_files:
        if stem not in declared:
            errors.append(f"policy: policies/{stem}.rego has no matching policy-enforced standard")


def check_catalog(artifacts):
    path = ROOT / "00-meta-model" / "catalog.toml"
    if not path.exists():
        errors.append("catalog: 00-meta-model/catalog.toml is missing")
        return None
    try:
        with open(path, "rb") as fh:
            catalog = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"catalog: catalog.toml does not parse ({exc})")
        return None
    elements = {}
    for el in catalog.get("element", []):
        eid = el.get("id")
        if eid in elements:
            errors.append(f"catalog: duplicate element id {eid}")
        elements[eid] = el
        art = artifacts.get(eid)
        if art is None:
            errors.append(f"catalog: element {eid} has no artifact in the repository")
            continue
        _, f = art
        for field in ("type", "name", "level"):
            if el.get(field) != f.get(field):
                errors.append(f"catalog: element {eid} {field} '{el.get(field)}' does not match its artifact header '{f.get(field)}'")
    verbs = set(SCHEMAS.get("relation_types", []))
    for rel in catalog.get("relation", []):
        for endpoint in ("source", "target"):
            if rel.get(endpoint) not in elements:
                errors.append(f"catalog: relation references unknown element {rel.get(endpoint)}")
        if rel.get("relation") not in verbs:
            errors.append(f"catalog: relation verb '{rel.get('relation')}' is not in schemas.json relation_types")
    return catalog


def check_views(catalog):
    path = ROOT / "00-meta-model" / "views.toml"
    if not path.exists():
        errors.append("views: 00-meta-model/views.toml is missing")
        return
    try:
        with open(path, "rb") as fh:
            register = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"views: views.toml does not parse ({exc})")
        return
    errors_before = len(errors)
    element_ids = {el["id"] for el in catalog.get("element", [])} if catalog else set()
    relations = {(r["source"], r["relation"], r["target"]) for r in catalog.get("relation", [])} if catalog else set()
    seen = set()
    for view in register.get("view", []):
        vid = view.get("id", "<no-id>")
        if not re.match(r"^VW-[0-9]{3}$", str(vid)):
            errors.append(f"views: view id '{vid}' does not match VW-NNN")
        if vid in seen:
            errors.append(f"views: duplicate view id {vid}")
        seen.add(vid)
        if view.get("level") not in SCHEMAS.get("view_levels", []):
            errors.append(f"views: {vid} level '{view.get('level')}' is not a valid view level")
        if view.get("focus") not in SCHEMAS.get("view_focus_areas", []):
            errors.append(f"views: {vid} focus '{view.get('focus')}' is not a valid focus area")
        for eid in view.get("elements", []):
            if eid not in element_ids:
                errors.append(f"views: {vid} shows element {eid} which is not in the catalog")
        for flag in ("membership_complete", "relation_complete"):
            if not isinstance(view.get(flag), bool):
                errors.append(f"views: {vid} must declare {flag} as true or false")
        declared = view.get("relations")
        if declared is not None:
            if view.get("relation_complete") is not False:
                errors.append(f"views: {vid} declares a relation subset, so relation_complete must be false")
            shown = set(view.get("elements", []))
            for item in declared:
                parts = item.split(" ")
                if len(parts) != 3:
                    errors.append(f"views: {vid} relation entry '{item}' is not 'SOURCE verb TARGET'")
                    continue
                triple = tuple(parts)
                if triple not in relations:
                    errors.append(f"views: {vid} declares relation '{item}' which is not in the catalog")
                elif triple[0] not in shown or triple[2] not in shown:
                    errors.append(f"views: {vid} declares relation '{item}' with an endpoint it does not show")
        elif view.get("relation_complete") is not True:
            errors.append(f"views: {vid} draws every catalogued relation between its elements, so relation_complete must be true (or declare a subset)")
    if len(errors) > errors_before:
        return
    spec = importlib.util.spec_from_file_location("render_views", ROOT / "00-meta-model" / "render_views.py")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    expected = renderer.expected_files()
    out_dir = ROOT / "05-evidence" / "views"
    for rel, content in expected.items():
        target = ROOT / rel
        if not target.exists():
            errors.append(f"views: generated output {rel} is missing; run python3 00-meta-model/render_views.py")
        elif target.read_text() != content:
            errors.append(f"views: generated output {rel} is stale; run python3 00-meta-model/render_views.py")
    if out_dir.is_dir():
        for f in sorted(out_dir.iterdir()):
            if f.is_file() and f.name != "README.md" and f"05-evidence/views/{f.name}" not in expected:
                errors.append(f"views: 05-evidence/views/{f.name} is not a registered view output; views are generated, not added by hand")


def main():
    check_layout()
    artifacts = check_headers(collect_artifacts())
    check_references(artifacts)
    check_policy_pairing(artifacts)
    catalog = check_catalog(artifacts)
    check_views(catalog)
    if "--emit-json" in sys.argv:
        out = sys.argv[sys.argv.index("--emit-json") + 1]
        data = {"artifacts": [f for _, f in sorted(artifacts.values(), key=lambda x: x[1].get("id", ""))]}
        Path(out).write_text(json.dumps(data, indent=2))
        print(f"wrote {out} ({len(data['artifacts'])} artifacts)")
    if errors:
        print(f"FAIL ({len(errors)} problem(s)):")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK: layout, {len(artifacts)} artifact headers, references, policy pairing, catalog, view fidelity, and evidence all pass.")


if __name__ == "__main__":
    main()
