### capture-spec.sh writes the blind spec with a Bug section carrying what happened, expected, steps to reproduce and environment when the issue carries the bug label ⟦criterion 1⟧
- extract the duplicated `gh issue view <n> --json body -q .body` call in capture-spec.sh:20 and tick-issue-criterion.sh:27 into a sourced lib helper
- pass the body into `part()` as a parameter rather than closing over the script-level `$body`
