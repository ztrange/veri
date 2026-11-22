{{SHARED}}

## Phase: develop-test-quality

The run's steps are done. Before its pull request is readied, read the test files this run
touched and report the cases among them that a reviewer should not trust as they stand. No
verifier checks this report, so **change no file and make no commit**: read, judge, report.

### The test files

{{TEST_FILES}}

{{INCLUDE:../../SMELLS.md}}

Judge the cases of the files above by the catalogue's **Rules for test code**.

{{INCLUDE:_develop-spec-context-only.md}}

1. Read each test file above in full, and the code its cases exercise.
2. Report each case of those files that is one of these kinds, each on its own line:
   - `weak-assertion`: the case asserts less than its criterion's observable.
   - `redundant`: the case asserts nothing another case of those files does not.
   - `implementation-coupled`: the case imports or asserts on a name private to the code
     under test, or computes its expected value with that code.
   - `fixed-wait`: the case sleeps a fixed time, or waits out a window of fixed length, for a
     condition it could wait on directly under a timeout.
3. Name each case as `<file>::<case>`, the file as listed above and the case as its file
   defines it, and say in one line why it is that kind.
4. When no case of those files is one of those kinds, report the one line `FINDING: none`.

### Report (last lines of your output)

FINDING: <weak-assertion | redundant | implementation-coupled | fixed-wait> | <file>::<case> | <why, in one line>

one line per finding, or

FINDING: none

REPORT-FORMAT test-quality | keys FINDING: | suite exempt: the leaf changes no file and runs no suite
