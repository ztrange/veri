# Plan for #3998 — PRD 019.3: a pr-ready.sh exit 2 is judged once, and RETRY readies the PR again

- [x] `build-adjudicate-prompt.sh <n> pr-ready-failed 2 .tdd/pr-ready.err <command…>` exits 0, `ADJUDICATE.md` listing `pr-ready-failed` with no route ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> pr-ready-failed <leaf-output>` writes one `adjudicated cause=pr-ready-failed outcome=<o> reason=<r>` event for each of a `retry`, a `bail` and an unparsable answer ⟦criterion 2⟧
- [ ] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=pr-ready-failed` event precedes the issue's last `conductor-start` ⟦criterion 4⟧
- [ ] `JOURNAL.md`'s `adjudicated` row names `pr-ready-failed` among its causes ⟦criterion 6⟧
- [ ] `ADJUDICATE.md`, `DRAFT-PR.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS ⟦criterion 5⟧
