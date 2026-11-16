# Plan for #4013 — PRD 024.8: verifiers can run at a lower effort

- [x] `VERI_EFFORT_VERIFIER` is an entry of `tunables.TUNABLES` defaulting to empty, whose parse refuses any value but `low`, `medium`, `high`, `xhigh` or `max` ⟦criterion 1⟧
- [x] set, a `verify-*` leaf's argv carries `--effort <value>`; unset or empty, it carries no `--effort` ⟦criterion 2⟧
- [x] set, no develop, revise, adjudicate or grader leaf's argv carries `--effort` from it ⟦criterion 3⟧
- [x] a bad `VERI_EFFORT_VERIFIER` makes preflight exit 2 printing `stopped at 5 VERI_EFFORT_VERIFIER` before any leaf ⟦criterion 4⟧
- [x] with the knob set and `VERIFY_LEAF_ARGS` carrying `--effort`, `verify.sh` exits 2 naming both ⟦criterion 5⟧
- [x] the report's `Models requested:` line names `VERI_EFFORT_VERIFIER` with its value or `unset` ⟦criterion 6⟧
- [x] with the knob set, a `VERIFY_LEAF_ARGS` carrying `--effort=<v>` makes `verify.sh` exit 2 as `--effort <v>` does ⟦criterion 5⟧
- [x] a verifier leaf's `launch` event carries `effort` when `VERI_EFFORT_VERIFIER` is set, and no `effort` key when it is unset or empty ⟦criterion 6⟧
