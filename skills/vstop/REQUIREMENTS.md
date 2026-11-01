## skills/vstop/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| X1 | Invoked as `/vstop [<issue>\|--all] [ledger\|leaf\|now]`, default `ledger`, each grade passed to `stop-run.sh --mode` as the mode it accepts: `ledger`→`at-ledger`, `leaf`→`at-leaf`, `now`→`now`. | The three grades Mario asked for. |
| X2 | After each conductor exits, it shows a clean tree, an empty `@{u}..HEAD` and a committed ledger, and reports where each run would resume. | Nothing should exist only locally. |
| X3 | It is never used to lower N (P8). | |
