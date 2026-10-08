# Plan for #1035 — refactor-triage, develop-refactor.md and refactor-overflow still describe candidates as structural-or-cosmetic after #992's out-of-scope class

- [x] refactor-triage's exit-2 diagnostic for a candidate line whose class is none of the four names all four accepted classes (structural, cosmetic, test-only, out-of-scope) and still ends with the offending line, with exit code 2 and empty stdout unchanged ⟦criterion 1⟧
- [x] refactor-triage.sh's header comment lists the four candidate classes and says only structural reaches stdout ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] develop-refactor.md's sub-step 1 tells the leaf to report a structural transform it does not apply on a CANDIDATES: structural line and one outside the issue's bounds on a CANDIDATES: out-of-scope line, pinned by a text case in the prompt's suite that goes red when the out-of-scope instruction is removed ⟦criterion 3⟧
- [ ] refactor-overflow.sh with both unreached structural candidates and out-of-scope transforms files a body with two headed lists — the structural candidates the closing pass could not reach, and the out-of-scope transforms the pass did not attempt — under the unchanged title ⟦criterion 4⟧
- [ ] refactor-overflow.sh with only out-of-scope transforms files a body carrying only the out-of-scope heading ⟦criterion 5⟧
- [ ] refactor-overflow.sh with only unreached structural candidates files a body carrying only the structural heading ⟦criterion 5⟧
- [ ] refactor-triage refuses an empty cosmetic candidate line with exit 2 and stderr naming the line ⟦criterion 6⟧
- [ ] refactor-triage refuses an empty test-only candidate line with exit 2 and stderr naming the line ⟦criterion 6⟧
- [ ] refactor-triage refuses an empty out-of-scope candidate line with exit 2 and stderr naming the line ⟦criterion 6⟧
- [ ] refactor-owed.sh append records nothing for an empty cosmetic, test-only or out-of-scope candidate line, one case per class ⟦criterion 6⟧
