# Plan for #1846 — A verifier refused for modifying the repository leaves no record of what changed, so a probe-and-restore bail can't be diagnosed

- [x] When verify.py refuses a verifier leaf for modifying the repository because a stub verifier changed a tracked file's content, it writes the full git diff between the before and after trees for the changed paths to a file under .tdd/ named after the leaf, written before the tree is reset, holding the content change byte-exactly, and the refusal message names that file ⟦criterion 1⟧
- [x] When a stub verifier changes only a tracked file's mode, the diff file verify.py writes on refusal under .tdd/ named after the leaf shows that mode change byte-exactly ⟦criterion 1⟧
- [ ] prompts/verify-green.md's probe instruction says the .orig copy sits beside the file it copies, never in a shared directory such as /tmp ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] The rendered verify-green prompt's probe instruction says the .orig copy sits beside the file it copies, never in a shared directory such as /tmp, pinned by a case on the rendered prompt ⟦criterion 2⟧
