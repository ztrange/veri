# Plan for #439 — The plan is the one artifact nothing verifies, so a narrowed criterion is certified as done

- [x] build-verify-prompt.sh accepts a plan phase and builds its prompt from the issue spec and the ledger named as its third argument ⟦criterion 1⟧
- [x] build-verify-prompt.sh exits 2 with nothing on stdout for a plan invocation that names no ledger or names one it cannot read ⟦criterion 1⟧
- [x] The plan prompt asks whether the steps tagged for a criterion together deliver that criterion as written, and requires a REJECT reason to name the criterion and the part of it no step covers ⟦criterion 2⟧
- [x] The plan prompt directs a PASS when every criterion is delivered by the steps tagged for it ⟦criterion 3⟧
- [x] The plan prompt requires a step judged too big for one Red to Green to Refactor cycle to be named in the reason under either verdict ⟦criterion 4⟧
- [x] The plan prompt states that a step carrying no criterion tag is never by itself a reason to REJECT ⟦criterion 5⟧ ⟂ refactor pending
- [ ] The plan phase prompt carries only the issue spec and the ledger, and the four cycle phase prompts carry no ledger ⟦criterion 7⟧
- [ ] SKILL.md has the conductor run the plan verifier once after the ledger is committed and before the first step, and a REJECT rewrites the plan and re-verifies instead of ending the run ⟦criterion 6⟧
- [ ] SKILL.md treats a plan verification that rendered no verdict as a system failure bail rather than a PASS ⟦criterion 8⟧
- [ ] SKILL.md's script entries for build-verify-prompt.sh, verify.sh and run-verdict.sh name the plan phase beside the four cycle phases
