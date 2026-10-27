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

## skills/tdd/scripts/prompts/develop-contract-b.md

| ID | Requirement | Why |
|---|---|---|
| CB1 | The prompt says this is the contract-b phase of an interface change: neither product code nor any test calls the old interface any more, and the old interface's proxy is deleted. (Opening paragraph, first two sentences.) | The leaf deletes the proxy only once nothing calls it. |
| CB2 | The prompt says behaviour does not change: every test that was green stays green, and test files stay frozen. (Opening paragraph, last sentence.) | The phase is a pure deletion; a changed test would hide a behaviour change. |
| CB3 | Step 1 tells the leaf to delete the old interface's proxy from production. (Numbered list, item 1.) | It is the one change this phase makes. |
| CB4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| CB5 | Step 3 tells the leaf never to modify a test file: a contract-b commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| CB6 | The numbered list has three items in this order: delete the proxy (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The deletion is proven green before it is committed. |

## skills/tdd/scripts/prompts/develop-expand.md

| ID | Requirement | Why |
|---|---|---|
| EX1 | The prompt says this is the expand phase of an interface change: production gains the new interface, and the old interface becomes a proxy that delegates to it. (Opening paragraph, first two sentences.) | The leaf must know what the phase adds and what the old interface turns into. |
| EX2 | The prompt says behaviour does not change: every test that was green stays green, and test files stay frozen. (Opening paragraph, last sentence.) | The expand is a refactor; a changed test would hide a behaviour change. |
| EX3 | Step 1 tells the leaf to add the new interface to production and turn the old one into a proxy over it, and to move no caller yet, because that is the migrate phase. (Numbered list, item 1.) | Moving callers is the next phase's work, so the diff stays one kind of change. |
| EX4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| EX5 | Step 3 tells the leaf never to modify a test file: an expand commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| EX6 | The numbered list has three items in this order: add the interface and proxy the old one (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The change is proven green before it is committed. |

## skills/tdd/scripts/prompts/develop-migrate.md

| ID | Requirement | Why |
|---|---|---|
| MG1 | The prompt says this is the migrate phase of an interface change: the new interface exists, the old one is a proxy over it, and the callers move to the new interface. (Opening paragraph, first two sentences.) | The leaf must know the state it starts from and what it moves. |
| MG2 | The prompt says behaviour does not change: every test that was green stays green, and test files stay frozen. (Opening paragraph, last sentence.) | The migrate is a refactor; a changed test would hide a behaviour change. |
| MG3 | Step 1 tells the leaf to move every product caller of the old interface to the new interface, and to leave the old interface in place, because removing it is the contract phase. (Numbered list, item 1.) | The proxy's removal is later work, so a missed caller still works through the proxy. |
| MG4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| MG5 | Step 3 tells the leaf never to modify a test file: a migrate commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| MG6 | The numbered list has three items in this order: move the callers (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The change is proven green before it is committed. |
