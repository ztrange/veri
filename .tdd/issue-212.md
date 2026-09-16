# Plan for #212 — A verifier that rendered its verdict was reported killed-stuck, and the verdict was thrown away

- [x] A leaf the watchdog kills whose progress log holds a terminal result event is reported with the leaf's own outcome, exit 0, not exit 2 killed-stuck
- [x] A killed leaf whose terminal result event is an error is reported exit 1, not exit 0
- [x] A leaf recovered from its terminal result event is launched exactly once, with no stuck-retry
- [x] A recovered leaf's captured stdout ends with the clean result text, so parse-verdict.sh reads its verdict ⟂ refactor pending
- [ ] A leaf killed with no terminal result event in its log is still killed and still reported exit 2 with its kill cause on stderr
- [ ] supervise.sh's header records that a leaf's stream can finish before its rc file is written, so a kill is not proof that no answer was obtained
