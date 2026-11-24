# Plan for #4721 — verify-green misses the later route when two steps share a criterion marker: _later never calls later_owner_by_id

- [ ] wrong-test-route.sh routes `later <step>` when verify-green reports missing, on the earlier of two open steps sharing a `⟦criterion N⟧` marker, the later step's own criterion text ⟦criterion 1⟧
