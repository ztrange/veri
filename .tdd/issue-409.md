# Plan for #409 — A step that hit trouble loses its evidence: leaf logs are keyed by leaf name and overwritten by the next step

- [x] preserve-attempt.sh commits the worktree as it stands to a ref under refs/veri/attempts/ named by issue, step, phase and attempt, and git show reads that commit's tree back ⟦criterion 1⟧
- [x] preserving leaves the work branch untouched: the branch's HEAD, index and git log output are the same before and after, so a rebase-merge of the branch carries none of the preserved commit ⟦criterion 2⟧
- [x] preserve-attempt.sh also copies the leaf's progress log and its final-output file to preserved names carrying the step, phase, attempt and the mark that triggered the preservation ⟦criterion 3⟧
- [x] a REJECT or a malformed verdict makes verify.sh preserve that attempt, and the preserved names pair with the verdict event ⟦criterion 1⟧
- [x] a malformed verdict, the no-verdict half of the same criterion, preserves the verifier attempt under its own ref and copies ⟦added⟧ ⟦criterion 1⟧
- [x] a killed-stuck leaf makes supervise.sh preserve that attempt, both on a retry and on the final killed-stuck exit ⟦criterion 1⟧
- [x] a PASS verdict and a leaf that exits success or clean failure write no ref and no preserved copy ⟦criterion 4⟧
- [x] the conductor preserves the attempt on a bail and on a prediction-diverged mark, so those two conductor-side marks are covered like the leaf-side ones ⟦criterion 1⟧
- [x] preservation changes no leaf prompt and puts the developer's rationale nowhere a verifier leaf reads: the preserved commit is unreachable from HEAD and its message carries no rationale ⟦criterion 5⟧
