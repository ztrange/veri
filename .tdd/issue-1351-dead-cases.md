# Dead cases dropped in #1351

| suite | case | reason |
|---|---|---|
| `skills/tdd/scripts/tests/step-budget.test.sh` | the suite lives in tests/, with the suites that run their script through its entry point | It asserted only where its own file sits, a property of the path and not of `step-budget.sh`; with the suite's other cases moved to pytest, deleting the suite leaves no behaviour unpinned. |
