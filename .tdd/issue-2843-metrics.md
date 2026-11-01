### 📊 Metrics — issue 2843

Wall time for the issue: 1978 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2848.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.13 over 31 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87707 tokens, largest 176153 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87707 |
| 2 | $0.09 | 96224 |
| 3 | $0.04 | 98478 |
| 4 | $0.03 | 99523 |
| 5 | $0.02 | 99927 |
| 6 | $0.09 | 108677 |
| 7 | $0.05 | 112474 |
| 8 | $0.13 | 125811 |
| 9 | $0.07 | 131030 |
| 10 | $0.05 | 134039 |
| 11 | $0.09 | 142487 |
| 12 | $0.03 | 143223 |
| 13 | $0.06 | 146863 |
| 14 | $0.04 | 148616 |
| 15 | $0.04 | 150003 |
| 16 | $0.04 | 150758 |
| 17 | $0.04 | 152044 |
| 18 | $0.05 | 154416 |
| 19 | $0.05 | 156836 |
| 20 | $0.05 | 159173 |
| 21 | $0.04 | 160481 |
| 22 | $0.05 | 162511 |
| 23 | $0.04 | 163423 |
| 24 | $0.04 | 164654 |
| 25 | $0.05 | 166843 |
| 26 | $0.05 | 169461 |
| 27 | $0.06 | 172133 |
| 28 | $0.04 | 173278 |
| 29 | $0.04 | 174293 |
| 30 | $0.04 | 175194 |
| 31 | $0.04 | 176153 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 1 | 2 | 1282 | 0 | 33686 | 0.10 |
| diff | 4 | 2 | 0 | 0 | 275 | 45 | 17 | 32 | 4435 | 436042 | 84983 | 0.30 |
| red | 7 | 3 | 0 | 0 | 265 | 92 | 27 | 54 | 10961 | 806815 | 135458 | 0.53 |
| green | 6 | 3 | 0 | 0 | 407 | 55 | 27 | 46 | 6445 | 660802 | 99095 | 0.38 |
| refactor | 4 | 1 | 0 | 0 | 83 | 24 | 14 | 22 | 2390 | 297230 | 63218 | 0.21 |
| pin | 1 | 1 | 0 | 0 | 22 | 9 | 3 | 6 | 1017 | 82709 | 18834 | 0.07 |
| prose | 3 | 0 | 0 | 0 | 85 | 77 | 3 | 6 | 12472 | 3681 | 134666 | 0.46 |
| skill-edit | 1 | 0 | 0 | 0 | 11 | 9 | 5 | 10 | 931 | 270387 | 46240 | 0.15 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 11 | 0 | 0 | 577 | 98 | 34 | 66 | 10314 | 868318 | 197131 | 0.68 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 489 | 138 | 55 | 96 | 16216 | 1415280 | 238143 | 0.90 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only, no production change: in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, the older cases whose recorded command prints nothing unmutated and exits non-zero mutated (test_2506_a_record_whose_command_passes_unmutated_and_fails_mutated_exits_0_and_leaves_the_file_alone, test_2814_a_record_through_a_vanished_timed_test_run_path_is_replayed_and_not_reported_as_needing_a_look, test_2814_a_record_through_a_timed_test_run_path_that_still_exists_is_replayed_through_that_path) record a command that prints one result line both unmutated and mutated, so each keeps its name, its assertions and its meaning of a real red once a silent unmutated run stops counting as red ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 9 | 16 | 2410 | 213584 | 52368 | 0.18 | 217 | n/a | n/a | n/a |  |  | full |
| A record whose unmutated run exits 0 with empty stdout and stderr, and whose mutated run exits non-zero, prints `needs a look: <file>` on stdout and pin-recheck.sh exits 1; the recorded file is restored byte for byte. One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, driving pin-recheck.sh against a real git repository ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 52 | 19 | 36 | 5542 | 519368 | 86883 | 0.32 | 343 | unknown | 0/5 | nothing-left |  |  | full |
| A record whose unmutated run printed output and whose mutated run exits non-zero while sharing a line with it (a real test failure) still counts as red, exit 0 as today: test_2827_a_mutated_run_that_exits_non_zero_and_still_prints_the_unmutated_result_line_counts_as_red_and_exits_0 stays in the suite with its body unchanged and passing, and the branch's diff weakens no part of it ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 20 | 8 | 16 | 2025 | 222458 | 32615 | 0.12 | 214 | n/a | n/a | n/a |  |  | full |
| A record whose mutation did not build (non-empty unmutated output, mutated output sharing no line) writes the mutated run's stdout and stderr to stderr, limited to its last 40 lines, when it prints `needs a look`. One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, whose mutated run prints more than 40 lines across stdout and stderr ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 19 | 36 | 5848 | 524869 | 87530 | 0.33 | 309 | unknown | 0/5 | nothing-left |  |  | full |
| A record whose unmutated run exits non-zero writes that run's stdout and stderr to stderr, limited to its last 40 lines, when it prints `needs a look`. One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, whose unmutated run prints more than 40 lines across stdout and stderr ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 54 | 26 | 42 | 6400 | 598068 | 102349 | 0.38 | 333 | unknown | 1/5 | nothing-left |  |  | full |
| A record whose unmutated run exits 0 with no output, and whose mutated run prints `error: build failed` and exits non-zero, writes that mutated output to stderr when it prints `needs a look` (the issue's Expected 2 and reproduction step 4). One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 7 | 14 | 3023 | 205251 | 39843 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| skills/tdd/SCRIPTS.md's pin-recheck.sh entry states that exit 1 also covers a mutated run that exits non-zero when the unmutated run printed nothing, and that a `needs a look` record from a failed run writes that run's output to stderr, limited to its last 40 lines ⟦skill-edit⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 58 | 7 | 14 | 8832 | 272552 | 136276 | 0.46 | 93 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A record whose unmutated run exits 0 with empty stdout and stderr, and whose mutated run exits non-zero, prints `needs a look: <file>` on stdout and pin-recheck.sh exits 1; the recorded file is restored byte for byte. One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, driving pin-recheck.sh against a real git repository ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| A record whose mutation did not build (non-empty unmutated output, mutated output sharing no line) writes the mutated run's stdout and stderr to stderr, limited to its last 40 lines, when it prints `needs a look`. One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, whose mutated run prints more than 40 lines across stdout and stderr ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| A record whose unmutated run exits non-zero writes that run's stdout and stderr to stderr, limited to its last 40 lines, when it prints `needs a look`. One process-marked case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py, whose unmutated run prints more than 40 lines across stdout and stderr ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 67 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 35 | 53 | 49 | 41 | 48 | 37 | 44 | 37 | 40 |  |  |  |  |  |  |  |
| affected | 5 | 4 | 5 | 8 | 8 | 6 | 6 | 5 | 6 | 5 | 5 | 4 | 6 | 6 | 6 | 7 |
| target | 4 | 7 | 7 | 4 | 4 | 4 | 3 | 5 | 4 | 4 | 5 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 97 | 178 | 39933 | 2557666 | 616180 | 4.33 (estimate) |
