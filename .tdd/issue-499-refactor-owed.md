### capture-spec.sh appends a `## Refactor` section naming the refactor run kind when the issue carries the `refactor` label, and emits no such section for an issue without it ⟦criterion 1⟧
- split capture-spec.test.sh case 4 into two cases (labelled / unlabelled) so the run_problems save-and-merge around the second run_spec disappears
