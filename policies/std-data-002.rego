# Compiled form of STD-DATA-002 (Data Classification and Handling).
# Source of truth: 01-enterprise/1.4-standards/STD-DATA-002.md
# Evaluated in CI against the artifact headers emitted by
# 00-meta-model/verify.py --emit-json. A non-empty deny set fails the build.
package architecture

# A target-state system must bind at least one standard.
deny contains msg if {
	some art in input.artifacts
	art.type == "system"
	art.status == "target"
	count(object.get(art, "standards", [])) == 0
	msg := sprintf("system %v is target state but binds no standards", [art.id])
}

# A system that binds STD-DATA-002 must declare a data classification.
deny contains msg if {
	some art in input.artifacts
	art.type == "system"
	some sid in art.standards
	sid == "STD-DATA-002"
	not art.data_classification
	msg := sprintf("system %v binds STD-DATA-002 but declares no data_classification", [art.id])
}
