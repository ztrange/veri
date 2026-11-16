# Plan for #3961 — PRD 022.10: CI's token can only read

- [x] ci.yml declares a top-level `permissions:` block whose only entry is `contents: read` ⟦criterion 1⟧
- [x] a workflow file with no top-level `permissions:` block is refused, the refusal naming the file ⟦criterion 2⟧
- [x] a workflow file granting any `write` permission is refused, the refusal naming the file ⟦criterion 2⟧
- [x] every file under `.github/workflows/` is swept by those refusals ⟦criterion 2⟧
