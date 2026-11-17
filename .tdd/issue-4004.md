# Plan for #4004 — PRD 019.9: a criterion-unreadable exit 2 is judged once before the run bails

- [x] `build-adjudicate-prompt.sh <n> criterion-unreadable 2 <stderr-file> <command…>` exits 0, `ADJUDICATE.md` listing `criterion-unreadable` with no route ⟦criterion 1⟧
- [ ] `adjudicate.sh record <n> criterion-unreadable <leaf-output>` writes one `adjudicated cause=criterion-unreadable outcome=<o> reason=<r>` event for a `retry`, a `bail` and an unparsable answer ⟦criterion 2⟧
- [ ] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=criterion-unreadable` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `ADJUDICATE.md`, `SKILL.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS, `SKILL.md` at or under 139,698 bytes ⟦criterion 3⟧ ⟦criterion 5⟧ ⟦criterion 6⟧
