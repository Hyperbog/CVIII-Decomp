## Purpose and scope

Describe the subsystem, target game/platform (or state **shared**), and intended change.

**Universal policy:** [Mod-Forward Development Methodology](../MOD_FORWARD_METHODOLOGY.md). For platform-specific details, link the project's modding profile and evidence rules.

## Mod-forward review (mark N/A with a reason when not applicable)

- [ ] **Vanilla baseline:** Original gameplay/data remain the default, or an intentional difference is explicitly described.
- [ ] **Replaceability:** Tunable values and content are data-driven or have a documented extension seam, not a new arbitrary hardcoded dependency.
- [ ] **Stable identity:** Public resources, settings, actions and events use stable namespaced IDs rather than raw source offsets or array indices.
- [ ] **Additive use:** The interface can add new entries/entities/pages without editing unrelated logic, or the limitation is documented.
- [ ] **Compatibility:** Schema/API/save/config version changes, migrations, dependency order and conflicts have a stated behavior.
- [ ] **Validation/security:** Invalid and hostile mod content is rejected safely; unsupported executable code is not implicitly trusted.
- [ ] **Editor readiness:** Any new editable data uses the runtime's canonical format (or has a documented path to it).
- [ ] **Provenance:** Source originals remain private; ROM/disk/asset identity and original-behavior claims are evidence-backed.
- [ ] **Tests:** Vanilla/no-mod, replacement/additive and malformed-content cases are covered where applicable; unrun tests are explicitly listed.
- [ ] **Status honesty:** Distinguish implemented and tested functionality from placeholders, plans, private tooling and unverified integration.

## Evidence and test results

**ROM-/disk-free tests run:**

**Owner-local original-media tests run (if any):**

**Native/gameplay/editor integration tested (if any):**

**Not yet verified / known limitations:**

## Mods and compatibility impact

**New/changed resource IDs or configuration keys:**

**Existing packs/saves affected and migration plan:**

**Modder workflow example or N/A explanation:**

## Historical certification

If this PR is a decompilation/recompilation change, list separately any newly
certified semantic bytes, original replay/parity evidence and unresolved gaps.
**Do not increase metrics for architecture documents or synthetic fixtures alone.**
