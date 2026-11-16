# Plan for #3970 — PRD 022.11: the conductor's needs-user bail is not silenced by a stranger's comment

- [x] run_conductor.done_posted counts a ### ✅ Done comment posted since the last resume only when github.trusted_comment trusts it: with the only such comment untrusted, the needs-user bail event and comment are made ⟦criterion 1⟧
- [x] a trusted ### ✅ Done comment posted since the last resume still suppresses the needs-user bail and comment ⟦criterion 2⟧
- [x] a trusted ### ✅ Done comment on page 2, after a full page of untrusted comments, still suppresses the bail
- [x] a comments answer that is not JSON is no answer: exit 2 naming the issue, no needs-user bail or comment
