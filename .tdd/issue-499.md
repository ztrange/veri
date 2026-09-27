# Plan for #499 — a refactor run kind: Cover then Transform then Verify, with the smell as its Red

- [x] capture-spec.sh appends a `## Refactor` section naming the refactor run kind when the issue carries the `refactor` label, and emits no such section for an issue without it ⟦criterion 1⟧
- [x] build-develop-prompt.sh accepts the `cover` and `transform` phases and prints a prompt for each from its own template, while an unknown phase is still refused with exit 2 and no stdout ⟦criterion 2⟧
- [x] build-verify-prompt.sh accepts a `transform` phase that takes the step's predicate record in the test-path slot and a hex base sha, and prints a prompt telling the verifier to judge `git diff <base-sha>..HEAD` rather than the files a green commit touched, while an unknown phase is still refused with exit 2 ⟦criterion 2⟧
- [x] build-verify-prompt.sh plan, given a spec carrying the `## Refactor` section, tells the verifier to REJECT a plan whose steps do not each name one refactoring and state its smell as a runnable shell predicate, and a spec without that section gets no such instruction ⟦criterion 3⟧
- [x] SKILL.md tells a refactor-kind run to plan each step as one named refactoring whose criterion is a shell predicate false before the step and true after it ⟦criterion 3⟧
- [x] cover-outcome.sh reads a cover leaf's report and exits 0 printing the catching test on `COVERED: yes` with a `CAUGHT_BY:` line, exits 1 on `COVERED: no`, and exits 2 on a report with neither ⟦criterion 4⟧
- [x] the develop-cover template instructs the leaf to mutate the code the step will move, run the suite, expect red, restore the edit, prove the tree unchanged, and end with `COVERED:` and `CAUGHT_BY:` lines; SKILL.md refuses to continue past Cover when `git status --porcelain` is non-empty afterwards ⟦criterion 4⟧ ⟂ refactor pending
- [ ] classify-bail.sh classifies the `uncovered` cause as `process` ⟦criterion 5⟧
- [ ] a coverage-blocker script files an unlabelled coverage issue for the refactor issue and adds that new issue under the refactor issue's `## Blocked by` heading, replacing a `None` line, so solvable-issues.sh no longer lists the refactor issue ⟦criterion 5⟧
- [ ] SKILL.md's Cover step on `COVERED: no` bails with cause `uncovered`, narrates the remedy (find a seam, surround the behaviour) and runs the coverage-blocker script ⟦criterion 5⟧
- [ ] transform-touches-tests.sh exits 1 naming the file when any commit in `<base-sha>..HEAD` changes a test file, and exits 0 when none does ⟦criterion 6⟧
- [ ] SKILL.md's refactor-kind cycle runs Cover → Transform → Verify, rejects a transform whose commits touch a test file via transform-touches-tests.sh, and abandons a step by resetting to its base sha ⟦criterion 6⟧
- [ ] SKILL.md's Draft PR step titles a run on an issue labelled `refactor` with the `refactor:` prefix, beside `fix:` and `feat:` ⟦criterion 7⟧
