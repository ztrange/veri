{{SHARED}}

## Phase: verify-branch

The whole branch is under judgement against the issue's acceptance criteria. The run
branched at `{{BASE_SHA}}`. Judge the whole branch against the issue's criteria from
`git diff {{BASE_SHA}}..HEAD` alone, and do not read the range's commit messages:
`git log` and `git show` on the range carry the author's rationale.

### The issue's behavior spec

{{ISSUE_SPEC}}

Run the fast command, `{{FAST_CMD}}`, then the test files covering the files the
diff touched, as `affected-suites.sh` prints them, each through the wrapper:

{{INCLUDE:_exit-status-back.md}} so a red run stays red.

PASS if the branch satisfies every acceptance criterion. REJECT, naming each criterion or
behaviour the diff leaves unmet or unpinned by a case, otherwise, and write one
`MISSING_TEST: <behaviour>` line for each criterion or behaviour no case pins. REJECT, too, if the fast
command or those test files are red. End with `VERDICT: PASS` or `VERDICT: REJECT`.
