## skills/tdd/scripts/prompts/develop-revise.md

| ID | Requirement | Why |
|---|---|---|
| DV1 | In a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt the permission to edit a test appears once, and it covers only the failing test the full run or CI left red; every other test stays frozen (#1653, #1920). | The repair can fix the test that is actually wrong without opening every other test to edits; PR #1907's review showed a mutant reading "Any test may change" survived. |

## skills/tdd/scripts/prompts/develop-contract-a.md

| ID | Requirement | Why |
|---|---|---|
| CA1 | The prompt says this is the contract-a phase of an interface change: no product caller of the old interface remains, the tests that still exercise it move off it, tests are rewritten or deleted, and production stays frozen. (Opening paragraph.) | The leaf must know which of the four interface phases it is in and what it may touch. |
| CA2 | Step 1 tells the leaf to rewrite every test of the old interface against the new one, or to delete it where a test of the new interface already covers the same behaviour. (Numbered list, item 1.) | A test of the old interface that survives would keep the proxy alive. |
| CA3 | Step 1 tells the leaf to leave the old interface in place, because deleting its proxy is contract-b. (Numbered list, item 1, last sentence.) | The proxy's deletion belongs to the next phase. |
| CA4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`, and never to modify a production file: a contract-a commit that touches one is rejected. (Numbered list, item 3.) | The commit carries the issue number, and the frozen half of the phase is enforced by rejection. |
| CA5 | The numbered list has three items in this order: rewrite or delete the tests (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The tests are moved before the run proves them green, and the commit follows the proof. |
