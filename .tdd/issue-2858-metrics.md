### 📊 Metrics — issue 2858

Wall time for the issue: 2487 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 7 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.46 over 40 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86597 tokens, largest 187015 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86597 |
| 2 | $0.09 | 95670 |
| 3 | $0.04 | 97766 |
| 4 | $0.03 | 98945 |
| 5 | $0.02 | 99337 |
| 6 | $0.02 | 99935 |
| 7 | $0.06 | 104469 |
| 8 | $0.06 | 109705 |
| 9 | $0.06 | 113891 |
| 10 | $0.13 | 126668 |
| 11 | $0.05 | 129839 |
| 12 | $0.04 | 131511 |
| 13 | $0.03 | 132243 |
| 14 | $0.04 | 134476 |
| 15 | $0.03 | 135028 |
| 16 | $0.03 | 135632 |
| 17 | $0.03 | 135976 |
| 18 | $0.03 | 136542 |
| 19 | $0.03 | 136900 |
| 20 | $0.03 | 137562 |
| 21 | $0.03 | 138332 |
| 22 | $0.04 | 140260 |
| 23 | $0.05 | 142863 |
| 24 | $0.06 | 146201 |
| 25 | $0.06 | 149712 |
| 26 | $0.04 | 151032 |
| 27 | $0.04 | 151732 |
| 28 | $0.10 | 160191 |
| 29 | $0.06 | 163513 |
| 30 | $0.05 | 165083 |
| 31 | $0.06 | 168079 |
| 32 | $0.04 | 169468 |
| 33 | $0.05 | 172050 |
| 34 | $0.06 | 175128 |
| 35 | $0.05 | 177564 |
| 36 | $0.04 | 178550 |
| 37 | $0.05 | 180568 |
| 38 | $0.04 | 181311 |
| 39 | $0.07 | 185614 |
| 40 | $0.05 | 187015 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1188 | 0 | 33184 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 97 | 18 | 6 | 12 | 2247 | 140523 | 47866 | 0.16 |
| red | 10 | 3 | 1 | 0 | 518 | 206 | 50 | 92 | 25407 | 1549074 | 260374 | 1.35 |
| pin | 5 | 4 | 1 | 0 | 126 | 65 | 18 | 36 | 7509 | 511273 | 93614 | 0.36 |
| green | 4 | 0 | 0 | 0 | 1057 | 153 | 39 | 66 | 17034 | 1190135 | 214400 | 1.13 |
| red-supersede | 1 | 0 | 0 | 0 | 47 | 25 | 6 | 12 | 3457 | 201292 | 24276 | 0.12 |
| exhausted | 1 | 0 | 0 | 0 | 88 | 16 | 3 | 4 | 1665 | 48113 | 20328 | 0.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 9 | 2 | 0 | 449 | 123 | 37 | 72 | 14221 | 998793 | 203937 | 0.75 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 233 | 127 | 31 | 62 | 17117 | 995521 | 149888 | 0.65 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1263 | 242 | 55 | 90 | 27169 | 1646096 | 340217 | 1.96 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 386 | 0.93 |
| pin | 0 | 0.00 | 36 | 0.08 |
| green | 0 | 0.00 | 1057 | 1.13 |
| red-supersede | 0 | 0.00 | 47 | 0.12 |
| exhausted | 0 | 0.00 | 88 | 0.14 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The two older unit cases in skills/tdd/scripts/tests/py/unit/test_pr_ready.py that pin the exact call list of a mismatched head (test_pr_ready_reads_the_head_again_every_veri_poll_seconds_until_it_is_the_sha and test_pr_ready_exits_2_unready_naming_both_shas_when_the_head_never_becomes_the_sha) keep asserting the same behaviour (reads of the head, sleeps, the ready route, the exit and stderr) but tolerate extra non-head-read calls, with any git call answered as failed, so they stay green before and after the remote check lands; test-only, no production change ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 18 | 6 | 12 | 2247 | 140523 | 47866 | 0.16 | 162 | n/a | n/a | n/a |  |  | full |
| When the remote branch holds <sha> but the PR API still reports the old head, pr-ready.sh keeps polling as today and readies once the head matches (the existing wait is not removed), pinned by a case with a real git repository and bare remote holding <sha> and a fake gh ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 9 | 18 | 4448 | 286995 | 41029 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| When the remote cannot be asked because git ls-remote fails, pr-ready.sh falls through to the existing poll and its existing exit codes, so a network blip is no new refusal, pinned by a case whose origin is unreachable ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 10 | 20 | 4359 | 312507 | 41785 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| When git ls-remote answers but lists no such branch on the remote, pr-ready.sh falls through to the existing poll and its existing exit codes rather than refusing | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 4594 | 316455 | 41375 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| When the PR's branch name cannot be read from pulls/<n> (.head.ref), pr-ready.sh falls through to the existing poll and its existing exit codes rather than refusing | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 8 | 16 | 4741 | 243652 | 40773 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| When the remote branch the PR is headed by holds a sha other than <sha>, pr-ready.sh exits 2 at the first mismatched head read, without reading the PR head more than once more, and stderr names the remote's sha, <sha> and the branch; a process case in a real git repository with a bare remote at another sha and a fake gh, setting VERI_POLL large and asserting the call returns without sleeping ⟦criterion 1⟧ | 13 | 3 | 2 | 0 | 0 | 0 | 323 | 79 | 136 | 36930 | 2340278 | 448030 | 2.40 | unknown | red 2/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 34 | 29 | 30 |  |  |  |  |  |  |  |  |  |  |  |
| affected | 5 | 3 | 3 | 3 | 5 | 5 | 20 | 19 | 18 | 18 | 18 | 19 | 18 | 762 |
| target | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 19 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 123 | 224 | 58507 | 3640410 | 694042 | 5.82 (estimate) |
