### The median is taken over completed full steps only, told apart by leaf count from `step-cost.sh --steps`, so a log whose completed steps are mostly cheap pins still projects the remainder at the full-step median ⟦criterion 3⟧
- cases 1 and 3 of run-affordable.test.sh log the same three full steps verbatim; a shared fixture helper would remove it, but an earlier cycle wrote that code (out of this cycle's bounds)
### `run-affordable.sh <n>` exits 3 with nothing on stdout when the event log holds no completed full step, only pins or no usage at all ⟦criterion 4⟧
- cases 1 and 3 of run-affordable.test.sh build the same three-full-step fixture line for line, and could share one helper (this cycle did not write either case, so it is out of scope here)
