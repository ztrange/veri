# Plan for #624 — extract-result.sh loses a developer leaf's report when the leaf keeps working after it

- [x] given a log whose result record carries `IMPL_PATH:` and `SUITE:` lines, followed by a later result record carrying neither, `extract-result.sh` prints the earlier record's text and exits 0 ⟦criterion 1⟧
- [x] given a log whose result record carries `SPLIT:` lines, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 2⟧
- [x] given a log whose result record carries a `TEST_PATH:` line, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 3⟧
- [x] given a log whose result record carries only a `SUITE:` line, followed by a later result record carrying no report line, `extract-result.sh` prints the earlier record's text ⟦criterion 4⟧
- [x] given two result records that both carry a report line, `extract-result.sh` prints the later one ⟦criterion 5⟧
- [x] given result records none of which carries a report line or a `VERDICT:` line, `extract-result.sh` prints the last record's text ⟦criterion 6⟧
- [x] a result record carrying a `VERDICT:` line, followed by a later record without one, still yields the `VERDICT:` record ⟦criterion 7⟧
- [x] input containing no result record is passed through to stdout unchanged ⟦criterion 8⟧
