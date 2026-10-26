This step replaces cases, so it is not one criterion, one case: write one pytest replacement
case for each bash case the step named, each in its own `def test_...`, no extra cases, and no
generality the step does not ask for. For each of them, report one line
`REPLACES: <case name> => <pytest test id>` for each case the step named, the case name
exactly as the step spells it, without the quote characters the step wraps it in. {{INCLUDE:_develop-node-id-rule.md}}
