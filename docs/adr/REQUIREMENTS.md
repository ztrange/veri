## docs/adr/0016-uncovered-lines-are-debt-the-page-reports.md

| ID | Requirement | Why |
|---|---|---|
| AG1 | `docs/build-walkthrough.py` used to fail when `docs/wt/commentary.py` left any line of any script uncovered, with `make docs` exiting 1, and no longer does. (Opening paragraph.) | The record names the behaviour it reverses. |
| AG2 | Uncovered lines render exactly as every other line does, the note column beside them says `commentary owed`, and the build prints `owed: <script> L<a>–<b>` on stderr and exits 0. (Opening paragraph.) | The debt is shown and reported, not hidden. |
| AG3 | What stays fatal is a listing that could not be rendered at all: a chunk that claims lines another chunk already claimed, a chunk that runs past the end of the file, and a `{{p-id|…}}` naming a reference entry that does not exist, which is a typo, not debt. (Opening paragraph.) | A wrong page is still refused. |
| AG4 | The page's promise is stated in two halves: the source it shows is always verbatim, the file as it is today; the prose beside it may lag, and where it lags the page says so. (Second paragraph.) | Readers can trust the listing whether or not it is explained. |
| AG5 | The old guard charged every script-touching PR at merge time for prose, a `make docs` regen commit and the amend-past-the-tag dance, while the listing could not drift anyway because the generator reads the scripts. (Context, first paragraph.) | Why the strict build was not worth its cost. |
| AG6 | Rejected: a per-script allow-list of "prose pending" files, a second place to keep in sync that goes stale silently; and keeping the build strict but not running it at merge, which hides the debt and leaves the next `make docs` broken. (Context, second paragraph.) | The alternatives are on record, so they are not re-proposed. |
| AG7 | Development and documentation decouple: `docs/merge-gates.sh` owes no `docs-fresh` for a change under `skills/`, and `docs/docs-owed.sh` lists the scripts with uncovered lines, the scripts whose blame is newer than the page's build and the tags the capability index does not list, and with `--file` keeps one issue in the `ready-for-agent:docs` pool holding that list. (Consequences.) | Where the debt is filed instead of blocking a merge. |

## docs/adr/0018-a-preamble-token-is-priced-per-night.md

| ID | Requirement | Why |
|---|---|---|
| AP1 | An auto-loaded file is re-sent and re-billed at cache-read rates on every request of every session that loads it, so the unit that matters before adding prose to `CLAUDE.md` or `skills/tdd/SKILL.md` is a rate, not the file's size or a past cut's share of a bill. (Opening paragraph.) | The decision is about pricing prose before it is written. |
| AP2 | The rate: one preamble token resident in every request costs ~$0.0019 per night, about $1.90 per thousand tokens, at 1,285 requests a night; a token resident only in a conductor's requests costs ~$0.00062 a night, ~$0.62 per thousand, at 410 of them. (Opening quote.) | The figure a reader multiplies by. |
| AP3 | The rate was measured on the overnight run of 2026-09-14 22:00 → 2026-09-15 06:08 and is quoted with that date, because a price per night is meaningless without the night it was counted on; a later run at a different volume supersedes it. (Paragraph after the quote.) | A dated figure can be seen to be out of date. |
| AP4 | That night ran 1,285 deduplicated requests across 94 sessions for $313, 410 of them conductors, and the rate is arithmetic on those counts and a cache-read price of $1.50 per million tokens. (Context, first paragraph.) | The rate can be recomputed from what is recorded. |
| AP5 | Applied to #202's two files, the rate reproduces what #202 measured: `skills/tdd/SKILL.md` 19,449 tokens at $0.00062, ~$12 a night; `CLAUDE.md` 3,607 tokens at $0.0019, ~$7; #202's scope-loop cut −1,676 tokens, −$1.03. (Context, table.) | The check that the rate is the right unit. |
| AP6 | Rejected: a maximum size asserted by a test on either file, because the price is an input to a judgement, not the judgement; and a figure recomputed by a script at build time, because a record should hold still and be seen to be out of date. (Context, last paragraph.) | The alternatives are on record. |
| AP7 | Prose added to an auto-loaded file can be priced before it is written (tokens × the rate), and prose only one phase needs can move behind a `Read`, at the cost that a conductor which must read a file before it can act might fail to read it; the figure goes stale by design and is replaced by an ADR that supersedes this one with its own date and counts. (Consequences.) | How the rate is used, and how it is retired. |

## docs/adr/0019-the-contingent-half-of-skill-md-stays-resident.md

| ID | Requirement | Why |
|---|---|---|
| AC1 | Of the three cuts #202 tabled to the conductor's preamble it took one, the scope loop (1,676 tokens, now behind a `Read` on a branch decided at turn 1), and the other two are declined: not backlog, not "later", not blocked on anyone's time. (Opening paragraph.) | Declined, not deferred, so nobody re-files them. |
| AC2 | The two declined cuts are the once-per-run procedure (3,684 tokens, 18.9% of the file) and the contingent paths the conductor takes when something has already gone wrong, pin, revise, bail and resume (3,142 tokens, 16.2%). (Opening list.) | Names exactly what stays resident. |
| AC3 | Together they are 6,826 tokens, ~$4.20 a night at ADR-0018's conductor rate, stated as the price of the decision. (Paragraph after the list.) | The cost is recorded, not rediscovered as an argument. |
| AC4 | A `Read` can fail: on a wrong path after a rename, on a leaf's tree that is not the conductor's, on a model that skips it; for the scope loop the failure is cheap because the branch is chosen at turn 1, before anything has started. (Context, second paragraph.) | Why the same mechanism was safe for the one cut taken. |
| AC5 | The contingent paths are read on the turn something is already broken, and a conductor that must read a file before it can bail is a conductor that might not bail: progress is not preserved, the branch is not pushed, the issue carries no classified diagnosis; the once-per-run procedure fails the same way. (Context, third paragraph.) | The hazard that declines the cuts. |
| AC6 | Rejected alongside: moving the sections and keeping a summary resident, which pays twice and leaves two statements to drift; and deferring the question. (Context, last paragraph.) | The alternatives are on record. |
| AC7 | That half of `skills/tdd/SKILL.md` is closed: a table showing again that it is large is no reason to reopen it, and what would reopen it is a mechanism that makes the read unfailable, such as the harness loading the file for the branch, or a bail that cannot be reached without it. (Consequences, first paragraph.) | Says what evidence would change the decision. |
| AC8 | `CLAUDE.md` is untouched by this decision: its case histories are reasoning a leaf cannot act on, a different judgement and #202's third step. (Consequences, last paragraph.) | The decision's scope is one file. |
