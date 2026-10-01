# Plan for #565 — finish the test-suite comment sweep: the classifier gaps, tests/unit, fixtures and headers (continues #494)

Scope: every shell file under `skills/tdd/scripts/tests/`. "The sweepable report" is `skills/tdd/scripts/comment-class.sh --sweepable <files>`; it is empty when it prints nothing. "The leading header block" is the run of `#` lines directly after a file's `#!` line — the block `--sweepable` leaves out.

- [x] comment-class.sh --sweepable omits a tab-indented `#!` line that opens a `<<-` heredoc's body, since bash strips the tabs before writing it ⟦criterion 1⟧
- [x] comment-class.sh classifies every `#` line of a file and drops none after a `"$(cmd 'a "b')"` shape (a `"` inside a single-quoted argument inside `"$(…)"`) ⟦criterion 2⟧
- [x] The sweepable report is empty for every shell file under `tests/unit/` whose name starts with c through e, other than `comment-class.test.sh` ⟦criterion 3⟧
- [x] The sweepable report is empty for `tests/unit/ledger.test.sh`, the one unit suite starting with a letter no criterion names
- [x] The sweepable report is empty for every shell file under `tests/unit/` whose name starts with m through p ⟦criterion 4⟧
- [x] The sweepable report is empty for `tests/unit/red-divergence.test.sh` ⟦criterion 5⟧
- [x] The sweepable report is empty for `tests/unit/run-affordable.test.sh` ⟦criterion 5⟧
- [x] The sweepable report is empty for `tests/unit/step-budget.test.sh` and `tests/unit/step-cost.test.sh` ⟦criterion 6⟧
- [x] The sweepable report is empty for `tests/unit/stop-requested.test.sh` ⟦criterion 6⟧
- [x] The sweepable report is empty for every shell file under `tests/fixtures/`, and for `tests/unit-guard/git` and `tests/offline/gh` ⟦criterion 7⟧
- [x] The sweepable report is empty for `tests/unit/comment-class.test.sh`, the case labels of its own sweepable-report cases included ⟦criterion 8⟧
- [x] The leading header block of every top-level `tests/*.sh` whose name starts with a through e carries only its contract, and no line of it cites an issue number (`#<digits>`) ⟦criterion 9⟧
- [x] The leading header block of every top-level `tests/*.sh` whose name starts with f through p carries only its contract, and no line of it cites an issue number (`#<digits>`) ⟦criterion 9⟧
- [x] The leading header block of every top-level `tests/*.sh` whose name starts with q through z, other than the `skill-*` files, carries only its contract, and no line of it cites an issue number (`#<digits>`) ⟦criterion 9⟧
- [x] The leading header block of every `tests/skill-*.test.sh` whose name after `skill-` starts with a through l carries only its contract, and no line of it cites an issue number (`#<digits>`) ⟦criterion 9⟧
- [x] The leading header block of every `tests/skill-*.test.sh` whose name after `skill-` starts with m through z carries only its contract, and no line of it cites an issue number (`#<digits>`) ⟦criterion 9⟧
- [x] The leading header block of every shell file under `tests/unit/`, `tests/fixtures/`, `tests/unit-guard/` and `tests/offline/` carries only its contract, and no line of it cites an issue number (`#<digits>`) ⟦criterion 9⟧
- [x] Repair the red full run: no-job-spec-kills.test.sh ("FAIL - no file under skills/ ends a background process by a job spec" at skill-leaf-env.test.sh:407, its exemption keyed to :452), no-nested-suites.test.sh ("FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here" at comment-class.test.sh:395–406 sweep_verdict lines) and no-sigpipe-pipelines.test.sh ("FAIL - no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF" at run-conductor.test.sh:36) all pass again ⟦added⟧ ⟦criterion 9⟧
- [ ] Every suite still ends with its count line, and `make test` is green on the swept tree ⟦full-suite⟧ ⟦criterion 10⟧
