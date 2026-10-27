## skills/tdd/scripts/prompts/develop-revise.md

| ID | Requirement | Why |
|---|---|---|
| DV1 | In a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt the permission to edit a test appears once, and it covers only the failing test the full run or CI left red; every other test stays frozen (#1653, #1920). | The repair can fix the test that is actually wrong without opening every other test to edits; PR #1907's review showed a mutant reading "Any test may change" survived. |
