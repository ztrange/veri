# Plan for #880 — build-develop-prompt.sh revise diff exits 2: a REJECTed ⟦diff-checked⟧ step can never get a revise leaf

- [x] A revise of an unknown phase is refused with exit 2 and a message naming diff among the accepted revise phases red|green|refactor|diff ⟦criterion 2⟧
- [x] build-develop-prompt.sh revise diff <spec> <step> <test-cmd> <reason-file> exits 0 and prints a revise prompt carrying the step text and the verifier's rejection reason ⟦criterion 1⟧
- [x] The revise prompt built for diff does not ask the leaf to write or rewrite a test, since a diff-checked step adds none ⟦criterion 3⟧ ⟂ refactor pending
- [ ] SKILL.md's Revising on a REJECT section covers the diff phase: the revise leaf is built with revise diff, and the re-verify is the blind diff verifier run against the same base sha as the original verify-diff verdict, its PASS ticked as the diff-checked PASS bullet describes ⟦criterion 4⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 5⟧
