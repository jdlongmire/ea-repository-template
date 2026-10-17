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

Front matter is a flat subset of YAML: `key: value` lines and inline lists
`key: [A, B]`. That subset is deliberate: it is all a typed header needs,
and it parses with the standard library only. No third-party packages.

Exit code 0 means every check passed. Failures print one per line.
"""
import json
import re
import sys
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
    for area in ARTIFACT_AREAS:
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


def main():
    check_layout()
    artifacts = check_headers(collect_artifacts())
    check_references(artifacts)
    check_policy_pairing(artifacts)
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
    print(f"OK: layout, {len(artifacts)} artifact headers, references, policy pairing all pass.")


if __name__ == "__main__":
    main()
