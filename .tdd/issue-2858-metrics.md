### 📊 Metrics — issue 2858

Wall time for the issue: 1778 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2859.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $7.48 over 101 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86597 tokens, largest 190126 tokens
Conductor context: first turn 86636 tokens, largest 170957 tokens
Conductor context: first turn 86622 tokens, largest 159642 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 86597 |
| 2 | $0.11 | 95670 |
| 3 | $0.05 | 97766 |
| 4 | $0.05 | 98945 |
| 5 | $0.04 | 99337 |
| 6 | $0.04 | 99935 |
| 7 | $0.07 | 104469 |
| 8 | $0.08 | 109705 |
| 9 | $0.08 | 113891 |
| 10 | $0.14 | 126668 |
| 11 | $0.07 | 129839 |
| 12 | $0.06 | 131511 |
| 13 | $0.05 | 132243 |
| 14 | $0.06 | 134476 |
| 15 | $0.05 | 135028 |
| 16 | $0.05 | 135632 |
| 17 | $0.04 | 135976 |
| 18 | $0.05 | 136542 |
| 19 | $0.05 | 136900 |
| 20 | $0.05 | 137562 |
| 21 | $0.05 | 138332 |
| 22 | $0.06 | 140260 |
| 23 | $0.07 | 142863 |
| 24 | $0.07 | 146201 |
| 25 | $0.08 | 149712 |
| 26 | $0.06 | 151032 |
| 27 | $0.05 | 151732 |
| 28 | $0.12 | 160191 |
| 29 | $0.07 | 163513 |
| 30 | $0.07 | 165083 |
| 31 | $0.07 | 168079 |
| 32 | $0.06 | 169468 |
| 33 | $0.08 | 172050 |
| 34 | $0.07 | 175128 |
| 35 | $0.08 | 177564 |
| 36 | $0.06 | 178550 |
| 37 | $0.07 | 180568 |
| 38 | $0.06 | 181311 |
| 39 | $0.08 | 185614 |
| 40 | $0.07 | 187015 |
| 41 | $0.07 | 189292 |
| 42 | $0.07 | 190126 |
| 43 | $0.57 | 86636 |
| 44 | $0.09 | 93639 |
| 45 | $0.05 | 96067 |
| 46 | $0.07 | 99866 |
| 47 | $0.13 | 110979 |
| 48 | $0.05 | 112012 |
| 49 | $0.04 | 112786 |
| 50 | $0.05 | 113621 |
| 51 | $0.06 | 116095 |
| 52 | $0.13 | 127513 |
| 53 | $0.05 | 128266 |
| 54 | $0.06 | 131144 |
| 55 | $0.06 | 132883 |
| 56 | $0.05 | 133764 |
| 57 | $0.06 | 136098 |
| 58 | $0.13 | 146376 |
| 59 | $0.07 | 149337 |
| 60 | $0.05 | 149887 |
| 61 | $0.06 | 150767 |
| 62 | $0.07 | 154286 |
| 63 | $0.07 | 157148 |
| 64 | $0.07 | 159868 |
| 65 | $0.08 | 162742 |
| 66 | $0.09 | 167952 |
| 67 | $0.07 | 170957 |
| 68 | $0.55 | 86622 |
| 69 | $0.08 | 94316 |
| 70 | $0.04 | 96484 |
| 71 | $0.04 | 98815 |
| 72 | $0.08 | 105834 |
| 73 | $0.03 | 106897 |
| 74 | $0.03 | 108303 |
| 75 | $0.02 | 108590 |
| 76 | $0.03 | 109000 |
| 77 | $0.04 | 111840 |
| 78 | $0.04 | 114552 |
| 79 | $0.03 | 115362 |
| 80 | $0.08 | 121916 |
| 81 | $0.04 | 123263 |
| 82 | $0.04 | 124700 |
| 83 | $0.03 | 125582 |
| 84 | $0.04 | 127892 |
| 85 | $0.03 | 128926 |
| 86 | $0.10 | 137965 |
| 87 | $0.04 | 139754 |
| 88 | $0.06 | 143238 |
| 89 | $0.05 | 145648 |
| 90 | $0.05 | 147701 |
| 91 | $0.05 | 150009 |
| 92 | $0.04 | 150957 |
| 93 | $0.05 | 153261 |
| 94 | $0.04 | 154230 |
| 95 | $0.05 | 156148 |
| 96 | $0.05 | 158265 |
| 97 | $0.04 | 158715 |
| 98 | $0.04 | 159642 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1188 | 0 | 33184 | 0.09 |
| diff | 6 | 3 | 0 | 0 | 396 | 61 | 24 | 48 | 6997 | 659859 | 116338 | 0.43 |
| red | 15 | 5 | 1 | 0 | 836 | 328 | 77 | 134 | 39822 | 2316099 | 401619 | 2.17 |
| pin | 7 | 5 | 2 | 0 | 176 | 91 | 25 | 50 | 10400 | 721907 | 137587 | 0.52 |
| green | 13 | 1 | 3 | 0 | 1880 | 299 | 89 | 150 | 35053 | 2512973 | 386063 | 2.07 |
| red-supersede | 2 | 0 | 0 | 0 | 90 | 55 | 12 | 24 | 7205 | 402114 | 48304 | 0.23 |
| exhausted | 1 | 0 | 0 | 0 | 88 | 16 | 3 | 4 | 1665 | 48113 | 20328 | 0.14 |
| red-missing | 1 | 0 | 0 | 0 | 44 | 28 | 5 | 10 | 3752 | 162979 | 22444 | 0.11 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 2 | 4 | 351 | 49723 | 15896 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 21 | 15 | 6 | 0 | 1238 | 252 | 78 | 150 | 29125 | 2152973 | 364990 | 1.42 |
| developer | claude-sonnet-5-5 | 16 | 0 | 0 | 0 | 769 | 391 | 87 | 160 | 48739 | 2743251 | 453398 | 2.43 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 1522 | 248 | 73 | 116 | 28569 | 1977543 | 363375 | 1.97 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 159 | 0.12 |
| red | 704 | 1.74 | 0 | 0.00 |
| pin | 172 | 0.47 | 0 | 0.00 |
| green | 5253 | 4.98 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The two older unit cases in skills/tdd/scripts/tests/py/unit/test_pr_ready.py that pin the exact call list of a mismatched head (test_pr_ready_reads_the_head_again_every_veri_poll_seconds_until_it_is_the_sha and test_pr_ready_exits_2_unready_naming_both_shas_when_the_head_never_becomes_the_sha) keep asserting the same behaviour (reads of the head, sleeps, the ready route, the exit and stderr) but tolerate extra non-head-read calls, with any git call answered as failed, so they stay green before and after the remote check lands; test-only, no production change ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 18 | 6 | 12 | 2247 | 140523 | 47866 | 0.16 | 162 | n/a | n/a | n/a |  |  | full |
| When the remote branch holds <sha> but the PR API still reports the old head, pr-ready.sh keeps polling as today and readies once the head matches (the existing wait is not removed), pinned by a case with a real git repository and bare remote holding <sha> and a fake gh ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 9 | 18 | 4448 | 286995 | 41029 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| When the remote cannot be asked because git ls-remote fails, pr-ready.sh falls through to the existing poll and its existing exit codes, so a network blip is no new refusal, pinned by a case whose origin is unreachable ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 10 | 20 | 4359 | 312507 | 41785 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| When git ls-remote answers but lists no such branch on the remote, pr-ready.sh falls through to the existing poll and its existing exit codes rather than refusing | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 4594 | 316455 | 41375 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| When the PR's branch name cannot be read from pulls/<n> (.head.ref), pr-ready.sh falls through to the existing poll and its existing exit codes rather than refusing | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 8 | 16 | 4741 | 243652 | 40773 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| When the remote branch the PR is headed by holds a sha other than <sha>, pr-ready.sh exits 2 at the first mismatched head read, without reading the PR head more than once more, and stderr names the remote's sha, <sha> and the branch; a process case in a real git repository with a bare remote at another sha and a fake gh, setting VERI_POLL large and asserting the call returns without sleeping ⟦criterion 1⟧ | 32 | 7 | 6 | 0 | 0 | 0 | 679 | 176 | 302 | 80106 | 5054299 | 867279 | 4.58 | 1291 | red 3/2, green 4/2 | 0/5 | nothing-left |  |  | already-satisfied |
| Test-only, no production change: the two unit cases in skills/tdd/scripts/tests/py/unit/test_pr_ready.py that call run_cli with no cwd (test_pr_ready_reads_the_head_again_every_veri_poll_seconds_until_it_is_the_sha and test_pr_ready_exits_2_unready_naming_both_shas_when_the_head_never_becomes_the_sha) pass cwd=tmp_path, so pr-ready's git call runs outside the repository the tests live in and the conftest guard is not tripped; conftest.py and its guard are not edited or exempted ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 9 | 18 | 2065 | 255622 | 30786 | 0.12 | unknown | n/a | n/a | n/a |  |  | full |
| Test-only, no production change, no pin: test_pr_ready_reads_the_head_again_every_veri_poll_seconds_until_it_is_the_sha and test_pr_ready_exits_2_unready_naming_both_shas_when_the_head_never_becomes_the_sha in skills/tdd/scripts/tests/py/unit/test_pr_ready.py stop pinning the exact gh call list against the PR's .head.ref read the next step adds: their expected calls admit that one read (e.g. they compare only the head-sha reads and the ready call), so they pass both before and after it; their behaviour, the existing wait, is unchanged ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 18 | 2685 | 263714 | 37686 | 0.15 | 222 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the remote branch the PR is headed by holds a sha other than <sha>, pr-ready.sh exits 2 at the first mismatched head read, without reading the PR head more than once more, and stderr names the remote's sha, <sha> and the branch; a process case in a real git repository with a bare remote at another sha and a fake gh, setting VERI_POLL large and asserting the call returns without sleeping ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 34 | 29 | 30 | 63 | 49 | 43 | 49 | 59 | 35 | 42 | 49 | 50 | 44 | 38 | 31 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 5 | 3 | 3 | 3 | 5 | 5 | 20 | 19 | 18 | 18 | 18 | 19 | 18 | 762 | 10 | 8 | 16 | 16 | 14 | 8 | 7 | 17 | 17 | 12 | 7 | 8 | 9 | 0 | 14 | 10 | 1 | 9 | 5 |
| target | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 19 | 4 | 5 | 4 | 3 | 4 | 0 | 8 | 7 | 4 | 5 | 6 | 5 | 5 | 5 | 6 | 7 | 7 | 6 | 5 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 238 | 426 | 106433 | 6873767 | 1181763 | 13.30 (estimate) |
