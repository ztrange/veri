# Plan for #4001 — PRD 019.6: a replaces-report-failed exit 2 is judged once before the run bails

- [x] `build-adjudicate-prompt.sh <n> replaces-report-failed 2 .tdd/develop-replaces-report.err <command…>` exits 0, `ADJUDICATE.md` listing `replaces-report-failed` with no route ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> replaces-report-failed <leaf-output>` writes one `adjudicated cause=replaces-report-failed outcome=<o> reason=<r>` event for a `retry`, a `bail` and an unparsable answer ⟦criterion 2⟧
- [ ] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=replaces-report-failed` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `ADJUDICATE.md`, `SKILL.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS, `SKILL.md` at or under 139,698 bytes ⟦criterion 5⟧ ⟦criterion 6⟧
