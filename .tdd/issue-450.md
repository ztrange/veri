# Plan for #450 — `build-develop-prompt.sh` accepts an `over-budget` phase naming the cost fact, not a rejection reason

- [x] `build-develop-prompt.sh over-budget <spec> <step> <cmd> <spent> <budget>` renders a prompt carrying the step text, the spent figure, the budget figure and the issue spec ⟦criterion 1⟧
- [x] The rendered over-budget prompt asks for the same two report shapes the exhausted phase asks for (SPLIT: lines or the needs-user answer), so exhausted-outcome.sh reads it unchanged ⟦criterion 2⟧
- [x] The rendered over-budget prompt states that a crossing is not a verdict and that "one behaviour, simply expensive" is an available answer ⟦criterion 3⟧
- [x] The over-budget prompt gives the "neither — one behaviour, simply expensive" answer its own report shape, telling the leaf to print no SPLIT: and no NEEDS_USER: line when it chooses it ⟦added⟧ ⟦criterion 3⟧
- [x] A spent or budget figure that is not a non-negative decimal number exits 2 and renders nothing, both validated before any template is read ⟦criterion 4⟧
- [x] over-budget with fewer than five arguments after the phase exits 2 ⟦criterion 5⟧
- [x] The over-budget prompt names no rejection reason and no verdict, and the phase takes no parameter that could carry one ⟦criterion 6⟧
- [x] Every other phase renders byte-identically to before this change ⟦criterion 7⟧
