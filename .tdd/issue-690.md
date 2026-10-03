# Plan for #690 — a suite-repair step's prompts name every suite the full run left red, not only the first

- [x] build-develop-prompt.sh green, given a step text carrying ⟦suite-repair⟧ that lists two red suites each with its first failing case's name, prints a prompt naming both suites and both case names and instructing the leaf to make every listed suite green, with no text added by the caller ⟦criterion 1⟧
- [x] build-develop-prompt.sh revise green, given a step text carrying ⟦suite-repair⟧ that lists two red suites, prints a prompt telling the revise leaf to make every listed suite green, as develop-green does ⟦criterion 1⟧
- [x] build-verify-prompt.sh --step for the green phase, given a ⟦suite-repair⟧ step text listing two red suites, prints a prompt telling the verifier to PASS only when every listed suite is green, judged by running the full test command rather than the fast one ⟦criterion 2⟧
- [x] a ⟦suite-repair⟧ step text naming a single red suite builds develop-green and verify-green prompts that name that one suite and its failing case ⟦criterion 3⟧
- [x] develop-green and verify-green prompts built for a step text without ⟦suite-repair⟧ are byte-identical to the prompts the unmodified builders produce for the same arguments ⟦criterion 4⟧
- [x] SKILL.md's full-run paragraph says the repair step's text lists every suite the full run left red, each with its first FAIL - line, that the prompts take that list from the step text through their templates, and that the conductor never edits a built prompt ⟦criterion 5⟧
