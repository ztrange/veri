# Plan for #2900 — A pin's red proof is a hand mutation, never the real before-state

- [ ] `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` exits 1 when the command passes on the restored before-state ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before` leaves `<test-path>` exactly as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before` leaves every file under `.tdd/` as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before` removes a file added since `<sha>` (tracked or untracked) while the command runs ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before` brings back a file deleted since `<sha>`, with its `<sha>` content, while the command runs ⟦criterion 1⟧
- [ ] after the command, `mutation-probe.sh --before` puts every tracked file it restored back to its working-tree bytes ⟦criterion 1⟧
- [ ] after the command, `mutation-probe.sh --before` removes again a file it brought back from `<sha>` ⟦criterion 1⟧
- [ ] after the command, `mutation-probe.sh --before` puts back every untracked file it removed, byte for byte ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before <sha>` exits 2 without running the command when `<sha>` does not resolve to a commit ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before <sha>` exits 2 without running the command when `<sha>` is not 7-40 lowercase hex (`^[0-9a-f]{7,40}$`) ⟦criterion 1⟧
- [ ] `mutation-probe.sh --before <sha>` exits 2 without running the command when no file other than `<test-path>` and `.tdd/` differs between `<sha>` and the working tree ⟦criterion 1⟧
- [ ] when the before-state probe exits 0, it appends a record to `VERI_MUTATION_RECORD` carrying `before <sha>`, `keep <test-path>` and `command` ⟦criterion 1⟧
- [ ] a process case (`@pytest.mark.process`, in `test_mutation_probe_process.py`) on a scratch git repo in the shape of the issue's Steps to reproduce (`view.py`, `quote.py` changed on the branch, a test stubbing `{"deps": 10}`) shows `mutation-probe.sh --before <base> --keep <test>` exits 1 and the working tree is unchanged afterwards ⟦criterion 1⟧
- [ ] `skills/tdd/scripts/prompts/verify-pin.md`: check 2 first runs the before-state probe `{{MUTATION_PROBE}} --before {{BRANCH_BASE}} --keep '{{TEST_PATH}}' -- <command>`, REJECTs naming "the real before-state stays green" on its exit 1, and allows a hand mutation only when it exits 2 because no file differs (VP5, VP8) ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] `build-verify-prompt.sh pin` fills a `{{BRANCH_BASE}}` slot in the pin template with the run's branch point, `git merge-base HEAD origin/<default>`, carrying only that commit name ⟦criterion 2⟧
- [ ] `build-verify-prompt.sh pin` refuses with exit 2 when the branch base it would fill into `{{BRANCH_BASE}}` is not 7-40 lowercase hex ⟦criterion 2⟧
- [ ] Guard go-red: with the before-state probe's exit 1 inverted, or with the slot left out of the pin prompt, the cases above go red; watched failing, then restored ⟦human-owed⟧ ⟦criterion 3⟧
