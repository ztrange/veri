{{SHARED}}

## Phase: verify-pin

You judge 1 to 5 tests, `{{TEST_PATHS}}`, against the step's criterion, for a
criterion the code **already satisfies**, so there is nothing to make fail. Read them as they
stand at `HEAD`, never at the branch point: an earlier step of this run most often built the
behaviour they cover. Either they are existing tests the developer names as already covering the
criterion (`HOLDS`: committed at `HEAD`, and `git status` shows no change), or one of them is the
test the step added, the uncommitted change on top of `HEAD` (`PASSES`).

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **It passes now.** Run every named test yourself against the current, unmodified code.
   Each must **pass** — not error, not skip. Make each run through the wrapper
   {{INCLUDE:_timed-test-run.md}}
   and names the tier each belongs to:

       {{TIMED_TEST_RUN}} target '<test id>' <the command that runs that test>

   {{INCLUDE:_exit-status-back.md}} so a failing run stays
   failing — and any named test failing is a REJECT naming it.
2. **They cover the criterion.** Together, the named tests assert the criterion's observable
   outcome. A test that runs the code without asserting that outcome, or asserts a
   neighbouring behaviour, does not cover it: REJECT naming what no named test asserts. When
   the spec has a `## Bug` section, the bug paragraph after these checks (`_verify-red-bug.md`,
   the one verify-red reads) reaches you, and
   coverage means the named tests assert the bug's *Expected*; read it for a pin, whose tests
   pass, so no failure of theirs is matched against *What happened*.
3. **Quality of the test** — only for a test the step added (`PASSES`), never for an existing
   one (`HOLDS`), whose style is not this step's product. REJECT if the test is:
   - **missing a named case** — the step's text names a test case the step asks to be
     pinned (a "separate case", a second behaviour) and the change adds no case for it:
     REJECT naming the missing case, or
   - **trivial** — it asserts a constant or something no plausible change could break, or
   - **over-coupled** — it asserts on private internals / implementation details rather
     than the observable behavior the spec describes, or
   - **too complex** — it pins more than this one criterion, or is so elaborate its own
     correctness is in doubt, or
   - **pins mechanism, not behaviour** — it asserts a process count, a fork count, or a
     timing (those belong to `make profile`, never to an assertion), or counts real
     process launches via a `PATH` shim over a suite run where the criterion actually names
     a single call: that call belongs to an in-process spy on the one wrapper function, not
     a shim counting real processes, or
   - **not lightweight** — it exercises a costly real dependency (network, a git remote,
     the `claude` binary, a real sleep/wait, a server) that a stub, fake or the injected
     clock could stand in for, and the behavior under test is not that dependency's real
     use, or
   - **fails on an incidental error** — its only observable is that something throws or
     exits non-zero, with no assertion on which error or on the behaviour, unless that
     specific error is what the criterion names, or
   - **not self-contained** — it runs another test suite, whole or sliced, or re-runs the
     suite it lives in, instead of exercising the unit directly.

{{BUG_REPRODUCTION}}
PASS only if every check that applies holds: checks 1 and 2 always, check 3 only on `PASSES`.
Leave the working tree exactly as you found it.
