# Plan for #933 — a leaf in a Claude Code cloud session still runs under the launching session's id: a variable outside SESSION_VARS carries it

- [ ] The carrier variable is named by bisection in a Claude Code cloud session and added to SESSION_VARS in lib/session-env.sh, with a comment recording where it was observed and whether the child still authenticates without it ⟦human-owed⟧ ⟦criterion 1⟧
- [x] run-leaf.sh run with CLAUDE_CODE_SESSION_ID unset, or set to the empty string, removes nothing beyond SESSION_VARS: a stub claude records VERI_TEST_CMD and an unrelated variable with the caller's values ⟦criterion 4⟧
- [x] run-leaf.sh passes through every variable whose value does not contain the session id: with CLAUDE_CODE_SESSION_ID set, a stub claude records VERI_TEST_CMD with the caller's value and GIT_CONFIG_GLOBAL as run-leaf.sh set it ⟦criterion 5⟧
- [x] run-leaf.sh run with CLAUDE_CODE_SESSION_ID=<fake id> and an unrelated variable whose value contains <fake id> (VERI_FAKE_CARRIER=x-<fake id>-y) starts a stub claude whose recorded environment has neither ⟦criterion 2⟧
- [x] run-conductor.sh run with CLAUDE_CODE_SESSION_ID=<fake id> and VERI_FAKE_CARRIER=x-<fake id>-y starts a stub claude whose recorded environment has neither ⟦criterion 3⟧ ⟂ refactor pending
- [ ] No case already in run-leaf.test.sh or run-conductor.test.sh has its assertions changed by this branch ⟦diff-checked⟧ ⟦criterion 5⟧
