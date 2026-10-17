### 📊 Metrics — issue 1339

Wall time for the issue: 152 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 6 planned.
Outcome: the run bailed — unreplaced-cases, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 2 | 4 | 1277 | 64724 | 42635 | 0.19 |
| red | 1 | 0 | 0 | 0 | 71 | 66 | 9 | 18 | 9898 | 543680 | 63439 | 0.41 |
| replaces-report | 1 | 0 | 0 | 0 | 19 | 16 | 3 | 6 | 2442 | 115897 | 44685 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 13 | 10 | 2 | 4 | 1277 | 64724 | 42635 | 0.19 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 90 | 82 | 12 | 24 | 12340 | 659577 | 108124 | 0.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 71 | 0.41 |
| replaces-report | 0 | 0.00 | 19 | 0.21 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the detach-command.test.sh cases hold as pytest cases in skills/tdd/scripts/tests/py/unit/test_detach_command.py (a process-marked case may live in skills/tdd/scripts/tests/py/test_detach_command.py) — each a pytest case driving the script's command-line interface in-process through the run_cli fixture, faking only process boundaries, asserting the same exit code, stdout, stderr, files and events byte for byte as the bash case does (same windows, same stop rules; a length bound counts bytes as under LC_ALL=C); a case whose assertion depends on real git, a signal, a detach or a symlinked entry point is marked @pytest.mark.process("<the boundary it observes>") and every other case is small and passes under make unit; a behaviour an existing pytest case already pins is not duplicated, that existing case being named as its replacement; no production change: every script, SKILL.md and CLAUDE.md stay unchanged, so each case and every helper it calls are defined in that test file and Red is expected to report AGAINST_UNMODIFIED: PASSES; each REPLACES: line is written at column 0, no bullet, with the full pytest node id <path from the repo root>::<test name> and the bash case name exactly as its report line spells it: replaces `detach-command: #601 start returns at once, wait gives the recorded code, 3 while running, 2 for a death`, `detach-command: #601 wait exits 1, printing the recorded code, for a command that finished non-zero`, `detach-command: #622 a writer whose reader closes early dies of SIGPIPE silently, as it does from a shell`, `detach-command: #622 start still runs its command in a session of its own, records .exit and .out, and wait exits 0 for a clean finish`, `detach-command: #964 wait refuses a max-seconds that is a word with exit 2 and the usage line while the command runs`, `detach-command: #964 wait refuses a max-seconds that is a word with exit 2 and the usage line when the exit file already holds 0`, `detach-command: #1155 wait refuses a VERI_POLL of abc or -1 with exit 2 and one stderr line naming it, before any round`, `detach-command: #1155 wait refuses a VERI_POLL that sleep accepted (1e-1, 0.1s, 1m) with exit 2 and one stderr line naming it, before any round`, `detach-command: a mode other than start or wait exits 2 with exactly the usage line on stderr and nothing on stdout`, `detach-command: run through a symlink to the skill directory from another working directory, start and wait use that directory's .tdd/ and create none beside the skill`, `detach-command: a command started by start sees SIGINT, SIGQUIT and SIGXFSZ ignored and SIGPIPE at its default` in skills/tdd/scripts/tests/detach-command.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 82 | 12 | 24 | 12340 | 659577 | 108124 | 0.62 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s |
| --- | ---: |
| affected | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 14 | 28 | 13617 | 724301 | 150759 | 0.81 |
