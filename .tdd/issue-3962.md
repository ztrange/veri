# Plan for #3962 — PRD 022.20: CI's actions are pinned by commit

- [x] a workflow `uses:` line that does not name a 40-hex commit sha is refused, the refusal naming the file and line ⟦criterion 2⟧
- [x] a sha-pinned `uses:` line without a trailing comment naming its tag is refused, naming the file and line ⟦criterion 1⟧
- [x] every `uses:` line under `.github/workflows/` names a 40-hex commit sha followed by a comment naming its tag ⟦criterion 1⟧
