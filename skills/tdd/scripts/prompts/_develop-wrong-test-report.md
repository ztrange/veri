

or, when the green you are redoing has a test that looks wrong, those lines replaced by one:

WRONG_TEST: <why the test looks wrong>

Name in that line the existing test case the step's criterion contradicts.
Name the case by its own name as its test file spells it, with no describe, class or file prefix.

or, when older cases fail only because the step supersedes what they pin, those lines replaced by
one per such case:

SUPERSEDED: <the older case's name, written out in full as its test file spells it, without quotes>

A case the step's change does not supersede is a `WRONG_TEST:` line, never a `SUPERSEDED:` one.
