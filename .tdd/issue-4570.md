# Plan for #4570 — wait-ci exits 0 on an empty rollup when the PR workflow is quoted-key, JSON, flow-root or over 1 MB, which trigger_lines reads as no pull_request trigger

- [x] wait-ci keeps its wait on a no-checks PR whose only workflow holds a pull_request trigger as a quoted `on` key, a JSON document, a flow-mapping root or a file over 1 MB whose contents come back empty ⟦criterion 1⟧
- [x] triggers_on_pull_request answers True for a local workflow holding a pull_request trigger as a quoted `on` key, a JSON document or a flow-mapping root ⟦criterion 1⟧
