## skills/veri-stop/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| X1 | Invoked as `/veri-stop [<issue>\|--all] [ledger\|leaf\|now]`, default `ledger`, mapped to `stop-run.sh --mode`. | The three grades Mario asked for. |
| X2 | After each conductor exits, it shows a clean tree, an empty `@{u}..HEAD` and a committed ledger, and reports where each run would resume. | Nothing should exist only locally. |
| X3 | It is never used to lower N (P8). | |
