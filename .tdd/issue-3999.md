# Plan for #3999 — PRD 019.4: a report-missing exit 2 is judged once before the run bails

- [x] `build-adjudicate-prompt.sh <n> report-missing 2 <stderr-file> <command…>` exits 0, `ADJUDICATE.md` listing `report-missing` with no route ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> report-missing <leaf-output>` writes one `adjudicated cause=report-missing outcome=<o> reason=<r>` event for a `retry`, a `bail` and an unparsable answer, printing `retry` and exiting 0 for the first ⟦criterion 2⟧
- [ ] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=report-missing` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `ADJUDICATE.md`, `SKILL.md`, `DIFF-CHECKED.md`, `PHASED.md`, `REFACTOR-KIND.md`, `STRUCTURAL.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS, `SKILL.md` at or under 139,698 bytes ⟦criterion 5⟧ ⟦criterion 6⟧
