# Plan for #4721 — verify-green misses the later route when two steps share a criterion marker: _later never calls later_owner_by_id

- [x] wrong-test-route.sh routes `later <step>` when verify-green reports missing, on the earlier of two open steps sharing a `⟦criterion N⟧` marker, the later step's own criterion text ⟦criterion 1⟧
- [x] skills/tdd/SKILL.md (Green section, `later <step>` bullet) and REQUIREMENTS.md rows CY130 and SC76 state the shared-marker exception: a later open step carrying the current step's `⟦criterion N⟧` owns a MISSING_TEST behaviour that contains its own ledger text, markers removed ⟦skill-edit⟧
