### run-leaf.sh run with CLAUDE_CODE_SESSION_ID=<fake id> and an unrelated variable whose value contains <fake id> (VERI_FAKE_CARRIER=x-<fake id>-y) starts a stub claude whose recorded environment has neither ⟦criterion 2⟧
- test-only | fold the four repeated `grep -Fx '<var>=<value>' "$work/env" > /dev/null 2>&1 || problems+=(…)` assertions in the #933 cases of run-leaf.test.sh into one helper
