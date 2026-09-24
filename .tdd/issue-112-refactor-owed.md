### capture-spec.sh writes the blind spec with a Bug section carrying what happened, expected, steps to reproduce and environment when the issue carries the bug label ⟦criterion 1⟧
- extract the duplicated `gh issue view <n> --json body -q .body` call in capture-spec.sh:20 and tick-issue-criterion.sh:27 into a sourced lib helper
- pass the body into `part()` as a parameter rather than closing over the script-level `$body`
### capture-spec.sh writes a spec with no Bug section when the issue does not carry the bug label ⟦criterion 1⟧
- capture-spec.sh asks `gh issue view` twice (once for `body,labels`, once for `body`); folding it into one call halves the remote question, but the script's own comment rejects it — one filter answering both questions must encode the label alongside the body, and any marker the body could also contain is a marker the body can forge
