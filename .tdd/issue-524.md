# Plan for #524 — make test can fail a green suite: the recipe tail -n 1 | grep -Eq count-line check dies of SIGPIPE on Linux

- [x] no-sigpipe-pipelines.test.sh also audits the Makefile's recipe lines, reporting a recipe line that ends a pipeline in a reader leaving before EOF (a grep whose options carry q, or a head) as Makefile:<line> — shown on a planted offending recipe; the recipe shell declares no pipefail, so the Makefile is audited without that condition ⟦criterion 3⟧
- [x] The make test / make unit recipe's count-line check reads the suite's last line to EOF (grep -E … > /dev/null, or feeding the reader by redirection rather than a pipe; never trap '' PIPE, never dropping pipefail), so the audit over the real Makefile names no site ⟦criterion 1⟧
- [ ] A suite whose last output line is not a count line is still failed by make test, named `<suite>: never reached its count line`, exactly as before the repair ⟦criterion 2⟧
- [ ] A Makefile recipe site where leaving before EOF is deliberate is exempted by an entry in the audit's exemption table keyed Makefile:<line> carrying a reason, and an exemption entry with no reason still fails the run ⟦criterion 3⟧
