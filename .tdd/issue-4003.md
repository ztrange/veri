# Plan for #4003 — PRD 019.8: a reconcile exit 2 is judged once before the run bails reconcile-failed

- [x] `build-adjudicate-prompt.sh <n> reconcile-failed 2 <stderr-file> <command…>` exits 0, `ADJUDICATE.md` listing `reconcile-failed` with no route ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> reconcile-failed <leaf-output>` writes one `adjudicated cause=reconcile-failed outcome=<o> reason=<r>` event for a `retry`, a `bail` and an unparsable answer ⟦criterion 2⟧
- [x] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=reconcile-failed` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `ADJUDICATE.md`, `RECONCILE.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS ⟦criterion 3⟧ ⟦criterion 5⟧
