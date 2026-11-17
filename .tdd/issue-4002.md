# Plan for #4002 — PRD 019.7: an unreplaced-cases exit 2 is judged once and can route to the correction leaf

- [x] `build-adjudicate-prompt.sh <n> unreplaced-cases 2 <stderr-file> <command…>` exits 0 and its prompt carries the line `Routes: replaces-report`, `ADJUDICATE.md` listing `unreplaced-cases` with its route `replaces-report` ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> unreplaced-cases <leaf-output>` writes one `adjudicated cause=unreplaced-cases outcome=<o> reason=<r>` event for a `retry`, a `bail`, a `route replaces-report` (printing `route replaces-report`, exit 1) and an unparsable answer ⟦criterion 2⟧
- [ ] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=unreplaced-cases` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `ADJUDICATE.md`, `SKILL.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS, `SKILL.md` at or under 139,698 bytes ⟦criterion 5⟧ ⟦criterion 6⟧
