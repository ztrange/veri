### capture-spec.sh writes the blind spec with a Bug section carrying what happened, expected, steps to reproduce and environment when the issue carries the bug label ⟦criterion 1⟧
- extract the duplicated `gh issue view <n> --json body -q .body` call in capture-spec.sh:20 and tick-issue-criterion.sh:27 into a sourced lib helper
- pass the body into `part()` as a parameter rather than closing over the script-level `$body`
### capture-spec.sh writes a spec with no Bug section when the issue does not carry the bug label ⟦criterion 1⟧
- capture-spec.sh asks `gh issue view` twice (once for `body,labels`, once for `body`); folding it into one call halves the remote question, but the script's own comment rejects it — one filter answering both questions must encode the label alongside the body, and any marker the body could also contain is a marker the body can forge
### SKILL.md captures the blind spec through capture-spec.sh rather than a bare gh issue view ⟦criterion 1⟧
- cases 1 and 2 each run `section '## Bug'` into a per-case temp file and then test its emptiness — a two-line pattern that could become one `bug_section` helper (low value: it renames more than it removes)
### build-verify-prompt.sh red emits its reproduction paragraph, requiring the observed failure to match what happened, only when the spec has a Bug section, with its four parameters unchanged ⟦criterion 2⟧
- hoist `prompt_has`/`prompt_says`/`prompt_lacks`, duplicated verbatim in build-verify-prompt.test.sh and build-develop-prompt.test.sh, into a shared test helper file
- the four-part bug-spec fixture is written out in both suites' bug cases; one fixture under tests/fixtures/ would carry it once
