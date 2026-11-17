# Plan for #4000 — PRD 019.5: a step-add-refused exit 2 is judged once before the run bails

- [x] `build-adjudicate-prompt.sh <n> step-add-refused 2 <stderr-file> <command…>` exits 0, `ADJUDICATE.md` listing `step-add-refused` with no route ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> step-add-refused <leaf-output>` writes one `adjudicated cause=step-add-refused outcome=<o> reason=<r>` event for a `retry`, a `bail` and an unparsable answer ⟦criterion 2⟧
- [x] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=step-add-refused` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `ADJUDICATE.md`, `SKILL.md`, `REVISE.md`, `DRAFT-PR.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS, `SKILL.md` at or under 139,698 bytes ⟦criterion 5⟧ ⟦criterion 6⟧
