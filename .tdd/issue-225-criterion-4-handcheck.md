# #225 criterion 4 — the recorded hand-check

Done outside the `/tdd` procedure, which structurally cannot produce this record: a leaf may not
run another suite (`no-nested-suites.test.sh`), and no test can read an issue comment without
going to the network. The issue body settled that the deliverable is the record, per suite, not
an automated relaunch.

For each suite: confirmed green on the unmodified tree, broke one passage it guards, watched it
go red, restored the file with `git checkout --`, confirmed green again. One break at a time.

| suite | passage broken | observed red |
|---|---|---|
| `selection-order-recorded.test.sh` | `CONTEXT.md:168`, the *Selection layer* entry — `each band ascending by number` -> `each band in the usual order` | `0 passed, 1 failed`, exit 1 |
| `model-knobs-recorded.test.sh` | `skills/tdd/SKILL.md:86`, the `supervise.sh` bullet — `VERI_MODEL_VERIFIER` -> `VERI_MODEL_CHECKER` | `7 passed, 1 failed`, exit 1 |
| `lane-rule-recorded.test.sh` | `CLAUDE.md:248` — `` `no-docs-reads.test.sh` fails the run `` -> `a guard suite fails the run`, removing the case's name | `0 passed, 1 failed`, exit 1 |
| `unit-tier-recorded.test.sh` | `CLAUDE.md:219`, the fast-tier admission bar — `about 100 ms per` -> `about a tenth of a second per` | `1 passed, 1 failed`, exit 1 |

The four `FAIL - ` lines, verbatim:

```
FAIL - CONTEXT.md's Selection layer and Solvable entries, skills/tdd/SKILL.md's solvable-issues.sh bullet and CLAUDE.md record the three-band order and VERI_PRIORITY_LABEL, and say priority reorders the solvable set without enlarging it
    CONTEXT.md's Selection layer entry does not say states the three-band order — priority, then bug, then the rest, each band ascending by number
```
```
FAIL - skills/tdd/SKILL.md's supervise.sh bullet and CLAUDE.md name VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, and CLAUDE.md says why developer and verifier are separate knobs
    skills/tdd/SKILL.md's supervise.sh bullet does not say lists the three model tunables beside the ones it already lists — it names no single passage carrying VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER
```
```
FAIL - CLAUDE.md states the lane rule in both sections an agent reads: the page is the other lane's work and a development run never runs a docs target, a suite here never reads the generated tree, and docs-owed.sh and docs-fresh are what catch prose lag
    CLAUDE.md's '## Testing idiom' section does not say that a suite here never reads a path in the generated tree, nor which case says so by name
```
```
FAIL - CLAUDE.md's 'Testing idiom' section names skills/tdd/scripts/tests/unit/ as the fast tier and states its admission bar
    CLAUDE.md's 'Testing idiom' section does not say the admission bar — about 100 ms per case, and no git, network, servers, real waits or nested suites
```

After all four restores, `git status --porcelain` is empty and the four suites print
`1 passed, 0 failed`, `8 passed, 0 failed`, `1 passed, 0 failed`, `2 passed, 0 failed`, each
exit 0 — re-run and confirmed independently of the run that performed the breaks.

Steps 8 and 9 are ticked against this record rather than against a green commit, because the
step's deliverable is the record. That is why the procedure bailed on it twice instead of
producing it.
