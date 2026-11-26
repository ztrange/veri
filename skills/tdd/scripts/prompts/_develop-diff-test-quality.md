**This is a test-quality step.** Fix only the one test case the step names, so that it no
longer has the weakness the step states, and change no production code and no other case.
Commit the fix as a `test:` commit, its subject starting `test:`. Then add one report line
that lets the conductor prove the fixed case live, by flipping its expected value and
seeing it go red:

FLIP: <test file> '<old>→<new>'

`<test file>` is the fixed case's file, `<old>` a literal of the fixed case's expected value
exactly as the file holds it after your commit, and `<new>` a different value that the code
under test does not produce.

If the strengthened case is red against the current code, it may have found a bug, so the
above commit and `FLIP:` line do not apply. Revert the case, commit nothing for it, change no
production code, and report one line instead, where `<X>` is what the case expects and `<Y>`
what the code yields:

POSSIBLE-BUG: <file>::<case> expects <X>, code yields <Y>
