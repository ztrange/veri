# Plan for #966 — the variable that carries the parent session to a leaf's claude in a Claude Code cloud session is named by bisection and stripped

- [x] run-leaf.sh, run with CLAUDE_CODE_SESSION_ID set to a fake id and CLAUDE_CODE_REMOTE_SESSION_ID set to a value that does not contain that fake id, launches a stub claude (via CLAUDE_BIN) whose recorded environment carries no CLAUDE_CODE_REMOTE_SESSION_ID — a case in run-leaf.test.sh ⟦criterion 3⟧
- [x] run-conductor.sh, run with CLAUDE_CODE_SESSION_ID set to a fake id and CLAUDE_CODE_REMOTE_SESSION_ID set to a value that does not contain that fake id, launches a stub claude (via CLAUDE_BIN) whose recorded environment carries no CLAUDE_CODE_REMOTE_SESSION_ID — a case in run-conductor.test.sh ⟦criterion 3⟧
- [x] the branch's diff leaves CLAUDE_CODE_REMOTE_SESSION_ID in SESSION_VARS in skills/tdd/scripts/lib/session-env.sh, and adds to that file's comment block a record that it is the variable carrying the parent session to a child claude, found by #966's bisection in a Claude Code cloud session (Linux, uid 0, claude 2.1.289), that its value does not contain CLAUDE_CODE_SESSION_ID so #948's value scan let it through, and that the child still authenticates without it ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] no assertion of any case run-leaf.test.sh or run-conductor.test.sh held before the branch is changed by the branch's diff ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] fix the full-suite failure: skills/tdd/scripts/tests/py/test_comment_class.py — FAILED test_main_sweeps_the_scripts_lib_and_suites_to_empty_sweepable_reports_no_cited_issue_and_unchanged_class_3_lines: no comment line in scripts/*.sh or scripts/lib/*.sh may cite an issue number, and skills/tdd/scripts/lib/session-env.sh:7 does (#948, #966) ⟦suite-repair⟧ ⟦criterion 3⟧
- [ ] every case run-leaf.test.sh and run-conductor.test.sh held before the branch still passes ⟦full-suite⟧ ⟦criterion 3⟧

## Notes (the bisection evidence the plan rests on; no step pins it)

Gathered by the conductor from the cloud session's own Bash tool, before planning — a leaf cannot gather it, since run-leaf.sh strips the session variables from every leaf's environment. claude --version: 2.1.289 (Claude Code). Names only; no value was printed.

- Step 1 (`env -u` of the nine SESSION_VARS names): the child printed the parent's session_id.
- Step 2 (`env -i HOME PATH HTTPS_PROXY`): the child printed a fresh session_id and answered ok.
- Step 3 (bisection over the 140 names the `env -i` line drops, the nine SESSION_VARS names and _/PWD/OLDPWD/SHLVL excluded; all 140 added back reproduced the parent's id): seven rounds, one variable left — CLAUDE_CODE_REMOTE_SESSION_ID. Added back alone, it brings back the parent's session_id.
- Step 4: its value does NOT contain $CLAUDE_CODE_SESSION_ID. Sourcing #948's lib/session-env.sh and calling strip_session_env leaves it set, and the child still printed the parent's session_id.
- Step 5: the `env -u` line plus `-u CLAUDE_CODE_REMOTE_SESSION_ID` answered ok, is_error false, with a fresh session_id: the child authenticates without it.

So criterion 3 is the branch that applies. Criterion 2 (#948 already strips it) does not: neither its name is in SESSION_VARS nor does its value contain the session id. Criterion 4 (the child cannot authenticate without it) does not: step 5 authenticated.
