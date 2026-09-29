### 📊 Metrics — issue 134

Wall time for the issue: 0 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 7376 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/572.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 1 | 2 | 0 | 0 | 29 | 3 | 6 | 3622 | 34872 | 81388 | 0.37 |
| red | 8 | 2 | 0 | 0 | 0 | 230 | 67 | 126 | 23859 | 2636390 | 306433 | 1.99 |
| green | 6 | 2 | 1 | 0 | 0 | 167 | 52 | 94 | 16227 | 1923465 | 181173 | 1.27 |
| refactor | 4 | 2 | 0 | 0 | 0 | 39 | 17 | 34 | 3597 | 567217 | 118303 | 0.62 |
| pin | 4 | 4 | 0 | 0 | 0 | 92 | 29 | 58 | 9508 | 1096483 | 135492 | 0.86 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.90 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| projects/docs/build-walkthrough.py renders a skills/tdd/scripts/*.sh that has no commentary.SCRIPTS entry in a sandbox build: exit 0, a section whose id is derived from the filename, and the script's source verbatim ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 210 | 63 | 120 | 19485 | 2456798 | 250355 | 1.69 | 0 | 1/2 | 0/5 | nothing-left |  |  | full |
| that unlisted script's whole file sits under the existing "commentary owed" mark, and the build's stderr `owed:` summary names it (owed: <script> L1–<last>) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 26 | 4535 | 494491 | 68242 | 0.42 | unknown | unknown | unknown | unknown |  |  | pin |
| the masthead and table-of-contents counts (script count, total source lines, the upkeep table and rail) include the unlisted script, and an unlisted script adds no git question beyond the one-per-script budget ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 19 | 38 | 7218 | 805674 | 78342 | 0.55 | unknown | unknown | unknown | unknown |  |  | pin |
| projects/docs/check-walkthrough.py passes on a page built from a sandbox carrying an unlisted script ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 24 | 46 | 7862 | 991082 | 80224 | 0.60 | unknown | unknown | unknown | unknown |  |  | pin |
| projects/docs/docs-owed.sh lists a script present on disk but absent from commentary.SCRIPTS as `unlisted: <script>`, whether or not the page has been rebuilt since ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 35 | 64 | 9764 | 1145466 | 191086 | 1.09 | 0 | unknown | 0/5 | nothing-structural |  |  | full |
| projects/docs/docs-owed.sh still exits 3 with no output when every script is listed and covered ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 11 | 18 | 4327 | 330044 | 73152 | 0.40 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| projects/docs/build-walkthrough.py renders a skills/tdd/scripts/*.sh that has no commentary.SCRIPTS entry in a sandbox build: exit 0, a section whose id is derived from the filename, and the script's source verbatim ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 0 | 0.29 |
| projects/docs/docs-owed.sh lists a script present on disk but absent from commentary.SCRIPTS as `unlisted: <script>`, whether or not the page has been rebuilt since ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 0 | 0.33 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
