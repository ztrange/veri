

or, when the green you are redoing has a test that looks wrong, those lines replaced by one:

WRONG_TEST: <why the test looks wrong>

Only when the step's criterion contradicts an existing test case other than the step's own, add a separate line:

CONTRADICTS: <case>

Name the case by its own name as its test file spells it, with no describe, class or file prefix. A case cited only as evidence that the step's own test is wrong is named in the `WRONG_TEST:` text, never on a `CONTRADICTS:` line.

or, when older cases fail only because the step supersedes what they pin, those lines replaced by
one per such case:

SUPERSEDED: <the older case's name, written out in full as its test file spells it, without quotes>

A case the step's change does not supersede is a `WRONG_TEST:` line, never a `SUPERSEDED:` one.
